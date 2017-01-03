import os
import tempfile
from io import BytesIO

from celery.task.control import inspect
from flask import (Flask, after_this_request, jsonify, render_template,
                   redirect, request, send_file, url_for)
from werkzeug import secure_filename

from tasks import check_alive, encode_video


app = Flask(__name__)

WORKING_DIR = os.path.join(tempfile.gettempdir(), 'twitter-video')
if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)


@app.route('/')
def index():
    return render_template('index.html')


@app.context_processor
def utility_processor():
    return dict(
        ping=check_alive
    )


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if not file:
        return 'Not OK'

    orig_name = file.filename
    fd, fname = tempfile.mkstemp(dir=WORKING_DIR, suffix='.mp4')
    os.close(fd)
    file.save(fname)
    task = encode_video.delay(orig_name, fname, WORKING_DIR)
    return redirect(url_for('wait', taskid=task.id))


@app.route('/waiting/<taskid>')
def wait(taskid):
    task = encode_video.AsyncResult(taskid)
    state = task.state
    if not task.ready():
        return render_template(
            'refresh.html',
            state=state, taskid=taskid)

    return redirect(url_for('download', taskid=taskid))


@app.route('/check/<taskid>')
def check(taskid):
    task = encode_video.AsyncResult(taskid)
    return jsonify({
        'state': task.state,
        'done': task.ready(),
        'destination': url_for('download', taskid=taskid),
    })


@app.route('/download/<taskid>')
def download(taskid):
    task = encode_video.AsyncResult(taskid)
    orig_name, output_fname = task.get()

    @after_this_request
    def clear_file(response):
        os.unlink(output_fname)
        return response

    dst_fname = orig_name
    if not dst_fname.endswith('.mp4'):
        dst_fname += '.mp4'

    return send_file(output_fname, as_attachment=True,
                     attachment_filename=dst_fname)
