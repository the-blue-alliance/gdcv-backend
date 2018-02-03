import logging
from media.media_provider import MediaProvider
from queue import Queue
logging.getLogger().setLevel(logging.INFO)
media = MediaProvider()
q = Queue()
media.fetch_youtube_video('3P_c9DqyRzg', q, save_every_n_frames=100)
