from tpip_pptx.tag import Tag


class Slide():
    tag = Tag()
    
    def __init__(self):
        pass

    def delete_slides(self,presentation, index):
        xml_slides = presentation.slides._sldIdLst  
        slides = list(xml_slides)
        try:
            slides[index]
            xml_slides.remove(slides[index])
        except ValueError:
            print("error") 
     
    def remove_extra_slides(self,presentation):
        extra = 'EXTRA_SLIDE'
        slides = [slide for slide in presentation.slides]
        slide_indexs_to_delete = []
        for slide in slides:
            for shape in slide.shapes:
                if shape.has_text_frame:
                    matches = self.tag.check_tag_exist(extra,shape)
                    if(matches):
                        slide_indexs_to_delete.append(slides.index(slide))

        if(len(slide_indexs_to_delete) > 0):
            array_index = 0
            for s_index in slide_indexs_to_delete:
                slide_index = s_index
                self.delete_slides(presentation, slide_index - array_index)
                array_index += 1 
                    
        return presentation