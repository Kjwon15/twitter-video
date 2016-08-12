import os
import tempfile

from celery import Celery
from ffmpy import FFmpeg

REDIS_URL = os.environ.get('REDIS_URL')

app = Celery('tasks', broker=REDIS_URL, backend=REDIS_URL)


@app.task
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
