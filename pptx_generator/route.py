import json
from src.handlers.generate_pptx import generate_pptx
def generate(event, context):
    print("event",event)
    generate_pptx()
   

