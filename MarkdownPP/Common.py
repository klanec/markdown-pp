from os import path, mkdir
from shutil import copyfile
import logging
logging.basicConfig(filename='debug.log', level=logging.DEBUG)

class PROJECT_DIR:

    TOPLEVEL = None
    IMAGES_DIR = None
    FRONTMATTER_FILE = None
    LOG = None
    LOG_FILE = False
    CONVERT_TO_ABSOLUTE_PATHS = False
    MOVE_FILES_TO_PROJECT_DIR = False
    INPUT_FILE = ''
    COPIED_FILES = {}



def process_path(md_file, img_file_path):
    '''
    Takes the path of a markdown file and the image file path embedded in it. 
    Returns either the absolute path to the file or copies the file to the project dir and returns the path relative to the output markdwon report.

    relies on path.join(A, B) returning B if both A and B are absolute paths.
    '''
    dir = path.dirname(md_file)
    filename = path.basename(img_file_path)
    old_abs_path = path.abspath(path.join(dir, img_file_path))

    if not path.isfile(old_abs_path):
        return 'Process_path ERROR: Embedded file not found.'

    NORMAL = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[32;49;22m'

    if PROJECT_DIR.CONVERT_TO_ABSOLUTE_PATHS:
        return old_abs_path

    elif PROJECT_DIR.MOVE_FILES_TO_PROJECT_DIR:  
        # Check if it has been copied before, return if so
        if old_abs_path in PROJECT_DIR.COPIED_FILES.keys():
            return PROJECT_DIR.COPIED_FILES[old_abs_path]
        if not path.isdir(PROJECT_DIR.IMAGES_DIR): 
            mkdir(PROJECT_DIR.IMAGES_DIR)
        
        # If a file of that name exists, rename with (1), (2), (3), etc
        new_abs_path = path.join(PROJECT_DIR.IMAGES_DIR, filename)
        new_abs_name, new_abs_ext = path.splitext(new_abs_path)
        i = 1
        while path.isfile(new_abs_path):
            new_abs_path = f'{new_abs_name}({i}){new_abs_ext}'
            i+=1
        
        new_abs_path = copyfile(old_abs_path, new_abs_path)
        new_rel_path = path.relpath(new_abs_path, PROJECT_DIR.TOPLEVEL)

        PROJECT_DIR.COPIED_FILES[old_abs_path] = new_rel_path

        # Return the new relative path
        return new_rel_path

    else: 
        return img_file_path
    

def markdown_table(data, first_row_header=False):
    '''
    The filthy cheater's way to get really nice markdown tables from any input.
    Requires pandas and tabulate (available through pip)

    parameters:
        data (list): list of dictionaries

    return:
        list: markdown table of data, as a list of lines, ready for Transform
    '''
    from pandas import DataFrame

    # Create a dataframe, then apply a lambda to each cell such that list type cells are converted to bullet points in html
    df = DataFrame(data).applymap(lambda x: '<ul><li>'+'</li><li>'.join(x)+'</li></ul>' if isinstance(x, list) else x)

    if first_row_header:
        new_header = df.iloc[0] #grab the first row for the header
        df = df[1:] #take the data less the header row
        df.columns = new_header #set the header row as the df header

    table = df.to_markdown(index=False, tablefmt="pipe")

    return [l+'\n' for l in table.split('\n') if l]