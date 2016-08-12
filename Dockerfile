from jrottenberg/ffmpeg:ubuntu

run apt-get -qq update
run apt-get install -y python-pip
workdir /app
add src .
run pip install -r requirements.txt


expose 80
entrypoint []
cmd honcho -f Procfile.honcho start
