from flask import Flask, jsonify
import requests
from threading import Lock
 
app = Flask(__name__)
 
BACKENDS = [
    "http://127.0.0.1:5003",
    "http://127.0.0.1:5004",
    "http://127.0.0.1:5005"
]
next_index = 0
index_lock = Lock()
 
@app.route("/library", methods=["GET"])
def balance():
    global next_index
 
    # Reserve one starting position per incoming request.
    with index_lock:
        start = next_index
        next_index = (next_index + 1) % len(BACKENDS)
 
    # Try each backend at most once.
    for offset in range(len(BACKENDS)):
        backend = BACKENDS[(start + offset) % len(BACKENDS)]
        try:
            response = requests.get(
                backend + "/library", timeout=1.5
            )
            response.raise_for_status()
            result = response.json()
            result["routed_via"] = "Flask Round Robin Balancer"
            return jsonify(result), response.status_code
        except (requests.exceptions.RequestException, ValueError):
            continue
 
    return jsonify({
        "error": "All Library Service instances unavailable"
    }), 503
 
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000,
            debug=False, threaded=True)
