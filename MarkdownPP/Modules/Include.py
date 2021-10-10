# Copyright 2015 John Reese
# Licensed under the MIT license

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import glob
import re
import yaml
from os import path, getcwd, replace

from MarkdownPP.Module import Module
from MarkdownPP.Transform import Transform

from MarkdownPP.Common import PROJECT_DIR, process_path

from MarkdownPP.Common import frontmatter_regex
from MarkdownPP.Common import frontmatter_this_regex
from MarkdownPP.Common import include_code_regex
from MarkdownPP.Common import embedded_image_regex
from MarkdownPP.Common import md_title_regex

from MarkdownPP.Common import all_frontmatter


class Include(Module):
    """
    Module for recursively including the contents of other files into the
    current document using a command like `!INCLUDE "path/to/filename"`.
    Target paths can be absolute or relative to the file containing the command
    """
    DEFAULT = True
    REMOTE = False
    
    # matches !INCLUDE directives in .mdpp files
    includere = re.compile(r"^!INCLUDE\s+(?:\"([^\"]+)\"|'([^']+)')\s*(?:,\s*L?E?V?E?L?\s?(\d+))?\s*$") # New regex allows us to write LEVEL before shift value for clarity

    # matches unescaped formatting characters such as ` or _
    formatre = re.compile(r"[^\\]?[_*`]")

    # includes should happen before anything else
    priority = 1

    def transform(self, data):
        transforms = []

        linenum = 0
        for line in data:
            match = self.includere.search(line)
            image_match = embedded_image_regex.search(line)

            if match:
                includedata = self.include(match)
                transform = Transform(linenum=linenum, oper="swap",
                                       data=includedata)
                transforms.append(transform)
            elif image_match:
                # Handle images linked to in the top level file (not in included files)
                embed_img = image_match.group(3)
                replace_path = process_path(md_file=PROJECT_DIR.INPUT_FILE, file_to_embed=embed_img, get_abs=(not PROJECT_DIR.COLLECT))
                if 'Process_path ERROR' in replace_path:
                    new_embed = f'!ERROR "{line.rstrip()}" <!-- !ERROR: {replace_path.split(":")[-1]} -->'
                else:
                    new_embed = line.replace(embed_img, replace_path)

                print('\n\nTOPLEVEL IMG:\n', embed_img, '\n', replace_path)
                transform = Transform(linenum=linenum, oper="swap", data=[new_embed])
                transforms.append(transform)
            
            linenum += 1
        return transforms

    def include_file(self, filename, pwd="", shift=0):
        try:
            with open(filename, "r", encoding = self.encoding) as f:
                data = f.readlines()
                
            # YAML Frontmatter is detected, parsed and stored in memory
            frontmatter = ''
            match = frontmatter_regex.match(''.join(data))
            if match:
                frontmatter, data = match.groups()         # get yaml frontmatter as string
                frontmatter = yaml.safe_load(frontmatter)   # get yaml frontmatter as dictionary from string
                if isinstance(frontmatter, list) or isinstance(frontmatter, dict):
                    #self.all_frontmatter[filename] = frontmatter
                    all_frontmatter[filename] = frontmatter
                
                # Sneakily substitute "!FRONTMATTER this," to "!FRONTMATTER id.id,"
                this_id = f"id.{frontmatter.get('id', 'UNDEF')}"
                data = frontmatter_this_regex.sub(f"!FRONTMATTER {this_id},", data)

                data = [line+'\n' for line in data.split('\n')]

            # line by line, apply shift and recursively include file data
            linenum = 0
            includednum = 0

            for line in data:
                include_match = self.includere.search(line)
                image_match = embedded_image_regex.search(line)
                include_code_match = include_code_regex.search(line)

                if include_match:
                    dirname = path.dirname(filename)
                    data[linenum:linenum+1] = self.include(include_match, dirname)
                    includednum = linenum
                    # Update line so that we won't miss a shift if
                    # heading is on the 1st line.
                    line = data[linenum]

                elif image_match:
                    # Handle images linked to in subfiles through the !INCLUDE directive
                    embed_img = image_match.group(3)

                    replace_path = process_path(md_file=filename, file_to_embed=embed_img, get_abs=(not PROJECT_DIR.COLLECT))
                    new_embed = line.replace(embed_img, replace_path)

                    #print('\n\nSUBFILE IMG:\n', embed_img, '\n', replace_path)
                    data[linenum:linenum+1] = [new_embed]

                elif include_code_match:
                    # Make links to included code in sub files absolute such that the includcode module can parse later
                    code_file = include_code_match.group(1) or include_code_match.group(2)
                    
                #    print(path.join(path.dirname(filename), code_file))
                    replace_path = path.join(path.dirname(filename), code_file)
                    new_include_code = line.replace(code_file, replace_path)

                    data[linenum:linenum+1] = [new_include_code]
                    #print(new_include_code)
                

                if shift:
                    # Applies shift to header levels, if specified
                    titlematch = md_title_regex.search(line)
                    if titlematch:
                        to_del = []
                        for _ in range(shift):
                            # Skip underlines with empty above text
                            # or underlines that are the first line of an
                            # included file
                            prevtxt = re.sub(self.formatre, '',
                                             data[linenum - 1]).strip()
                            isunderlined = prevtxt and linenum > includednum
                            if data[linenum][0] == '#':
                                data[linenum] = "#" + data[linenum]
                            elif data[linenum][0] == '=' and isunderlined:
                                data[linenum] = data[linenum].replace("=", '-')
                            elif data[linenum][0] == '-' and isunderlined:
                                data[linenum] = '### ' + data[linenum - 1]
                                to_del.append(linenum - 1)
                        for l in to_del:
                            del data[l]

                linenum += 1

            return data

        except (IOError, OSError) as exc:
            print(exc)

        return []

    def include(self, match, pwd=""):
        # file name is caught in group 1 if it's written with double quotes,
        # or group 2 if written with single quotes
        fileglob = match.group(1) or match.group(2)

        shift = int(match.group(3) or 0)

        result = []
        if pwd != "":
            fileglob = path.join(pwd, fileglob)

        files = sorted(glob.glob(fileglob))

        if len(files) > 0:
            for filename in files:
                result += self.include_file(filename, pwd, shift)
        else:
            result.append("")

        return result
