# Test

This test consists of 2 modules:

* Router, deciding which worker to send requests
* Worker, that loads the models and caches up to 2 models at a time

By running `docker-compose up`, you spin up one router and one worker, both
communicating though a redis server.

If the worker stops publishing its status for more than 2 seconds,
it's considered dead, and the router stops routing requests to it.

A new worker may join at any time, and will be immediately available for the router.

The hashing algorithm is pretty naive. When a new worker joins or leaves the cluster, most of
the models will end up being loaded and cached again by all workers. This is something that could be improved.


To test:
- Add folders on worker/models with TF saved models with model IDs (numeric)
    - For example: `workers/models/1/`, `workers/models/2/`, etc
- Run `docker-compose up`
- Request random models loading. For example, fake request inferences for models from 10 to 15:

    ```bash
    while [ 0 ]; do 
      time curl localhost:5000/$(shuf -n 1 -i 10-15); 
      sleep 0.1; 
    done
    ```
You will see several requests taking many seconds, and a few returning quickly due to the LRU cache of the workers.

Each worker caches up to 2 models in memory, and `docker-compose up` by default will spin up only one worker.

Now, keep the `while` above running to test the requests, and add more workers:

```
docker-compose up --scale worker=2 -d worker
```

Now, more requests should be cached and return faster, but the total capacity of the cluster is still 2 x 2 = 4 models.
We are requesting randomly 5 diferent models. So, if we scale the workers to 3, after some seconds we should be able
to see all the requests returning pretty quickly.

The test was all made with flask for simplicity, but the communication between the router and the workers could
benefit from a better protocol, such as gRPC.