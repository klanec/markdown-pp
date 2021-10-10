#!/usr/bin/env python

# Copyright (C) 2010 John Reese
# Modified in 2021 with love by Nicholas Harris

# Licensed under the MIT license

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import sys
import MarkdownPP
import click
import sys
import logging

from os import path
from os import mkdir, access, getcwd, remove
from os import W_OK, X_OK

from MarkdownPP import Modules
from MarkdownPP.Common import PROJECT_DIR


# Terminal output ANSI color codes
class colors:
    BLUE = '\033[36;49;22m'
    MAGB = '\033[35;49;1m'
    GREEN = '\033[32;49;22m'
    NORMAL = '\033[0m'
    RED = '\033[91m'


# Create help string
help_str = '\b\nModules: (in run order)\n '
modules = sorted(Modules.modules, key = lambda x: Modules.modules[x]().priority)
for name in modules:
    m = Modules.modules[name]()
    d = 'enabled |' if m.DEFAULT else '* disabled |'
    r = (colors.RED + 'REMOTE CALLS' + colors.NORMAL) if m.REMOTE else (colors.GREEN + 'local only' + colors.NORMAL)
    help_str += "\n{: >18} {: >12} {: >15}".format(f'{name} |', d, r)


@click.command(help=help_str)
@click.option('--output', '-o', help='Output single file.', type=click.File(mode='w'))
@click.option('--collect', '-c', help='Output self-contained report and all files to a directory.', type=click.Path(dir_okay=True, file_okay=False)) # Add timestamp by default
@click.option('--include', '-i', help='Run only the specified modules (comma separated)', type=str)
@click.option('--exclude', '-e', help='Run all modules except the specified modules (comma separated)', type=str)
@click.option('--all-modules', '-a', help='Run all modules', is_flag=True)
@click.option('--log', '-l', help='Enable debug, warn and error logging', is_flag=True)                # Not yet implemented
@click.argument('input', type=click.File(mode='r'))
def cli(output, collect, include, exclude, all_modules, log, input):

    PROJECT_DIR.COLLECT = collect

    # Save the input file path 
    PROJECT_DIR.INPUT_FILE = path.abspath(input.name)
 
    # Set modules to run
    modules = list(MarkdownPP.modules)
    if include and exclude:
        click.echo("Can't include and exclude modules!")
        return -1
    elif include or exclude:
        # Check included/excluded are legal modules, set modules to process
        input_modules = include.split(',') if include else exclude.split(',')
        illegal = [module for module in input_modules if (module not in modules) and module]
        if illegal:
            click.echo(f'Illegal modules: {", ".join(illegal)}')
            return -1
        if include:
            modules = input_modules
        else:
            modules = [mod for mod in modules if mod not in input_modules]
    elif not all_modules:
        # Run default only unless all_modeuls is true
        modules = [name for name in Modules.modules if Modules.modules[name]().DEFAULT]
    
    # Handle output file / directory
    if output and collect:
        click.echo("Won't output to a file and a directory at the same time. chose either --output or --collect.")
        return -1
    if not output and not collect:
        # Set output to stdout if no other specified.
        output = sys.stdout
    if collect:
        collection_dir = path.abspath(collect)
        # Make a directory if it doesn't exist
        if not path.exists(collection_dir):
            try:
                mkdir(collection_dir)
            except FileNotFoundError:
                click.echo('Path to directory must be valid. Only collection directory will be created')
                return -1
        # Set output to be in collection directory
        output = open(path.join(collection_dir, 'Report.md'), mode='w')
        if path.isdir(collection_dir) and access(collection_dir, W_OK | X_OK):
            # If collection dir is a directory and writable, set accordingly
            PROJECT_DIR.TOPLEVEL = collection_dir
            PROJECT_DIR.IMAGES_DIR = path.join(collection_dir, 'images')
            PROJECT_DIR.FRONTMATTER_FILE = path.join(collection_dir, 'frontmatter.yaml')
            PROJECT_DIR.LOG_FILE = path.join(collection_dir, 'debug.log')
        else:
            click.echo(f'Make sure collection directory is not a file and is writable.\n\t{collect} ')
            return -1
    else:
        # Otherwise set current working directory
        cwd = getcwd()
        PROJECT_DIR.TOPLEVEL = cwd
        PROJECT_DIR.IMAGES_DIR = path.join(cwd, 'images')
        PROJECT_DIR.FRONTMATTER_FILE = path.join(cwd, 'frontmatter.yaml')
        PROJECT_DIR.LOG_FILE = path.join(cwd, 'debug.log')



    # Run preprocessor
    MarkdownPP.MarkdownPP(input=input, output=output, modules=modules)

    # Close the handlers
    input.close()
    if output:
        output.close()