import argparse
import datetime
import json
import requests
import os
import subprocess
import urllib
from googleapiclient.discovery import build


def get_current_events(auth_key):
    url = 'https://www.thebluealliance.com/api/v3/events/2018'
    content = urllib.request.urlopen(
        urllib.request.Request(
            url,
            headers={
                'X-TBA-Auth-Key': auth_key,
                'User-Agent': 'gdcv-admin'
            }))
    return json.loads(content.read())


def event_is_live(event_info):
    now = datetime.datetime.now()
    event_end = datetime.datetime.strptime(event_info['end_date'], "%Y-%m-%d")
    event_end += datetime.timedelta(days=1)
    event_start = datetime.datetime.strptime(event_info['start_date'], "%Y-%m-%d")
    event_start += datetime.timedelta(days=-1)
    now = datetime.datetime.now()
    return now > event_start and now < event_end


def load_current_vms(args):
    compute = build('compute', 'v1')
    result = compute.instances().list(project=args.project, zone=args.gce_zone).execute()
    return result.get("items", [])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['sync'])
    parser.add_argument('--apiv3_key', default=os.environ.get('TBA_APIv3_KEY', None))
    parser.add_argument('--project', default='tbatv-prod-hrd')
    parser.add_argument('--gce_zone', default='us-central1-f')
    args = parser.parse_args()

    if args.action == 'sync':
        # Sync GCE VMs with the currently active events
        events = get_current_events(args.apiv3_key)
        live_events = {e["key"]: e for e in events if event_is_live(e)}
        live_event_keys = set(live_events.keys())
        print("Found {} currently live events".format(len(live_events)))

        vms = load_current_vms(args)
        gdcv_instances = [vm for vm in vms if 'gdcv' in vm["name"]]
        gdcv_keys = set([vm["name"].split('-')[1] for vm in gdcv_instances])
        print("GCE currently has {} GDCV instances".format(len(gdcv_instances)))

        vms_to_create = live_event_keys - gdcv_keys
        vms_to_delete = gdcv_keys - live_event_keys

        print("Need to create {} VMs and delete {} VMs".format(len(vms_to_create), len(vms_to_delete)))
        for event_key in vms_to_create:
            event = live_events[event_key]
            twitch_stream = next(iter([w for w in event["webcasts"] if w["type"] == 'twitch']), None)
            livestream = next(iter([w for w in event["webcasts"] if w["type"] == 'livestream']), None)
            stream_url = None
            if twitch_stream:
                stream_url = 'https://twitch.tv/{}'.format(twitch_stream["channel"])
            elif livestream:
                stream_url = 'https://livestream.com/accounts/{}/events/{}'.format(
                    livestream["channel"], livestream["file"])
            if not stream_url:
                print("Event {} does not have a supported stream, skipping".format(event_key))
                continue
            print("Using webcast {} for {}".format(stream_url, event_key))
            startup_message = {
                'type': 'process_stream',
                'event_key': event_key,
                'stream_url': stream_url,
            }
            # Can't figure out to do this as simply with the API
            print("Creating VM with startup: {}".format(json.dumps(startup_message)))
            subprocess.run([
                'gcloud', 'beta', 'compute', 'instances',
                'create-with-container', 'gdcv-{}'.format(event_key),
                '--container-image', 'gcr.io/tbatv-prod-hrd/gdcv-prod:latest',
                '--zone', args.gce_zone,
                '--metadata', '^~^starting_message={}'.format(json.dumps(startup_message))
            ])

        compute = build('compute', 'v1')
        for event_key in vms_to_delete:
            print("Deleting {} worker".format(event_key))
            result = compute.instances().delete(project=args.project, zone=args.gce_zone, instance='gdcv-{}'.format(event_key)).execute()


if __name__ == '__main__':
    main()
