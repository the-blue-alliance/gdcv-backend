
struct ProcessYoutubeVideoReq {
  1: required i64 year,
  2: required string matchKey,
  3: required string videoKey,
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

  /* Test Interface Methods */

  string getMetadataValue(1: string key);

  string sendPubSubMessage(1: string message);

  string getPubSubMessage();

  void insertTestRow(1: string message);

  string getAllTestMessages();

  void clearAllTestMessages();

  string processTestImage();
}
