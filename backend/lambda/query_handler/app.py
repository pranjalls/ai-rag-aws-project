import json
import boto3
import os
from opensearchpy import OpenSearch

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

def ask_llm(context, question):
    prompt = f"""
Answer the question using only the context below.

Context:
{context}

Question:
{question}
"""

    response = bedrock.invoke_model(
        modelId="anthropic.claude-v2",
        body=json.dumps({
            "prompt": prompt,
            "max_tokens_to_sample": 300
        })
    )

    return json.loads(response["body"].read())["completion"]

def lambda_handler(event, context):
    body = json.loads(event["body"])
    question = body["question"]

    embedding = get_embedding(question)

    search = client.search(
        index=INDEX_NAME,
        body={
            "size": 3,
            "query": {
                "knn": {
                    "embedding": {
                        "vector": embedding,
                        "k": 3
                    }
                }
            }
        }
    )

    context_text = " ".join(
        [hit["_source"]["content"] for hit in search["hits"]["hits"]]
    )

    answer = ask_llm(context_text, question)

    return {
        "statusCode": 200,
        "body": json.dumps({"answer": answer})
    }
