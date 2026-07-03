# 🤝 Personalized Networking Assistant

An AI-powered networking assistant that helps users generate personalized conversation starters for professional events based on their interests and the event description. The application also provides fact-checking, conversation history, and feedback management.

---

## 📌 Project Overview

Networking at conferences, hackathons, seminars, and professional events can be challenging, especially when meeting new people.

The Personalized Networking Assistant uses AI to:
- Analyze the event description
- Understand user interests
- Generate personalized conversation starters
- Verify factual information
- Store conversation history
- Collect user feedback

---

## 🚀 Features

### ✅ AI Event Analysis
- Classifies event topics using NLP models.
- Identifies relevant categories from event descriptions.

### 💬 Personalized Conversation Starters
- Generates context-aware networking conversation starters.
- Uses GPT-2 text generation.

### ✅ Fact Checking
- Verifies information using Wikipedia.
- Provides reliable factual responses.

### 📜 Conversation History
- Stores previously generated networking suggestions.
- Allows users to review earlier conversations.

### ⭐ Feedback System
- Collects user feedback.
- Stores ratings and comments.

### 🎨 Modern Streamlit UI
- Glassmorphism-inspired interface
- Responsive design
- Interactive user experience

---

# 🛠️ Tech Stack

## Backend
- Python
- FastAPI
- Uvicorn

## Frontend
- Streamlit
- HTML
- CSS

## AI & NLP
- Hugging Face Transformers
- DistilBERT
- GPT-2

## Data Storage
- JSON Files

## APIs
- Wikipedia API

---

# 📂 Project Structure

```
personalized_networking_assistant/
│
├── app/
│   ├── main.py
│   ├── config.py
│   ├── models/
│   ├── routers/
│   └── services/
│
├── frontend/
│   └── ui.py
│
├── data/
│   ├── history.json
│   └── feedback.json
│
├── requirements.txt
└── README.md
```

---

# ⚙️ Installation

Clone the repository

```bash
git clone https://github.com/harikameka/personalized_networking_assistant.git
```

Go to the project directory

```bash
cd personalized_networking_assistant
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Run the Backend

```bash
python -m app.main
```

Server starts at

```
http://127.0.0.1:8000
```

Swagger Documentation

```
http://127.0.0.1:8000/docs
```

---

# ▶️ Run the Frontend

Open another terminal

```bash
streamlit run frontend/ui.py
```

The Streamlit interface will open automatically in your browser.

---

# 📡 API Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/generate` | Generate personalized conversation starters |
| POST | `/api/fact-check` | Verify facts |
| GET | `/api/history` | View conversation history |
| POST | `/api/feedback` | Submit user feedback |
| GET | `/api/feedback` | Retrieve feedback |

---

# 💡 Example Input

```json
{
  "event_description": "Google Cloud AI Summit",
  "user_interests": [
    "Python",
    "Machine Learning",
    "Generative AI"
  ]
}
```

---

# 📤 Example Output

```json
{
  "categories": [
    "Technology",
    "Artificial Intelligence"
  ],
  "conversation_starters": [
    "What inspired you to attend this AI summit?",
    "Have you explored Google's Gemini models?",
    "Which AI session are you most excited about?"
  ]
}
```

---

# 🧠 AI Workflow

```
User Input
      │
      ▼
Event Description
      │
      ▼
DistilBERT Classification
      │
      ▼
GPT-2 Conversation Generation
      │
      ▼
Wikipedia Fact Checking
      │
      ▼
History & Feedback Storage
      │
      ▼
Response to User
```

---

# 📸 Screenshots

Add screenshots here:

- Home Page
- Conversation Generator
- Fact Checker
- Swagger API
- Conversation History

---

# 🎯 Future Enhancements

- User Authentication
- Database Integration (MongoDB/PostgreSQL)
- Voice-based Conversation Suggestions
- Multi-language Support
- Cloud Deployment
- Mobile Responsive UI
- AI Recommendation Improvements

---

# 👩‍💻 Authors

**Harika Meka**

GitHub: https://github.com/harikameka

---

# 📄 License

This project is developed for educational and learning purposes.
