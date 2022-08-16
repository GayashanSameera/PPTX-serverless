from tpip_pptx.tag import Tag
from tpip_pptx.constants import CommandRegexSub, CommandRegex
from tpip_pptx.table import Table
import pydash

class Expression(Tag):
    def __init__(self):
        pass

    def if_condition(self, commands_dic, presentation, slide, shape, slides_index, dataObj):
        pattern = CommandRegex.PATTERN_IF.value
        matches = super().get_tag_content(pattern, shape)
        
        if( not matches or len(matches) < 1):
            return

        for match in matches:
            pattern_condition = CommandRegex.PATTERN_CONDITION.value
            matched_condition = super().get_tag_from_string(pattern_condition,match)

            pattern_content = CommandRegex.PATTERN_CONTENT.value
            matched_content = super().get_tag_from_string(pattern_content,match)
            
            for contidion in matched_condition:
                object_value = super().eval_executor(contidion, dataObj)

                #replace text
                text_replace_pattern = CommandRegex.TEXT.value
                text_matches = super().get_tag_from_string(text_replace_pattern, matched_content[0])
                if( text_matches and len(text_matches) > 0):
                    text_replace = ""
                    if(object_value):
                        updated_data = super().text_tag_update(matched_content[0],dataObj)
                        if(updated_data and updated_data["text"]):
                            text_replace = updated_data["text"]
                    # this is not working if you use tabspaces, but you can use spaces
                    super().replace_tags(str(f"{CommandRegexSub.IF.value} {match}{CommandRegexSub.IF_END.value}"), text_replace, shape)

                #remove tables
                table_remove_pattern = CommandRegex.TABLE_REMOVE.value
                table_remove_matches = super().get_tag_from_string(table_remove_pattern, matched_content[0])
                if( table_remove_matches and len(table_remove_matches) > 0):
                    if(object_value):
                        table = Table()
                        table.remove_tables(slide,matched_content[0])
                        super().replace_tags(str(f"{CommandRegexSub.IF.value} {match}{CommandRegexSub.IF_END.value}"), "", shape)

                #remove table row
                table_row_remove_pattern = CommandRegex.TABLE_ROW_REMOVE.value
                table_row_remove_matches = super().get_tag_from_string(table_row_remove_pattern, matched_content[0])
                if( table_row_remove_matches and len(table_row_remove_matches) > 0):
                    if(object_value):
                        table = Table()
                        table.remove_table_rows(slide,matched_content[0])
                        super().replace_tags(str(f"{CommandRegexSub.IF.value} {match}{CommandRegexSub.IF_END.value}"), "", shape)
                
                #remove table column
                table_column_remove_pattern = CommandRegex.TABLE_COLUMN_REMOVE.value
                table_column_remove_matches = super().get_tag_from_string(table_column_remove_pattern, matched_content[0])
                if( table_column_remove_matches and len(table_column_remove_matches) > 0):
                    if(object_value):
                        table = Table()
                        table.remove_table_column(slide,matched_content[0])
                        super().replace_tags(str(f"{CommandRegexSub.IF.value} {match}{CommandRegexSub.IF_END.value}"), "", shape)

    def for_loop(self, commands_dic, presentation, slide, shape, slides_index, dataObj):
        pattern = CommandRegex.PATTERN_FOR.value
        matches = super().get_tag_content(pattern, shape)
        
        if( not matches or len(matches) < 1):
            return

        for match in matches:
            pattern_condition = CommandRegex.PATTERN_CONDITION.value
            matched_condition = super().get_tag_from_string(pattern_condition,match)

            pattern_content = CommandRegex.PATTERN_CONTENT.value
            matched_content = super().get_tag_from_string(pattern_content,match)
            
            for contidion in matched_condition:
                object_value = pydash.get(dataObj, contidion)
                text_result = ""
                if(object_value):
                    for data in object_value:
                        updated_data = super().text_tag_update(matched_content[0],data)
                        if(updated_data and updated_data["text"]):
                            text_result += updated_data["text"] + "\n"

            # this is not working if you use tabspaces, but you can use spaces
            super().replace_tags(str(f"{CommandRegexSub.FOR.value} {match} {CommandRegexSub.FOR_END.value}"), text_result, shape)
 