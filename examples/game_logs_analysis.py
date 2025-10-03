#!/usr/bin/env python3
"""
דוגמה מעשית: ניתוח לוגים של משחק עם LLM Integration Pipeline

דוגמה זו מראה איך להשתמש במערכת לניתוח לוגים של שרת משחק,
זיהוי בעיות, וקבלת המלצות אוטומטיות.
"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.data_connectors.factory import DataConnectorFactory
from app.agents.anomaly_detector import AnomalyDetectorAgent
from app.reports.factory import ReportGeneratorFactory
from app.reports.base import ReportData


async def analyze_game_logs():
  """ניתוח לוגים של משחק - דוגמה מעשית."""
  
  print("🎮 ניתוח לוגים של משחק - LLM Integration Pipeline")
  print("=" * 60)
  
  # 1. יצירת דאטה לדוגמה
  print("\n📝 יוצר דאטה לדוגמה...")
  sample_logs = create_sample_game_logs()
  
  # שמירת הדאטה לקובץ
  log_file = Path("examples/game_logs.json")
  log_file.parent.mkdir(exist_ok=True)
  
  with open(log_file, "w") as f:
    for log in sample_logs:
      f.write(json.dumps(log) + "\n")
  
  print(f"✅ נוצר קובץ לוגים: {log_file}")
  
  # 2. הגדרת Data Connector
  print("\n🔌 מגדיר חיבור לנתונים...")
  connector_config = {
    "file_path": str(log_file),
    "log_format": "json"
  }
  
  connector = DataConnectorFactory.create_connector("log", connector_config)
  
  if not connector.test_connection():
    print("❌ שגיאה בחיבור לנתונים")
    return
  
  print("✅ חיבור לנתונים הוגדר בהצלחה")
  
  # 3. שליפת נתונים
  print("\n📊 שולף נתונים...")
  end_time = datetime.now()
  start_time = end_time - timedelta(hours=24)
  
  data = list(connector.fetch_data(start_time, end_time))
  print(f"✅ נשלפו {len(data)} רשומות לוג")
  
  # 4. ניתוח עם AI
  print("\n🤖 מפעיל ניתוח AI...")
  detector_config = {
    "llm_provider": "openai",  # או "anthropic"
    "sensitivity": "medium"
  }
  
  detector = AnomalyDetectorAgent(detector_config)
  
  try:
    result = await detector.analyze(data)
    print("✅ ניתוח AI הושלם בהצלחה")
    
    # הצגת תוצאות
    print(f"\n📈 תוצאות הניתוח:")
    print(f"   • סה\"כ אנומליות: {len(result.anomalies)}")
    print(f"   • אנומליות קריטיות: {len([a for a in result.anomalies if a.severity == 'critical'])}")
    print(f"   • אנומליות גבוהות: {len([a for a in result.anomalies if a.severity == 'high'])}")
    
    # הצגת אנומליות
    if result.anomalies:
      print(f"\n🚨 אנומליות שזוהו:")
      for i, anomaly in enumerate(result.anomalies[:5], 1):  # הצג 5 הראשונות
        print(f"   {i}. [{anomaly.severity.upper()}] {anomaly.description}")
        print(f"      קטגוריה: {anomaly.category}")
        print(f"      ביטחון: {anomaly.confidence:.1%}")
        print()
  
  except Exception as e:
    print(f"⚠️ ניתוח AI נכשל (ייתכן שחסר API key): {e}")
    
    # יצירת תוצאות לדוגמה
    result = create_sample_analysis_result()
    print("✅ השתמש בתוצאות לדוגמה")
  
  # 5. יצירת דוח
  print("\n📋 יוצר דוח...")
  report_data = ReportData(
    title="דוח ניתוח לוגים של משחק",
    summary=result.summary,
    anomalies=[anomaly.__dict__ for anomaly in result.anomalies],
    metrics=result.metrics,
    recommendations=result.recommendations,
    generated_at=datetime.utcnow(),
    data_source="Game Server Logs",
    analysis_period={
      "start": start_time.strftime("%Y-%m-%d %H:%M:%S"),
      "end": end_time.strftime("%Y-%m-%d %H:%M:%S")
    }
  )
  
  # יצירת דוח HTML
  html_generator = ReportGeneratorFactory.create_generator("html", {})
  html_content = await html_generator.generate_report(report_data)
  
  html_file = Path("examples/game_analysis_report.html")
  with open(html_file, "w", encoding="utf-8") as f:
    f.write(html_content)
  
  print(f"✅ דוח HTML נוצר: {html_file}")
  
  # יצירת דוח JSON
  json_generator = ReportGeneratorFactory.create_generator("json", {})
  json_content = await json_generator.generate_report(report_data)
  
  json_file = Path("examples/game_analysis_report.json")
  with open(json_file, "w", encoding="utf-8") as f:
    f.write(json_content)
  
  print(f"✅ דוח JSON נוצר: {json_file}")
  
  # 6. סיכום
  print(f"\n🎉 הניתוח הושלם בהצלחה!")
  print(f"\n📁 קבצים שנוצרו:")
  print(f"   • {log_file}")
  print(f"   • {html_file}")
  print(f"   • {json_file}")
  
  print(f"\n💡 המלצות:")
  for i, rec in enumerate(result.recommendations, 1):
    print(f"   {i}. {rec}")


def create_sample_game_logs():
  """יוצר לוגים לדוגמה של משחק."""
  logs = []
  base_time = datetime.now() - timedelta(hours=24)
  
  # דוגמאות לוגים של משחק
  game_events = [
    {"level": "INFO", "message": "Player connected", "status": 200},
    {"level": "INFO", "message": "Game started", "status": 200},
    {"level": "INFO", "message": "Player moved", "status": 200},
    {"level": "INFO", "message": "Player scored", "status": 200},
    {"level": "WARN", "message": "High latency detected", "status": 200},
    {"level": "ERROR", "message": "Connection timeout", "status": 500},
    {"level": "ERROR", "message": "Database connection failed", "status": 500},
    {"level": "ERROR", "message": "Memory allocation failed", "status": 500},
    {"level": "FATAL", "message": "Server crash", "status": 500},
  ]
  
  for i in range(1000):
    # הוספת וריאציה בזמן
    timestamp = base_time + timedelta(
      minutes=i // 10,
      seconds=i % 60
    )
    
    # בחירת אירוע
    event = game_events[i % len(game_events)]
    
    # הוספת אנומליות לדוגמה
    if i % 50 == 0:  # כל 50 רשומות
      event = {"level": "ERROR", "message": "CRITICAL: Server overload", "status": 500}
    elif i % 100 == 0:  # כל 100 רשומות
      event = {"level": "WARN", "message": "Suspicious player behavior detected", "status": 200}
    
    log_entry = {
      "timestamp": timestamp.isoformat(),
      "level": event["level"],
      "message": event["message"],
      "status": event["status"],
      "response_time": 0.1 + (i % 10) * 0.1,
      "player_id": f"player_{1000 + i}",
      "game_room": f"room_{i % 10}",
      "ip_address": f"192.168.1.{i % 254 + 1}",
      "user_agent": "GameClient/1.0"
    }
    
    logs.append(log_entry)
  
  return logs


def create_sample_analysis_result():
  """יוצר תוצאות ניתוח לדוגמה."""
  from app.agents.base import Anomaly, AnalysisResult
  
  anomalies = [
    Anomaly(
      severity="critical",
      category="server_crash",
      description="זוהו 5 קריסות שרת במהלך 24 השעות האחרונות",
      confidence=0.95,
      data={"crash_count": 5, "time_period": "24h"},
      detected_at=datetime.utcnow()
    ),
    Anomaly(
      severity="high",
      category="performance",
      description="זמני תגובה גבוהים מזוהים בחדר 3",
      confidence=0.87,
      data={"room": "room_3", "avg_response_time": 2.5},
      detected_at=datetime.utcnow()
    ),
    Anomaly(
      severity="medium",
      category="security",
      description="התנהגות חשודה מזוהה אצל שחקן player_1500",
      confidence=0.72,
      data={"player_id": "player_1500", "suspicious_actions": 15},
      detected_at=datetime.utcnow()
    )
  ]
  
  return AnalysisResult(
    anomalies=anomalies,
    summary="ניתוח לוגים של משחק הושלם. זוהו 3 אנומליות: קריסות שרת, בעיות ביצועים, והתנהגות חשודה.",
    recommendations=[
      "בדוק את הגדרות הזיכרון של השרת",
      "פנה לחדר 3 לבדיקת רשת",
      "חקור את התנהגות השחקן player_1500",
      "הגדר התראות אוטומטיות לזמני תגובה גבוהים"
    ],
    metrics={
      "total_entries_analyzed": 1000,
      "total_anomalies_detected": 3,
      "critical_anomalies": 1,
      "high_anomalies": 1,
      "medium_anomalies": 1
    }
  )


if __name__ == "__main__":
  asyncio.run(analyze_game_logs())
