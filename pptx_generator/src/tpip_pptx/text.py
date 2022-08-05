from constants import CommandRegexSub
from tag import Tag

class Text(Tag):
    def __init__(self):
        pass

    def text_replace(self, slide, pattern, shape):
        match, object_value = super().get_object_values(pattern, shape)
        super().replace_tags(str(f"{CommandRegexSub.INS.value} {match} +++"), str(object_value), shape)

    def text_tag_update(pattern, text):
        match, object_value = super().get_object_values_string(pattern, text)
        if (object_value != False):
            current_text = current_text.replace(str(f"{CommandRegexSub.INS.value} {match} +++"), str(object_value))