# Copyright (C) 2016 Smart Software Solutions, Inc
# Licensed under the MIT license

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import re

from urllib.request import urlopen
from urllib.parse import urlparse
from urllib.error import HTTPError

from MarkdownPP.Modules.Include import Include

class IncludeURL(Include):
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
    priority = 0.1

    def include(self, match):
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
