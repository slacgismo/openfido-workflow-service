#!/bin/sh

export FLASK_APP=run.py
export FLASK_RUN_PORT=5003
export FLASK_ENV=production
export PATH=/opt/openfido-app-service/.venv/bin:$PATH
export SQLALCHEMY_DATABASE_URI="postgresql://postgres:dev-password@localhost/appservice"
export SECRET_KEY=demo-app
export S3_ACCESS_KEY_ID=minio_access_key
export S3_SECRET_ACCESS_KEY=minio123
export S3_ENDPOINT_URL="http://localhost:9000"

cd /opt/openfido-app-service
sh start.sh
