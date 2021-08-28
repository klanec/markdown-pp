# TODO:

- [ ] Handle project directory nicely
  - [ ] add -stdout flag, default to normal behaviour with file output  
  - [ ] remove frontmatter.yaml files after run
- [ ] Add debug, info and error level logging to entire project. 
- [ ] Add argparse for all added options:
  - [ ] Logging yes/no
  - [ ] quiet (suppress TODO / ERROR from terminal output)
  - [ ] output directory (all artefacts output to one dir with timestamp by default)
- [?] Migrate to click arg parsing?


## Include.py module

- [ ] Add code to "flatten" references to files (pictures etc) in included files. 
  - [ ] Detect embedded file
  - [ ] Create project folder
  - [ ] Move file to project folder
- [ ] All frontmatter code should only be run if the frontmatter module will run

## Frontmatter.py module

- [ ] Error on non-unique ID in frontmatter
- [ ] Don't Search recursively for frontmatter.yaml. Should be in defined location.
- [ ] Add the ability to output `plain(field)` for text output

## Error.py module

- [ ] add output to terminal as to which file caused error and which line

## TableOfErrors.py module

- [ ] Add code for recognizing error tags
- [ ] Copy TOC module to create a Table of Errors at the beginning of the document... (or maybe an actual table with the erroneous command? then its all in one place)

## TableOfTodos.py module

- [ ] implement me. Copy TOC

## !TOC

- [ ] Change regex to accept !TABLE_OF_CONTENTS and !CONTENTS_TABLE

## Testing

- [ ] For the love of god, implement testing
- [ ] add documentation for new functionality
