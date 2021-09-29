FROM gcr.io/deeplearning-platform-release/pytorch-gpu.1-8
WORKDIR /root

# To shorten build time, copy requirements.txt first.
COPY src/requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

COPY src/ .

ENV GOOGLE_APPLICATION_CREDENTIALS /root/key/key.json
ENTRYPOINT ["python", "create_data_for_app.py"]
