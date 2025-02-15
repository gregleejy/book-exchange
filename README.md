# 📚 Peer-to-Peer Book Exchange Platform

An AI-powered **Peer-to-Peer Book Exchange Platform** that enables users to buy, sell, and exchange books while leveraging **AI-driven recommendations** for books and friends. The platform features **personalized book matching**, a **chatbot for book discovery**, a **leaderboard**, a **virtual shop**, and **AI-powered friend recommendations**.

## 🚀 Features

- **📖 AI-Powered Book Recommendations** (Based on user preferences & chat conversations)
- **🤖 Chatbot for Book Suggestions** (Extracts entities and keywords for better matches)
- **👥 Friend Recommendations** (Finds users with similar reading interests)
- **🏆 Leaderboard** (Tracks user engagement through points)
- **🛒 Virtual Shop** (Redeem points for book-related rewards)
- **🔄 Book Marketplace** (Buy, sell, and exchange books with other users)
- **🧑‍🏫 Study Groups** (Engage in discussions with users of similar interests)
  
---

## 🧠 AI Models Implemented

This project leverages **Natural Language Processing (NLP) models** and **Machine Learning techniques** to enhance book and friend recommendations.

### 📚 Book & Chat Matching
| Model/Technique  | Purpose |
|------------------|---------|
| `SentenceTransformer (all-MiniLM-L6-v2)` | Used for **semantic similarity** between book descriptions and user preferences/chat |
| `KeyBERT` | Extracts **key topics** from user conversations for chatbot recommendations |
| `TF-IDF Vectorization` | Generates **numerical representations** of text for alternative book recommendations |
| `Cosine Similarity` | Measures **text similarity** for matching books and friends |
| `Spacy (en_core_web_sm)` | Performs **Named Entity Recognition (NER)** for better book extraction from user queries |

### 👫 Friend Matching
| Model/Technique  | Purpose |
|------------------|---------|
| `TF-IDF Vectorization` | Converts friend preferences into **vector representations** |
| `Cosine Similarity` | Matches users based on **reading preferences** |

---

## 🛠️ Installation

### 📌 Prerequisites

- **Python 3.9+**
- **pip**
- **Flask**
- **PyTorch**
- **scikit-learn**
- **pandas**
- **spacy**
- **sentence-transformers**
- **keybert**
- **fuzzywuzzy**
- **torch**

### 📥 Setup Guide

```sh
# 1️⃣ Clone the Repository
git clone https://github.com/gregleejy/book-exchange-platform.git
cd book-exchange-platform

# 2️⃣ Install Dependencies
pip install -r requirements.txt

# 3️⃣ Download Spacy NLP Model
python -m spacy download en_core_web_sm

# 4️⃣ Run the Flask API
python app.py
```

---

## 🎯 API Endpoints

### 🔹 User Authentication
#### **1️⃣ Login**
```http
POST /login
```
**Request Body:**
```json
{
  "username": "greg"
}
```
**Response:**
```json
{
  "message": "Welcome, greg!",
  "points": 0
}
```

#### **2️⃣ Save User Preferences**
```http
POST /save_preferences
```
**Request Body:**
```json
{
  "username": "greg",
  "preferences": ["Science Fiction", "Fantasy", "Self-Help"]
}
```
**Response:**
```json
{
  "message": "Preferences saved successfully!",
  "preferences": ["Science Fiction", "Fantasy", "Self-Help"]
}
```

---

### 🔹 AI-Powered Book Recommendations
#### **3️⃣ Match Books Based on Preferences**
```http
GET /match_books?username=greg
```
**Response:**
```json
{
  "matched_books": [
    {
      "title": "Dune",
      "description": "A sci-fi classic about interstellar politics and survival."
    },
    {
      "title": "The Hobbit",
      "description": "A prelude to The Lord of the Rings."
    }
  ]
}
```

#### **4️⃣ Chatbot Book Recommendations**
```http
POST /chat_recommendations
```
**Request Body:**
```json
{
  "conversation": "I want a book about futuristic societies and AI."
}
```
**Response:**
```json
{
  "matched_books": [
    {
      "title": "Neuromancer",
      "description": "A deep dive into cyberpunk and AI."
    },
    {
      "title": "The Three-Body Problem",
      "description": "A science fiction novel about contact with an alien civilization."
    }
  ]
}
```

---

### 🔹 AI-Based Friend Matching
#### **5️⃣ Recommend Friends**
```http
POST /recommend_friends
```
**Request Body:**
```json
{
  "preferences": ["Self-Help", "Business"]
}
```
**Response:**
```json
{
  "matched_friends": [
    {
      "name": "Alice",
      "preferences": ["Self-Help", "Psychology"],
      "status": "Active"
    },
    {
      "name": "Bob",
      "preferences": ["Business", "Finance"],
      "status": "Looking for books"
    }
  ]
}
```

---

### 🔹 Book Marketplace
#### **6️⃣ View Market**
```http
GET /market
```
**Response:**
```json
{
  "market_books": [
    {
      "title": "The Lean Startup",
      "description": "A deep dive into business growth strategies.",
      "price": 20
    },
    {
      "title": "The Hobbit",
      "description": "A classic fantasy novel.",
      "price": 18
    }
  ]
}
```

#### **7️⃣ Sell a Book**
```http
POST /market/add
```
**Request Body:**
```json
{
  "username": "greg",
  "title": "The Subtle Art of Not Giving a F*ck",
  "description": "A self-help book on letting go of stress.",
  "price": 10
}
```
**Response:**
```json
{
  "message": "✅ Book listed for sale!",
  "market_books": [...]
}
```

---

## 📜 Future Enhancements

- **🔍 Improved AI Friend Matching**: More sophisticated similarity calculations
- **📢 Community Discussion Forum**: A space for users to discuss books
- **🎮 Gamification Features**: More rewards & challenges
- **📊 User Book Analytics**: Insights into user reading habits
- **📡 API Integration with External Bookstores**: Fetch book details dynamically

---

## 🏆 Contributors

- **👨‍💻 Gregory Lee (@gregleejy)** - **AI & Backend**
- **🛠 Open for Contributions!** 🚀 

---

## 📜 License

MIT License © 2025 Greg Lee
