import os
import tempfile

from celery import Celery
from ffmpy import FFmpeg

BROKER_URL = os.environ.get('BROKER_URL')
BACKEND_URL = os.environ.get('BACKEND_URL')

app = Celery('tasks', broker=BROKER_URL, backend=BACKEND_URL)


@app.task(track_started=True)
def encode_video(result_dir, fname, orig_name):
    fd, out_name = tempfile.mkstemp(dir=result_dir, suffix='.mp4')
    os.close(fd)
    ff = FFmpeg(
        inputs={fname: None},
        outputs={out_name: '-acodec aac -vcodec h264 '
                 '-vf scale=720:-2 '
                 '-strict -2 -y'}
    )
    ff.run()
    os.unlink(fname)

    return out_name, orig_name
