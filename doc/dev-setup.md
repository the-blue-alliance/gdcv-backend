# gdcv Development

The gdcv application is containerized, so there are minimal thing you'll need installed on your host machine. 

## Dependencies
You will need the following dependencies installed:
 - [`docker`](http://docker.io/)
 - [`vagrant`](vagrantup.com)
 - [`pex`](https://github.com/pantsbuild/pex)

## Local Dev Container

The local development environment is similar to that the [TBA website](https://github.com/the-blue-alliance/the-blue-alliance/blob/master/docs/dev-container.md). Install `vagrant` and `docker` and get started with `vagrant up --provider=docker`. Once the container builds and starts, you can `vagrant ssh` in and run `tmux attach` to see all the running services. There are multiple `tmux` panes, one for each Google Cloud dependency that has been stubbed out to run locally.

## Connecting to the Container

The development container exposes a [thrift server](https://en.wikipedia.org/wiki/Apache_Thrift) on port 6000 that you can use to invoke debug endpoints. The RPC endpoints can be found at [`if/gdcv.thrift`](https://github.com/the-blue-alliance/gdcv-backend/blob/master/if/gdcv.thrift).

## Running Integration Tests

Currently, there is a skeleton integration test that you can run with `./local-client/run-tests.sh`. This script will invoke thrift endpoints and ensure that some major components work end to end.

## Running Unit Tests

TODO :)
