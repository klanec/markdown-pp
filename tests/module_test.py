import unittest
import secrets
import yaml

from MarkdownPP import MarkdownPP
from MarkdownPP import modules as Modules
from MarkdownPP.Common import frontmatter_storage

from tempfile import NamedTemporaryFile as tmpfile
from tempfile import TemporaryDirectory as tmpdir
from tempfile import gettempdir

from io import StringIO
from os import path




class IncludeDir_Test(unittest.TestCase):

    def test_includedir_basic(self):
        '''Tests the basic !INCLUDEDIR tag. No recursion, no specified extensions'''
        # Create temp dirs
        with tmpdir() as topleveldir:
            with tmpdir(dir=topleveldir) as subdir:
                # Create temp files
                with tmpfile(suffix='.md', mode='w+', dir=topleveldir) as t1, \
                    tmpfile(suffix='.md', mode='w+', dir=topleveldir) as t2, \
                    tmpfile(suffix='.jpg', mode='w+', dir=subdir) as img, \
                    tmpfile(suffix='.py', mode='w+', dir=subdir) as code:

                    input = StringIO(f'foobar\n!INCLUDEDIR "{topleveldir}"\n')
                    output = StringIO()
                    mdpp = MarkdownPP(input=input, modules=['includedir'], output=output)
                    output.seek(0)


                    # Check these in output
                    for file in [t1, t2]:
                        find = f'!INCLUDE "{file.name}"'
                        self.assertTrue(find in output.read())
                        output.seek(0)

                    # Check these not in output
                    for file in [img, code]:
                        find = f'!INCLUDE "{file.name}"'
                        self.assertFalse(find in output.read())
                        output.seek(0)



    def test_includedir_recurse(self):
        '''Tests the !INCLUDEDIR, RECURSE tag. no specified extensions'''
        # Create temp dirs
        with tmpdir() as topleveldir:
            with tmpdir(dir=topleveldir) as subdir:
                # Create temp files
                with tmpfile(suffix='.md', mode='w+', dir=topleveldir) as t1, \
                    tmpfile(suffix='.md', mode='w+', dir=topleveldir) as t2, \
                    tmpfile(suffix='.jpg', mode='w+', dir=subdir) as img, \
                    tmpfile(suffix='.py', mode='w+', dir=subdir) as code:

                    input = StringIO(f'foobar\n!INCLUDEDIR "{topleveldir}", RECURSE\n')
                    output = StringIO()
                    mdpp = MarkdownPP(input=input, modules=['includedir'], output=output)    
                    output.seek(0)
                    print(output.read())
                    output.seek(0)
                    # Check these in output
                    for file in [t1, t2, img, code]:
                        find = None
                        print(file.name, file.name[-3:])
                        if file.name[-3:] == '.md':
                            find = f'!INCLUDE "{file.name}"'
                        elif file.name[-4:] == '.jpg':
                            basename = path.splitext(path.basename(file.name))[0]
                            find = f'![{basename}]({file.name})'
                        elif file.name[-3:] == '.py':
                            find = f'!INCLUDECODE "{file.name}"'
                        print('FIND:', find)
                        self.assertTrue(find in output.read())
                        output.seek(0)

 
    def test_includedir_formats(self):
        '''Tests the !INCLUDEDIR, RECURSE, FORMATS tag. no specified extensions'''
        # Create temp dirs
        with tmpdir() as topleveldir:
            with tmpdir(dir=topleveldir) as subdir:
                # Create temp files
                with tmpfile(suffix='.md', mode='w+', dir=topleveldir) as t1, \
                    tmpfile(suffix='.md', mode='w+', dir=topleveldir) as t2, \
                    tmpfile(suffix='.jpg', mode='w+', dir=subdir) as img, \
                    tmpfile(suffix='.py', mode='w+', dir=subdir) as code:

                    input = StringIO(f'foobar\n!INCLUDEDIR "{topleveldir}", RECURSE, FORMATS (py, jpg)\n')
                    output = StringIO()
                    mdpp = MarkdownPP(input=input, modules=['includedir'], output=output)
                    output.seek(0)
                    #print(output.read())
                    output.seek(0)
                    # Check these in output
                    for file in [t1, t2, img, code]:
                        find = None
                        #print(file.name, file.name[-3:])
                        if file.name[-3:] == '.md':
                            continue # Skip md files as not specified in FORMATS
                        elif file.name[-4:] == '.jpg':
                            basename = path.splitext(path.basename(file.name))[0]
                            find = f'![{basename}]({file.name})'
                        elif file.name[-3:] == '.py':
                            find = f'!INCLUDECODE "{file.name}"'
                        #print('FIND:', find)
                        self.assertTrue(find in output.read())
                        output.seek(0) #TODO: figure out why INCLUDECODE is running without explicit approval



