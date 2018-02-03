import thriftpy

from thriftpy.rpc import make_client


def main():
    print("Fetching status of local gdcv server...")
    gdcv_thrift = thriftpy.load('gdcv/if/gdcv.thrift', module_name='gdcv_thrift')
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
    result = client.getPubSubMessage()
    print("Got message {} through local Pub/Sub".format(result))

    print("Testing db...")
    testMessage = "Hello World!"
    client.clearAllTestMessages()
    result = client.insertTestRow(testMessage)
    print("All rows: {}".format(client.getAllTestMessages()))

    print("Testing frc-livescore...")
    print("Test image: {}".format(client.processTestImage()))

if __name__ == "__main__":
    main()
