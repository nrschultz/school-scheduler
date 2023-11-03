# School Scheduler

This application uses [PuLP](https://coin-or.github.io/pulp/index.html) to generate a classroom schedule for a high school like environment given a set of inputs.

## Requirements

This application runs in a Docker container defined by the [Dockerfile](/Dockerfile), so you should have Docker installed to run it

## Running the Scheduler

The following command will build the image from the Dockerfile, then run the scheduler with some data generated within the code.

```
docker build . -t nrschultz/pulp-runner; docker run nrschultz/pulp-runner python SchoolScheduleEngine/__init__.py
```
