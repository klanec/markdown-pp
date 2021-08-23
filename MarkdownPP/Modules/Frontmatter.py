from MarkdownPP.Module import Module
from MarkdownPP.Transform import Transform

import os
import yaml
import re

import logging

class Frontmatter(Module):
    """
    Module for building various structures from data extracted
    from included file's frontmatter section. 

    Basic command format is:
    !FRONTMATTER selector, structure(data)

    For example:
    !FRONTMATTER all, bullet_list(references)
    !FRONTMATTER this, numbered_list(references)
    !FRONTMATTER this, table(title, summary, reference)

    TODO:
        - Project directory needs to be handled better
        - frontmatter.yaml should have a defined location, not searched for recursively
    """
    columnre = re.compile(f"([^,\(\)\s]+)") # Gets lit of matches for "(a, b, c)"
    frontmatterre = re.compile(r"^!FRONTMATTER\s+([^,]+), *([\w.-]{1,32}\(.*?\)),? *(sort ([\w.-]+)\s(ascending|asc|descending|desc))?\s?$", flags=re.MULTILINE)
    frontmatter = ''

    selectors = ['all', 'this']
    structures = ['bullet.list', 'numbered.list', 'table']

    priority = 0.1

    logging.basicConfig(filename='debug.log', level=logging.DEBUG)
    logging.debug('class instantiated')

    def transform(self, data):
        logging.debug('running tansform()')
        transforms = []

        frontmatter_path = ''
        frontmatter = ''

        # Find and read the YAML frontmatter file
        for root, dirs, files in os.walk('.'):
            if 'frontmatter.yaml' in files:
                frontmatter_path = os.path.join(root, 'frontmatter.yaml')
        if frontmatter_path:
            with open(frontmatter_path, 'r') as fp:
                self.frontmatter = yaml.safe_load(fp.read())
                logging.debug('transform() -> loaded frontmatter')
        else:
            logging.debug('transform() -> Frontmatter path not found!')
        

        linenum = 0
        for line in data: # Go line by line through the mdpp file
            match = self.frontmatterre.search(line) # Find the Frontmatter tags
            if match:
                logging.debug(f'transform() -> !FRONTMATTER tag found: {str(linenum)}:{match.string.rstrip()}')
                
                frontmatterdata = self.process_frontmatter(match) # Process frontmatter tag to get markdown

                transform = Transform(linenum=linenum, oper="swap",
                                      data=frontmatterdata)

                transforms.append(transform)

            linenum += 1

        return transforms

 
    def process_frontmatter(self, match):
        '''
        Takes requested format for data, columns and selector and returns the appropriate markdown

        See below format guide for the command:
        !FRONTMATTER selector.tag, format(col1, col2, col3) [sort col1 descending]

        parameters:
            match (re.Match): Match object for the !FRONTMATTER tag string
        '''
        if not self.frontmatter:
            return [ f'!ERROR "{match.string.rstrip()}" <!-- !ERROR:  No frontmatter found -->\n']

        where=match.group(1)
        format=match.group(2)
        sort_column = match.group(4)
        sort_order = 'asc' if match.group(5) is None else match.group(5)

        formats = ['table', 'list', 'list.numbers', 'list.bullets']

        #   "table(a, b, c)" -> structure:"table" and columns:"(a, b, c)"
        structure, columns_str = format.split('(')
        columns = self.columnre.findall(columns_str)

        # Trim down frontmatter according to input
        data = self.selector(
            select = columns,
            _from = self.frontmatter,
            where = where,
            sort_col=sort_column, 
            sort_ord=sort_order
        )

        # REMOVE THIS
        if not data:
            return [ f'!ERROR "{match.string.rstrip()}" <!-- !ERROR:  No matching data found in frontmatter -->\n']

        # get correct output based on requested data format
        return {
            'table': lambda d: self.markdown_table_pandas(data=d), # Temporarily set to pandas, which is big but looks nicer
            'table.pandas': lambda d: self.markdown_table_pandas(data=d), # Not yet implemented
            'list': lambda d: self.markdown_list(data=d, t='bullets'),
            'list.bullets':lambda d: self.markdown_list(data=d, t='bullet'),
            'list.numbers':lambda d: self.markdown_list(data=d, t='numbered'),
        }.get(structure, lambda d: f'!ERROR "{match.string.rstrip()}" <!-- !ERROR:  Requested data structure not recognized -->\n')(data) # CONTINUE HERE.  Test this

    
    @staticmethod
    def markdown_list(data, t = 'bullet', indent=0):
        '''
        Takes a string, list, or dictionary and returns a list representing that entity as markdown.
        If its a dictionary, we print the key, iterate the indent level and recurse on the values
        If its a list, we iterate the indent level and recurse on each item
        If its a string (or anything else) we simply return it in a list

        parameters:
            data: the data to process. String, List or Dict
            t (str): the type of list. 'numbered' or 'bullet'
            indent: the amount of whitespace between the current element and the margin

        returns:
            list: a line-by-line list of markdown

        TODO: 
        - add ability to change list type based on indent level
        - When listing a single column dictionary, we shouldn't include the first indent level (try listing affected items after selector)
        '''
        def recurse_list(data, t='bullet',indent=0):
            '''
            Nested recursive function to allow in class recursion of staticmethod
            '''
            ts = {'numbered':'1.', 'bullet':'-', 'bullets':'-'}.get(t, '-')
            lines = []
            i = indent*'   '

            if isinstance(data, list):
                for item in data:
                    lines += recurse_list(item, t=t, indent=indent)
            elif isinstance(data, dict):
                for key,value in data.items():
                    if indent == 0:
                        lines += [] + recurse_list(value, t=t, indent=indent)
                    else:
                        lines += [f'{i+ts} {key}\n'] + recurse_list(value, t=t, indent=indent+1)
            else:
                lines = [f'{i+ts} {data}\n']

            return lines
        
        return recurse_list(data, t, indent)


    @staticmethod
    def selector(select, _from, where, sort_col='', sort_ord='asc', not_found='N/A'):
        ''' 
        Takes a YAML frontmatter dictionary and returns a list of dictionaries based on input.

        parameters:
            select (tuple): tuple containing the 'columns' to select from each fronmatter entry
            _from (dict): frontmatter YAML dictionary formatted as {FILE:FRONTMATTER}
            where (str): string indicating which frontmatter to use. 'id.abc' -> id contains or equal to 'abc'
            not_found (str): String to use in data field when column not found in frontmatter unit

        returns:
            list: a list of dictionaries, each one representing a row in the resulting table

        TODO:
        - Handle Boolean tag values in lists (eg show.True where show:[True, lol, apple]). since Pyyaml reads 'True' not as a string but as a boolean value
        - Move sorting functions from table to here. implemented. TEST THIS.
        - make selected columns case insensitive?
        '''
        keywords = {
            'any':['all', 'any', 'every', 'everything', 'anything']
        }
        sort_order = {
            'ascending':'asc',
            'descending':'desc',
            'desc':'desc'
        }.get(sort_ord.lower(), 'asc') # TODO: we assume 'asc' on incorrect input.. or should we throw an error?

        output = []

        if where in keywords['any']:
            for file, frontmatter in _from.items():
                # Select all specified items from the frontmatter
                output.append({el:frontmatter.get(el, not_found) for el in select})
        else:
            key, value = map(lambda x: x.lower(), where.split('.'))
            for file, frontmatter in _from.items():
                found_value = frontmatter.get(key,'')
                if found_value:
                    # Below boolean expression: 
                    # either found_value is a string and equal to our input value OR
                    # found_value is a boolean (cast to str) and is equal to input value OR
                    # found_value is a list (cast all to str) of values and contains our input string
                    if      (isinstance(found_value, str) and found_value.lower() == value) or \
                            (isinstance(found_value, bool) and str(found_value).lower() == value) or \
                            (isinstance(found_value, list) and value in map(lambda x: str(x).lower(), frontmatter.get(key, []))):
                        output.append({el:frontmatter.get(el, not_found) for el in select})
        
        if sort_col:
            output = sorted(output, key=lambda x: x[sort_col], reverse=sort_order=='desc')

        return output


    @staticmethod
    def markdown_table(data): # Remove
        '''
        Takes a list of dictionaries, build a markdown table

        TODO:
        - Correctly sort IP addresses
        '''
        lines = []
        normalize = lambda x: '<br>'.join(map(str, x)) if isinstance(x, list) else str(x) # LISTDOWN HERE?

        #REMOVE
        with open('WAT.txt', 'w') as wp:
            wp.write(str(data))

        lines.append('|' + '|'.join(data[0].keys()) + '|\n')
        lines.append('| :----------: ' * len(data[0].keys()) + '|\n')
        for item in data:
            for key in item.keys():
                lines.append('|' + normalize(item.get(key, '')))
            lines[-1] += '|\n'
        
        return lines


    @staticmethod
    def markdown_table_pandas(data):
        '''
        The filthy cheater's way to get really nice markdwon tables from any input.
        Requires pandas and tabulate (available through pip)

        parameters:
            data (list): list of dictionaries

        return:
            str: markdown table of data
        '''
        from pandas import DataFrame
        #df = DataFrame(data).applymap(lambda x: '- '+'<br/>- '.join(x) if isinstance(x, list) else x)
        df = DataFrame(data).applymap(lambda x: '<ul><li>'+'</li><li>'.join(x)+'</li></ul>' if isinstance(x, list) else x)
        return [l+'\n' for l in df.to_markdown(index=False, tablefmt="pipe").split('\n') if l]


    @staticmethod
    def color(text, c='blue', end='\n'): # This needs to be a separate module file
        return f'<span style="color:{c}">{text}</span>{end}'


        
