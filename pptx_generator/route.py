import json
from src.handlers.generate_pptx import generate_pptx

def generate(event, context):
    print("event",event)
    return generate_pptx(event, context)
   

