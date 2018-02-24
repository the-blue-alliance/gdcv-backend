import thriftpy

from thriftpy.rpc import make_client


def main():
    print("Fetching status of local gdcv server...")
    gdcv_thrift = thriftpy.load('if/gdcv.thrift', module_name='gdcv_thrift')
    client = make_client(gdcv_thrift.FrcRealtimeScoringService, '127.0.0.1', 6000)

    print("{} v{} is {}, since {}".format(
        client.getName(),
        client.getVersion(),
        client.getStatus(),
        client.aliveSince())
    )

    metadataKey = "testKey"
    print ("Testing metadata server... {}={}".format(
        metadataKey,
        client.getMetadataValue(metadataKey))
    )

    print("Testing Pub/Sub...")
    testMessage = "Hello World!"
    result = client.sendPubSubMessage(testMessage)
    print("Result from pubsub send: {}".format(result))

    print("Testing db...")
    testMessage = "Hello World!"
    client.clearAllTestMessages()
    result = client.insertTestRow(testMessage)
    print("All rows: {}".format(client.getAllTestMessages()))

    print("Testing frc-livescore...")
    print("Test image: {}".format(client.processTestImage()))

    print("Testing parsing youtube video")
    req = gdcv_thrift.ProcessYoutubeVideoReq()
    req.year = 2017
    req.matchKey = '2017cmpmo_f1m1'
    req.videoKey = 'CL1lSdTkTUk'
    resp = client.processYoutubeVideo(req)
    print("Response: {} {}".format(resp.success, resp.message))

if __name__ == "__main__":
    main()
