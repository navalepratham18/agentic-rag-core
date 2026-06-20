import os
import requests
import logging
from flask import Flask, render_template, request, jsonify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Reads the internal Docker network URL we set in docker-compose.yml
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/v1/chat")

@app.route("/")
def index():
    """Serves the main chat interface."""
    return render_template("index.html")

@app.route("/api/send", methods=["POST"])
def send_message():
    """Proxies the user's message to the heavily armored FastAPI backend."""
    user_message = request.json.get("query")
    if not user_message:
        return jsonify({"error": "Empty message rejected."}), 400
        
    try:
        logger.info(f"Forwarding query to backend: {user_message}")
        # Forward the request to the orchestrator.
        # Timeout is 120s to account for LLaMA 3.2 local generation time.
        response = requests.post(
            BACKEND_URL, 
            json={"query": user_message},
            timeout=120 
        )
        response.raise_for_status()
        
        backend_data = response.json()
        
        # Extract the synthesized LLM response from the backend payload
        llm_reply = backend_data.get("data", {}).get("response", "No response generated.")
        source = backend_data.get("source", "unknown")
        
        return jsonify({"reply": llm_reply, "source": source})
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Backend network failure: {e}")
        return jsonify({"error": "The Agentic orchestrator is unreachable."}), 502

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)