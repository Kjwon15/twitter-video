from ubuntu:xenial

run apt-get update
run apt-get install -y python-pip ffmpeg
add src .
run pip install -r requirements.txt

expose 80
cmd honcho start
