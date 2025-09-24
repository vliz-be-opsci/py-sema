# about conformance testing

We use a simple format to capture the expectations on any implementation of these template extensions.
Its purpose is to be 
* not too complicated too write / read the actual rules expressed
* not too complicated to have them automatically validated and tested


## parts of the test-compliance format

These files are composed of essentially 4 types of sections: comments, assignments, templates, results.
Each of these start with a dedicated start-line that is recognisable by their leading character:
  * `#` for comments
  * `=` for assignments
  * `?` for templates
  * `$` for results
  
As the format is to be evaluated from top to bottom, the typical sequence will be to have multiple blocks that all folow this pattern:
  * an opening `#`-comment-section
  * an initialising `=`-assignment-section
  * a number of variant `?`-template-sections that all are expected to produce the same result
  * a single `$`-result-section that captures the expected results for the previous templates
  * at least one, typically empty `#`-comment-section to wrap the result nicely 




## formal part

```ebnf

compliance-content := compliance-lines*

compliance-line := ignorable-whitespace? (empty-line | section-start-line | content-line) ignorable-whitespace? NEWLINE

NEWLINE := '\n'

ignorable-whitespace := (' ', '\t', '\n', ...)+ 

empty-line := ''

section-start-line := comment-start-line | assignment-start-line | template-start-line | result-start-line

comment-start-line := '#' remainder
assignment-start-line := '=' remainder
template-start-line := '?' remainder
result-start-line := '$' remainder

remainder := .* #works as the label / title of the section / but is ignored, not part of the 'content'

content-line := [^#=?$] .*

```

- content-lines are implied as being part of, completing, filling whatever section that got started before it
- this means any orphaned content-lines at the top of the file, preceeding the first section-start-line will be simply ignored / discarded


## implementation suggestions

* trim lines
* simply ignore empty lines
* note that comment-lines at least complete any previous section, so they require more attention than just ignoring them
* keep track of original file locations and line-numbers to provide useful error-reports about what portions are not "conforming"
* aggregate multiple ?-template-sections so they can all be checked versus one expected $-result-section

## known limitations

This format does not allow to have content-lines that start with one of the control chars #=?$.  Not as assignment, template, result.


## best practices

* start test-block with = for reset at least
* indent content 2 chars as lines get trimmed anyway
* allow control chars to be followed with additional text - it gets ignored, is not part of the content, can help as comment