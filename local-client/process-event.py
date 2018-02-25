import argparse
import thriftpy

from thriftpy.rpc import make_client


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('key', help="TBA event key to process")
    args = parser.parse_args()

    gdcv_thrift = thriftpy.load('if/gdcv.thrift', module_name='gdcv_thrift')
    client = make_client(gdcv_thrift.FrcRealtimeScoringService, '127.0.0.1', 6000)

    print("Enqueueing {} for CV processing".format(args.key))
    req = gdcv_thrift.ProcessEventReq()
    req.eventKey = args.key
    resp = client.enqueueEvent(req)

    print("Response: {}".format(resp.message))

if __name__ == "__main__":
    main()
