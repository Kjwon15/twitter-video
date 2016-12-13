from jrottenberg/ffmpeg:ubuntu

run apt-get -qq update
run apt-get install -y python3-pip

run useradd -m app
user app
env PATH=/home/app/.local/bin:$PATH

workdir /app
add src .
run pip3 install --user -r requirements.txt


expose 5000
entrypoint []
cmd honcho start
