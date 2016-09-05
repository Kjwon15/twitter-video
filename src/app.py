from io import BytesIO

from flask import (Flask, after_this_request, jsonify, render_template,
                   redirect, request, send_file, url_for)

from tasks import encode_video


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if not file:
        return 'Not OK'

    fdata = file.read()
    orig_name = file.filename
    task = encode_video.delay(fdata, orig_name)
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
    encoded_blob, orig_fname = task.get()

    return send_file(BytesIO(encoded_blob), as_attachment=True,
                     attachment_filename=orig_fname)
