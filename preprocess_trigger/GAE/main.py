import yaml
from google.cloud import aiplatform


def sf_app_GAE_trigger(data, _):
    # 設定ファイルの読み込み
    with open('settings.yaml') as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    file_name = data['name']
    print('upload file name:', file_name)

    # 同時に二つのファイル(strengths.csvとdemogra.csv)がアップロードされる仕様により、
    # ジョブが2回実行されてしまうのを防ぐため

    if file_name == 'original/strengths.csv':
        # settings
        project = config['project_id']
        display_name = config['display_name']
        image_name = config['image_name']
        image_tag = config['image_tag']
        container_image_uri = "gcr.io/{0}/{1}:{2}".format(project, image_name, image_tag)
        location = config['location']
        api_endpoint = config['api_endpoint']

        # The AI Platform services require regional API endpoints.
        client_options = {"api_endpoint": api_endpoint}
        # Initialize client that will be used to create and send requests.
        # This client only needs to be created once, and can be reused for multiple requests.
        client = aiplatform.gapic.JobServiceClient(client_options=client_options)
        custom_job = {
            "display_name": display_name,
            "job_spec": {
                "worker_pool_specs": [
                    {
                        "machine_spec": {
                            "machine_type": "e2-standard-4",
                            # "accelerator_type": aiplatform.gapic.AcceleratorType.NVIDIA_TESLA_K80,
                            # "accelerator_count": 1,
                        },
                        "replica_count": 1,
                        "container_spec": {
                            "image_uri": container_image_uri,
                            "command": [],
                            "args": [],
                        },
                    }
                ]
            },
        }
        parent = f"projects/{project}/locations/{location}"
        response = client.create_custom_job(parent=parent, custom_job=custom_job)
        print("preprocess triggered")

    else:
        return
