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

### 環境変数の読み込み

```bash
# .env ファイルを修正したあとに実行する
source .env
# GAE 用のディレクトリに .env をコピーする
cp .env FlaskApp/src/
```

### GCS バケットの作成

```bash
gsutil mb -l $REGION gs://$BUCKET_NAME
```

### Cloud Functions のデプロイ

まず、[サービスアカウントを作成し、json 形式の認証キーをダウンロードする。](https://cloud.google.com/vertex-ai/docs/training/create-custom-job#create_custom_job-python)  
ダウンロードしたキーを [data_extraction/src/key/key.json](data_extraction/src/key/key.json) に保存する。

```bash
gcloud auth login
gcloud config set project $PROJECT_ID
```

次に、コンテナを Container Registry にプッシュする。
```bash
cd data_extraction

# src/settings.yaml の変更 ('base_dir'のみ変更でok)
vim src/settings.yaml
vim src/GNN_and_GS/config.yaml

# Docker コンテナをローカルでビルド
# ※ Image は 19GB 弱あります
docker build -f Dockerfile -t $IMAGE_URI ./
docker run -it $IMAGE_URI

# コンテナを Container Registry に push する
docker push $IMAGE_URI
```

Cloud Functions にデプロイする。
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/<path>/StrengthsFinderApp/data_extraction/src/key/key.json"

cd preprocess_trigger

# settings.yaml の変更 ('project_id'のみ変更でok)
vim src/settings.yaml

gcloud functions deploy sf_app_preprocess_trigger \
--region $REGION \
--runtime python38 \
--trigger-resource $BUCKET_NAME \
--trigger-event google.storage.object.finalize
```

### 初期データをGCSに配置

データを GCS に格納する。  
CloudFunctions が正常にデプロイできていれば、`sf_app_preprocess_trigger` が VertexAI 上で実行される。  
正常終了すれば、`gs://<BUCKET_NAME>/preprocessed/` 以下にデータが保存される。

```
gsutil cp sample_data/mst/* gs://$BUCKET_NAME/mst/
gsutil cp sample_data/original/* gs://$BUCKET_NAME/original/
```


### GAE のデプロイ

```bash
gcloud app create --region=$REGION
```

`FlaskApp/src/settings.yaml` を書き換えたあと、以下を実行。

```bash
cd FlaskApp/src
gcloud app deploy
```