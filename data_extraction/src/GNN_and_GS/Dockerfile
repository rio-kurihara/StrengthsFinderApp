FROM gcr.io/deeplearning-platform-release/pytorch-gpu.1-8
WORKDIR /root

# To shorten build time, copy requirements.txt first.
COPY GNN_and_GS/requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

COPY GNN_and_GS/ .
COPY key/key.json key/

ENV GOOGLE_APPLICATION_CREDENTIALS /root/key/key.json
ENTRYPOINT ["python", "GAE.py"]
