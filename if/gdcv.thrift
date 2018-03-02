
struct ProcessSingleMatchReq {
  1: required string matchKey,
  2: optional string videoKey,
}

struct ProcessEventReq {
  1: required string eventKey;
}

struct ProcessStreamReq {
  1: required string eventKey;
  2: optional string streamUrl;
  3: bool skipDateCheck;
}

struct EnqueueProcessResponse {
  1: required bool success,
  2: string message,
}

service FrcRealtimeScoringService {

  string getName();

  string getVersion();

  i64 aliveSince();

  string getStatus();

  EnqueueProcessResponse enqueueSingleMatch(1: ProcessSingleMatchReq req);

  EnqueueProcessResponse enqueueEvent(1: ProcessEventReq req);

  EnqueueProcessResponse enqueueStream(1: ProcessStreamReq req);

  void blockUntilNotProcessing();

  /* Test Interface Methods */

  string getMetadataValue(1: string key);

  string sendPubSubMessage(1: string message);

  void insertTestRow(1: string message);

  string getAllTestMessages();

  void clearAllTestMessages();

  string processTestImage();
}
