SMS Backend Coordinator API
===========================

This API is responsible for performing our business logic related to sms processes
as well

Running Tests
-------------

The test suite relies on several other applications (postgres 10, rabbit mq).

In order to simplify bringing up the infrastructure, the test runner can execute inside
of a docker container.

We utilize 'wait-for-it.sh' to delay running the application until we're 100% available.
Check [here](https://github.com/vishnubob/wait-for-it) for documentation.


```
$ docker-compose up -f docker-compose-test.yml
```

Running Development Server
--------------------------

```
$ docker-compose up
```

This will launch the django debug server after applying all migrations.

Server will be available on http://localhost:8000


Building the Documentation
--------------------------

The documentation for this API is placed under the 'docs' folder.  A complete HTML version of the
documentation can be built by executing "make html" within that directory.

Alternatively, there is a Dockerfile that will build the documentation.

Ideally, you would mount some volume to the host so you can actually use the docs when it's done.
Fortunately, there is also a docker compose file, that will do just that, and then launch a web
server on port 8001 for you, with your documentation available.



TODO
----

Each app in this package should represent a business process
therefore, picking and packing should be in separate packages.
