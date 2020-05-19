FROM python:3

COPY . /app
WORKDIR /app

RUN apt-get update \
 && apt-get -y full-upgrade

RUN pip install -r requirements.txt \
 && pip list --outdated

RUN useradd tracker
USER tracker

EXPOSE 8000
ENTRYPOINT ["python", "server.py"]
