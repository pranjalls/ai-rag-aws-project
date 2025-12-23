import json
import boto3
import os
from opensearchpy import OpenSearch
from uuid import uuid4

s3 = boto3.client("s3")
textract = boto3.client("textract")
bedrock = boto3.client("bedrock-runtime")

OPENSEARCH_HOST = os.environ["OPENSEARCH_HOST"]
INDEX_NAME = "documents"

client = OpenSearch(
    hosts=[{"host": OPENSEARCH_HOST, "port": 443}],
    use_ssl=True,
    verify_certs=True
)

def get_embedding(text):
    response = bedrock.invoke_model(
        modelId="amazon.titan-embed-text-v1",
        body=json.dumps({"inputText": text})
    )
    return json.loads(response["body"].read())["embedding"]

def lambda_handler(event, context):
    bucket = event["bucket"]
    key = event["key"]

    response = textract.detect_document_text(
        Document={"S3Object": {"Bucket": bucket, "Name": key}}
    )

    full_text = " ".join(
        [b["Text"] for b in response["Blocks"] if b["BlockType"] == "LINE"]
    )

    chunks = [full_text[i:i+800] for i in range(0, len(full_text), 800)]

    for chunk in chunks:
        embedding = get_embedding(chunk)
        doc_id = str(uuid4())

        client.index(
            index=INDEX_NAME,
            body={
                "content": chunk,
                "embedding": embedding
            },
            id=doc_id
        )

    return {
        "statusCode": 200,
        "body": json.dumps("Document indexed successfully")
    }
