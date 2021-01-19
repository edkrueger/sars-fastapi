FROM python:3.8-slim
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY . ./
CMD exec gunicorn --bind :$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker  --threads 8 app.main:app
