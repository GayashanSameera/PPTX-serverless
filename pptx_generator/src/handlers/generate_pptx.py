import pydash
from pptx.util import Inches
from pptx import Presentation
import enum
import re


dataObj = {
       
        "schemeName": "XYZ Pension Scheme",
        "title": "Q2 2021 Summary Report",
        "heading":"Investment performance to 30 June 2021",
	
    }

prs = Presentation('input.pptx')
print(prs)


    
class CommandRegex(enum.Enum):
    IMAGE = r'\+\+\+IM (.*?) \+\+\+',
    TEXT  = r'\+\+\+INS (.*?) \+\+\+'
    
class Command(enum.Enum):
        IF_CONDITION = "if_condition"
        FOR_LOOP = "for_loop"
        REPLACE_IMAGE = "replace_images"
        REPLACE_TABLE = "replace_table"
        UPDATE_TABLE_TEXT = "update_table_text"
        DRAW_TABLE = "draw_tables"
        TEXT_REPLACE = "text_replace"
    

class Tag:
        def __init__(self,pattern):
                self.pattern = pattern
        
        def get_tag_content(self,pattern, shape):
             print('inside matches')
            # print('pattern',pattern)
    
           
             print('check123',shape.text)
             matches = re.findall(pattern,shape.text)
             print('INS', matches)
             return matches
        
        def replace_tags(self,replaced_for,replaced_text,shape):
            # print("vvv")
            print('replace_for',replaced_for)
            print('replace_text',replaced_text)
            if shape.has_text_frame:
                print('Has text', shape.has_text_frame)
                text_frame = shape.text_frame
                print('text_frame',text_frame)
            for paragraph in text_frame.paragraphs:
                print('paragraph',paragraph)
                for run in paragraph.runs:
                    cur_text = run.text
                    print('cur_text',cur_text)
                    new_text = cur_text.replace(replaced_for, replaced_text)
                    print('new_text',new_text)
                    run.text = new_text
    
        def get_object_values(self,pattern,shape):
            # print('seee', shape)
            matches = self.get_tag_content(pattern,shape)
            # print('Matches', matches)
            if( not matches or len(matches) < 1):
                return
            for match in matches:
                object_value = pydash.get(dataObj, match)
                return match , object_value
              
        def get_object_values_string(self,pattern,shape):
             if( not matches or len(matches) < 1):
               return { "text": text }

             for match in matches:
               object_value = pydash.get(dataObj, match, False)
               if(object_value != False):
                    current_text = current_text.replace(str(f"+++INS {match} +++"), str(object_value))

    
             return { "text": current_text }
                
            
        def get_tag_from_string(pattern,string):
            matches = re.findall(pattern, string)
            return matches
        
        
        
        

class Image(Tag):
        def __init__(self):
            pass
            
        def replace_images(self,slide,pattern,shape): 
          
          print('shape',shape)
          print('pattern',pattern)   
          # print('start')
          match , object_value = super().get_object_values(pattern,shape)
          print('object_value',object_value,"match",match)
          # print('end')
          # # print("shape.text",shape)
          # Tag.get_object_values(pattern,shape)
          url = pydash.get(object_value, "url")
          left = pydash.get(object_value, "size.left")
          height = pydash.get(object_value, "size.height")
          top = pydash.get(object_value, "size.top")
          width = pydash.get(object_value, "size.width")
          
          print("shapeTextFrame",shape)
          slide.shapes.add_picture(url, Inches(left), Inches(top), Inches(width) ,Inches(height) )
          super().replace_tags(str(f"+++IM {match} +++"),"", shape)
          
        def printHello(self,name):
           print(name)
        
 
class Text(Tag):
  
   def __init__(self):
      pass
          
   def text_replace(self, slide, pattern,shape):
      match, object_value =super().get_object_values(pattern,shape)
      print("Match", dataObj)
      super().replace_tags(str(f"+++INS {match} +++"), str(object_value), shape)
      
   def text_tag_update(pattern,text):
       match, object_value = super().get_object_values_string(self,pattern,shape)
       if(object_value != False):
            current_text = current_text.replace(str(f"+++INS {match} +++"), str(object_value))
        
