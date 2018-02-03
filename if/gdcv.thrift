
service FrcRealtimeScoringService {

  string getName();

  string getVersion();

  i64 aliveSince();

  string getStatus();

  string getMetadataValue(1: string key);

  string sendPubSubMessage(1: string message);

  string getPubSubMessage();

  void insertTestRow(1: string message);

  string getAllTestMessages();

  void clearAllTestMessages();

  string processTestImage();
}
