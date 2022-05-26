import time
from threading import Thread
from typing import List

import redis
from flask import Flask
import requests
from retry import retry


app = Flask(__name__)
redis_db = redis.Redis(host='redis', port=6379)


class WorkersWatcher(Thread):
    workers: List[str]

    def run(self):
        prefix = "worker/"
        while True:
            self.workers = [
                i[len(prefix):].decode('utf8')
               for i in redis_db.scan_iter(f'{prefix}*')]
            time.sleep(1)

    def get_node(self, model_id):
        # Pretty naive hash sharding.
        # Shakes a bit on rebalancing
        index = model_id % len(self.workers)
        return self.workers[index]


workers_watcher = WorkersWatcher()
workers_watcher.daemon = True
workers_watcher.start()


@retry(tries=3, delay=1)
def make_inference(model_id):
    node = workers_watcher.get_node(int(model_id))
    return node, requests.get(f"http://{node}/{model_id}", timeout=30)


@app.route('/<model_id>')
def hello(model_id):
    node, resp = make_inference(model_id)
    return f"I went to node {node} and got back: {resp.content}\n"
