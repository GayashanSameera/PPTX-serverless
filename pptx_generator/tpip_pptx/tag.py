import re
import pydash

from tpip_pptx.constants import CommandRegexSub, CommandRegex

class Tag:
    def __init__(self, pattern):
        self.pattern = pattern

    def get_tag_content(self, pattern, shape):
        print("pattern111",pattern)
        print("shape.text",shape.text) 
        matches = re.findall(pattern, shape.text)
        print("get_tag_content-matches",matches)
        return matches

    def replace_tags(self, replaced_for, replaced_text, shape):
        if shape.has_text_frame:
            text_frame = shape.text_frame
            for paragraph in text_frame.paragraphs:
                for run in paragraph.runs:
                    cur_text = run.text
                    new_text = cur_text.replace(replaced_for, replaced_text)
                    run.text = new_text
                    
    def check_tag_exist(self,tag, shape):
        matches = tag in shape.text
        return matches

    def get_object_values(self, pattern, shape,dataObj):
        matches = self.get_tag_content(pattern, shape)
        if (not matches or len(matches) < 1):
            return
        for match in matches:
            object_value = pydash.get(dataObj, match, default={})
            return match, object_value

    def get_tag_from_string(self,pattern, string):
        print("pattern>>>>>>",pattern,"string?////////////",string)
        matches = re.findall(pattern, string)
        print("get_tag_string",matches)
        return matches

    # def get_object_values_string(self, pattern, text,dataObj):
    #     print("Pattern", "String", pattern, text)
    #     matches = self.get_tag_from_string(pattern, text)
    #     print("get object value string", matches)
    #     if (not matches or len(matches) < 1):
    #         return {"text": text}

    #     for match in matches:
    #         object_value = pydash.get(dataObj, match, False)
    #         print("get object value", object_value)
    #         if (object_value != False):
    #             current_text = current_text.replace(str(f"{CommandRegexSub.INS.value} {match} +++"), str(object_value))
    #             print("Current text", current_text)

    #     return {"text": current_text}

    def eval_executor(self,logic,dataObj):
        return eval(logic,dataObj)
        
    def text_tag_update(self,text, dataObj):
        current_text = text
        pattern = CommandRegex.TEXT.value
        matches = self.get_tag_from_string(pattern, text)
        if( not matches or len(matches) < 1):
            return { "text": text }

        for match in matches:
            object_value = pydash.get(dataObj, match, False)
            if (object_value != False):
                current_text = current_text.replace(str(f"{CommandRegexSub.INS.value} {match} +++"), str(object_value))

        return {"text": current_text}

    def eval_executor(self,logic,dataObj):
        return eval(logic,dataObj)
        
    # def text_tag_update(self,pattern, text,dataObj):
    #     match, object_value = super().get_object_values_string(pattern, text,dataObj)
    #     if (object_value != False):
    #         current_text = current_text.replace(str(f"{CommandRegexSub.INS.value} {match} +++"), str(object_value))