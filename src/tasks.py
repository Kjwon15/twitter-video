import os
import tempfile

from celery import Celery
from ffmpy import FFmpeg

BROKER_URL = os.environ.get('BROKER_URL')
BACKEND_URL = os.environ.get('BACKEND_URL')

app = Celery('tasks', broker=BROKER_URL, backend=BACKEND_URL)


@app.task(track_started=True)
def encode_video(fdata, orig_name):
    fp = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    filename = fp.name
    fp.close()
    ff = FFmpeg(
        inputs={'pipe:0': None},
        outputs={filename: '-acodec aac -vcodec h264 '
                 '-vf scale=720:-2 '
                 '-strict -2 -y'}
    )
    ff.run(input_data=fdata)

    with open(filename) as fp:
        return orig_name, fp.read()
