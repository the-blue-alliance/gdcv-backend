
class FrcRealtimeWorker(object):
    # 1. Read from metadata service about what we should connect to
    # 2. Get a frame from the stream using livestreamer
    # 3. Pass frame to frc-livescore for processing
    # 4. Send realtime data to firebase
    # 5. After match is over, dump all to sql
    pass
