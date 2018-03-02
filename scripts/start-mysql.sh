#! /bin/bash

# Either starts a local mysqld or the Google Cloud SQL proxy

source scripts/log_paths.sh

# First, wait for the metadata server to start and read config values
echo "Waiting for metadata server stub to start..."
while [ ! -f $metadata_log ]
do
  sleep 1
done
tail -f $metadata_log | while read LOGLINE
do
   [[ "${LOGLINE}" == *"Running on"* ]] && pkill -P $$ tail
done

echo "Loading database engine from metadata"
db_engine=$(curl -s "http://metadata.google.internal/computeMetadata/v1/project/attributes/db_engine" -H "Metadata-Flavor: Google")
echo "Using db engine $db_engine"

service mysql stop
case "$db_engine" in
  local)
    echo "Starting local mysqld"
    mkdir -p /var/run/mysqld
    chown mysql:mysql /var/run/mysqld
    mysqld_safe
    ;;

  cloud_sql)
    echo "Downloading metadata stub"
    wget -q https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O /cloud_sql_proxy
    chmod +x /cloud_sql_proxy

    instance_name=$(curl -s "http://metadata.google.internal/computeMetadata/v1/project/attributes/cloud_sql_instance_name" -H "Metadata-Flavor: Google")
    sql_port=$(curl -s "http://metadata.google.internal/computeMetadata/v1/project/attributes/sql_port" -H "Metadata-Flavor: Google")

    echo "Starting Cloud SQL proxy"
    /cloud_sql_proxy -instances=$instance_name=tcp:3306 -credential_file=/gdcv/cloud-sql-auth.json
    ;;

  *)
    echo "Unknown db engine $db_engine"
    exit -1
    ;;
esac
