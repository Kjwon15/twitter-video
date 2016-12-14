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
def encode_video(orig_name, input_fname, working_dir):
    with tempfile.NamedTemporaryFile(delete=False, dir=working_dir, suffix='.mp4') as fp:
        output_fname = fp.name

    try:
        ff = FFmpeg(
            inputs={input_fname: None},
            outputs={output_fname: '-acodec aac -vcodec h264 '
                     '-vf "scale=640:trunc(ow/a/2)*2" '
                     '-pix_fmt yuv420p '
                     '-loglevel warning '
                     '-strict -2 -y'}
        )
        ff.run()
        os.unlink(input_fname)
    except Exception as e:
        with tempfile.NamedTemporaryFile(
            delete=False, suffix='_' + orig_name) as fp:
            print('Save this file to {}.'.format(fp.name))
            fp.write(fdata)
        raise

    return orig_name, output_fname
