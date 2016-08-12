import os
import shutil
import tempfile

from flask import Flask, render_template, redirect, request, send_file, url_for
from werkzeug import secure_filename

from tasks import encode_video


app = Flask(__name__, template_folder='.')
result_dir = tempfile.mkdtemp()


class TempDir(object):

    def __enter__(self):
        self.name = tempfile.mkdtemp()
        return self.name

    def __exit__(self, exc_type, exc_value, traceback):
        shutil.rmtree(self.name)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if not file:
        return 'Not OK'

    orig_name = secure_filename(file.filename)
    fd, fname = tempfile.mkstemp(dir=result_dir, suffix='.mp4')
    os.close(fd)
    file.save(fname)
    task = encode_video.delay(result_dir, fname, orig_name)
    return redirect(url_for('wait', taskid=task.id))


@app.route('/waiting/<taskid>')
def wait(taskid):
    task = encode_video.AsyncResult(taskid)
    state = task.state
    if not task.ready():
        return render_template('refresh.html', state=state)

    return redirect(url_for('download', taskid=taskid))


@app.route('/download/<taskid>')
def download(taskid):
    task = encode_video.AsyncResult(taskid)
    encoded_fname, orig_fname = task.get()
    return send_file(encoded_fname, as_attachment=True,
                     attachment_filename=orig_fname)
