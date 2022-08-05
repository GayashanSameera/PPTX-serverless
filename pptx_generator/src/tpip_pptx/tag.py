import re
import pydash

from constants import CommandRegexSub
from src.handlers.generate_pptx import generate_pptx

class Tag:
    def __init__(self, pattern):
        self.pattern = pattern

    def get_tag_content(self, pattern, shape):
        matches = re.findall(pattern, shape.text)
        return matches

    def replace_tags(self, replaced_for, replaced_text, shape):
        if shape.has_text_frame:
            text_frame = shape.text_frame
            for paragraph in text_frame.paragraphs:
                for run in paragraph.runs:
                    cur_text = run.text
                    new_text = cur_text.replace(replaced_for, replaced_text)
                    run.text = new_text
                    
    def check_tag_exist(tag, shape):
        matches = tag in shape.text
        return matches

    def get_object_values(self, pattern, shape):
        matches = self.get_tag_content(pattern, shape)
        if (not matches or len(matches) < 1):
            return
        for match in matches:
            object_value = pydash.get(generate_pptx.dataObj, match, default={})
            return match, object_value

    def get_tag_from_string(self,pattern, string):
        matches = re.findall(pattern, string)
        return matches

    def get_object_values_string(self, pattern, text):
        matches = self.get_tag_from_string(pattern, text)
        if (not matches or len(matches) < 1):
            return {"text": text}

        for match in matches:
            object_value = pydash.get(generate_pptx.dataObj, match, False)
            if (object_value != False):
                current_text = current_text.replace(str(f"{CommandRegexSub.INS.value} {match} +++"), str(object_value))

        return {"text": current_text}

