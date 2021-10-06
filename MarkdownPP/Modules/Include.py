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


class Include(Module):
    """
    Module for recursively including the contents of other files into the
    current document using a command like `!INCLUDE "path/to/filename"`.
    Target paths can be absolute or relative to the file containing the command
    """
    DEFAULT = True
    REMOTE = False
    
    #---- Frontmatter additions
    # Place to store all front matter collected throughout this module. This will be written to disk as a pickle? yaml? after module completes
    all_frontmatter = {}
    vprint = print if False else lambda *a, **k: None # verbose print. set boolean for debugging

    frontmatterre = re.compile(r"\A---(.*?)---\s*(.*?)\s*\Z", flags=re.DOTALL | re.MULTILINE)

    thisre = re.compile(r'!FRONTMATTER\s+this,')
    #----

    # matches !INCLUDE directives in .mdpp files
    includere = re.compile(r"^!INCLUDE\s+(?:\"([^\"]+)\"|'([^']+)')\s*(?:,\s*L?E?V?E?L?\s?(\d+))?\s*$") # New regex allows us to write LEVEL before shift value for clarity

    # matches title lines in Markdown files
    titlere = re.compile(r"^(:?#+.*|={3,}|-{3,})$")

    # matches images embedded with <img> or ![]() methods
    imagere = re.compile(r'^(<img |\[?!\[[\w\s=-]*?\]).*?(src="|\()([\w\/.-]+?)([" #\)?])(.*)$')
    # Link to image in match.group(3)

    # matches unescaped formatting characters such as ` or _
    formatre = re.compile(r"[^\\]?[_*`]")

    # includes should happen before anything else
    priority = 0

    def transform(self, data):
        transforms = []

        linenum = 0
        for line in data:
            match = self.includere.search(line)
            image_match = self.imagere.search(line)

            if match:
                includedata = self.include(match)
                transform = Transform(linenum=linenum, oper="swap",
                                       data=includedata)
                transforms.append(transform)
            
            elif image_match:
                # Handle images linked to in the top level file (not in included files)
                embed_img = image_match.group(3)
                replace_path = process_path(md_file=PROJECT_DIR.INPUT_FILE, img_file_path=embed_img)
                if 'Process_path ERROR' in replace_path:
                    new_embed = f'!ERROR "{line.rstrip()}" <!-- !ERROR: {replace_path.split(":")[-1]} -->'
                else:
                    new_embed = line.replace(embed_img, replace_path)

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
            match = self.frontmatterre.match(''.join(data))
            if match:
                frontmatter, data = match.groups()         # get yaml frontmatter as string
                frontmatter = yaml.safe_load(frontmatter)   # get yaml frontmatter as dictionary from string
                if isinstance(frontmatter, list) or isinstance(frontmatter, dict):
                    self.all_frontmatter[filename] = frontmatter
                
                # Sneakily substitute "!FRONTMATTER this," to "!FRONTMATTER id.id,"
                this_id = f"id.{frontmatter.get('id', 'UNDEF')}"
                data = self.thisre.sub(f"!FRONTMATTER {this_id},", data)

                data = [line+'\n' for line in data.split('\n')]

            # line by line, apply shift and recursively include file data
            linenum = 0
            includednum = 0

            for line in data:
                include_match = self.includere.search(line)
                image_match = self.imagere.search(line)

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

                    replace_path = process_path(md_file=filename, img_file_path=embed_img)
                    new_embed = line.replace(embed_img, replace_path)

                    data[linenum:linenum+1] = [new_embed]

                if shift :
                    # Applies shift to header levels, if specified
                    titlematch = self.titlere.search(line)
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

        if self.all_frontmatter:
            with open(PROJECT_DIR.FRONTMATTER_FILE, 'w') as fp:
                fp.write(yaml.dump(self.all_frontmatter))

        return result