class Include_Test(unittest.TestCase):

    def test_include_basic(self):
        '''Tests the basic include tag functionality'''
        with tmpfile(suffix='.md', mode='w+') as testfile:
            testfile.write('# foo\n1\n2\n3\n4')
            testfile.seek(0)

            input = StringIO(f'foobar\n!INCLUDE "{testfile.name}"\n')
            result = f'foobar\n{testfile.read()}'
            output = StringIO()
            mdpp = MarkdownPP(input=input, modules=['include'], output=output)
            output.seek(0)
            self.assertEqual(output.read(), result)

    def test_include_shift(self):
        '''Tests the shift functionality of headers in an include file'''
        with tmpfile(suffix='.md', mode='w+') as testfile:
            testfile.write('# foo\n1\n2\n3\n4')
            testfile.seek(0)

            for i in range(1, 4):
                input = StringIO(f'foobar\n!INCLUDE "{testfile.name}", LEVEL {i}\n')
                result =f'foobar\n{testfile.read().replace("#","#"*(i+1))}' 
                testfile.seek(0)
                
                output = StringIO()
                mdpp = MarkdownPP(input=input, modules=['include'], output=output)
                output.seek(0)

                self.assertEqual(output.read(), result)

            # Test shorthand
            for i in range(1, 4):
                input = StringIO(f'foobar\n!INCLUDE "{testfile.name}", {i}\n')
                result =f'foobar\n{testfile.read().replace("#","#"*(i+1))}' 
                testfile.seek(0)
                
                output = StringIO()
                mdpp = MarkdownPP(input=input, modules=['include'], output=output)
                output.seek(0)

                self.assertEqual(output.read(), result)

    def test_include_glob(self):
        '''Tests the unix path expansion in the include tag'''
        secret = secrets.token_hex(6)
        fileglob = path.join(gettempdir(), f'{secret}*.md')
        input = StringIO(f'foobar\n!INCLUDE "{fileglob}"\n')
        with tmpfile(prefix=secret, suffix='.md', mode='w+') as tempfile1, \
             tmpfile(prefix=secret, suffix='.md', mode='w+') as tempfile2:
            
            tempfile1.write('# foo\n1\n2\n3\n4')
            tempfile1.seek(0)
            tempfile2.write('# file2\nfile2')
            tempfile2.seek(0)
            
            sorted_tempfiles = sorted([tempfile1, tempfile2], key=lambda x:x.name)
            result = f'foobar\n{sorted_tempfiles[0].read()}{sorted_tempfiles[1].read()}'

            output = StringIO()
            mdpp = MarkdownPP(input=input, modules=['include'], output=output)
            output.seek(0)

            self.assertEqual(output.read(), result)

    def test_include_frontmatter(self):
        '''Test the yaml frontmatter scraping in the !INCLUDE module'''

        test_yaml = '''spies:
- Engineer
- Medic
- Scout
'''

        test_string = "The engineer is a spy!"
        test_file_string = f"---\n{test_yaml}\n---\n{test_string}"

        with tmpfile(suffix='.md', mode='w+') as tempfile:
            tempfile.write(test_file_string)
            tempfile.seek(0)

            input = StringIO(f'foobar\n!INCLUDE "{tempfile.name}"\n')
            result =f'foobar\n{test_string}\n' 

            output = StringIO()
            mdpp = MarkdownPP(input=input, modules=['include'], output=output)
            output.seek(0)

            # Assume file processed correctly
            self.assertEqual(output.read(), result)
            # Assumer frontmatter processed correctly
            self.assertEqual(len(frontmatter_storage.frontmatter), 1)
            self.assertEqual(frontmatter_storage.frontmatter[tempfile.name], yaml.safe_load(test_yaml))


    def test_include_frontmatter_this(self):
        '''Tests replacement of `!FRONTMATTER this, ...` to `!FRONTMATTER id.$id, ...` which is handled at include time'''
        id = secrets.token_hex(4)
        test_yaml = f'id: {id}'
        test_string = "!FRONTMATTER this, plain(id)"
        test_file_string = f"---\n{test_yaml}\n---\n{test_string}"

        # TODO: addtesting of roplevel `this`

        with tmpfile(suffix='.md', mode='w+') as tempfile:
            tempfile.write(test_file_string)
            tempfile.seek(0)

            input = StringIO(f'foobar\n!INCLUDE "{tempfile.name}"\n')
            result =f'foobar\n{test_string.replace("this", f"id.{id}")}\n' 

            output = StringIO()
            mdpp = MarkdownPP(input=input, modules=['include'], output=output)
            output.seek(0)

            # Assume file processed correctly
            self.assertEqual(output.read(), result)


