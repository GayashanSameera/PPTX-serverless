import pydash
import os
from pptx.util import Inches
from io import BytesIO
import io
import math
from pptx.util import Pt
import boto3
from botocore.exceptions import ClientError
import logging
from pptx.oxml.xmlchemy import OxmlElement
from lxml import etree
from copy import deepcopy
from pptx.table import Table, _Row, _Column, _Cell
from pptx.dml.color import RGBColor
import base64
from pptx import Presentation
import enum
import json
import re

POC_PPTX_BUCKET = os.environ.get("POC_PPTX_BUCKET")


class CommandRegex(enum.Enum):
    IMAGE = r'\+\+\+IM (.*?) \+\+\+',
    TEXT = r'\+\+\+INS (.*?) \+\+\+'
    UPDATE_TABLE_TEXT = r'\+\+\+TB_TX_UP (.*?) \+\+\+',
    CREATE_TABLE = r'\+\+\+TB_ADD (.*?) \+\+\+',
    PATTERN_FOR = r'\+\+\+FOR (.*?) FOR-END\+\+\+',
    PATTERN_CONTENT = r'\<\<(.*?)\>\>',
    PATTERN_CONDITION = r'\(\((.*?)\)\)',
    TABLE_DRAW = r'\+\+\+TB_DRW (.*?) \+\+\+'

class CommandRegexSub(enum.Enum):
    IMG = '+++IM'
    INS = '+++INS'
    TB_ADD = '+++TB_ADD'
    TB_TX_UP = '+++TB_TX_UP'
    TB_ID ='+++TB_ID'
    TB_DRW = '+++TB_DRW'
    FOR = '+++FOR'
    FOR_END = 'FOR-END+++'


class Command(enum.Enum):
    IF_CONDITION = "if_condition"
    FOR_LOOP = "for_loop"
    REPLACE_IMAGE = "replace_images"
    REPLACE_TABLE = "replace_table"
    UPDATE_TABLE_TEXT = "update_table_text"
    DRAW_TABLE = "draw_tables"
    TEXT_REPLACE = "text_replace"


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

    def get_command(self, command_name):
        if command_name == Command.REPLACE_IMAGE:
            image = Image()
            def getParams(commands_dic, presentation, slide, shape, slides, dataObj):
               return image.replace_images(slide, CommandRegex.IMAGE.value[0], shape)
            return getParams

        elif command_name == Command.TEXT_REPLACE:
            text = Text()
            def getParams(commands_dic, presentation, slide, shape, slides, dataObj):
                return text.text_replace(slide, CommandRegex.TEXT.value[0], shape)
            return getParams
        
        elif command_name == Command.UPDATE_TABLE_TEXT:
            table = Table()
            return table.update_table_text
          
        elif command_name == Command.DRAW_TABLE:
            table = Table()
            return table.drow_tables
            
        else:
            raise Exception("Invalid command name")


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

    def get_tag_from_string(pattern, string):
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


class Image(Tag):
    def __init__(self):
        pass

    def replace_images(self, slide, pattern, shape):
        match, object_value = super().get_object_values(pattern, shape)

        url = pydash.get(object_value, "url", default="")
        left = pydash.get(object_value, "size.left", default=1)
        height = pydash.get(object_value, "size.height", default=1)
        top = pydash.get(object_value, "size.top", default=5)
        width = pydash.get(object_value, "size.width", default=5)

        decodeimg = base64.b64decode(url)
        img = io.BytesIO(decodeimg)
        slide.shapes.add_picture(img, Inches(left), Inches(top), Inches(width), Inches(height))
        super().replace_tags(str(f"{CommandRegexSub.IMG.value} {match} +++"), "", shape)


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

