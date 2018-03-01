#! /bin/bash
set -e

echo "Current python version: "
python3 --version

echo "Downloading latest source from GitHub"
rm -rf /gdcv
git clone https://github.com/the-blue-alliance/gdcv-backend.git /gdcv
cd /gdcv
git log -n 1

echo "Updating gdcv dependencies"
pip3 install -r ./requirements.txt --upgrade

echo "Downloading metadata stub"
wget -q https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O /cloud_sql_proxy
chmod +x /cloud_sql_proxy

instance_name=$(curl -s "http://metadata.google.internal/computeMetadata/v1/project/attributes/cloud_sql_instance_name" -H "Metadata-Flavor: Google")
sql_port=$(curl -s "http://metadata.google.internal/computeMetadata/v1/project/attributes/sql_port" -H "Metadata-Flavor: Google")

echo "Configuring GCP Authentication"
auth_path=/gdcv/cloud-sql-auth.json
sql_log=/var/log/gdcv_sql.log
gcp_auth=$(curl -s "http://metadata.google.internal/computeMetadata/v1/project/attributes/gcp_auth" -H "Metadata-Flavor: Google")
echo $gcp_auth > $auth_path
export GOOGLE_APPLICATION_CREDENTIALS=$auth_path

echo "Downloading and installing frc-livescore"
livescore_commit=$(curl -s "http://metadata.google.internal/computeMetadata/v1/project/attributes/livescore_commit" -H "Metadata-Flavor: Google")
rm -rf /frc-livescore
git clone https://github.com/andrewda/frc-livescore.git /frc-livescore
cd /frc-livescore
git checkout $livescore
python3 setup.py bdist_wheel --universal
find . -name '*.whl' -exec pip3 install --upgrade --force-reinstall {} \;

echo "Starting Cloud SQL proxy"
/cloud_sql_proxy -instances=$instance_name=tcp:3306 -credential_file=$auth_path | tee $sql_log &

echo "Waiting 5 seconds for Cloud SQL proxy to start"
sleep 5

echo "Starting gdcv..."
cd /gdcv
python3 ./gdcv/main.py
