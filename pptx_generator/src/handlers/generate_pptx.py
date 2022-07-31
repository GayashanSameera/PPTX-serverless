import pydash
from pptx.util import Inches
from pptx.oxml.xmlchemy import OxmlElement
from pptx.dml.color import RGBColor
from lxml import etree
from copy import deepcopy
from pptx.table import Table, _Row, _Column, _Cell
from pptx.enum.text import PP_ALIGN
import re
import enum

class CommandRegex(enum.Enum):
    TEXT = r'\+\+\+INS (.*?) \+\+\+'

class Command(enum.Enum):
    IF_CONDITION = "if_condition"
    FOR_LOOP = "for_loop"
    REPLACE_IMAGE = "replace_image"
    REPLACE_TABLE = "replace_table"
    UPDATE_TABLE_TEXT = "update_table_text"
    DRAW_TABLE = "draw_tables"
    TEXT_REPLACE = "replace_text"

# Parent Tag class
class Tag:
    def __init__(self,pattern):
       self.pattern = pattern
    
    def get_tag_content(pattern, shape):
         matches = re.findall(pattern, shape.text)
         return matches
     
    def replace_tags(replaced_for,replaced_text, shape):
        print()
        if shape.has_text_frame:
         text_frame = shape.text_frame
         for paragraph in text_frame.paragraphs:
            for run in paragraph.runs:
                cur_text = run.text
                new_text = cur_text.replace(replaced_for, replaced_text)
                run.text = new_text

        if shape.has_table:
         for row in shape.table.rows:
            for cell in row.cells:
                if replaced_for in cell.text:
                    new_text = cell.text.replace(replaced_for, replaced_text)
                    cell.text = new_text
 
    def get_object_values(pattern, shape):
        matches = super().get_tag_content(pattern,shape)
        if( not matches or len(matches) < 1):
             return
        for match in matches:
            object_value = pydash.get(replacements, match)
            return object_value
         
    def get_tag_from_string(pattern,string):
        matches = re.findall(pattern, string)
        return matches
    
    def text_tag_update(text, pattern):
        current_text = text
        matches = self.get_tag_from_string(pattern, text)
        if( not matches or len(matches) < 1):
            return { "text": text }

        for match in matches:
            object_value = pydash.get(replacements, match, False)
            if(object_value != False):
                current_text = current_text.replace(str(f"+++INS {match} +++"), str(object_value))
        
        return { "text": current_text } 

class Image(Tag):
    def __init__(self):
        super().__init__()
        self.pattern = r'\+\+\+IM (.*?) \+\+\+' 
        
    def replace_images(pattern,shape,slide):    
        
        matches = super().get_tag_content(pattern,shape)
        if( not matches or len(matches) < 1):
             return
        for match in matches:
            object_value = pydash.get(replacements, match)
        
            url = pydash.get(object_value, "url")
            left = pydash.get(object_value, "size.left")
            height = pydash.get(object_value, "size.height")
            top = pydash.get(object_value, "size.top")
            width = pydash.get(object_value, "size.width")
        
            slide.shapes.add_picture(url, Inches(left), Inches(top), Inches(width) ,Inches(height) )
            super().replace_tags(str(f"+++IM {match} +++"), "", shape)

class Text(Tag):
    def __init__(self):
        super().__ini__()
        self.pattern = CommandRegex.TEXT

    def replace_text(slide, shape, pattern):
        match, object_value = super().get_object_values(pattern,shape)
        super().replace_tags(str(f"+++INS {match} +++"), str(object_value), shape)  

class Expression(Tag):
    def __init__(self):
        super().__init__()

    def if_condition(self):
        print("if condition func executed")

    def for_loop(self):
        print("for loop func executed")
        
class CommandRegistry:
    def __init__(self):
        self.commands = {
            "+++IF": "if_condition",
            "+++FOR": "for_loop",
            "+++IM": "replace_image",
            "+++TB_ADD": "replace_table",
            "+++TB_TX_UP": "update_table_text",
            "+++TB_DRW": "draw_tables",
            "+++INS": "replace_text"
        }
    
    def get_commands_dictionary(self):
        return self.commands

    def get_commands_list(self):
        return self.commands.keys()

    def get_command(self, command_name):
        if command_name == Command.TEXT_REPLACE:
            text = Text()
            text.replace_text()
        elif command_name == Command.FOR_LOOP:
            expression = Expression()
            return expression.for_loop
        else:
            raise Exception("Invalid command name")