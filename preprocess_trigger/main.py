from google.cloud import aiplatform

def preprocess_trigger(data, context):
    file_name = data['name']
    print('upload file name:', file_name)
    
    # 同時に二つのファイル(strengths.csvとdemogra.csv)がアップロードされる仕様により、
    # ジョブが2回実行されてしまうのを防ぐため

    if file_name == 'original/strengths.csv':
        # settings
        project = "mleg-283307"
        display_name = "preprocess"
        container_image_uri = "gcr.io/mleg-283307/torch18gpu_container_image:latest"
        location = "asia-northeast1"
        api_endpoint = "asia-northeast1-aiplatform.googleapis.com"

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
