from MarkdownPP.Module import Module
from MarkdownPP.Transform import Transform
from MarkdownPP.Common import markdown_table

from secrets import token_hex

import os
import re
import logging

class Comment(Module):
    """
    Module for adding various types of comments to final markdown document
    
    Basic command format for default color is:
    !COMMENT "Hello, World!" 
    !TODO "Add more foo, remove bar"

    Specify color as follows:
    !COMMENT "Hello, World!" Green
    !TODO "Add more foo, remove bar" DarkRed

    Default color for !COMMENT is DodgerBlue, default color for !TODO is OrangeRed

    All HTML colours are supported:
    https://www.w3schools.com/tags/ref_colornames.asp

    This module also handles the !ERROR tag but this is for the preprocessor to mark tags it failed to process for the user. Not intended to be used manually
    """
    DEFAULT = True
    REMOTE = False

    commentre =  re.compile(r'^!(COMMENT|TODO)\s?\"(.+)\"\s?([a-zA-Z]*)\s?(<!--.*-->)?$')
    # Match group 1 -> COMMENT|TODO
    # Match group 2 -> the comment/todo string
    # Match group 3 (optional) -> HTML style comment following tag

    table_of_todo_re = re.compile(r'^!(TABLE_OF_TODOS|TOT)$')

    priority = 8

    def transform(self, data):
        transforms = []
        todos = []
        linenum = 0
        literal = False

        for linenum, line in enumerate(data):
            match = self.commentre.search(line)

            if line[:3] == '```':
                literal = not literal
                continue
            elif literal:
                continue
            elif match:
                err_nonce = ''
                if 'TODO' in match.group(1):
                    err_nonce = token_hex(5)
                    todos.append((err_nonce, match.group(2)))
                comment = self.process_comment(match, err_nonce=err_nonce)
                transform = Transform(linenum=linenum, oper='swap',
                                        data=comment)
                transforms.append(transform)
       
        for linenum, line in enumerate(data):
            # Go through again searching for the !TABLE_OF_TODOS tag
            tot_match = self.table_of_todo_re.search(line)
            if tot_match:
                todos_hdr = [('Search Me', 'TO DO')] + todos
                table = markdown_table(todos_hdr, first_row_header=True)
                
                title_transform = Transform(linenum=linenum, oper='prepend', data=['\n**Table of TODOs**\n'])
                table_transform = Transform(linenum=linenum, oper='swap', data=table)
                
                transforms.append(table_transform)
                transforms.append(title_transform)
        return transforms


    def process_comment(self, match, err_nonce=''):
        '''
        Takes the comment or todo tag and returns the appropriate HTML colored <span> tag
        '''
        comment_type = match.group(1)
        comment = f'{comment_type}: {match.group(2)}'
        color = match.group(3)
        err = match.group(4)

        if not color:
            color = {
                'COMMENT':'DodgerBlue',
                'TODO':'OrangeRed',
                # 'ERROR':'FireBrick'
            }[comment_type]
        err_nonce = f" ({err_nonce})" if err_nonce else ""
        formatted = f'<span style="color:{color}">{comment}{err_nonce}</span>{err if err else ""}\n'

        if err:
            formatted = formatted.rstrip() + ' ' + err + '\n'

        return formatted



    # @staticmethod
    # def color(text, c='blue', end='\n'):
    #     return f'<span style="color:{c}">{text}</span>{end}'