#! /bin/bash
set -e

echo "Current python version:"
python3 --version

echo "Updating gce_metadata_stub dependenies"
pip3 install -r ./gce_metadata_stub/requirements.txt --upgrade

echo "Updating gdcv dependencies"
pip3 install -r ./requirements.txt --upgrade

find bin/ -name '*.whl' -exec pip3 install --upgrade --force-reinstall {} \;

session=gdcv
tmux start-server

if tmux has-session -t $session ; then
    echo "Found existing session. Killing and recreating..."
    tmux kill-session -t $session
fi

source scripts/log_paths.sh
echo "Clearing old log files..."
rm -f $worker_log
rm -f $metadata_log
rm -f $pubsub_log
rm -f $sql_log

echo "Starting GDCV server in new tmux session"
tmux new-session -d -s $session
tmux new-window -t "$session:1" -n cv-worker "./scripts/shim-dev-worker.sh 2>&1 | tee $worker_log"
tmux new-window -t "$session:2" -n gce-metadata "python3 ./gce_metadata_stub/gce_metadata_server.py -p 80 2>&1 | tee $metadata_log; read"
tmux new-window -t "$session:3" -n pubsub "gcloud beta emulators pubsub start 2>&1 | tee $pubsub_log; read"
tmux new-window -t "$session:4" -n sql "./scripts/start-mysql.sh 2>&1 | tee $sql_log; read"
tmux select-window -t "$session:1"

tmux list-sessions
tmux list-windows
