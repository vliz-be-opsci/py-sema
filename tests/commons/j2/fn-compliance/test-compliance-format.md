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

The lines following these starting lines make up the actual 'content' of the section. 
This means that the start of a new section implies that the content of the previous one is complete. Stated in reverse: complete the content of any section by starting a new one, since newlines are ignored that might be done by a single `#`-sign on a line

Any remaining characters on the section starting-line itself is not considered part of the content (and can be ignored).

Depending on the type of section, the content is to be applied in different ways:

### The content of `#`-comment-section
This content has no effect and is to be ignored. Note the starting-line of such section will at lease finalise and close up the previous one.

As such, during sequential processing of the conformance test file it does not redefine (or reset) either the assigned context or the accumulated template-results.

### The content of `=`-assign-section
The content of the assign section is to be parsed as a json-dict that describes the context-variables to be made available to the template-evaluation.

The specified variables are to be extending / overwriting a pre-agreed `BASE_CONTEXT` dictionary that also contains implementation native datatypes used in these tests.

In case the content is empty, it will be considered the equivalent of `{}` and thus will lead to a simple clone of th `BASE_CONTEXT` dict to be applied.

In case no assign section is present, the same `BASE_CONTEXT` will be available during the processing of all template-sections.

Any new assign-section will lead to a reset / reconstruction of the context-variables to be used. This however does not have an effect on accumulated template-results still to be checked.

### The content of `?`-template-section
The content of the template-section is to be seen as a template that can be expanded while applying the resulting context set by any previous assign-section.

Errors during this evaluation should lead to a failure and break off further processing of the compliance test.

The expanded result of this evaluation is to be accumulated in a growing list of template-results that all can be checked simultanously.

The evaluation will not bear any side-effects on the available context-variables.


### The content of `$`-result-section
The content of the result-section is literally capturing the expected output of any template-section that preceeds it.

The prime effect of "executing" this section is that any earlier accumulated template-results up to that moment are compared to its content, thus actually implementing the conformance-validation.  Invalid results should lead to a test-failure and an extensive logging of which template filename and linenumber.

When all results do match, the list of accumulated results is reset, and further conformance testing can proceed.

Any defined context-variables (by assign-section) will not be changed.


### regular usage pattern

As the format is to be evaluated from top to bottom, the typical sequence will be to have multiple blocks that all folow this pattern:
  * an opening `#`-comment-section
  * an initialising `=`-assignment-section
  * a number of variant `?`-template-sections that all are expected to produce the same result
  * a single `$`-result-section that captures the expected results for the previous templates
  * at least one, typically empty `#`-comment-section to wrap the result nicely 

Example:
```
    todo
```


## aggreed contents of the BASE_CONTEXT 

```python
    todo
```

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

* check first char for section-start
* trim content-lines to ignore leadin-trailing whitespace
* simply ignore empty lines
* as a counterpart, remove empty lines produced in template results as well
* note that comment-lines at least complete any previous section, so they require more attention than just ignoring them
* keep track of original file locations and line-numbers to provide useful error-reports about what portions are not "conforming"

## known limitations

### result-lines can not (easily) start with any of the `#=?$` chars
This format does not allow to have content-lines that start with one of the control chars #=?$. 

However, by indenting content-lines (2 char recommended) this can be overcome, so they can be matched as a valid expected outcome of a test.

### result-lines can not be empty (or only white-chars)
This format trims leading and trailing whitechars and ignores empty content-lines.  
As a consequence any (non-zero) number of them in a template-result will never match the captured expected result in a `$`-result-section


## best practices for writing conformance test files

* start independent test-blocks with a `=`-assignment-section for reset of the context-variable at least
* indent content 2 chars as lines get trimmed anyway (ie leading and trailing whitespace is ignored)
* allow control chars to be followed with additional text - it gets ignored, is not part of the content, and can help as comment
* provide multiple `?`-template-sections so they can all be checked versus one expected `$`-result-section
* testing for white-space effects is best surrounded with visible characters for clarity (and required at the start and end of lines because of the trimming)