Twitter video
=============

Re-encode your video with twitter-compatible options

Twitter is so bad. They don't handle your video when it's not encoded with H.264, AAC.
So we have to re-encode video with some options. I don't like to download codec, encoder, etc. So I made a simple util.


Preparation for Dokku
---------------------

```sh
# Use redis as celery broker
$ dokku redis:create twitter-video-redis
$ dokku redis:link twitter-video-redis twitter-video
# Link upload dir
$ dokku docker-options:add deploy "-v /tmp:/tmp"
# Scale up worker
$ dokku ps:scale twitter-video worker=1
```
