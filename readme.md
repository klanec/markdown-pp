
**Table of TODOs**
| Search Me   | TO DO                                                        |
|:------------|:-------------------------------------------------------------|
| b07709557c  | Explain command line arguments                               |
| 7d5101558e  | example of the above                                         |
| b2f027f9d7  | make this description more comprehensible                    |
| 1888733757  | fix frontmatter module to save frontmatter from toplevel too |
| 38c424a37b  | Finish this                                                  |
| f3ae6e5d3d  | This is a default Red TODO tag                               |
| f56074801d  | This is a pretty Purple TODO tag                             |


**Table of Errors**
| Search Me   | Error Tag                                 | Error Cause                             |
|:------------|:------------------------------------------|:----------------------------------------|
| cb8b7db7b1  | !FRONTMATTER all, shaolin(shadow, boxing) | Requested data structure not recognized |


Markdown Preprocessor (MarkdownPP)
==================================

The Markdown Preprocessor is a Python module designed to add extended features
on top of the excellent Markdown syntax defined by John Gruber.  These additions
are mainly focused on creating larger technical documents without needing to use
something as heavy and syntactically complex as Docbook.

MarkdownPP uses a set of selectable modules to apply a series of transforms to
the original document, with the end goal of generating a new Markdown document
that contains sections or features that would be laborious to generate or
maintain by hand.

Documents designed to be preprocessed by MarkdownPP should try to follow the
convention of naming files with a .mdpp extension, so that MarkdownPP can
generate a document with the same name, but with the standard .md extension.
As an example, this document in raw format is named "readme.mdpp", and the
generated document from MarkdownPP is named "readme.md" so that GitHub can find
and process that document when viewing the repository.

!TABLE_OF_CONTENTS level 3

Installation and Usage
----------------------

Pull this repository and run `python3 setup.py install`

Make sure to install the requirements:

- pandas
- pyyaml
- tabulate

Arguments
---------

<span style="color:OrangeRed">TODO: Explain command line arguments (b07709557c)</span>

Modules
--------

### Includes

Tag:
`!INCLUDE "path/to/file.md"`

Alternate Forms:
`!INCLUDE "file.md", LEVEL 3`
`!INCLUDE "file.md", 3` "LEVEL" string is optional
`!INCLUDE "$path/to/many/*.md"`

In order to facilitate large documentation projects, MarkdownPP has an Include
module that will replace a line of the form `!INCLUDE "path/to/filename"` with
the contents of that file, recursively including other files as needed.

File `foo.mdpp`:

	Hello

File `bar.mdpp`:

	World!

File `index.mdpp`:

	!INCLUDE "foo.mdpp"
	!INCLUDE "bar.mdpp"

Compiling `index.mdpp` with the Include module will produce the following:

	Hello
	World!

Furthermore, the Include module supports the shifting of headers in the
file to be included. For example,

File `foo.mdpp`:

    # Foo
    ## Bar

File `index.mdpp`:

    # Title
    ## Subtitle
    !INCLUDE "foo.mdpp", 2

Compiling `index.mdpp` with the Include module and using `2` as shift
parameter will yield:

    # Title
    ## Subtitle
    ### Foo
    #### Bar

The Include module will also handle embedded images such that the
output file has valid links regardless of where they were relative to the 
input file.

<span style="color:OrangeRed">TODO: example of the above (7d5101558e)</span>

Finally, the include module allows for specifying files with unix style 
pattern expansion. Imagine the following directory structure:

```
files/
├── a.md
├── b.md
└── c.md
```

All files can be included in a single statement as below:

```
!INCLUDE "files/*.md"
```


### IncludeURLs

Tag:
`!INCLUDEURL "$url"`

Since this module makes external calls, it is disabled by default. Include it 
explicitly with `-i`/`--incude` or by running all modules with `-a`/`--all`

Facilitates the inclusion of remote files, such as files kept in a subversion
or GitHub repository. Like Include, the IncludeURL module can replace a line of
the form `!INCLUDEURL "http://your.domain/path/to/filename"` with the contents
returned from that url, recursively including additional remote urls as needed.

IncludeURL runs immediately after the Include module finishes executing. This
means that is it possible to include local files that then require remote files,
but impossible parse !INCLUDE statements found in remote files. This is prevent
ambiguity as to where the file would be located.

Remote file `http://your.domain/foo.mdpp`:

    Hello

Remote file `http://your.domain/bar.mdpp`:

    Remote World!

Local file `index.mdpp`:

    !INCLUDEURL "http://your.domain/foo.mdpp"
    !INCLUDEURL "http://your.domain/bar.mdpp"

Compiling `index.mdpp` with the IncludeURL module will produce the following:

    Hello
    Remote World!

### IncludeCode

Tag:
`!INCLUDECODE "poc.py"`

Alternate forms:
`!INCLUDECODE "hello.py" (python), 1:2` Set the syntax highlighting to python and grab only lines 1 to 2

