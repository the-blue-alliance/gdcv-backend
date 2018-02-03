#! /bin/bash

# A script that waits for the stubbed Google Cloud dependencies to start up
# It also configures the proper environment variables for the Pub/Sub emulator

source scripts/log_paths.sh

# First, wait for the metadata server to start and read the project ID
echo "Waiting for metadata server stub to start..."
while [ ! -f $metadata_log ]
do
  sleep 1
done
tail -f $metadata_log | while read LOGLINE
do
   [[ "${LOGLINE}" == *"Running on"* ]] && pkill -P $$ tail
done

echo "Loading project-id from local metadata server"
project_id=$(curl "http://metadata.google.internal/computeMetadata/v1/project/attributes/project-id" -H "Metadata-Flavor: Google")
echo "Using project-id $project_id"

echo "Waiting for Pub/Sub emulator to start..."
while [ ! -f $pubsub_log ]
do
  sleep 1
done
tail -f $pubsub_log | while read LOGLINE
do
   [[ "${LOGLINE}" == *"Server started"* ]] && pkill -P $$ tail
done

echo "Extracting Pub/Sub emulator port"
pubsub_port=$(egrep -o '^.*Server started.*$' $pubsub_log | egrep -o '[[:digit:]]{4}$')
pubsub_host="localhost:$pubsub_port"
echo "Assuming Pub/Sub emulator is running at $pubsub_host"

echo "Starting gdcv..."
export PUBSUB_EMULATOR_HOST="$pubsub_host"
export PUBSUB_PROJECT_ID="$project_id"
python3 ./gdcv/main.py