class Table(Tag):
        def __init__(self):
            pass 

        def update_table_text(self,presentation, slide, shape, slide_index, dataObj):
            pattern = CommandRegex.UPDATE_TABLE_TEXT.value[0]
            matches = super().get_tag_content(pattern, shape)

            if( not matches or len(matches) < 1):
                return

            for match in matches:
                styles = False
                data = False
                data_path = False
                table_id = match

                if "DATA" in match:
                    data_path = match.split(" DATA ")[1]
                    table_id = match.split(" DATA ")[0]

                if data_path and data_path in dataObj:
                    data = dataObj[data_path]

                if data and "styles" in data:
                    styles = data["styles"]

                table_id_tag = str(f"{CommandRegexSub.TB_ID.value} {table_id} +++")
                for _shape in slide.shapes:
                    if _shape.has_table: 
                        for row in _shape.table.rows:
                            for cell in row.cells:
                                if table_id_tag in cell.text:
                                    self.execute_table_tags(_shape, _shape.table, data, styles,CommandRegex.FOR.value[0])
                                    new_text = cell.text.replace(str(f"{CommandRegexSub.TB_ID.value} {table_id} +++"), "")
                                    cell.text = new_text
                                    break

                super().replace_tags(str(f"{CommandRegexSub.TB_TX_UP.value} {match} +++"), "", shape)

        def execute_table_tags(self,shape , table, data, styles,pattern_for):
            row_index = 0
            for row in table.rows:
                col_index = 0
                for cell in row.cells:
                    pattern_for = CommandRegex.FOR.value[0]
                    matches_for = super().get_tag_from_string(pattern_for, cell.text)
                    if( matches_for and len(matches_for) > 0):
                        for match in matches_for:
                            pattern_condition = CommandRegex.CONDITION.value[0]
                            matched_condition = super().get_tag_from_string(pattern_condition,match)

                            pattern_content = CommandRegex.CONTENT.value[0]
                            matched_content = super().get_tag_from_string(pattern_content,match)
                            for contidion in matched_condition:
                                object_value = pydash.get(data, contidion)
                                text_result = ""
                                if(object_value):
                                    data_count = 1
                                    for _data in object_value:
                                        updated_data = super().text_tag_update(matched_content[0],_data)
                                        if(updated_data and updated_data["text"] and len(object_value) > data_count):
                                            text_result += updated_data["text"] + "\n"
                                        elif(updated_data and updated_data["text"]):
                                            text_result += updated_data["text"]
                                        data_count += 1
                                new_text = cell.text.replace(str(f"{CommandRegexSub.FOR.value} {match} {CommandRegexSub.FOR_END.value}"), text_result)
                                cell.text = new_text
                                try:
                                    self.table_styles(cell,row_index,col_index,styles)
                                except ValueError:
                                    print("error")
                        

                    pattern_text = CommandRegex.TEXT.value
                    matches_text_update = super().get_tag_from_string(pattern_text, cell.text)
                    if( matches_text_update and len(matches_text_update) > 0):
                        for match in matches_text_update:
                            new_text = cell.text.replace(str(f"{CommandRegexSub.INS.value} {match} +++"), pydash.get(data, match))
                            cell.text = new_text
                            try:
                                self.table_styles(cell,row_index,col_index,styles)
                            except ValueError:
                                print("error")
                    col_index += 1 
                row_index +=1     
            
        def table_styles(cell,row_index,col_index,styles  ):
            try:
                row_st_index = str(f'rw_{row_index}')
                col_st_index = str(f'cl_{col_index}')
                para_index = 0
                for paragraph in cell.text_frame.paragraphs:
                    para = cell.text_frame.paragraphs[para_index]
                    if(styles and 'all' in styles):
                        common_styles = styles['all']

                        if('font_size' in common_styles):
                            para.font.size = Pt(common_styles['font_size'])
                        if('font_name' in common_styles):
                            para.font.name = common_styles['font_name']
                        if('bold' in common_styles):
                            para.font.bold = common_styles['bold']
                        if('italic' in common_styles):
                            para.font.italic = common_styles['italic']
                        if("font_color" in common_styles):
                            para.font.color.rgb = RGBColor(common_styles["font_color"][0], common_styles["font_color"][1],common_styles["font_color"][2])
                        if("alignment" in common_styles):
                            if common_styles["alignment"] == "center":
                                para.alignment = PP_ALIGN.CENTER
                        if("background_color" in common_styles):
                            cell.fill.solid()
                            cell.fill.fore_color.rgb = RGBColor(common_styles["background_color"][0], common_styles["background_color"][1],common_styles["background_color"][2])

                    if(styles and row_st_index in styles):
                        _styles = styles[row_st_index]
                    if( "column_indexes" in _styles):
                        if(col_index in _styles["column_indexes"]):
                            if('font_size' in _styles):
                                para.font.size = Pt(_styles['font_size'])
                            if('font_name' in _styles):
                                para.font.name = _styles['font_name']
                            if('bold' in _styles):
                                para.font.bold = _styles['bold']
                            if('italic' in _styles):
                                para.font.italic = _styles['italic']
                            if("font_color" in _styles):
                                para.font.color.rgb = RGBColor(_styles["font_color"][0], _styles["font_color"][1],_styles["font_color"][2])
                            if("background_color" in _styles):
                                cell.fill.solid()
                                cell.fill.fore_color.rgb = RGBColor(_styles["background_color"][0], _styles["background_color"][1],_styles["background_color"][2])
                    else:
                        if('font_size' in _styles):
                            para.font.size = Pt(_styles['font_size'])
                        if('font_name' in _styles):
                            para.font.name = _styles['font_name']
                        if('bold' in _styles):
                            para.font.bold = _styles['bold']
                        if('italic' in _styles):
                            para.font.italic = _styles['italic']
                        if("font_color" in _styles):
                            para.font.color.rgb = RGBColor(_styles["font_color"][0], _styles["font_color"][1],_styles["font_color"][2])
                        if("background_color" in _styles):
                            cell.fill.solid()
                            cell.fill.fore_color.rgb = RGBColor(_styles["background_color"][0], _styles["background_color"][1],_styles["background_color"][2])

                if(styles and col_st_index in styles):
                    col_styles = styles[col_st_index]

                    if('font_size' in col_styles):
                        para.font.size = Pt(col_styles['font_size'])
                    if('font_name' in col_styles):
                        para.font.name = col_styles['font_name']
                    if('bold' in col_styles):
                        para.font.bold = col_styles['bold']
                    if('italic' in col_styles):
                        para.font.italic = col_styles['italic']
                    if("font_color" in col_styles):
                        para.font.color.rgb = RGBColor(col_styles["font_color"][0], col_styles["font_color"][1],col_styles["font_color"][2])
                    if("background_color" in col_styles):
                        cell.fill.solid()
                        cell.fill.fore_color.rgb = RGBColor(col_styles["background_color"][0], col_styles["background_color"][1],col_styles["background_color"][2])
        
                para_index += 1
            except ValueError:
                print("error")
                
        
        def replace_tables(self,pattern,presentation,slide,shape,slide_index,dataObj):
            match , object_value = super().get_object_values(pattern, shape)
            if(object_value):
                super().replace_tags(str(f"{CommandRegexSub.TB_ADD.value} {match} +++"), "", shape)
                self.create_table(presentation, slide, shape, slide_index, object_value)
                
                
        def create_table(presentation, slide, shape, slide_index, dataObj):
            row_count = pydash.get(dataObj,dataObj.cashFlows.row_count,default=5)
            cols = pydash.get(dataObj,dataObj.cashFlows.colum_count,default=3)
            headers = pydash.get(dataObj,dataObj.cashFlows.headers)
            row_data = pydash.get(dataObj,dataObj.cashFlows.rows)
            styles = pydash.get(dataObj,dataObj.cashFlows.styles)
            table_count_per_slide = pydash.get(dataObj,dataObj.cashFlows.table_count_per_slide,default=2)
            
            
            total_rows = len(row_data)
            total_table_count = math.ceil(total_rows / row_count)

            slide_count = math.ceil(total_table_count / table_count_per_slide) 
            extra_slide_count = slide_count - 1

            s = 0
            end = 0
            current_slide = 0
            while s < slide_count:
                j = 0
                left = 1

                if total_table_count > table_count_per_slide :
                    table_count = table_count_per_slide
                else:
                    table_count = total_table_count

                slide_row_start = 0
                slide_row_end = 0
                extra_slide_exists = False

                if(s > 0 and (not presentation.slides[slide_index + s])):
                    break

                if(s > 0 and current_slide != s):
                    for new_slide_shape in presentation.slides[slide_index + s].shapes:
                        extra_slide_exists = is_extra_slide(presentation, slide_index + s, True)
                        if(extra_slide_exists):
                            break
                    current_slide = s

                if(s > 0 and (not extra_slide_exists)):
                    return 
                

                while j < table_count:
                    shape = presentation.slides[slide_index + s].shapes.add_table(row_count + 1, cols, Inches(left) , Inches(styles["top"]), Inches(styles["width"]), Inches(styles["row_height"]))
                    table = shape.table
                    tables_headers(table, headers)

                    slide_row_start = (row_count * j ) + 1 + end
                    slide_row_end = slide_row_start + (row_count - 1)

                    tables_rows(table,row_data, slide_row_start, slide_row_end ,total_rows )
                    left += 2
                    j += 1

            end = slide_row_end
            total_table_count -= table_count_per_slide
            s += 1
            
            def is_extra_slide(presentation, slide_index, remove_tag):
                extra_slide_exists = False
                extra = 'EXTRA_SLIDE'
                for new_slide_shape in presentation.slides[slide_index].shapes:
                    if new_slide_shape.has_text_frame:
                        matches = super().check_tag_exist(extra, new_slide_shape)
                        if(matches):
                            extra_slide_exists = True
                            if(remove_tag):
                                super().replace_tags(str(f"+++ {extra} +++"), "", new_slide_shape)
                            break
                return extra_slide_exists
            
            
            def tables_headers(table, headers):
                i = 0
                for header in headers:
                    table.cell(0, i).text = header
                    cell = table.cell(0, i)
                    cell.fill.solid()
                    cell.fill.fore_color.rgb = RGBColor(200, 253, 251)
                    _set_cell_border(cell,"949595", '12000')
                    para = cell.text_frame.paragraphs[0]
                    para.font.bold = True
                    para.font.size = Pt(5)
                    para.font.name = 'Comic Sans MS'
                    para.font.color.rgb = RGBColor(19, 170, 246)
                    table.columns[i].width = Inches(0.6)
                    i += 1
                    
            def tables_rows(table, rowData, start, end,totalRows):
                j = start
                cell_start = 1

                entCount = end
                if end > totalRows:
                    entCount = totalRows

                while j < entCount + 1:
                    element = rowData[j - 1]
                    k = 0
                    if element:
                        for key, value in element.items():
                            table.cell(cell_start, k).text = value
                            cell = table.cell(cell_start, k)
                            cell.fill.solid()
                            cell.fill.fore_color.rgb = RGBColor(228, 228, 228)
                            _set_cell_border(cell,"949595", '12000')
                            para = cell.text_frame.paragraphs[0]
                            para.font.size = Pt(6)
                            para.font.name = 'Comic Sans MS'
                            k += 1
                    j += 1
                    cell_start += 1
                    
            def SubElement(parent, tagname, **kwargs):
                element = OxmlElement(tagname)
                element.attrib.update(kwargs)
                parent.append(element)
                return element
            
            def _set_cell_border(cell, border_color="000000", border_width='12700'):
                tc = cell._tc
                tcPr = tc.get_or_add_tcPr()
                for lines in ['a:lnL','a:lnR','a:lnT','a:lnB']:
                    ln = SubElement(tcPr, lines, w=border_width, cap='flat', cmpd='sng', algn='ctr')
                    solidFill = SubElement(ln, 'a:solidFill')
                    srgbClr = SubElement(solidFill, 'a:srgbClr', val=border_color)
                    prstDash = SubElement(ln, 'a:prstDash', val='solid')
                    round_ = SubElement(ln, 'a:round')
                    headEnd = SubElement(ln, 'a:headEnd', type='none', w='med', len='med')
                    tailEnd = SubElement(ln, 'a:tailEnd', type='none', w='med', len='med')
                    
                    
        def drow_tables(self,presentation, slide, shape, slide_index, dataObj):
            pattern = CommandRegex.TABLE_DRAW.value[0]
            matches = super().get_tag_content(pattern, shape)
            if( not matches or len(matches) < 1):
                return

            for match in matches:
                styles = False
                data = False
                data_path = False
                table_id = match

            if "DATA" in match:
                data_path = match.split(" DATA ")[1]
                table_id = match.split(" DATA ")[0]

            if data_path and data_path in dataObj:
                data = dataObj[data_path]

            if data and "styles" in data:
                styles = data["styles"]

            table_id_tag = str(f"{CommandRegexSub.TB_ID.value} {table_id} +++")
            for _shape in slide.shapes:
                if _shape.has_table: 
                    for row in _shape.table.rows:
                        for cell in row.cells:
                            if table_id_tag in cell.text:
                                self.execute_table_drower(_shape.table, data, styles)
                                new_text = cell.text.replace(str(f"{CommandRegexSub.TB_ID.value} {table_id} +++"), "")
                                cell.text = new_text
                                break

            super().replace_tags(str(f"{CommandRegexSub.TB_DRW.value} {match} +++"), "", shape)
        
        def execute_table_drower(self,table, dataObj,styles):
            row_data = pydash.get(dataObj,dataObj.cashFlows.rows,default=[])
            row_index = 1
            for row in row_data:
                colum_index = 0
                if row_index > 1:
                    self.add_new_row_to_existing_table(table)
                for column in row:
                    cell = table.cell(row_index, colum_index)
                    cell.text = column
                    
                    try:
                        self.table_styles(cell,row_index,colum_index,styles)
                    except ValueError:
                        print("error")

                    colum_index += 1
                row_index += 1
                
        def add_new_row_to_existing_table(table):
            new_row = deepcopy(table._tbl.tr_lst[1])
            for tc in new_row.tc_lst:
                cell = _Cell(tc, new_row.tc_lst)
                cell.text = '' # defaulting cell contents to empty text

                table._tbl.append(new_row) 
                return table.rows[1]

