import re
import pydash

from tpip_pptx.constants import CommandRegexSub, CommandRegex

class Tag:
    def __init__(self):
        pass

    def get_tag_content(self, pattern, shape):
        matches = re.findall(pattern, shape.text)
        return matches

    def replace_tags(self, replaced_for, replaced_text, shape):
        if shape.has_text_frame:
            text_frame = shape.text_frame
            for paragraph in text_frame.paragraphs:
                for run in paragraph.runs:
                    if run.text == replaced_for:
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
        else:
            matching_val = {}
            for match in matches:
                print("matches",matches)
                print("match",match)
                if match in dataObj:
                    print("inside")
                    object_value = pydash.get(dataObj, match, default={})   
                    matching_val[match] = object_value
                print("macth_val",matching_val)
            return matching_val
        

    def get_tag_from_string(self,pattern, string):
        matches = re.findall(pattern, string)
        return matches

   
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

    
        