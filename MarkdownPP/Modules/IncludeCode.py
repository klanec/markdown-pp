# Copyright (C) 2016 Smart Software Solutions, Inc
# Changes by Nicholas Harris 2021
# Licensed under the MIT license

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import re

from os import path
from MarkdownPP.Common import PROJECT_DIR

from MarkdownPP.Module import Module
from MarkdownPP.Transform import Transform

from MarkdownPP.Common import include_code_regex

class IncludeCode(Module):
    """
    Module for recursively including the contents of other local code
    files into the current document using a command like
    `!INCLUDECODE "codes/mycode.py"`.
    Targets must be valid, absolute urls.
    """
    DEFAULT = True
    REMOTE = False

    # include code should happen after includes, but before everything else
    priority = 2


    def transform(self, data):
        transforms = []

        linenum = 0
        for line in data:
            match = include_code_regex.search(line)

            if match:
                include_code_data = self.include_code(match)
                transform = Transform(linenum=linenum, oper="swap", data=include_code_data)
                transforms.append(transform)
            
            linenum += 1
        return transforms

    def _select_lines(self, code_file, lines):
        # No lines given
        if lines is None:
            return code_file
        # Single line
        if ':' not in lines:
            # Line counting starts at 1. Need to offset by -1
            return code_file[(int(lines) - 1)]

        # Multiline python style e.g. 1:5, :5, 5:
        from_line, to_line = [int(x) if x else None for x in lines.split(':')]
        if from_line is None or from_line <= 0:
            from_line = 1
        if to_line is None or to_line > len(code_file):
            to_line = len(code_file)
        # Line counting starts at 1. Need to offset by -1
        return code_file[(from_line - 1):to_line]

    def include_code(self, match, pwd=""):
        dirname = path.dirname(PROJECT_DIR.INPUT_FILE)

        code_file = match.group(1) or match.group(2)
        code_file = path.join(dirname, code_file)
        
        lang = match.group(3)
        lines = match.group(4)

        if not path.isabs(code_file):
            code_file = path.join(pwd, code_file)

        try:
            with open(code_file, "r") as fs:
                code_data = fs.readlines()

            return (
                "```" + (str(lang) if lang is not None else "") + "\n"
                + "".join(self._select_lines(code_data, lines))
                + "\n```\n"
            )

        except (IOError, OSError) as exc:
            print(exc)

        return []
