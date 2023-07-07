FROM python:3.10-slim

ENV PYTHONUNBUFFERED True

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

RUN apt-get update && apt-get install gcc --yes
RUN pip install --no-cache-dir -r requirements.txt

CMD sh run.sh