Facilitates the inclusion of local code files. GFM fences will be added
around the included code.

Local code file `hello.py`:

    def main():
        print "Hello World"


    if __name__ == '__main__':
        main()


Local file `index.mdpp`:

    # My Code

    !INCLUDECODE "hello.py"
    Easy as that!

Compiling `index.mdpp` with IncludeCode module wil produce the following:

    # My Code

    ```
    def main():
        print "Hello World"


    if __name__ == '__main__':
        main()
    ```
    Easy as that!

Furthermore the IncludeCode module supports line extraction and language
specification. The line extraction is like python list slicing (e.g. 3:6; lines
three to six). Please note that line counting starts at one, not at zero.

Local file `index.mdpp`:

    # My Code

    !INCLUDECODE "hello.py" (python), 1:2
    Easy as that!

Compiling `index.mdpp` with IncludeCode module will produce the following:

    # My Code

    ```python
    def main():
        print "Hello World"
    ```
    Easy as that!


### Include Directory

Tag:
`!INCLUDEDIR "$directory"`

Alternate Forms:
`!INCLUDEDIR "$directory", RECURSE`
`!INCLUDEDIR "$directory", FORMATS ($ext1, $ext2 ...)`  RECURSE can be added here but must come before FORMATS

This feature allows for including all files in a given directory, allowing you to filter based on file
extension and recurse into subdirectories. It supports including markdown files, embedding images and
including code.

Given directory structure:
```
files/
├── directory
│   ├── subfile1.md
│   └── subfile2.md
├── file1.md
├── file2.md
└── image1.png
```

You can include all files in the top directory like so:
```
!INCLUDEDIR "files/"
```

This will result in the following block:
```
!INCLUDE "/home/klanec/Documents/code/markdown-pp/example/TEST/files/file1.md"

!INCLUDE "/home/klanec/Documents/code/markdown-pp/example/TEST/files/file2.md"

![image1](/home/klanec/Documents/code/markdown-pp/example/TEST/files/image1.png)
```

You can recurse in to subdirectories as follows:
`!INCLUDEDIR "files/", RECURSE`


### Table of Contents

Tag:
`!TABLE_OF_CONTENTS`
`!TOC` (Shorthand)

Alternate forms:
`!TABLE_OF_CONTENTS, LEVEL 3` Only process up to header level 3
`!TABLE_OF_CONTENTS, 3` "LEVEL" string is optional

The biggest feature provided by MarkdownPP is the generation of a table of
contents for a document, with each item linked to the appropriate section of the
markup.  The table is inserted into the document wherever the preprocessor finds
`!TOC` or `!TABLE_OF_CONTENTS` at the beginning of a line.  Named `<a>` tags are inserted above each
Markdown header, and the headings are numbered hierarchically based on the
heading tag that Markdown would generate. The module also supports specifying the header level to
include in the output table by adding the number (1 to 6) after the tag. See below:

Usage:
`!TOC` Generates table of contents up to 6th subheading
`!TOC 3` Generates table of contents up to 3rd subheading
`!TOC level 4` Generates table of contents up to 4th subheading ('level' string optional for readability)
`!TOC` can be substituted with `!TABLE_OF_CONTENTS`

### Frontmatter

Tag:
`FRONTMATTER selector, data_structure(column1, column2, column3)`

Alternate Form:
`FRONTMATTER selector, data_structure(column1, column2, column3), SORT column1 ascending`


<span style="color:OrangeRed">TODO: make this description more comprehensible (b2f027f9d7)</span>

In the Include module, yaml frontmatter is parsed at the start of any markdown file included with the Include
module. The !FRONTMATTER tag allows for arranging that collected data in a variety of useful ways.


Given frontmatter

```
---
id: readme
animal: dog
breed: Dalmation
name: Elvis
owner:
- Alice
- Bob
---
```

The tag:

`!FRONTMATTER animal.dog, table(name, breed, owner)`

will generate the following table:
<span style="color:OrangeRed">TODO: fix frontmatter module to save frontmatter from toplevel too (1888733757)</span>

| name   | breed     | owner                               |
|:-------|:----------|:------------------------------------|
| Elvis  | Dalmation | <ul><li>Alice</li><li>Bob</li></ul> |

