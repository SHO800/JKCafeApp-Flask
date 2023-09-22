from register import app, socketio
import socket

host = socket.gethostname()
localip = socket.gethostbyname(host)
socketio.run(app, allow_unsafe_werkzeug=True, host="0.0.0.0", port=80)
# socketio.run(app, allow_unsafe_werkzeug=True, host=localip, port=80)
# app.run()