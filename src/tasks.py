import os
import tempfile

from celery import Celery
from celery.task.control import inspect
from ffmpy import FFmpeg

BROKER_URL = os.environ.get('BROKER_URL')
BACKEND_URL = os.environ.get('BACKEND_URL')

app = Celery('tasks', broker=BROKER_URL, backend=BACKEND_URL)


def check_alive():
    i = inspect(app=app)
    return i.ping()


@app.task(track_started=True)
def encode_video(fdata, orig_name):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as fp:
        filename = fp.name

    try:
        with tempfile.NamedTemporaryFile() as tmp_input:
            tmp_input.write(fdata)
            tmp_input.flush()
            ff = FFmpeg(
                inputs={tmp_input.name: None},
                outputs={filename: '-acodec aac -vcodec h264 '
                         '-vf "scale=640:trunc(ow/a/2)*2" '
                         '-pix_fmt yuv420p '
                         '-loglevel warning '
                         '-strict -2 -y'}
            )
            ff.run()
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
