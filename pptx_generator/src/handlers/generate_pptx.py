import pydash
import os
from pptx.util import Inches
from io import BytesIO
import io
import boto3
from botocore.exceptions import ClientError
import logging
import base64
from pptx import Presentation
import enum
import time
import re

POC_PPTX_BUCKET = os.environ.get("POC_PPTX_BUCKET")

def generate_pptx():
    
    start_time = time.perf_counter ()

    s3_client = boto3.client('s3')
    response = s3_client.get_object(Bucket=POC_PPTX_BUCKET, Key='task.pptx')
    data = response['Body'].read()

    print("-- response --")
    print(response)

    print("-- data --")
    print(data)
    
    f = open("/tmp/task.pptx", "wb")
    f.write(data)
    f.close()
    

    presentationObject = Presentation('/tmp/task.pptx')    
    dataObj = {
        
            "assetChart": { "url" : "img1.png" , "size": {"left":1,"top":1, "height":3, "width":4.2}},
            "schemeName": "XYZ Pension Scheme",
            "title": "Q2 2021 Summary Report",
            "heading":"Investment performance to 30 June 2021",

        }
   
    
    executor = CommandExecutor(presentationObject, dataObj)
    executor.execute()

    try:
        with BytesIO() as fileobj:
            presentationObject.save(fileobj)
            fileobj.seek(0)
            PATH = 'given/path/output.pptx'
            res = s3_client.upload_fileobj(fileobj, POC_PPTX_BUCKET, PATH)
    except ClientError as e:
        logging.error(e)
        return False
                    

    end_time = time.perf_counter ()
    print(end_time - start_time, "seconds")
    
    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response
    
    
class CommandRegex(enum.Enum):
        IMAGE = r'\+\+\+IM (.*?) \+\+\+',
        TEXT  = r'\+\+\+INS (.*?) \+\+\+'
        
class CommandRegexSub(enum.Enum):
        IMG = '+++IM'
        INS = '+++INS'
    
class Command(enum.Enum):
        IF_CONDITION = "if_condition"
        FOR_LOOP = "for_loop"
        REPLACE_IMAGE = "replace_images"
        REPLACE_TABLE = "replace_table"
        UPDATE_TABLE_TEXT = "update_table_text"
        DRAW_TABLE = "draw_tables"
        TEXT_REPLACE = "text_replace"
        
class CommandRegistry:
        def __init__(self):
            self.commands = {
                "+++IF": "if_condition",
                "+++FOR": "for_loop",
                "+++IM": "replace_image",
                "+++TB_ADD": "replace_table",
                "+++TB_TX_UP": "update_table_text",
                "+++TB_DRW": "draw_tables",
                "+++INS": "text_replace"
            }

        def get_commands_dictionary(self):
            return self.commands

        def get_commands_list(self):
            return self.commands.keys()

        def get_command(self,command_name):
            if command_name == Command.REPLACE_IMAGE:
                
                image = Image()
                def getParams(commands_dic,presentation,slide,shape,slides,dataObj):
                        
                    return image.replace_images(slide,CommandRegex.IMAGE.value[0],shape)
                        
                return getParams
                    
            elif command_name == Command.TEXT_REPLACE:
                    
                text = Text()
                def getParams(commands_dic,presentation,slide,shape,slides,dataObj):
                    return text.text_replace(slide,CommandRegex.TEXT.value[0],shape)
                        
                return getParams
                             
                    
            else:
                raise Exception("Invalid command name")
                
                
class Tag:
    
        def __init__(self,pattern):
            self.pattern = pattern
            
        def get_tag_content(self,pattern, shape):
            matches = re.findall(pattern,shape.text)
            return matches
            
        def replace_tags(self,replaced_for,replaced_text,shape):
            if shape.has_text_frame:
                text_frame = shape.text_frame
                for paragraph in text_frame.paragraphs:
                    for run in paragraph.runs:
                        cur_text = run.text
                        new_text = cur_text.replace(replaced_for, replaced_text)
                        run.text = new_text
        
        def get_object_values(self,pattern,shape):
            matches = self.get_tag_content(pattern,shape)
            if( not matches or len(matches) < 1):
                return
            for match in matches:
                object_value = pydash.get(generate_pptx.dataObj, match,default={})
                return match , object_value
                    
        def get_tag_from_string(pattern,string):
            matches = re.findall(pattern, string)
            return matches        
                
        def get_object_values_string(self,pattern,text):
            matches = self.get_tag_from_string(pattern, text)
            if( not matches or len(matches) < 1):
                return { "text": text }

            for match in matches:
                object_value = pydash.get(generate_pptx.dataObj, match, False)
                if(object_value != False):
                    current_text = current_text.replace(str(f"{CommandRegexSub.INS.value} {match} +++"), str(object_value))

        
            return { "text": current_text }
                    
                
        
class Image(Tag):
    
        def __init__(self):
            pass
                
        def replace_images(self,slide,pattern,shape): 
            match , object_value = super().get_object_values(pattern,shape)
    
            url = pydash.get(object_value, "url",default="")
            left = pydash.get(object_value, "size.left",default=1)
            height = pydash.get(object_value, "size.height",default=1)
            top = pydash.get(object_value, "size.top",default=5)
            width = pydash.get(object_value, "size.width",default=5)
            
            decodeimg = base64.b64decode(url)
            img = io.BytesIO(decodeimg)
            slide.shapes.add_picture(img, Inches(left), Inches(top), Inches(width) ,Inches(height) )
            super().replace_tags(str(f"{CommandRegexSub.IMG.value} {match} +++"),"", shape)
            
        
            
class Text(Tag):
    
        def __init__(self):
            pass
                
        def text_replace(self, slide, pattern,shape):
            match, object_value =super().get_object_values(pattern,shape)
            super().replace_tags(str(f"{CommandRegexSub.INS.value} {match} +++"), str(object_value), shape)
            
        def text_tag_update(pattern,text):
            match, object_value = super().get_object_values_string(pattern,text)
            if(object_value != False):
                    current_text = current_text.replace(str(f"{CommandRegexSub.INS.value} {match} +++"), str(object_value))
            
                                
class Expression(Tag):
        def __init__(self,pattern):
            super().__init__(pattern)

        def if_condition(self):
            print("if condition func executed")

        def for_loop(self):
            print("for loop func executed")
                

class CommandExecutor:
        registry = CommandRegistry()

        def __init__(self, presentation, dataObj):
            self.slide = None
            self.presentation = presentation
            self.dataObj = dataObj

        def execute(self):
            # get command names as a list
            commands = self.registry.get_commands_list()
                
            commands_dic = self.registry.get_commands_dictionary()
            

            # find commands in the presentation using 'commands' list & execute
            slides = [self.slide for self.slide in self.presentation.slides]
            for shape in self.slide.shapes:
                if shape.has_text_frame:
                    if shape.text:
                        try:
                            self.registry.get_command(Command.REPLACE_IMAGE)(commands_dic, self.presentation, self.slide, shape, slides.index(self.slide), self.dataObj)
                            # self.registry.get_command(Command.TEXT_REPLACE)(commands_dic, self.presentation, self.slide, shape, slides.index(self.slide), self.dataObj)
                        except Exception as e:
                            print(e.__class__)
                            
                            
        

    
    
   
   
        
    
    
   
        
        
