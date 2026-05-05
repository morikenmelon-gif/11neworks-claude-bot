from flask import Flask, request, jsonify
import requests
import anthropic
import os

app = Flask(__name__)

client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)

LINE_WORKS_BOT_TOKEN = os.environ.get("LINE_WORKS_BOT_TOKEN")
BOT_ID = os.environ.get("BOT_ID")

def call_claude(message):
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=500,
        messages=[
            {"role": "user", "content": message}
        ]
    )
    return response.content[0].text

def send_lineworks(user_id, text):
    url = f"https://www.worksapis.com/v1.0/bots/{BOT_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {LINE_WORKS_BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "accountId": user_id,
        "content": {
            "type": "text",
            "text": text
        }
    }
    
    requests.post(url, headers=headers, json=data)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    
    user_id = data["source"]["userId"]
    message = data["content"]["text"]

    reply = call_claude(message)
    send_lineworks(user_id, reply)

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
