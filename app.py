from flask import Flask, request, jsonify
import spacy
from sentence_transformers import SentenceTransformer, util
import torch
from books_dataset import book_dataset
from keybert import KeyBERT
from fuzzywuzzy import process

app = Flask(__name__)

# Load NLP models
nlp = spacy.load("en_core_web_sm")
model = SentenceTransformer("all-mpnet-base-v2")
kw_model = KeyBERT(model)

# Precompute book embeddings
book_descriptions = [book["description"] for book in book_dataset]
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
    query_embedding = model.encode(user_preferences, convert_to_tensor=True)
    cosine_similarities = util.pytorch_cos_sim(query_embedding, book_embeddings)[0]
    top_indices = torch.argsort(cosine_similarities, descending=True)[:10]
    recommended_books = [book_dataset[i] for i in top_indices]
    return jsonify({"matched_books": recommended_books})

@app.route("/search_book", methods=["GET"])
def search_book():
    title = request.args.get("title", "")
    if not title:
        return jsonify({"error": "Book title is required"}), 400
    best_match, score = process.extractOne(title, [book["title"] for book in book_dataset])
    if score < 60:
        return jsonify({"message": "No close matches found.", "book": None})
    matched_book = next((book for book in book_dataset if book["title"] == best_match), None)
    return jsonify({"book": matched_book})

@app.route("/chat_recommendations", methods=["POST"])
def chat_recommendations():
    data = request.get_json()
    conversation = data.get("conversation", "")
    if not conversation:
        return jsonify({"error": "Conversation is empty"}), 400
    doc = nlp(conversation)
    extracted_entities = [ent.text for ent in doc.ents]
    if not extracted_entities:
        extracted_keywords = kw_model.extract_keywords(conversation, keyphrase_ngram_range=(1, 2), stop_words="english", top_n=3)
        extracted_entities = [keyword[0] for keyword in extracted_keywords]
    if not extracted_entities:
        return jsonify({"message": "No key topics detected. Try again!", "matched_books": []}), 200
    query_embedding = model.encode(" ".join(extracted_entities), convert_to_tensor=True)
    similarity_scores = util.pytorch_cos_sim(query_embedding, book_embeddings)[0]
    top_indices = torch.argsort(similarity_scores, descending=True)[:5]
    matched_books = [book_dataset[i] for i in top_indices]
    return jsonify({"matched_books": matched_books})

@app.route("/market", methods=["GET"])
def market():
    return jsonify({"market_books": book_dataset})

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
        "id": len(book_dataset) + 1,
        "title": title,
        "description": description,
        "price": int(price),
        "seller": username
    }
    book_dataset.append(new_book)
    return jsonify({"message": "✅ Book listed for sale!", "market_books": book_dataset})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)