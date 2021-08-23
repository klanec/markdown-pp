from MarkdownPP.Module import Module
from MarkdownPP.Transform import Transform

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
    commentre =  re.compile(r'^!(COMMENT|TODO|ERROR)\s?\"(.+)\"\s?([a-zA-Z]*)\s?(<!--.*-->)?$')#^!(COMMENT|TODO)\s?\"(.*)\"\s?([a-zA-Z]*)$')

    priority = 1

    def transform(self, data):
        transforms = []

        linenum = 0
        for linenum, line in enumerate(data):
            match = self.commentre.search(line)
            if match:
                comment = self.process_comment(match)
                transform = Transform(linenum=linenum, oper='swap',
                                        data=comment)
                transforms.append(transform)

        return transforms


    def process_comment(self, match):
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
                'ERROR':'FireBrick'
            }[comment_type]

        formatted = self.color(comment, c=color)

        if err:
            formatted = formatted.rstrip() + ' ' + err + '\n'

        return formatted



    @staticmethod
    def color(text, c='blue', end='\n'):
        return f'<span style="color:{c}">{text}</span>{end}'