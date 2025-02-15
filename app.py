from flask import Flask, request, jsonify
import pandas as pd
import torch
from sentence_transformers import SentenceTransformer, util
import spacy
from keybert import KeyBERT
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import torch.nn.functional as F


# ✅ Load books dataset from CSV
BOOKS_CSV_PATH = "books_dataset.csv"
books_df = pd.read_csv(BOOKS_CSV_PATH)

# ✅ Convert DataFrame to list of dictionaries (to maintain previous data structure)
books_data = books_df.to_dict(orient="records")

# Load CSV file
friends_df = pd.read_csv("friend_data.csv", encoding="utf-8")

# 🔹 Normalize column names (convert to lowercase & strip spaces)
friends_df.columns = friends_df.columns.str.strip().str.lower()

# Debugging: Print column names after conversion
print("Processed column names:", friends_df.columns.tolist())

# 🔹 Ensure 'preferences' column exists
if "preferences" in friends_df.columns:
    friends_df["preferences"] = friends_df["preferences"].fillna("").apply(lambda x: x.split(", ") if isinstance(x, str) else [])
else:
    raise KeyError(f"❌ ERROR: 'preferences' column not found! Available columns: {friends_df.columns.tolist()}")

# 🔹 Convert DataFrame to list of dictionaries
friend_data = friends_df.to_dict(orient="records")

# 🔹 Store leaderboard in-memory
leaderboard_data = [
    {"Rank": 1, "Username": "Alice", "Points": 720},
    {"Rank": 2, "Username": "Bob", "Points": 650},
    {"Rank": 3, "Username": "Charlie", "Points": 580},
    {"Rank": 4, "Username": "You", "Points": 470},  # Placeholder for current user
    {"Rank": 5, "Username": "Eve", "Points": 410},
]

# Static shop items available for redemption
shop_items = [
    {"item": "🎟️ Free Ticket to Art Science Museum", "points": 50},
    {"item": "🎫 20% Off Popular/Books Kinokuniya Voucher", "points": 60},
    {"item": "📖 Exclusive Collector's Edition Bookmarks", "points": 30},
    {"item": "📚 $10 Book Voucher for Local Bookstores", "points": 70},
    {"item": "☕ Free Coffee at Starbucks (Perfect for Bookworms!)", "points": 40},
    {"item": "📦 Mystery Book Box (Surprise Book Inside)", "points": 100},
    {"item": "🎧 3-Month Subscription to an Audiobook Service", "points": 90},
    {"item": "🛋️ VIP Lounge Access at National Library", "points": 120},
    {"item": "🖋️ Personalized Engraved Fountain Pen", "points": 80},
    {"item": "📅 Free Entry to a Literary Festival", "points": 110},
]

# Dummy friend group dataset
study_groups = [
    {
        "group_name": "Sci-Fi Enthusiasts",
        "members": ["Alice", "Bob", "Charlie"],
        "book_sharing": [{"user": "Charlie", "book": "Dune"}],
        "discussion_topic": "Best Sci-Fi world-building in literature?",
        "active_status": "🔥 Active Now",
    },
    {
        "group_name": "Business Bookworms",
        "members": ["David", "Emma", "Frank"],
        "book_sharing": [{"user": "Emma", "book": "The Lean Startup"}],
        "discussion_topic": "Is 'Zero to One' better than 'The Lean Startup'?",
        "active_status": "💬 Ongoing Discussion",
    },
    {
        "group_name": "Fantasy Legends",
        "members": ["George", "Hannah", "Ian"],
        "book_sharing": [{"user": "Hannah", "book": "The Hobbit"}],
        "discussion_topic": "Which fantasy novel has the best magic system?",
        "active_status": "🟢 3 members online",
    },
    {
        "group_name": "Self-Help Squad",
        "members": ["Jack", "Kate", "Leo"],
        "book_sharing": [{"user": "Jack", "book": "Atomic Habits"}],
        "discussion_topic": "What's one self-help book that changed your life?",
        "active_status": "🔵 2 members reading",
    },
    {
        "group_name": "History Buffs",
        "members": ["Mike", "Nancy", "Olivia"],
        "book_sharing": [{"user": "Mike", "book": "Sapiens"}],
        "discussion_topic": "What’s the best book about ancient civilizations?",
        "active_status": "📖 Quiet, deep discussion",
    },
    {
        "group_name": "Tech Geeks",
        "members": ["Paul", "Quinn", "Rachel"],
        "book_sharing": [{"user": "Quinn", "book": "Deep Learning"}],
        "discussion_topic": "AI books vs online courses: Which is better?",
        "active_status": "⚡ Rapid fire conversation",
    },
    {
        "group_name": "Philosophy & Psychology",
        "members": ["Sarah", "Tom", "Uma"],
        "book_sharing": [{"user": "Sarah", "book": "Thinking, Fast and Slow"}],
        "discussion_topic": "Is human behavior more predictable than we think?",
        "active_status": "🤔 Deep thinking",
    },
]

