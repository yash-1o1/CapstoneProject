import os
import time
from flask import Flask, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from db import init_database, insert_message, get_recent_messages

# Track server start time for health endpoint
START_TIME = time.time()

# Connected users: { socket_id: { "name": str, "joined_at": str } }
connected_users = {}


def create_app(db_path=None):
    """Create and configure the Flask + SocketIO application."""
    frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
    app = Flask(__name__, static_folder=frontend_dir, static_url_path="")

    socketio = SocketIO(app, cors_allowed_origins="*")
    db = init_database(db_path)

    # --- REST Endpoints ---

    @app.route("/")
    def index():
        return send_from_directory(frontend_dir, "index.html")

    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "uptime": round(time.time() - START_TIME, 2)})

    # --- Socket.io Event Handlers ---

    @socketio.on("user:join")
    def handle_join(data):
        from flask import request

        name = (data.get("name") or "").strip()
        if not name or len(name) > 30:
            emit("error", {"message": "Display name must be 1-30 characters"})
            return

        connected_users[request.sid] = {"name": name, "joined_at": time.time()}

        # Send chat history to the joining user
        history = get_recent_messages(db)
        emit("chat:history", history)

        # Send updated user list to everyone
        user_list = [u["name"] for u in connected_users.values()]
        socketio.emit("users:list", user_list)

        # Notify others that this user joined
        emit("user:joined", {"name": name}, broadcast=True, include_self=False)

    @socketio.on("message:send")
    def handle_message(data):
        from flask import request

        sid = request.sid
        user = connected_users.get(sid)
        if not user:
            emit("error", {"message": "You must join before sending messages"})
            return

        text = (data.get("text") or "").strip()
        if not text or len(text) > 500:
            emit("error", {"message": "Message must be 1-500 characters"})
            return

        try:
            msg = insert_message(db, user["name"], text)
            socketio.emit("message:new", msg)
        except ValueError as e:
            emit("error", {"message": str(e)})

    @socketio.on("typing:start")
    def handle_typing_start():
        from flask import request

        user = connected_users.get(request.sid)
        if user:
            emit("typing:start", {"name": user["name"]}, broadcast=True, include_self=False)

    @socketio.on("typing:stop")
    def handle_typing_stop():
        from flask import request

        user = connected_users.get(request.sid)
        if user:
            emit("typing:stop", {"name": user["name"]}, broadcast=True, include_self=False)

    @socketio.on("disconnect")
    def handle_disconnect():
        from flask import request

        user = connected_users.pop(request.sid, None)
        if user:
            user_list = [u["name"] for u in connected_users.values()]
            socketio.emit("users:list", user_list)
            socketio.emit("user:left", {"name": user["name"]})

    return app, socketio, db


# Module-level app for gunicorn (Azure App Service)
app, socketio, _db = create_app()

if __name__ == "__main__":
    print("Chat server running on http://localhost:5000")
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
