import pydash
import re

def hello():
    print("hello")

class Tags:
    def __init__(self):
        pass

    def replace_tags():
        print()
    
    def get_tag_content(pattern, shape):
        matches = re.findall(pattern, shape.text)
        return matches

    def get_tag_from_string(pattern, string):
        matches = re.findall(pattern, string)
        return matches
    
class Text(Tags):
    def __init__(self):
        super().__ini__()
        self.pattern = r'\+\+\+INS (.*?) \+\+\+'

    def text_replace(slide, shape, pattern):
        matches = super().get_tag_content(pattern, shape)
        if( not matches or len(matches) < 1):
            return

        for match in matches:
            print("match",match)
            object_value = pydash.get(replacements, match)
            print("object_value",object_value)
            super().replace_tags(str(f"+++INS {match} +++"), str(object_value), shape)

    def text_tag_update(text, pattern):
        current_text = text
        matches = super().get_tag_from_string(pattern, text)
        if( not matches or len(matches) < 1):
            return { "text": text }

        for match in matches:
            object_value = pydash.get(replacements, match, False)
            if(object_value != False):
                current_text = current_text.replace(str(f"+++INS {match} +++"), str(object_value))
        
        return { "text": current_text }