FROM gcr.io/deeplearning-platform-release/pytorch-gpu.1-6
WORKDIR /root

COPY . .

COPY requirements.txt /tmp/
RUN pip install /tmp/requirements.txt
COPY . /tmp/

ENTRYPOINT ["python", "create_data_for_app.py"]