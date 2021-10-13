# Copyright 2015 John Reese
# Licensed under the MIT license

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from MarkdownPP import Modules
from MarkdownPP.Common import PROJECT_DIR
from .Processor import Processor

import sys
from secrets import token_hex
from os import getcwd
from os import path

class MarkdownPP:
    """
    Simplified front-end interface for the Processor and Module systems.
    Takes input and output file names or objects, and a list of module names.
    Automatically executes the preprocessor with the requested modules.
    """

    def __init__(self, input=None, output=None, modules=None, encoding=None, timestamp=None):
        if encoding == None:
            encoding = sys.getdefaultencoding()
        if not PROJECT_DIR.INPUT_FILE:
            # If run programmatically on StringIO() input (eg in the tests), we need to give a random value for input file in PWD
            PROJECT_DIR.INPUT_FILE = path.join(getcwd(), token_hex(8))
        all_frontmatter = {}
        pp = Processor(encoding)

        for name in [m.lower() for m in modules]:
            if name in Modules.modules:
                module = Modules.modules[name]()
                module.encoding = encoding
                pp.register(module)

        pp.input(input)
        pp.process()
        pp.output(output)