**Supported shorthand selectors**
- this (shorthand for the current file. The file's `id` tag will be dropped in its place)
- all (simply use all frontmatter)

**Supported data structures**
- plain (output as string)
- list
- table

**Supported sorting strings**
<span style="color:OrangeRed">TODO: Finish this (38c424a37b)</span>

### Comment

This module allows you to add two types of comments to the output file. These will be rendered in colour
such that they stand out. The 2 comment types as follows:

`!COMMENT "This is a default Blue comment"`
`!TODO "This is a default Red TODO tag"`

becomes:

<span style="color:DodgerBlue">COMMENT: This is a default Blue comment</span>

<span style="color:OrangeRed">TODO: This is a default Red TODO tag (f3ae6e5d3d)</span>

You can even change the colors (HTML colours are supported)

`!COMMENT "This is a Green comment" Green`
`!TODO "This is a pretty Purple TODO tag" Purple`

becomes:

<span style="color:Green">COMMENT: This is a Green comment</span>

<span style="color:Purple">TODO: This is a pretty Purple TODO tag (f56074801d)</span>

Another important function of the Comment module is the ability to generate a dynamic table
of all TODOs in the final output.

simply adding the `!TABLE_OF_TODOS` or `!TOT` for short will give the below:


**Table of TODOs**
| Search Me   | TO DO                                                        |
|:------------|:-------------------------------------------------------------|
| b07709557c  | Explain command line arguments                               |
| 7d5101558e  | example of the above                                         |
| b2f027f9d7  | make this description more comprehensible                    |
| 1888733757  | fix frontmatter module to save frontmatter from toplevel too |
| 38c424a37b  | Finish this                                                  |
| f3ae6e5d3d  | This is a default Red TODO tag                               |
| f56074801d  | This is a pretty Purple TODO tag                             |

Searching the `Search Me` token will show the corresponding error.

### Error

The Error module handles formatting `!ERROR` tags, which are placed automatically
where the preprocessor has failed in some way. This tag does not need to be used
manually. 

There is however a `!TABLE_OF_ERRORS` module, or `!TOE` for short. This will drop in
a table will a list of all errors in the document and a hex ID to search for the error
in your text editor. Adding a tag that will fail will demonstrate this:

`!FRONTMATTER all, shaolin(shadow, boxing)`

The oputput is:

<span style="color:FireBrick" id="cb8b7db7b1">ERROR cb8b7db7b1: !FRONTMATTER all, shaolin(shadow, boxing)</span> <!-- !ERROR:  Requested data structure not recognized -->

And the table of errors:


**Table of Errors**
| Search Me   | Error Tag                                 | Error Cause                             |
|:------------|:------------------------------------------|:----------------------------------------|
| cb8b7db7b1  | !FRONTMATTER all, shaolin(shadow, boxing) | Requested data structure not recognized |

### Reference

Similarly, MarkdownPP can generate a list of references that follow Markdown's
alternate link syntax, eg `[name]: <url> "Title"`.  A list of links will be
inserted wherever the preprocessor finds a line beginning with `!REF`.  The
generated reference list follows the same alternate linking method to ensure
consistency in your document, but the link need not be referenced anywhere in
the document to be included in the list.

Note, only links in the format `[name]: <url> "Title"` are included in the list.

### LaTeX Rendering

Since this module relies on an external service to generate pngs from LaTeX,
it is disabled by default. Include it explicitly with `-i`/`--incude` or `-a`/`--all`

Lines and blocks of lines beginning and ending with $ are rendered as LaTeX,
using [QuickLaTeX](http://www.holoborodko.com/pavel/quicklatex/).

For example,

	$\displaystyle \int x^2 = \frac{x^3}{3} + C$

becomes

![\displaystyle \int x^2 = \frac{x^3}{3} + C](http://quicklatex.com/cache3/ea/ql_0f9331171ded7fa9ef38e57fccf74aea_l3.png "\displaystyle \int x^2 = \frac{x^3}{3} + C")


### YouTube Embeds

Since this module makes external calls it is disabled by default. 
Include it explicitly with `-i`/`--incude` or `-a`/`--all`

As GitHub-flavored Markdown does not allow embed tags, each line of the form
`!VIDEO "[youtube url]"` is converted into a screenshot that links to the video,
roughly simulating the look of an embedded video player.

For example,

    !VIDEO "http://www.youtube.com/embed/7aEYoP5-duY"

becomes

!VIDEO "http://www.youtube.com/embed/7aEYoP5-duY"


Examples
--------

Example file.mdpp:

	# Document Title

	!TOC

	## Header 1
	### Header 1.a
	## Header 2

	!REF

	[github]: http://github.com "GitHub"

The preprocessor would generate the following Markdown-ready document file.md:

	# Document Title

	1\. [Header 1](#header1)
	1.1\. [Header 1.a](#header1a)
	2\. [Header 2](#header2)

	<a name="header1"></a>
	## Header 1
	<a name="header1a"></a>
	### Header 1.a
	<a name="header2"></a>
	## Header 2

	*	[GitHub][github]

	[github]: http://github.com "GitHub"


Support
-------

If you find any problems with MarkdownPP, or have any feature requests, please
report them to [GitHub][repo], and I will respond when possible.  Code
contributions are *always* welcome, and ideas for new modules, or additions to
existing modules, are also appreciated.


References
----------

*	[Markdown Preprocessor on GitHub][repo]

[repo]: http://github.com/jreese/markdown-pp "Markdown Preprocessor on GitHub"
