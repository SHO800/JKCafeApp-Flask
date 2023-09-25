from register import app, socketio

socketio.run(app, allow_unsafe_werkzeug=True, host="0.0.0.0", port=80)
