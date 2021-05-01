import socketio

class Piradio():
    def __init__(self):
        self.sio = socketio.Server()
        self.app = socketio.WSGIApp(sio)
