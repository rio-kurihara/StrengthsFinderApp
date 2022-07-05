FROM python:3.8-slim
WORKDIR /root

# To shorten build time, copy requirements.txt first.
COPY preprocess/requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

COPY preprocess/ .
COPY key/key.json key/

ENV GOOGLE_APPLICATION_CREDENTIALS /root/key/key.json
ENTRYPOINT ["python", "main.py"]
