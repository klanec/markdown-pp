from MarkdownPP.Module import Module
from MarkdownPP.Transform import Transform
from MarkdownPP.Common import markdown_table

import os
import re
import logging

from secrets import token_hex

class Error(Module):
    """
    Module that handles atuomatically formatting the !ERROR tag. 
    For the preprocessor to mark tags it failed to process for the user. 
    Not intended to be used manually
    """
    DEFAULT = True
    REMOTE = False

    error_re =  re.compile(r'^!ERROR\s?\"(.+)\"\s?<!--(.*)-->$')
    table_of_errors_re = re.compile(r'^!(TABLE_OF_ERRORS|TOE)$')

    priority = 9

    def transform(self, data):
        transforms = []
        errors = []
        literal = False
        for linenum, line in enumerate(data):
            # If !ERROR tag found, format and output
            err_match = self.error_re.search(line)


            if line[:3] == '```':
                literal = not literal
                continue
            elif literal:
                continue
            elif err_match:
                error = err_match.group(1).strip()
                err = err_match.group(2).strip()

                err_nonce = token_hex(5)

                errors.append((err_nonce, error, err.replace('!ERROR:', '').strip()))

                comment = f'<span style="color:FireBrick" id="{err_nonce}">ERROR {err_nonce}: {error}</span> <!-- {err} -->\n'
                transform = Transform(linenum=linenum, oper='swap',
                                        data=comment)
                transforms.append(transform)
        
        #print('searching for table of errors...')
        
        literal = False
        for linenum, line in enumerate(data):
            # If !TABLE_OF_ERRORS tag found, format and output
            toe_match = self.table_of_errors_re.search(line)

            if line[:3] == '```':
                literal = not literal
                continue
            elif literal:
                continue
            elif toe_match:
                #print(linenum, line.strip(), 'FOUND')
                errors_hdr = [('Search Me', 'Error Tag', 'Error Cause')] + errors
                table = markdown_table(errors_hdr, first_row_header=True)
                
                title_transform = Transform(linenum=linenum, oper='prepend', data=['\n**Table of Errors**\n'])
                table_transform = Transform(linenum=linenum, oper='swap', data=table)
                
                transforms.append(table_transform)
                transforms.append(title_transform)

        return transforms