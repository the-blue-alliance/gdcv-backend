# gdcv Development

The gdcv application is containerized, so there are minimal thing you'll need installed on your host machine. 

The local development environment is similar to that the [TBA website](https://github.com/the-blue-alliance/the-blue-alliance/blob/master/docs/dev-container.md). Install `vagrant` and `docker` and get started with `vagrant up --provider=docker`. Once the container builds and starts, you can `vagrant ssh` in and run `tmux attach` to see all the running services. There are multiple `tmux` panes, one for each Google Cloud dependency that has been stubbed out to run locally.
