import os
from io import BytesIO
import boto3
from botocore.exceptions import ClientError
import logging
from pptx import Presentation
import json
import pydash

from tpip_pptx.constants import Command, CommandRegex
from tpip_pptx.image import Image
from tpip_pptx.table import Table
from tpip_pptx.text import Text
from tpip_pptx.expression import Expression
from tpip_pptx.toc import Toc
from tpip_pptx.slide import Slide


POC_PPTX_BUCKET = os.environ.get("POC_PPTX_BUCKET")


class CommandRegistry:
    def __init__(self):
        self.commands = {
            "+++IF": "if_condition",
            "+++FOR": "for_loop",
            "+++IM": "replace_images",
            "+++TB_ADD": "replace_table",
            "+++TB_TX_UP": "update_table_text",
            "+++TB_DRW": "draw_tables",
            "+++INS": "text_replace"
        }

    def get_commands_dictionary(self):
        return self.commands

    def get_commands_list(self):
        return self.commands.keys()

    def get_command(self, command_name):
        if command_name == Command.REPLACE_IMAGE.value:
            image = Image()
            return image.replace_images
         
        elif command_name == Command.TEXT_REPLACE.value:
            text = Text()
            return text.text_replace
            
        elif command_name == Command.UPDATE_TABLE_TEXT.value:
            table = Table()
            return table.update_table_text
          
        elif command_name == Command.DRAW_TABLE.value:
            table = Table()
            return table.drow_tables

        elif command_name == Command.REPLACE_TABLE.value:
            table = Table()
            return table.replace_tables

        elif command_name == Command.REMOVE_TABLE.value:
            table = Table()
            return table.remove_tables

        elif command_name == Command.IF_CONDITION.value:
            expression = Expression()
            return expression.if_condition 

        elif command_name == Command.FOR_LOOP.value:
                expression = Expression()
                return expression.for_loop   
        else:
            raise Exception("Invalid command name")




class CommandExecutor:
    registry = CommandRegistry()

    def __init__(self, presentation, dataObj):
        self.presentation = presentation
        self.dataObj = dataObj

    def execute(self):
        # get command names as a list
        commands = self.registry.get_commands_list()

        commands_dic = self.registry.get_commands_dictionary()

        # find commands in the presentation using 'commands' list & execute
        slides = [self.slide for self.slide in self.presentation.slides]
        for slide in slides:
            for shape in slide.shapes:
                if shape.has_text_frame:
                    for cmd in commands:
                        if cmd in shape.text:
                            
                            try:
                                self.registry.get_command(commands_dic[cmd])(commands_dic, self.presentation, slide,
                                                                            shape, slides.index(slide), self.dataObj)
        
                            except Exception as e:
                                print(e)

        


def generate_pptx(event, context):
    json_data = json.loads(event['body'])
    dataObj = json.loads(pydash.get(json_data,'template'))
    templateKey = pydash.get(json_data,'templateKey')
    destPath = pydash.get(json_data,'destPath')
    outPutFileName = pydash.get(json_data,'outPutFileName')
    
    s3_client = boto3.client('s3')
    response = s3_client.get_object(Bucket=POC_PPTX_BUCKET, Key=str(f"{templateKey}.pptx"))
    data = response['Body'].read()
  
    f = open('/tmp/{templateKey}.pptx', "wb")
    f.write(data)
    f.close()
    presentationObject = Presentation('/tmp/{templateKey}.pptx')
   
    executor = CommandExecutor(presentationObject, dataObj)
    executor.execute()
    
    slideObj = Slide()
    slideObj.remove_extra_slides(presentationObject)

    toc = Toc()
    toc.drow_toc(presentationObject, dataObj)
    

    try:
        with BytesIO() as fileobj:
            presentationObject.save(fileobj)
            fileobj.seek(0)
            PATH = str(f"{destPath}/{outPutFileName}")
            res = s3_client.upload_fileobj(fileobj, POC_PPTX_BUCKET, PATH)
    except ClientError as e:
        logging.error(e)
        return False

    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "content": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response
