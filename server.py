from register import app, socketio

socketio.run(app, allow_unsafe_werkzeug=True)