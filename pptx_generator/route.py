import json
from src.handlers.generate_pptx import generate_pptx, local_pptx

def generate(event, context):
    # print("event",event)
    return generate_pptx(event, context)
   

if __name__ == '__main__':
    local_pptx()