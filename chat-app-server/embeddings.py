from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from flask_cors import CORS  # Import CORS
import ollama

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

def find_answer(query):
    print("FAISS Index Size:", index.ntotal)
    query_embedding = model.encode([query])
    D, I = index.search(query_embedding, k=1)  # Find closest match
    # print(f"Distance: {D[0][0]}, Matched Index: {I[0][0]}")  # Debugging
    if D[0][0] < 5.0:  # Lower distance = better match
        return faq_data[I[0][0]]["answer"]
    return "Sorry, I couldn't find an answer."

def ask_llama(query):
    faq_answer = find_answer(query)
    prompt = f"User question: {query}\nFAQ Answer: {faq_answer}\nMake this response more conversational:"
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