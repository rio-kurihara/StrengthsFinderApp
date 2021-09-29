# ストレングスファインダー 可視化アプリ

ストレングスファインダーの結果を複数人で共有するためのアプリです。以下の機能があります。

- チームメンバーの上位資質の傾向を提示
- 強みが似ているメンバーの提示
- チーム内における個人の突出した資質の提示
- チーム内で不足している資質の提示
- 1対1のマッチング

※TODO：アプリ画面

## Architecture

※TODO

## Requirement

* Google Cloud SDK 358.0.0
* docker 20.10.7
 
## Deployment

### 設定
```bash
export PROJECT_ID=<your_pjoject_id>
export BUCKET_NAME=<bucket_name>

# 以下は必要であれば変更する

export REGION=asia-northeast1
export IMAGE_REPO_NAME=torch18gpu_container_image
export IMAGE_TAG=latest
export IMAGE_URI=gcr.io/$PROJECT_ID/$IMAGE_REPO_NAME:$IMAGE_TAG
```

### GCS バケットの作成

```bash
gsutil mb gs://$BUCKET_NAME
# サンプルデータを GCS にコピーする
gsutil cp data_extraction/sample_data/original/* gs://$BUCKET_NAME/original/*
gsutil cp data_extraction/sample_data/mst/* gs://$BUCKET_NAME/mst/*
```

作成したら、以下の config ファイル内の <BUCKET_NAME> を変更する。  
- [data_extraction/src/settings.yaml](data_extraction/src/settings.yaml)
- [data_extraction/src/GNN_and_GS/config.yaml](data_extraction/src/GNN_and_GS/config.yaml)
- [FlaskApp/src/settings.yaml](FlaskApp/src/settings.yaml)


### GAE のデプロイ

```bash
gcloud auth login
gcloud app create --region=$REGION

cd FlaskApp/src
gcloud app deploy
```

### Cloud Functions のデプロイ

まず、[サービスアカウントを作成し、json 形式の認証キーをダウンロードする。](https://cloud.google.com/vertex-ai/docs/training/create-custom-job#create_custom_job-python)  
ダウンロードしたキーを [data_extraction/src/key/key.json](data_extraction/src/key/key.json) に保存する。

次に、コンテナを Container Registry にプッシュする。
```bash
cd data_extraction

# Docker コンテナをローカルでビルドしてテスト
docker build -f Dockerfile -t $IMAGE_URI ./
docker run -it $IMAGE_URI

# コンテナを Container Registry に push する
docker push $IMAGE_URI
```

Cloud Functions にデプロイする。
```bash
cd preprocess_trigger

gcloud functions deploy preprocess_trigger \
--region $REGION \
--runtime python38 \
--trigger-resource $BUCKET_NAME \
--trigger-event google.storage.object.finalize
```