class Expression(Tag):
    def __init__(self, pattern):
        super().__init__(pattern)

    def if_condition(self):
        print("if condition func executed")

    def for_loop(self):
        print("for loop func executed")


class CommandExecutor:
    registry = CommandRegistry()

    def __init__(self, presentation, dataObj):
        self.slide = None
        self.presentation = presentation
        self.dataObj = dataObj

    def execute(self):
        # get command names as a list
        commands = self.registry.get_commands_list()

        commands_dic = self.registry.get_commands_dictionary()

        # find commands in the presentation using 'commands' list & execute
        slides = [self.slide for self.slide in self.presentation.slides]
        for shape in self.slide.shapes:
            if shape.has_text_frame:
                if shape.text:
                    for cmd_values in (Command):
                        try:
                            self.registry.get_command(cmd_values)(commands_dic, self.presentation, self.slide,
                                                                         shape, slides.index(self.slide), self.dataObj)
    
                        except Exception as e:
                            print(e.__class__)


def generate_pptx(event, context):
    s3_client = boto3.client('s3')
    response = s3_client.get_object(Bucket=POC_PPTX_BUCKET, Key='task.pptx')
    data = response['Body'].read()

    f = open("/tmp/task.pptx", "wb")
    f.write(data)
    f.close()
    presentationObject = Presentation('/tmp/task.pptx')
    dataObj = {
        
        "schemeName": "XYZ Pension Scheme",
        "title": "Q2 2021 Summary Report",
        "heading":"Investment performance to 30 June 2021",
        "heading_assets":"Investment performance to 30 June 2021",
        "assetAllocation": "Asset allocation at 30 June 2021",
        "assetChart": { "url" : "img1.png" , "size": {"left":1,"top":1, "height":3, "width":4.2}},
        "overallPerformance": "Overall performance",
        "OPData":{
            "styles" : {
                "rw_1": {
                    "font_size": 9,
                    "font_name": "Arial",
                    "alignment": "center",
                },
                "rw_2": {
                    "font_size": 9,
                    "font_name": "Arial",
                    "alignment": "center",
                },
                "rw_3": {
                    "font_size": 9,
                    "font_name": "Arial",
                    "font_color": (0, 118, 214),
                    "alignment": "center",
                }
            },
            "3monthsAsset": "5.6%",
            "1yrAssets": "7.7%",
            "assetsInception": "14.0%",
            "3monthsliab": "3.1%",
            "1yrliabs": "-6.7%",
            "liabsInception": "-3.6%",
            "3monthsOutPerformance": "2.4%",
            "1yrpr": "14.4%",
            "prInception": "17.6%",
        },
        "ACperformance":{
            "styles" : {
                "rw_1": {
                    "font_color": (252, 250, 250),
                    "bold": True,
                    "background_color": (14, 99, 179)
                },
                "rw_2": {
                    "bold": True,
                    "background_color": (46, 197, 217)
                },
                "rw_8": {
                    "bold": True,
                    "background_color": (46, 197, 217)
                },
                "rw_10": {
                    "font_color": (252, 250, 250),
                    "bold": True,
                    "background_color": (14, 99, 179)
                },
                "all": {
                    "font_size": 9,
                    "font_name": "Arial",
                    "alignment": "center",
                    "background_color": (252, 250, 250)
                },
            },
            "rows": [
                ["Scheme Performance", "5.6%" ,"7.7%"], 
                ["Total Growth","4.0%","15.3%"],
                ["Equities","5.4%","28.0%"],
                ["Corporate Bonds","2.6%","-0.1%"],
                ["Sovereign Bonds", "2.0%", "-1.4%"],
                ["Alternatives","4.8%","12.3%"],
                ["Dynamic Strategies","2.0%","13.9%"],
                ["Total Matching","13.3%","-24.7%"],
                ["LDI Funds & Cash","13.3%","-24.7%"],
                ["Liability Benchmark","3.1%","-6.7%"],
            ]
        },
        "assetAllocation":{
            "styles" : {
                "all":{
                    "font_size": 8.5,
                    "font_name": "Arial",
                    "font_color": (163, 162, 162),
                },
                "cl_0": {
                    "bold": True,
                    "alignment": "middle",
                },
                "rw_1": {
                    "column_indexes": [0, 1],
                    "font_color": (6, 123, 191),
                },
                "rw_2": {
                    "column_indexes": [0,1],
                    "font_color": (209, 189, 13),
                },
                "rw_3": {
                    "column_indexes": [0,1],
                    "font_color": (5, 125, 51),
                },
                "rw_4": {
                    "column_indexes": [0,1],
                    "font_color": (176, 19, 11),
                }
            },
            "data": {
                "eq": "EQUITIES",
                "eq_values": [
                    { "label": "UK Equity", "march": "1.8%", "june": "1.8%" },
                    { "label": "North America Equity", "march": "1.8%", "june": "1.9%" },
                    { "label": "Europe (ex UK) Equity", "march": "3.0%", "june": "2.7%" },
                    { "label": "Japan Equity", "march": "2.9%", "june": "2.8%" },
                    { "label": "Asia Pacific ex-Japan Equity", "march": "1.7%", "june": "1.7%" },
                    { "label": "Emerging Markets Equity", "march": "3.4%", "june": "3.6%" },
                    { "label": "Global Developed Small Cap Equity", "march": "2.7%", "june": "2.7%" },
                    { "label": "Smart beta equity", "march": "5.9%", "june": "5.6%" },
                ],
                "glb_bonds":"GLOBAL BONDS",
                "glb_values": [
                    { "label": "Fallen Angels’ Credit", "march": "5.1%", "june": "5.7%" },
                    { "label": "UK Investment Grade Credit", "march": "3.1%", "june": "4.9%" },
                    { "label": "Euro Investment Grade Credit", "march": "0.3%", "june": "0.7%" },
                    { "label": "US Investment Grade Credit", "march": "2.2%", "june": "2.2%" },
                    { "label": "Overseas Government Bonds", "march": "7.2%", "june": "5.5%" },
                ],
                "alternatives":"ALTERNATIVES",
                "alt_values": [
                    { "label": "Property", "march": "3.4%", "june": "3.4%" },
                    { "label": "Listed Private Equity", "march": "1.8%", "june": "1.7%" },
                    { "label": "High Yield Bonds", "march": "4.0%", "june": "3.9%" },
                    { "label": "Listed Infrastructure", "march": "4.1%", "june": "3.6%" },
                    { "label": "Global REITs", "march": "4.5%", "june": "4.4%" },
                    { "label": "Emerging Market Bonds (Local)", "march": "4.1%", "june": "4.2%" },
                    { "label": "Emerging Market Bonds (USD)", "march": "1.8%", "june": "1.9%" },
                    { "label": "Commodities", "march": "1.4%", "june": "1.5%" },
                ],
                
                "dynamic_str":"DYNAMIC  STRATEGIES",
                "dyn_str_values": [
                    { "label": "Multi-Asset Target Return (MATR)", "march": "16.5%", "june": "16.2%" },
                ],
                "lia_match":"LIABILITY-MATCHING",
                "lia_values":[
                    { "label": "Liability-matching credit", "march": "0.0%", "june": "0.0%" },
                    { "label": "Liability driven investment strategies", "march": "17.4%", "june": "17.5%" },
                ],
                "ratios":[
                    { "label": "Interest rate hedge ratio*", "march": "74%", "june": "73%" },
                    { "label": "Inflation hedge ratio*", "march": "74%", "june": "73%" },
                ]
            }
        },
        "position": "SSE",
        "city": "NW",
        "image_title": "This is a sample image",
        "sample_image": { "url" : "Sample-image.png" , "size": {"left":1,"top":1, "height":3, "width":8}},
        "project_description": "React , Node , AWS serverless",
        'table_name': "Sample table to delete",
        "remove_table_1": True,
        'table_name_row': "Sample table to delete row",
        "table_1_row_3_present": False,
        'table_name_column': "Sample table to delete column",
        "table_1_col_4_present": False,
        "sample_name": "Loop sample data",
        "sample_data_1": [{"name": "Kamal", "age": 12},{"name": "Amal", "age": 22},{"name": "Nuwan", "age": 32}],
        "sample_data_2": [{"name": "Sama", "age": 12},{"name": "Amara", "age": 22},{"name": "Nayana", "age": 32}],
        "sample_data_3": [{"city": "Colombo", "number": 1},{"city": "Colombo", "number": 2},{"city": "Colombo", "number": 3}],
        "cashFlows":{
                "headers": ["cashflow year","cashflow fixed","cashflow real"],
                "row_count": 10,
                "colum_count": 3,
                "table_count_per_slide": 4,
                "styles": {
                    "top": 1,
                    "width": 0.6,
                    "row_height": 0.04,
                },
                "rows": [ 
                    {
                        "cashflow_year": "2020","cashflow_fixed":"1","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"2","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"3","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"4","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"5","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"6","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"7","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"8","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"9","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"10","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"11","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"12","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"13","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"14","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"15","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"16","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"17","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"18","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"19","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"20","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"21","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"22","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"23","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"24","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"25","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"26","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"27","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"28","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"29","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"30","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"31","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"32","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"33","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"34","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"35","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"36","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"37","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"38","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"39","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"40","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"41","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"42","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"43","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"44","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"45","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"51","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"52","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"53","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"54","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"55","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"56","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"57","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"58","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"59","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"510","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"151","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"512","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"153","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"154","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"155","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"61","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"62","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"63","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"64","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"65","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"66","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"67","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"68","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"69","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"170","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"171","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"172","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"173","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"174","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"175","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"17","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"82","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"83","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"84","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"85","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"86","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"87","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"88","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"89","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"190","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"191","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"192","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"193","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"194","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"195","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"17","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"82","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"83","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"84","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"85","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"86","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"87","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"88","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"89","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"190","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"191","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"192","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"193","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"194","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"195","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"1","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"2","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"3","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"4","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"5","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"6","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"7","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"8","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"9","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"10","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"11","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"12","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"13","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"14","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"15","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"16","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"17","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"18","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"19","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"20","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"21","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"22","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"23","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"24","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"25","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"26","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"27","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"28","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"29","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"30","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"31","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"32","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"33","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"34","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"35","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"36","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"37","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"38","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"39","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"40","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"41","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"42","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"43","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"44","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"45","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"51","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"5112","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"5113","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"5114","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"5115","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"5116","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"5117","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"58","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"5911","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"51110","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"15111","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"5112","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"1513","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"1514","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"1515","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"611","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"612","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"6113","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"614","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"615","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"616","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"617","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"618","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"619","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"1170","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"1171","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"1172","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"1173","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"1714","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"1715","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"1117","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"812","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"813","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"814","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"815","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"816","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"817","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"818","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"819","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"1910","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"1911","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"1912","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"1913","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"1914","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"1915","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"117","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"812","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"813","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"814","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"815","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"816","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"187","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"818","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"189","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"1190","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"1911","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"1192","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"1913","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"1941","cashflow_real": "123123"
                    },
                    {
                        "cashflow_year": "2020","cashflow_fixed":"1915","cashflow_real": "123123"
                    }
                 ]
            }
    }
    executor = CommandExecutor(presentationObject, dataObj)
    executor.execute()

    try:
        with BytesIO() as fileobj:
            presentationObject.save(fileobj)
            fileobj.seek(0)
            PATH = 'given/path/output.pptx'
            res = s3_client.upload_fileobj(fileobj, POC_PPTX_BUCKET, PATH)
    except ClientError as e:
        logging.error(e)
        return False

    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response
