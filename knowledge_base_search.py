### Knowledge base search



import json
import boto3

bedrock_agent_runtime_client = boto3.client("bedrock-agent-runtime", region_name='eu-central-1')
translate_client = boto3.client("translate") 
bedrock_client = boto3.client('bedrock-runtime', region_name = 'eu-central-1')

document_mapping = {'s3://digital-channel-smartsearch-13134343/mmb-manual-ib-s-mobilnim-klicem.pdf': 'https://www.moneta.cz/documents/20143/11740743/mmb-manual-ib-s-mobilnim-klicem.pdf'}

    

def ask_bedrock_llm_with_knowledge_base(query: str, model_arn ='arn:aws:bedrock:eu-central-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0', kb_id = '5DGQ8EC2TH') -> str:
    
    response = bedrock_agent_runtime_client.retrieve_and_generate(
        input={
            'text': query
        },
        retrieveAndGenerateConfiguration={
            'type': 'KNOWLEDGE_BASE',
            'knowledgeBaseConfiguration': {
                'knowledgeBaseId': kb_id,
                'modelArn': model_arn
            }
        },
    )





    generated_text = response['output']['text']
    print(generated_text)
    
    return generated_text


def lambda_handler(event, context):
    try:
        body = json.loads(event["body"])
        prompt = body.get("question", "")

        if not prompt:
            return {"statusCode": 400, "body": json.dumps({"error": "Prompt is required"})}

        response = ask_bedrock_llm_with_knowledge_base(prompt)

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": json.dumps({ "answer": response })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
            "headers": {"Content-Type": "application/json"},
        }