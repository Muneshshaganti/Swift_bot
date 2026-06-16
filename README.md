# SwiftIntelli Chatbot API

A FastAPI-based chatbot backend with:

- FAQ matching using RapidFuzz
- Intent-based responses
- Course information retrieval
- Context-aware follow-up questions
- Chat session management
- MySQL database integration
- Chat logging and unanswered-question tracking

## Project Structure

```text
.
├── main.py                # FastAPI application
├── chatbot_engine.py      # Core chatbot logic
├── db.py                  # MySQL database connection
├── models.py              # Pydantic request/response models
├── requirements.txt       # Python dependencies
└── README.md
```

## Features

### FAQ Matching
Uses RapidFuzz similarity matching to find the closest FAQ answer.

### Intent Recognition
Matches user messages against configured keywords and returns predefined responses.

### Course Search
Detects course-related keywords and returns course details such as:

- Title
- Duration
- Mode
- Language
- Category
- Description

### Context-Based Follow-Ups
Remembers the last selected course and answers questions like:

- What is the duration?
- What is the mode?
- What is the language?
- What is the fee?

### Session Management
Automatically creates and manages chat sessions.

### Logging
Stores:

- User messages
- Bot responses
- Chat logs
- Unanswered questions

---

## Requirements

- Python 3.10+
- MySQL Server

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/your-username/swiftintelli-chatbot.git
cd swiftintelli-chatbot
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate:

**Windows**
```bash
venv\Scripts\activate
```

**Linux / macOS**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Create .env File

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=chatbot_db
```

## Run the Application

```bash
uvicorn main:app --reload
```

Application URL:

```text
http://127.0.0.1:8000
```

## API Endpoints

### Health Check

```http
GET /health
```

Response:

```json
{
  "status": "healthy"
}
```

### Home

```http
GET /
```

### Chat Endpoint

```http
POST /chat
```

Request:

```json
{
  "session_id": "session_001",
  "message": "Tell me about Python course",
  "user_id": 1
}
```

Response:

```json
{
  "success": true,
  "data": {
    "response": "Course information...",
    "response_type": "course"
  }
}
```

## Database Tables

The application expects tables similar to:

- chat_sessions
- chat_messages
- chat_logs
- chat_faqs
- chat_keywords
- chat_intents
- chat_responses
- chat_fallbacks
- chat_course_keywords
- chat_context
- chat_unanswered_questions
- courses

## Dependencies

- FastAPI
- Uvicorn
- mysql-connector-python
- RapidFuzz
- NLTK
- python-dotenv
- python-multipart

## Production Recommendations

- Restrict CORS origins
- Use connection pooling
- Add authentication and authorization
- Replace keyword matching with NLP/LLM-based intent detection
- Add rate limiting
- Add structured logging
- Containerize with Docker

## License

MIT License
