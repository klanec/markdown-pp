# Copyright (C) 2016 Smart Software Solutions, Inc
# Licensed under the MIT license

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import re
import yaml

from urllib.request import urlopen
from urllib.parse import urlparse
from urllib.error import HTTPError

from MarkdownPP.Module import Module
from MarkdownPP.Transform import Transform

from MarkdownPP.Common import frontmatter_regex
from MarkdownPP.Common import frontmatter_this_regex
from MarkdownPP.Common import frontmatter_storage

class IncludeURL(Module):
    """
    Module for recursively including the contents of other remote files into
    the current document using a command like
    `!INCLUDEURL "http://www.example.com"`.
    Targets must be valid, absolute urls.
    """
    DEFAULT = False
    REMOTE = True

    includere = re.compile(r"^!INCLUDEURL\s+(?:\"([^\"]+)\"|'([^']+)')\s*(?:,\s*L?E?V?E?L?\s?(\d+))?\s*$")

    # include urls should happen after includes, but before everything else
    priority = 2


    def transform(self, data):
        transforms = []
        literal = False
        for linenum, line in enumerate(data):
            match = self.includere.search(line)

            if line[:3] == '```':
                literal = not literal
                continue
            elif literal:
                continue
            elif match:
                include_url_data = self.include(match)
                transform = Transform(linenum=linenum, oper="swap", data=include_url_data)
                transforms.append(transform)
            
            linenum += 1
        return transforms


    def include(self, match):
        # TODO: add shift functionality like in !INCLUDE
        url = match.group(1) or match.group(2)

        shift = int(match.group(3) or 0)

        parsed_url = urlparse(url)
        if not parsed_url.netloc and not parsed_url.path:
            return [] # TODO: add !ERROR for unresolved URL

        try:
            binary_data = urlopen(url).readlines()
            data = []
            for datum in binary_data:
                data.append(datum.decode())
            if data:
                # YAML Frontmatter is detected, parsed and stored in memory
                frontmatter = ''
                match = frontmatter_regex.match(''.join(data))
                if match:
                    frontmatter, data = match.groups()         # get yaml frontmatter as string
                    frontmatter = yaml.safe_load(frontmatter)   # get yaml frontmatter as dictionary from string
                    if isinstance(frontmatter, list) or isinstance(frontmatter, dict):
                        frontmatter_storage.frontmatter[parsed_url.geturl()] = frontmatter
                    
                    # Sneakily substitute "!FRONTMATTER this," to "!FRONTMATTER id.id,"
                    this_id = f"id.{frontmatter.get('id', 'UNDEF')}"
                    data = frontmatter_this_regex.sub(f"!FRONTMATTER {this_id},", data)

                    data = [line+'\n' for line in data.split('\n')]

                # recursively include url data
                for line_num, line in enumerate(data):
                    match = self.includere.search(line)
                    if match:
                        data[line_num:line_num+1] = self.include(match)

                    line_num += 1

                return data

            return []
        
        except HTTPError as e:
            return [ f'!ERROR "{match.string.rstrip()}" <!-- !ERROR: {e} -->\n']
