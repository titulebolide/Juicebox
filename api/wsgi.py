from app import app as application
from app import conf

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=conf['port'])
