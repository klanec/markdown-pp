# Copyright (C) 2016 Smart Software Solutions, Inc
# Licensed under the MIT license

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import re

from os import path
from os import walk, listdir

from MarkdownPP.Common import PROJECT_DIR

from MarkdownPP.Module import Module
from MarkdownPP.Transform import Transform
#from MarkdownPP.Modules.Include import Include


class IncludeDir(Module):
    """
    Module for recursively including the contents of all supported files in a specified directory.
    """
    DEFAULT = True
    REMOTE = False
        
    includedir_re = re.compile(r"^!INCLUDEDIR\s+(?:\"([^\"]+)\"|'([^']+)')\s*(?:,\s*RECURSE)?\s*(?:,\s*FORMATS \(([ .,\-a-zA-Z0-9]+)\))?$")

    # include dir should happen after before everything else
    priority = 0


    def transform(self, data):
        transforms = []

        linenum = 0
        for line in data:
            match = self.includedir_re.search(line)

            if match:
                include_dir = path.abspath(match.group(1))
                recurse = 'RECURSE' in match.group(0)

                # Get a list of all subfiles in specified folder
                if recurse:
                    subfiles_by_dir = [[path.join(root, file) for file in files] for root, dirs, files in walk(include_dir)]
                    subfiles = [file for directory in subfiles_by_dir for file in directory]
                else:
                    subfiles = [path.join(path.abspath(include_dir), file) for file in listdir(include_dir)]
                    subfiles = [file for file in subfiles if path.isfile(file)]

                images = ['.png','.apng', '.avif', '.gif', '.jpeg', '.jpg', '.svg', '.webp', '.bmp']
                md = ['.md', '.mdpp', '.txt']

                file_types = []
                if match.group(3):
                    file_types = ['.'+x.strip() for x in match.group(3).split(',')]

                data = []
                for file in subfiles:
                    name, ext = path.splitext(file)
                    # If the extension is in the list of specified extensions OR extensions were unspecified 
                    if ext in file_types or not file_types:
                        if ext in images:
                            data.append(f'![{path.basename(name)}]({file})\n\n')
                        elif ext in md:
                            data.append(f'!INCLUDE "{file}"\n\n')
                        else:
                            # Embed as code TODO: from here. Test this
                            data.append(f'!INCLUDECODE "{file}"\n\n')

                transform = Transform(linenum=linenum, oper="swap", data=data)
                transforms.append(transform)
            
            linenum += 1
        return transforms
