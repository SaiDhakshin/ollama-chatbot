from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from flask_cors import CORS  # Import CORS
import ollama
from textblob import TextBlob
import threading
import time
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load FAQ data from JSON file
with open("faqs.json", "r") as file:
    faq_data = json.load(file)


# Extract questions and generate embeddings
questions = [faq["question"] for faq in faq_data]
embeddings = model.encode(questions)


# Convert to FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))  # Add vectors to FAISS

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

def process_feedback():
    """Periodically check feedback and process it."""
    while True:
        try:
            feedback_list = []
            with open("feedback_data.txt", "r") as f:
                lines = f.readlines()

            if lines:
                with open("feedback_data.txt", "w") as f:  
                    f.write("")  # Clear file after reading
            
                for line in lines:
                    try:
                        feedback_entry = json.loads(line.strip())  # ✅ Proper JSON parsing
                        feedback_entry["bot_answer"] = feedback_entry["bot_answer"].replace("\\n", "\n")  # ✅ Decode newlines back
                    except json.JSONDecodeError as e:
                        print(f"❌ Error parsing JSON: {e} (Line: {line.strip()})")
                        continue  # Skip this entry
                    question = feedback_entry["question"]
                    correct_answer = feedback_entry["correct_answer"]

                    if not question or not correct_answer:
                        print(f"⚠️ Skipping entry due to missing data: {feedback_entry}")
                        continue  # Skip incomplete entries
                    for faq in faq_data:
                            if faq["question"].lower() == question.lower():
                                faq["answer"] = correct_answer
                                print(f"Updated FAQ: {question} -> {correct_answer}")
                                break
                    else:  
                        # ✅ If no match is found, insert a new question
                        new_faq = {"question": question, "answer": correct_answer}
                        faq_data.append(new_faq)
                        print(f"➕ Added New FAQ: {question} -> {correct_answer}")
                # Clear feedback file after processing
                open("feedback_data.txt", "w").close()  # ✅ Clear feedback file
                # Save the updated FAQ data back to faqs.txt
                with open("faqs.json", "w") as f:
                    json.dump(faq_data, f, indent=4)  # ✅ Save with formatting
        except Exception as e:
            print("Error processing feedback:", e)

        time.sleep(60)  # Run every 60 seconds

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    query = data.get("question", "")
    answer = ask_llama(query)
    return jsonify({"answer": answer})

@app.route("/feedback", methods=["POST"])
def feedback():
    data = request.json
    question = data.get("question", "")
    bot_answer = data.get("bot_answer", "")
    correct_answer = data.get("correct_answer", "")

    feedback_entry = {
        "question": question,
        "bot_answer": bot_answer,
        "correct_answer": correct_answer if correct_answer else "Not Provided",
    }
    print(feedback_entry)
    with open("feedback_data.txt", "a") as f:
        f.write(json.dumps(feedback_entry) + "\n")  # ✅ Proper JSON format

    return jsonify({"message": "Feedback received! Thank you."})


if __name__ == "__main__":
    # Start feedback processing in a separate thread
    # process_feedback()
    feedback_thread = threading.Thread(target=process_feedback, daemon=True)
    feedback_thread.start()
    app.run(port=5002)

# Example Query
user_query = "Can I get a refund?"
response = ask_llama(user_query)
print("Bot:", response)