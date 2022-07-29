import json
from src.handlers.generate_pptx import generatePptx
def generate(event, context):
    print("event",event)
    generatePptx()
    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response


# if __name__ == '__main__':
#     generate({},{})