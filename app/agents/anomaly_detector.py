"""Anomaly detection agent for log analysis."""

import re
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import Counter, defaultdict
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from app.agents.base import BaseAgent, Anomaly, AnalysisResult
from app.llm.manager import LLMManager
from app.llm.base import LLMMessage


class AnomalyDetectorAgent(BaseAgent):
  """Agent for detecting anomalies in log data."""
  
  def validate_config(self) -> None:
    """Validate agent configuration."""
    required_fields = ["llm_provider", "sensitivity"]
    for field in required_fields:
      if field not in self.config:
        raise ValueError(f"Missing required field: {field}")
    
    if self.config["sensitivity"] not in ["low", "medium", "high"]:
      raise ValueError("Sensitivity must be low, medium, or high")
  
  async def analyze(self, data: List[Dict[str, Any]]) -> AnalysisResult:
    """Analyze log data for anomalies."""
    if not data:
      return AnalysisResult(
        anomalies=[],
        summary="No data provided for analysis",
        recommendations=[],
        metrics={}
      )
    
    # Initialize LLM manager
    llm_manager = LLMManager()
    
    # Perform statistical analysis
    statistical_anomalies = self._detect_statistical_anomalies(data)
    
    # Perform pattern analysis
    pattern_anomalies = await self._detect_pattern_anomalies(data, llm_manager)
    
    # Perform semantic analysis
    semantic_anomalies = await self._detect_semantic_anomalies(data, llm_manager)
    
    # Combine all anomalies
    all_anomalies = statistical_anomalies + pattern_anomalies + semantic_anomalies
    
    # Generate summary and recommendations
    summary = await self._generate_summary(data, all_anomalies, llm_manager)
    recommendations = await self._generate_recommendations(all_anomalies, llm_manager)
    
    # Calculate metrics
    metrics = self._calculate_metrics(data, all_anomalies)
    
    return AnalysisResult(
      anomalies=all_anomalies,
      summary=summary,
      recommendations=recommendations,
      metrics=metrics
    )
  
  def _detect_statistical_anomalies(self, data: List[Dict[str, Any]]) -> List[Anomaly]:
    """Detect statistical anomalies."""
    anomalies = []
    
    # Extract numerical features
    features = self._extract_features(data)
    
    if len(features) < 10:  # Need minimum data for statistical analysis
      return anomalies
    
    # Convert to numpy array
    X = np.array(features)
    
    # Apply isolation forest
    iso_forest = IsolationForest(
      contamination=self._get_contamination_level(),
      random_state=42
    )
    
    anomaly_labels = iso_forest.fit_predict(X)
    anomaly_scores = iso_forest.decision_function(X)
    
    # Create anomalies from detected outliers
    for i, (label, score) in enumerate(zip(anomaly_labels, anomaly_scores)):
      if label == -1:  # Anomaly detected
        severity = self._calculate_severity(score)
        
        anomaly = Anomaly(
          severity=severity,
          category="statistical_outlier",
          description=f"Statistical anomaly detected with score: {score:.3f}",
          confidence=abs(score),
          data={
            "row_index": i,
            "features": features[i],
            "anomaly_score": float(score)
          },
          detected_at=datetime.utcnow()
        )
        anomalies.append(anomaly)
    
    return anomalies
  
  async def _detect_pattern_anomalies(
    self, 
    data: List[Dict[str, Any]], 
    llm_manager: LLMManager
  ) -> List[Anomaly]:
    """Detect pattern-based anomalies using LLM."""
    anomalies = []
    
    # Analyze error patterns
    error_patterns = self._analyze_error_patterns(data)
    
    # Analyze frequency patterns
    frequency_anomalies = self._analyze_frequency_patterns(data)
    
    # Use LLM for complex pattern analysis
    if error_patterns or frequency_anomalies:
      llm_analysis = await self._analyze_with_llm(
        data, 
        error_patterns, 
        frequency_anomalies, 
        llm_manager
      )
      anomalies.extend(llm_analysis)
    
    return anomalies
  
  async def _detect_semantic_anomalies(
    self, 
    data: List[Dict[str, Any]], 
    llm_manager: LLMManager
  ) -> List[Anomaly]:
    """Detect semantic anomalies using LLM."""
    anomalies = []
    
    # Extract text content for analysis
    text_samples = self._extract_text_samples(data)
    
    if not text_samples:
      return anomalies
    
    # Use LLM to analyze semantic content
    messages = [
      LLMMessage(
        role="system",
        content="""You are an expert log analyst. Analyze the following log entries for anomalies, errors, or suspicious patterns. 
        Look for:
        1. Error messages or exceptions
        2. Unusual patterns in requests or responses
        3. Security-related issues
        4. Performance problems
        5. Configuration issues
        
        Return your analysis in JSON format with anomalies array containing severity, category, description, and confidence."""
      ),
      LLMMessage(
        role="user",
        content=f"Analyze these log entries:\n\n{json.dumps(text_samples[:50], indent=2)}"
      )
    ]
    
    try:
      response = await llm_manager.generate_response(
        messages=messages,
        provider_name=self.config["llm_provider"],
        temperature=0.3
      )
      
      # Parse LLM response
      llm_anomalies = self._parse_llm_response(response.content)
      anomalies.extend(llm_anomalies)
    
    except Exception as e:
      print(f"LLM analysis failed: {e}")
    
    return anomalies
  
  def _extract_features(self, data: List[Dict[str, Any]]) -> List[List[float]]:
    """Extract numerical features from log data."""
    features = []
    
    for entry in data:
      feature_vector = []
      
      # Extract timestamp-based features
      if "timestamp" in entry:
        try:
          # Convert timestamp to hour of day, day of week, etc.
          ts = datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
          feature_vector.extend([
            ts.hour,
            ts.weekday(),
            ts.day,
            ts.month
          ])
        except:
          feature_vector.extend([0, 0, 0, 0])
      else:
        feature_vector.extend([0, 0, 0, 0])
      
      # Extract status code features
      if "status" in entry:
        status = int(entry["status"]) if str(entry["status"]).isdigit() else 0
        feature_vector.append(status)
        feature_vector.append(1 if 400 <= status < 500 else 0)  # Client error
        feature_vector.append(1 if 500 <= status < 600 else 0)  # Server error
      else:
        feature_vector.extend([0, 0, 0])
      
      # Extract response time features
      if "response_time" in entry:
        try:
          response_time = float(entry["response_time"])
          feature_vector.append(response_time)
        except:
          feature_vector.append(0)
      else:
        feature_vector.append(0)
      
      # Extract text length features
      text_content = str(entry.get("message", "")) + str(entry.get("request", ""))
      feature_vector.append(len(text_content))
      feature_vector.append(text_content.count("ERROR"))
      feature_vector.append(text_content.count("WARN"))
      feature_vector.append(text_content.count("FATAL"))
      
      features.append(feature_vector)
    
    return features
  
  def _analyze_error_patterns(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze error patterns in the data."""
    error_counts = Counter()
    error_messages = []
    
    for entry in data:
      # Look for error indicators
      text_content = str(entry.get("message", "")) + str(entry.get("request", ""))
      
      if any(keyword in text_content.upper() for keyword in ["ERROR", "EXCEPTION", "FAILED", "FATAL"]):
        error_counts["error_entries"] += 1
        error_messages.append(text_content[:200])  # First 200 chars
    
    return {
      "error_count": error_counts["error_entries"],
      "error_rate": error_counts["error_entries"] / len(data) if data else 0,
      "sample_errors": error_messages[:10]
    }
  
  def _analyze_frequency_patterns(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze frequency patterns."""
    # Group by time intervals
    time_groups = defaultdict(int)
    
    for entry in data:
      if "timestamp" in entry:
        try:
          ts = datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
          # Group by 5-minute intervals
          interval = ts.replace(minute=(ts.minute // 5) * 5, second=0, microsecond=0)
          time_groups[interval] += 1
        except:
          continue
    
    if not time_groups:
      return {}
    
    # Calculate frequency statistics
    frequencies = list(time_groups.values())
    mean_freq = np.mean(frequencies)
    std_freq = np.std(frequencies)
    
    return {
      "mean_frequency": mean_freq,
      "std_frequency": std_freq,
      "max_frequency": max(frequencies),
      "min_frequency": min(frequencies),
      "frequency_cv": std_freq / mean_freq if mean_freq > 0 else 0
    }
  
  async def _analyze_with_llm(
    self,
    data: List[Dict[str, Any]],
    error_patterns: Dict[str, Any],
    frequency_anomalies: Dict[str, Any],
    llm_manager: LLMManager
  ) -> List[Anomaly]:
    """Use LLM to analyze patterns."""
    messages = [
      LLMMessage(
        role="system",
        content="""Analyze log patterns and identify anomalies. Look for unusual patterns in error rates, frequency changes, or other indicators of problems."""
      ),
      LLMMessage(
        role="user",
        content=f"""Analyze these log patterns:
        
        Error Patterns: {json.dumps(error_patterns, indent=2)}
        Frequency Patterns: {json.dumps(frequency_anomalies, indent=2)}
        
        Sample log entries: {json.dumps(data[:20], indent=2)}
        
        Identify any anomalies and return in JSON format."""
      )
    ]
    
    try:
      response = await llm_manager.generate_response(
        messages=messages,
        provider_name=self.config["llm_provider"],
        temperature=0.3
      )
      
      return self._parse_llm_response(response.content)
    except Exception as e:
      print(f"LLM pattern analysis failed: {e}")
      return []
  
  def _extract_text_samples(self, data: List[Dict[str, Any]]) -> List[str]:
    """Extract text samples for semantic analysis."""
    samples = []
    
    for entry in data:
      # Combine relevant text fields
      text_parts = []
      
      for field in ["message", "request", "error", "description"]:
        if field in entry and entry[field]:
          text_parts.append(str(entry[field]))
      
      if text_parts:
        samples.append(" | ".join(text_parts))
    
    return samples
  
  def _parse_llm_response(self, response: str) -> List[Anomaly]:
    """Parse LLM response into anomaly objects."""
    anomalies = []
    
    try:
      # Try to extract JSON from response
      json_start = response.find('{')
      json_end = response.rfind('}') + 1
      
      if json_start != -1 and json_end > json_start:
        json_str = response[json_start:json_end]
        data = json.loads(json_str)
        
        if "anomalies" in data:
          for anomaly_data in data["anomalies"]:
            anomaly = Anomaly(
              severity=anomaly_data.get("severity", "medium"),
              category=anomaly_data.get("category", "llm_detected"),
              description=anomaly_data.get("description", "LLM detected anomaly"),
              confidence=anomaly_data.get("confidence", 0.5),
              data=anomaly_data.get("data", {}),
              detected_at=datetime.utcnow()
            )
            anomalies.append(anomaly)
    
    except Exception as e:
      print(f"Failed to parse LLM response: {e}")
    
    return anomalies
  
  async def _generate_summary(
    self,
    data: List[Dict[str, Any]],
    anomalies: List[Anomaly],
    llm_manager: LLMManager
  ) -> str:
    """Generate analysis summary."""
    messages = [
      LLMMessage(
        role="system",
        content="Generate a concise summary of log analysis results, highlighting key findings and overall system health."
      ),
      LLMMessage(
        role="user",
        content=f"""Analyze {len(data)} log entries and found {len(anomalies)} anomalies.
        
        Anomaly breakdown:
        {self._get_anomaly_breakdown(anomalies)}
        
        Generate a professional summary."""
      )
    ]
    
    try:
      response = await llm_manager.generate_response(
        messages=messages,
        provider_name=self.config["llm_provider"],
        temperature=0.3
      )
      return response.content
    except Exception as e:
      return f"Analysis completed: {len(anomalies)} anomalies detected in {len(data)} log entries."
  
  async def _generate_recommendations(
    self,
    anomalies: List[Anomaly],
    llm_manager: LLMManager
  ) -> List[str]:
    """Generate recommendations based on anomalies."""
    if not anomalies:
      return ["No anomalies detected. System appears healthy."]
    
    messages = [
      LLMMessage(
        role="system",
        content="Generate actionable recommendations for addressing the detected anomalies."
      ),
      LLMMessage(
        role="user",
        content=f"""Based on these {len(anomalies)} anomalies, provide specific recommendations:
        
        {self._get_anomaly_breakdown(anomalies)}
        
        Provide 3-5 actionable recommendations."""
      )
    ]
    
    try:
      response = await llm_manager.generate_response(
        messages=messages,
        provider_name=self.config["llm_provider"],
        temperature=0.3
      )
      
      # Parse recommendations from response
      recommendations = []
      for line in response.content.split('\n'):
        if line.strip() and (line.strip().startswith('-') or line.strip().startswith('•')):
          recommendations.append(line.strip()[1:].strip())
      
      return recommendations if recommendations else ["Review detected anomalies and take appropriate action."]
    except Exception as e:
      return ["Review detected anomalies and take appropriate action."]
  
  def _get_anomaly_breakdown(self, anomalies: List[Anomaly]) -> str:
    """Get anomaly breakdown by severity."""
    severity_counts = Counter(anomaly.severity for anomaly in anomalies)
    category_counts = Counter(anomaly.category for anomaly in anomalies)
    
    breakdown = "Severity breakdown:\n"
    for severity, count in severity_counts.items():
      breakdown += f"  {severity}: {count}\n"
    
    breakdown += "\nCategory breakdown:\n"
    for category, count in category_counts.items():
      breakdown += f"  {category}: {count}\n"
    
    return breakdown
  
  def _calculate_metrics(self, data: List[Dict[str, Any]], anomalies: List[Anomaly]) -> Dict[str, Any]:
    """Calculate analysis metrics."""
    total_entries = len(data)
    total_anomalies = len(anomalies)
    
    severity_counts = Counter(anomaly.severity for anomaly in anomalies)
    
    return {
      "total_entries_analyzed": total_entries,
      "total_anomalies_detected": total_anomalies,
      "anomaly_rate": total_anomalies / total_entries if total_entries > 0 else 0,
      "severity_breakdown": dict(severity_counts),
      "critical_anomalies": severity_counts.get("critical", 0),
      "high_anomalies": severity_counts.get("high", 0),
      "medium_anomalies": severity_counts.get("medium", 0),
      "low_anomalies": severity_counts.get("low", 0)
    }
  
  def _get_contamination_level(self) -> float:
    """Get contamination level based on sensitivity."""
    sensitivity_map = {
      "low": 0.01,
      "medium": 0.05,
      "high": 0.1
    }
    return sensitivity_map.get(self.config["sensitivity"], 0.05)
  
  def _calculate_severity(self, score: float) -> str:
    """Calculate severity based on anomaly score."""
    abs_score = abs(score)
    if abs_score > 0.5:
      return "critical"
    elif abs_score > 0.3:
      return "high"
    elif abs_score > 0.1:
      return "medium"
    else:
      return "low"
  
  def get_capabilities(self) -> List[str]:
    """Get agent capabilities."""
    return [
      "statistical_anomaly_detection",
      "pattern_analysis",
      "semantic_analysis",
      "error_detection",
      "frequency_analysis",
      "llm_enhanced_analysis"
    ]
