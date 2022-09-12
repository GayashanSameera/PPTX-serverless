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

    def get_object_values(self, pattern, shape,data_obj):
        matches = self.get_tag_content(pattern, shape)
        if (not matches or len(matches) < 1):
            return
        else:
            matching_val = {}
            for match in matches:
                if match in data_obj:
                    object_value = pydash.get(data_obj, match, default={})
                    if object_value != "":
                       matching_val[match] = object_value
            return matching_val , match
        

    def get_tag_from_string(self,pattern, string):
        matches = re.findall(pattern, string)
        return matches

   
    def eval_executor(self,logic,data_obj):
        try:
            return eval(logic,data_obj)
        except NameError:
            return None
            
        
        
    def text_tag_update(self,text, data_obj):
        current_text = text
        pattern = CommandRegex.TEXT.value
        matches = self.get_tag_from_string(pattern, text)
        if( not matches or len(matches) < 1):
            return { "text": text }

        for match in matches:
            object_value = pydash.get(data_obj, match, False)
            if (object_value != False):
                current_text = current_text.replace(str(f"{CommandRegexSub.INS.value} {match} +++"), str(object_value))

        return {"text": current_text}

    def get_table_remove_index_matches(self,pattern,matched_content):
        remove_pattern = pattern
        remove_matches = self.get_tag_from_string(remove_pattern, matched_content)
        remove_index_matches = remove_matches[0]
        return remove_matches,remove_index_matches
    
    def remove_table_tags(self,slide,id,remove_index_matches):
        id_tag = str(f"{id} {remove_index_matches} +++")
        for _shape in slide.shapes:
                if _shape.has_table: 
                    for row in _shape.table.rows:
                        for cell in row.cells:
                            for paragraph in cell.text_frame.paragraphs:
                                for run in paragraph.runs:
                                    if id_tag in run.text:
                                            new_text = run.text.replace(str(f"{id} {remove_index_matches} +++"), "")
                                            run.text = new_text
     
    
                                            
                        
     
    