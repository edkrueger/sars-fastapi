FROM python:3.7-slim
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./
RUN pip install pipenv
RUN pipenv install --deploy --system
CMD exec uvicorn --port $PORT --workers 1 app.main:app

