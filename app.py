from flask import Flask, request, jsonify, render_template
from Backend.Chatbot import ChatBot
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # allow JS frontend to call this API

# Serve index.html
@app.route("/")
def home():
    return render_template("index.html")

# Chat API
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_query = data.get("query", "")
    reply = ChatBot(user_query)
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True)