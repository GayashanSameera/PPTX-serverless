import pydash
import base64
import io

from pptx.util import Inches
from tpip_pptx.constants import CommandRegexSub
from tpip_pptx.tag import Tag


class Image(Tag):
    def __init__(self):
        pass

    def replace_images(self, slide, pattern, shape, dataObj):
        match, object_value = super().get_object_values(pattern, shape,dataObj)

        url = pydash.get(object_value, "url", default="")
        left = pydash.get(object_value, "size.left", default=1)
        height = pydash.get(object_value, "size.height", default=1)
        top = pydash.get(object_value, "size.top", default=5)
        width = pydash.get(object_value, "size.width", default=5)

        decodeimg = base64.b64decode(url)
        img = io.BytesIO(decodeimg)
        slide.shapes.add_picture(img, Inches(left), Inches(top), Inches(width), Inches(height))
        super().replace_tags(str(f"{CommandRegexSub.IMG.value} {match} +++"), "", shape)
