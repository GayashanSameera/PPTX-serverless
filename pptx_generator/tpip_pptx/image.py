import pydash
import base64
import io

from pptx.util import Inches
from tpip_pptx.constants import CommandRegexSub,CommandRegex
from tpip_pptx.tag import Tag


class Image(Tag):
    def __init__(self):
        pass

    def replace_images(self,commands_dic,presentation,slide,shape,slides,dataObj):
        pattern = CommandRegex.IMAGE.value
        matching_val = super().get_object_values(pattern, shape,dataObj)
        
        for val in matching_val:
            url = pydash.get(matching_val[val], "url", default="")
            left = pydash.get(matching_val[val], "size.left", default=1)
            height = pydash.get(matching_val[val], "size.height", default=1)
            top = pydash.get(matching_val[val], "size.top", default=5)
            width = pydash.get(matching_val[val], "size.width", default=5)

            decodeimg = base64.b64decode(url)
            img = io.BytesIO(decodeimg)
            slide.shapes.add_picture(img, Inches(left), Inches(top), Inches(width), Inches(height))
            super().replace_tags(str(f"{CommandRegexSub.IMG.value} {val} +++"), "", shape)
