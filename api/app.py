from piradio import Piradio

pr = Piradio()
pr.app.run(port=conf.SOCKET_PORT, host='127.0.0.1')
