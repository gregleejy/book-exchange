## **📚 Peer-to-Peer Book Exchange Platform POC**  

A **community-driven** web platform designed to facilitate **book exchange** through an AI-enhanced recommendation system. Users can **list books, search, exchange, donate, and participate in discussions** while earning rewards.  

---

## **🚀 Features**
- **Book Exchange Marketplace** – List and browse books based on user preferences.  
- **AI-Powered Matching** – Uses **SpaCy NER** to extract book-related entities for better recommendations.  
- **Scott Rizzgerald Chatbot 🤖** – A chatbot that suggests books based on user queries.  
- **Leaderboard & Reward System** – Users earn points for donating books and can redeem rewards.  
- **Friend Matching & Study Groups** – Find friends with similar reading preferences and engage in discussions.  

---

## **💾 Installation Guide**
### **1️⃣ Install Dependencies**
First, ensure **Python 3.8+** is installed. Then, install required libraries using:
```bash
pip install -r requirements.txt
```

### **2️⃣ Run the Backend API**
Start the Flask backend by running:
```bash
python app.py
```

### **3️⃣ Run the Frontend UI**
Start the Streamlit interface with:
```bash
streamlit run ui.py
```

The platform should now be accessible via **localhost** in your web browser.

---

## **📜 Project Structure**
```
📂 Peer-to-Peer Book Exchange Platform
├── 📜 app.py          # Backend Flask API for book management and AI recommendations
├── 📜 ui.py           # Streamlit frontend for user interaction
├── 📜 requirements.txt # List of required Python libraries
└── 📜 README.md       # Project documentation
```

---

## **⚙️ Technologies Used**
- **Backend**: Flask (for managing book data and AI recommendations)
- **Frontend**: Streamlit (for UI and user interactions)
- **Database**: Currently using in-memory data structures for quick prototyping (SQLite or PostgreSQL can be added for production)
- **AI Features**:  
  - **SpaCy NER** (for entity extraction in book recommendations)  
  - **Fuzzy Matching** (for book title search)

---

## **🔧 Future Enhancements**
- Implement **OAuth authentication** for user sign-in.  
- Expand book database with **external APIs** for real-time updates.  
- Introduce **Graph-based Friend Matching** for better networking.  

---

## **🤝 Contributing**
Feel free to contribute! Clone the repo and submit a pull request.  
```bash
git clone https://github.com/gregleejy/book-exchange-platform.git
```

---

## **📩 Contact**
For any issues, reach out via [GitHub Issues](https://github.com/gregleejy/book-exchange/issues).

---
