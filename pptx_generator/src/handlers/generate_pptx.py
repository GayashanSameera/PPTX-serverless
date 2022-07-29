import pydash
from pptx.util import Inches
from pptx.oxml.xmlchemy import OxmlElement
from pptx.dml.color import RGBColor
from lxml import etree
from copy import deepcopy
from pptx.table import Table, _Row, _Column, _Cell
from pptx.enum.text import PP_ALIGN
import re

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
 
    def get_object_values():
        matches = super().get_tag_content(pattern,shape)
        if( not matches or len(matches) < 1):
             return
        for match in matches:
            object_value = pydash.get(replacements, match)
            return object_value
         
    def get_tag_from_string(pattern,string):
        matches = re.findall(pattern, string)
        return matches
    
    

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
            
    