app = Flask(__name__)

# Load NLP models
nlp = spacy.load("en_core_web_sm")  # Small model for named entity recognition
kw_model = KeyBERT()  # KeyBERT for keyword extraction

# Load pre-trained sentence transformer for text similarity
model = SentenceTransformer("all-MiniLM-L6-v2")  # Lightweight and efficient model

# Ensure book descriptions are cleaned and tokenized
book_descriptions = [book["description"] for book in books_data]
book_embeddings = model.encode(book_descriptions, convert_to_tensor=True)

# In-memory user storage
users = {}  # {username: {"points": int, "books_shared": int, "categories": [], "friends": []}}

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    if not username:
        return jsonify({"error": "Username is required!"}), 400
    if username not in users:
        users[username] = {"points": 0, "books_shared": 0, "categories": [], "friends": []}
    return jsonify({"message": f"Welcome, {username}!", "points": users[username]["points"]})

@app.route("/save_preferences", methods=["POST"])
def save_preferences():
    data = request.get_json()
    username = data.get("username")
    preferences = data.get("preferences", [])
    if username not in users:
        return jsonify({"error": "User not found!"}), 403
    users[username]["categories"] = preferences
    return jsonify({"message": "Preferences saved successfully!", "preferences": preferences})

@app.route("/match_books", methods=["GET"])
def match_books():
    username = request.args.get("username")
    if username not in users:
        return jsonify({"error": "User not found!"}), 403

    user_preferences = " ".join(users[username].get("categories", []))

    if not user_preferences.strip():
        return jsonify({"message": "No preferences found. Showing popular books.", "matched_books": books_data[:5]})

    # Convert user preferences and books to TF-IDF vectors
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([user_preferences] + [book["description"] for book in books_data])

    # Compute cosine similarity scores
    similarity_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    # Get top 10 recommended books
    top_indices = similarity_scores.argsort()[-10:][::-1]
    recommended_books = [books_data[i] for i in top_indices]

    return jsonify({"matched_books": recommended_books})

@app.route("/search_book", methods=["GET"])
def search_book():
    title = request.args.get("title", "")
    if not title:
        return jsonify({"error": "Book title is required"}), 400
    best_match, score = process.extractOne(title, [book["title"] for book in books_data])
    if score < 60:
        return jsonify({"message": "No close matches found.", "book": None})
    matched_book = next((book for book in books_data if book["title"] == best_match), None)
    return jsonify({"book": matched_book})

# @app.route("/chat_recommendations", methods=["POST"])
# def chat_recommendations():
#     data = request.get_json()
#     conversation = data.get("conversation", "")

#     if not conversation:
#         return jsonify({"error": "Conversation is empty"}), 400

#     # Extract key topics using TF-IDF instead of KeyBERT
#     vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
#     tfidf_matrix = vectorizer.fit_transform([conversation] + [book["description"] for book in books_data])

#     # Compute cosine similarity
#     similarity_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

#     # Get top 5 book recommendations
#     top_indices = similarity_scores.argsort()[-5:][::-1]
#     matched_books = [books_data[i] for i in top_indices]

