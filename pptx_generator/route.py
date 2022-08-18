import json
from src.handlers.generate_pptx import generate_pptx

def generate(event, context):
    return generate_pptx(event, context)
   

