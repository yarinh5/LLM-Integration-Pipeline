# 🚀 Quick Start Guide - LLM Integration Pipeline

## התחלה מהירה בעברית

### 1. התקנה מהירה
```bash
# Windows
run.bat

# Linux/Mac
python run.py
```

### 2. הגדרת API Keys
ערוך את הקובץ `.env` והוסף את המפתחות שלך:
```env
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### 3. גישה לדשבורד
פתח את הדפדפן וגש ל: http://localhost:8000

## דוגמה מעשית: ניתוח לוגים של משחק

### שלב 1: יצירת Data Source
```bash
curl -X POST "http://localhost:8000/api/data-sources" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Game Server Logs",
    "type": "log",
    "config": {
      "file_path": "data/example_logs.json",
      "log_format": "json"
    }
  }'
```

### שלב 2: הפעלת ניתוח
```bash
curl -X POST "http://localhost:8000/api/analysis-jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Daily Game Log Analysis",
    "data_source_id": 1,
    "config": {
      "sensitivity": "medium",
      "llm_provider": "openai"
    }
  }'
```

### שלב 3: יצירת דוח
```bash
curl -X POST "http://localhost:8000/api/reports/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": 1,
    "format": "html"
  }'
```

## מה המערכת עושה?

1. **מחברת למקורות נתונים** - לוגים, מסדי נתונים, APIs
2. **מנתחת עם AI** - משתמשת ב-LLM לזיהוי אנומליות ובעיות
3. **יוצרת דוחות** - דוחות אוטומטיים עם המלצות
4. **מציגה בדשבורד** - ממשק ניהול מתקדם

## דוגמאות שימוש

### ניתוח לוגים של משחק
- זיהוי קריסות שרת
- ניתוח התנהגות שחקנים חריגה
- דוחות אוטומטיים לצוות DevOps

### ניתוח אבטחה
- זיהוי ניסיונות פריצה
- ניתוח לוגי גישה
- התראות אבטחה אוטומטיות

### ניתוח ביצועים
- זיהוי בעיות ביצועים
- ניתוח זמני תגובה
- המלצות אופטימיזציה

## פתרון בעיות נפוצות

### שגיאת API Key
```
❌ OpenAI API error: Invalid API key
```
**פתרון**: בדוק את הקובץ `.env` וודא שה-API key נכון

### שגיאת חיבור למסד נתונים
```
❌ Database connection failed
```
**פתרון**: הפעל את Docker Compose: `docker-compose up -d`

### שגיאת זיכרון
```
❌ Out of memory
```
**פתרון**: הגדל את הזיכרון ב-Docker או הפעל עם פחות נתונים

## תמיכה

- 📖 תיעוד מלא: `/docs`
- 🐛 דיווח באגים: GitHub Issues
- 💬 שאלות: GitHub Discussions

---

**בהצלחה! 🎉**
