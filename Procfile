web: uwsgi --module app:app --master --die-on-term --http-socket :5000
worker: celery -A tasks worker -l info
dev: FLASK_APP=app.py FLASK_DEBUG=1 flask run
