import argparse
from flask import Flask, jsonify

app = Flask(__name__)
port = 5000


@app.route("/library", methods=["GET"])
def library():
    return jsonify({
        "service": "Library Service",
        "instance_port": port,
        "message": "Request handled successfully"
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "port": port})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("port", nargs="?", type=int, default=5000)
    args = parser.parse_args()

    if not 1 <= args.port <= 65535:
        parser.error("Port must be between 1 and 65535.")

    port = args.port
    app.run(
        host="127.0.0.1",
        port=port,
        debug=False,
        threaded=True
    )