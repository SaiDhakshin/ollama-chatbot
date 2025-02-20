from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from flask_cors import CORS  # Import CORS
import ollama
from textblob import TextBlob

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Sample FAQ Data
faq_data = [
  {
    "question": "How do I reset my password?",
    "answer": "To reset your password, go to the login page, click 'Forgot Password', and follow the instructions to receive a reset link in your email."
  },
  {
    "question": "What is your refund policy?",
    "answer": "We offer a full refund within 30 days of purchase if the product is unused and in its original packaging. Please contact support for assistance."
  },
  {
    "question": "How can I contact customer support?",
    "answer": "You can contact our customer support team via email at support@example.com or call us at +1-800-123-4567."
  },
  {
    "question": "Do you offer international shipping?",
    "answer": "Yes, we offer international shipping. Shipping fees and delivery times vary based on your location."
  },
  {
    "question": "How do I track my order?",
    "answer": "Once your order is shipped, you will receive an email with a tracking link. You can also track your order from the 'My Orders' section on our website."
  },
  {"question": "Can I get a refund?", "answer": "We offer a full refund within 30 days..."},
  {"question": "How do I get my money back?", "answer": "We offer a full refund within 30 days..."},
  {"question": "What is the refund policy?", "answer": "We offer a full refund within 30 days..."}
]

# Extract questions and generate embeddings
questions = [faq["question"] for faq in faq_data]
embeddings = model.encode(questions)
print(embeddings)

# Convert to FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))  # Add vectors to FAISS

print("FAQ Embeddings Shape:", embeddings.shape)
print("Sample Embedding:", embeddings[0][:5])  # Print first 5 values

def normalize_query(query):
    synonyms = {
        "change": "reset",
        "money back": "refund",
        "ship": "deliver",
    }
    for word, synonym in synonyms.items():
        query = query.replace(word, synonym)
    return query

def correct_spelling(query):
    return str(TextBlob(query).correct())

def generate_llama_response(query):
    prompt = f"Answer this customer support question: {query}"
    response = ollama.chat(model="llama3.2", messages=[{"role": "user", "content": prompt}])
    return response

def find_answer(query):
    print("FAISS Index Size:", index.ntotal)
    # Handle casual greetings
    greetings = {
        "hi": "Hello! How can I assist you today?",
        "hello": "Hi there! What can I help you with?",
        "hey": "Hey! How can I assist?",
        "good morning": "Good morning! How may I help you?",
        "good afternoon": "Good afternoon! Need any assistance?",
        "good evening": "Good evening! How can I assist you today?",
    }

    small_talk = {
        "how are you": "I'm just a bot, but I'm here to help!",
        "what's your name": "I'm your customer support assistant.",
        "who made you": "I was created to assist customers like you!",
        "what can you do": "I can answer FAQs, help with support queries, and provide information!",
    }


    lower_query = query.lower().strip()  # Normalize input
    if lower_query in greetings:
        return greetings[lower_query]
    if lower_query in small_talk:
        return small_talk[lower_query]
    
    # Otherwise, continue with FAISS search
    normalized_query = normalize_query(lower_query)
    query_embedding = model.encode([normalized_query])
    D, I = index.search(query_embedding, k=1)  # Find closest match
    # print(f"Distance: {D[0][0]}, Matched Index: {I[0][0]}")  # Debugging
    if D[0][0] < 1.0:  # Lower distance = better match
        return faq_data[I[0][0]]["answer"]
    # If no FAQ match, generate response using LLaMA
    llama_response = generate_llama_response(query)
    return llama_response

def ask_llama(query):
    querySpell = correct_spelling(query)  # Apply spell check before searching
    faq_answer = find_answer(querySpell)
    prompt = f"User question: {query}\nFAQ Answer: {faq_answer}\nMake this response more conversational as if you are replying to a customer and dont mention any technical details:"
    response = ollama.chat(model="llama3.2", messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    query = data.get("question", "")
    answer = ask_llama(query)
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(port=5002)

# Example Query
user_query = "Can I get a refund?"
response = ask_llama(user_query)
print("Bot:", response)