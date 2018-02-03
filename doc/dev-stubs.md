# Development Stubs

The gdcv application depends heavily on the following Google Cloud components:
 - [Google Compute Engine Metadata Server](https://cloud.google.com/compute/docs/storing-retrieving-metadata)
 - [Google Cloud PubSub](https://cloud.google.com/pubsub/docs/)
 - [Google Cloud SQL](https://cloud.google.com/sql/docs/)

We don't want to be required to interact with production cloud dependencies when testing locally, so these components are mocked out for testing purposes.

### GCE Metadata Stub

This repository contains a modified [metadata server emulator](https://github.com/salrashid123/gce_metadata_server) in the directory `gce_metadata_stub`. In short, it has the following modifications from the original version:

 - python3 support (by running `2to3` on the source files)
 - Reads data from a local JSON file (`dev_metadata.json`) instead of a constant map

The dev container is started with a custom Hostfile mapping that redirects metadata server requests to teh emulator running in the container on port 80.

### Cloud PubSub Emulator

The dev container will also have an instance of the [Google Cloud PubSub Emulator](https://cloud.google.com/pubsub/docs/emulator) running. The main application startup [is wrapped by a script](https://github.com/the-blue-alliance/gdcv-backend/blob/master/scripts/shim-dev-worker.sh) that monitors the emulator log file and extracts the local port it is listening on. The wrapper then sets the appropriate environment variables so that the PubSub client library can connect to the correct port.

### Local mysql

The dev container has `mysqld` running locally. Connection details are stored in the local metadata file. The gdcv application connects to mysql running locally and uses it for all its database operations. [In production](https://cloud.google.com/sql/docs/mysql/connect-kubernetes-engine), there will be a SQL proxy running on the host, so gcdv does not have to act differently.
