
struct ProcessYoutubeVideoReq {
  1: required string matchKey,
  2: optional string videoKey,
}

struct ProcessYoutubeVideoResp {
  1: required bool success,
  2: string message,
}

service FrcRealtimeScoringService {

  string getName();

  string getVersion();

  i64 aliveSince();

  string getStatus();

  ProcessYoutubeVideoResp processYoutubeVideo(1: ProcessYoutubeVideoReq req);

  void blockUntilNotProcessing();

  /* Test Interface Methods */

  string getMetadataValue(1: string key);

  string sendPubSubMessage(1: string message);

  void insertTestRow(1: string message);

  string getAllTestMessages();

  void clearAllTestMessages();

  string processTestImage();
}