# def replace_images(slide,pattern,shape): 
#       tag = Tag(r'\+\+\+IM (.*?) \+\+\+')
#       print('shape',shape)
#       print('pattern',pattern)   
#       # print('start')
#       match , object_value = tag.get_object_values(pattern,shape)
#       print('object_value',object_value,"match",match)
#       # print('end')
#       # # print("shape.text",shape)
#       # Tag.get_object_values(pattern,shape)
#       url = pydash.get(object_value, "url")
#       left = pydash.get(object_value, "size.left")
#       height = pydash.get(object_value, "size.height")
#       top = pydash.get(object_value, "size.top")
#       width = pydash.get(object_value, "size.width")
      
#       print("shapeTextFrame",shape)
#       slide.shapes.add_picture(url, Inches(left), Inches(top), Inches(width) ,Inches(height) )
#       tag.replace_tags(str(f"+++IM {match} +++"),"", shape)
                              
class Expression(Tag):
        def __init__(self,pattern):
            super().__init__(pattern)

        def if_condition(self):
            print("if condition func executed")

        def for_loop(self):
            print("for loop func executed")
            

class CommandRegistry:
        def __init__(self):
            self.commands = {
                "+++IF": "if_condition",
                "+++FOR": "for_loop",
                "+++IM": "replace_image",
                "+++TB_ADD": "replace_table",
                "+++TB_TX_UP": "update_table_text",
                "+++TB_DRW": "draw_tables",
                "+++INS": "text_replace"
            }

        def get_commands_dictionary(self):
            return self.commands

        def get_commands_list(self):
            return self.commands.keys()

        def get_command(self,command_name):
            # print('shapeText',shapeText)
            # if command_name == Command.IF_CONDITION:
            #     expression = Expression()
            #     return expression.if_condition
            # elif command_name == Command.FOR_LOOP:
            #     expression = Expression()
            #     return expression.for_loop
            if command_name == Command.REPLACE_IMAGE:
              # def getData(shape,slide):
              #    return getData
              print("zzzzzzzzzz")
              try:
                 image = Image()
                 image.printHello('helooooo')
                 def forTest(commands_dic,presentation,slide,shape,slides,dataObj):
                   
                    return image.replace_images(slide,r'\+\+\+IM (.*?) \+\+\+',shape)
                  #  print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',a,b,c,d,e,f)
                 return forTest
              except Exception as e:
                print("hello")
                print(e)
            elif command_name == Command.TEXT_REPLACE:
              # def getData(shape,slide):
              #    return getData
              print("Text", command_name)
              try:
                 text = Text()
                 #text.text_replace()
                 def forTest(commands_dic,presentation,slide,shape,slides,dataObj):
                    print('dataObj', slide)
                    return text.text_replace(slide,r'\+\+\+INS (.*?) \+\+\+',shape)
                  #  print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',a,b,c,d,e,f)
                 return forTest
              except Exception as e:
                print("hello")
                print(e)         
            else:
                raise Exception("Invalid command name")


class CommandExecutor:
        registry = CommandRegistry()

        def __init__(self, presentation, dataObj):
            self.slide = None
            self.presentation = presentation
            self.dataObj = dataObj

        def execute(self):
            # get command names as a list
            commands = self.registry.get_commands_list()
            # print("a",commands)
            commands_dic = self.registry.get_commands_dictionary()
            # print("b",commands_dic)

            # find commands in the presentation using 'commands' list & execute
            slides = [self.slide for self.slide in self.presentation.slides]
            for shape in self.slide.shapes:
                if shape.has_text_frame:
                    print('slide', slides)
                    if shape.text:
                        try:
                            print("shape.text",shape.text)
                            self.registry.get_command(Command.TEXT_REPLACE)(commands_dic, self.presentation, self.slide, shape, slides.index(self.slide), self.dataObj)
                        except Exception as e:
                           print(e.__class__)
                          #  print(commands_dic, self.presentation, self.slide, shape, slides.index(self.slide), self.dataObj)
                        
    

    
executor = CommandExecutor(prs, dataObj)
executor.execute()
prs.save('output.pptx')
    
  
    
   
        
        
