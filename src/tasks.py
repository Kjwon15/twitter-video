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
                 '-vf "scale=640:trunc(ow/a/2)*2" '
                 '-pix_fmt yuv420p '
                 '-strict -2 -y'}
    )
    try:
        ff.run(input_data=fdata)
    except Exception as e:
        with tempfile.NamedTemporaryFile(
            delete=False, suffix='_' + orig_name) as fp:
            print('Save this file to {}.'.format(fp.name))
            fp.write(fdata)
        raise

    with open(filename) as fp:
        content = fp.read()
        os.remove(filename)
        return orig_name, content
