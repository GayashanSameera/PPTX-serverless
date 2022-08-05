import enum

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