import time
from functools import lru_cache
from threading import Thread
import socket
from tensorflow import keras

import redis
from flask import Flask

app = Flask(__name__)
redis_db = redis.Redis(host='redis', port=6379)


class StatusPublisher(Thread):
    def run(self):
        hostname = socket.gethostname()
        while True:
            redis_db.set(f'worker/{socket.gethostbyname(hostname)}:5000', 1, ex=2)
            time.sleep(1)


publisher = StatusPublisher()
publisher.daemon = True
publisher.start()


@lru_cache(maxsize=2)
def get_model(model_id):
    return keras.models.load_model(f'models/{model_id}')


@app.route('/<model_id>')
def hello(model_id):
    model = get_model(model_id)
    return f"Loaded model: {model}"