#     return jsonify({"matched_books": matched_books})

@app.route("/chat_recommendations", methods=["POST"])
def chat_recommendations():
    data = request.get_json()
    conversation = data.get("conversation", "")

    if not conversation:
        return jsonify({"error": "Conversation is empty"}), 400

    # Extract keywords using a language model
    doc = nlp(conversation)
    extracted_entities = [ent.text for ent in doc.ents]  # Named entities

    # If no named entities found, extract keywords using KeyBERT
    if not extracted_entities:
        extracted_keywords = kw_model.extract_keywords(
            conversation, keyphrase_ngram_range=(1, 2), stop_words="english", top_n=3
        )
        extracted_entities = [keyword[0] for keyword in extracted_keywords]

    # 🔹 New Fix: Use TF-IDF as a last resort for keyword extraction
    if not extracted_entities:
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform([conversation] + [book["description"] for book in books_data])
        feature_names = vectorizer.get_feature_names_out()
        top_tfidf_keywords = [feature_names[i] for i in tfidf_matrix[0].toarray().argsort()[0][-3:]]
        extracted_entities = top_tfidf_keywords

    if not extracted_entities:
        return jsonify({"message": "No key topics detected. Try again!", "matched_books": []}), 200

    # Convert extracted keywords to embeddings
    query_text = " ".join(extracted_entities[:5])  # Take only the top 5 keywords
    query_embedding = model.encode(query_text, convert_to_tensor=True)

    # Compute similarity between user query and book dataset embeddings
    similarity_scores = util.pytorch_cos_sim(query_embedding, book_embeddings)[0]

    top_indices = torch.argsort(similarity_scores, descending=True)[:10]  # Pick top 10
    import random
    random.shuffle(top_indices)  # Randomly shuffle to increase diversity
    recommended_books = [books_data[i.item()] for i in top_indices[:5] if 0 <= i.item() < len(books_data)]

    # Ensure index values are within bounds before accessing book_dataset
    recommended_books = [books_data[i.item()] for i in top_indices if 0 <= i.item() < len(books_data)]

    return jsonify({"matched_books": recommended_books})

# 🔹 AI-Based Friend Matching Endpoint
@app.route("/recommend_friends", methods=["POST"])
def recommend_friends():
    data = request.get_json()
    user_preferences = data.get("preferences", [])

    if not user_preferences:
        return jsonify({"matched_friends": []})

    # Convert preferences into strings for vectorization
    friend_preferences = [" ".join(f.get("preferences", [])) for f in friend_data]
    user_pref_str = " ".join(user_preferences)

    # ✅ Use TF-IDF for text vectorization (not embeddings)
    vectorizer = TfidfVectorizer(stop_words="english", lowercase=True, max_df=0.85)
    tfidf_matrix = vectorizer.fit_transform([user_pref_str] + friend_preferences)

    # ✅ Compute cosine similarity correctly using sklearn
    similarity_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    # ✅ Ensure scores are correctly ranked and sorted
    ranked_friends = sorted(zip(friend_data, similarity_scores), key=lambda x: x[1], reverse=True)[:5]

    matched_friends = [{"name": friend["name"], "preferences": friend["preferences"], "status": friend["status"]}
                       for friend, score in ranked_friends if score > 0]  # Filter out zero-similarity friends

    return jsonify({"matched_friends": matched_friends})

@app.route("/market", methods=["GET"])
def market():
    return jsonify({"market_books": books_data})

@app.route("/market/add", methods=["POST"])
def sell_book():
    data = request.get_json()
    username = data.get("username")
    title = data.get("title")
    description = data.get("description", "No description provided")
    price = data.get("price")
    if not username or not title or not price:
        return jsonify({"error": "All fields are required!"}), 400
    new_book = {
        "id": len(books_data) + 1,
        "title": title,
        "description": description,
        "price": int(price),
        "seller": username
    }
    books_data.append(new_book)
    return jsonify({"message": "✅ Book listed for sale!", "market_books": books_data})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)