class IncludeCode_Test(unittest.TestCase):
    test_code = '''
    def bob():
        return "Are we really actually code Alice?"
    
    def alice():
        return "Thats dangerous thinking, Bob."
    '''

    def test_includecode_basic(self):
        '''Test "!INCLUDECODE" basic tag syntax'''
        with tmpfile(suffix='.py', mode='w+') as testfile:
            testfile.write(self.test_code)
            testfile.seek(0)

            input = StringIO(f'foobar\n!INCLUDECODE "{testfile.name}"\n')

            result = f'foobar\n```\n{testfile.read()}\n```\n'

            output = StringIO()
            mdpp = MarkdownPP(input=input, modules=['includecode'], output=output)
            output.seek(0)

            self.assertEqual(output.read(), result)

    def test_includecode_alternate(self):
        '''Test "!INCLUDECODE" alternative tag syntax
        
        !INCLUDECODE "$file" ($language) x:y
            (where x is start line, y is end line)
        '''
        with tmpfile(suffix='.py', mode='w+') as testfile:
            testfile.write(self.test_code)
            testfile.seek(0)

            language = 'python'
            input = StringIO(f'foobar\n!INCLUDECODE "{testfile.name}" ({language}), 1:3\n')

            code_output = ''.join(testfile.readlines()[:3])
            result = f'foobar\n```{language}\n{code_output}\n```\n'.lstrip()

            output = StringIO()
            mdpp = MarkdownPP(input=input, modules=['includecode'], output=output)
            output.seek(0)

            self.assertEqual(output.read(), result)



class IncludeUrl_Test(unittest.TestCase):

    def test_includeurl_basic(self):
        '''Test !INCLUDEURL basic functionality'''
        from MarkdownPP.Modules import IncludeURL

        test_string = b"YOU'VE GOT MAIL!"

        class mock_urllib:
            netloc = True
            path == True
            def readlines(self):
                return [test_string]

        # Mock urllib in the module to return what we want
        IncludeURL.urlparse = lambda x: mock_urllib()
        IncludeURL.urlopen = lambda x: mock_urllib()

        input = StringIO(f'foobar\n!INCLUDEURL "http://127.0.0.1:8000/TEST.md"\n')
        result =f'foobar\n{test_string.decode()}' 

        output = StringIO()
        mdpp = MarkdownPP(input=input, modules=['includeurl'], output=output)
        output.seek(0)

        self.assertEqual(output.read(), result)



    def test_includeurl_frontmatter(self):
        '''Test YAML frontmatter inclusion in !INCLUDEURL embedded file'''
        from MarkdownPP.Modules import IncludeURL

        link = 'http://127.0.0.1:8000/TEST.md'

        test_yaml = "engineer: spy"
        test_string = "The engineer is a spy!"

        test_file = f"---\n{test_yaml}\n---\n{test_string}".encode()

        class mock_urllib:
            netloc = True
            path = True
            def geturl(self):
                return link
            def readlines(self):
                return [test_file]

        # Mock urllib in the module to return what we want
        IncludeURL.urlparse = lambda x: mock_urllib()
        IncludeURL.urlopen = lambda x: mock_urllib()

        input = StringIO(f'foobar\n!INCLUDEURL "{link}"\n')
        result =f'foobar\n{test_string}\n' 

        output = StringIO()
        mdpp = MarkdownPP(input=input, modules=['includeurl'], output=output)
        output.seek(0)

        # Assume file processed correctly
        self.assertEqual(output.read(), result)

        


    
if __name__ == '__main__':
    unittest.main()
