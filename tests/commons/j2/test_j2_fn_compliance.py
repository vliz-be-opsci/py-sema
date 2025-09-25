# our set of turtle extensions seeks to be compliant with an external formal specification
# that can be implemented on top of other Jinja2 implementations (like the one in php/symphony called twig)
# this test suite checks that we are compliant with that specification
# it does so through running over a number of shared test-vectors noted in a custom textual format
# these files are locally available in ./fn-compliance-vectors/*test
# and are regularly synced with the upstream source at https://github.com/ ...
import json
import datetime
import math
from sema.commons.glob import getMatchingGlobPaths
from conftest import log
from abc import ABC, abstractmethod
from pathlib import Path
from sema.commons.j2.syntax_builder import J2RDFSyntaxBuilder


MYBASE = Path(__file__).parent
FNC_PATH: Path = MYBASE / "fn-compliance"
TPL_PATH: Path = MYBASE / "templates"


BASE_CONTEXT: dict = {
    "txt_001": "001",
    "txt_1_dot_0": "1.0",
    "txt_esc": "TestIng \\\"'escaper",
    "txt_none": "",
    "txt_space": " ",
    "txt_tab": "\t",
    "txt_nl": "\n",
    "txt_false": "false",
    "txt_true": "true",

    "bool_t": True,
    "bool_f": False,

    "int_0": 0,
    "int_1": 1,
    "int_m111111": -111111,

    "float_0": 0.0,
    "float_1": 1.0,
    "float_m1": -1.0,
    "float_1_5": 1.5,
    "float_pi": math.pi,

    "date_May5_25": datetime.date(2025, 5, 5),

    "none": None,  # null, undefined, ...
    "list_none": [],
    "dict_none": {},
}


class ConformanceCheck:
    def __init__(self, from_file: Path) -> None:
        self.from_file: Path = from_file
        self.sections: list[Section] = []

    @staticmethod
    def from_file(from_file: Path):
        cc = ConformanceCheck(from_file)
        cc._build()
        return cc

    def _build(self) -> None:
        # read the file line by line, and use them to build and grow sections based on their lead character
        # so for each line, trim it, if not empty, add it with incremental line number to the current section
        # if that returns a new section, append that to self.sections and continue with that new section
        # initially, there is no current section, just use a new CommentSection to bypass that
        current_section = CommentSection(self, "", 0)
        current_line = 0
        for line in self.from_file.read_text().splitlines():
            current_line += 1
            if not line:
                continue
            new_section = current_section.append_line(line, current_line)
            if new_section is not current_section:
                self.sections.append(new_section)
                current_section = new_section

    def check(self) -> None:
        # start with an empty context dict, and an empty aggregate list
        # for each section in self.sections, call its evaluate with the current context and aggregate
        # if that returns False, log the error messages, and stop processing this vector
        # else update context and aggregate with the returned values, and continue with the next section
        context: dict = {}
        aggregate: list[tuple[str, Section]] = []
        for section in self.sections:
            context, ok, result = section.evaluate(context, aggregate)
            if not ok:
                for msg, sec in result:
                    log.error(f"error at {sec.describe()}:\n--\n{msg}\n--")
                log.error(f"stopping processing of {self.from_file !s} due to errors")
                assert False, f"conformance check failed for {self.from_file !s} see log for details"
            # else
            aggregate = result


class Section(ABC):
    LEADS: list[str] = []
    IMPLEMENTATIONS: dict[str, type] = {}

    @classmethod
    def registerImplementation(cls, impl: type) -> None:
        if not issubclass(impl, cls):
            raise ValueError(f"Cannot register {impl} as it is not a subclass of {cls}")
        if not hasattr(impl, "LEAD"):
            raise ValueError(f"Cannot register {impl} as it has no LEAD attribute")
        lead = getattr(impl, "LEAD")
        if not isinstance(lead, str):
            raise ValueError(f"Cannot register {impl} as its LEAD attribute is not a string")
        if lead in cls.LEADS:
            raise ValueError(f"Cannot register {impl} as its LEAD '{lead}' is already registered")
        cls.LEADS.append(lead)
        cls.IMPLEMENTATIONS[lead] = impl

    @staticmethod
    def create_new(parent: ConformanceCheck, line: str, at_line: int) -> "Section":
        for section_lead, impl in Section.IMPLEMENTATIONS.items():
            if line.startswith(section_lead):
                section = impl(parent, line, at_line)
                return section
        # else
        raise ValueError(f"Cannot create new section for line {line} at {at_line}")

    def __init__(self, parent: ConformanceCheck, line: str, at_line: int) -> None:
        self.parent = parent
        self.lead_line: str = line
        self.at_line: int = at_line
        self.content: str = ""
        self.lines: int = 0
        self._accepting_lines: bool = True

    @staticmethod
    def is_content_line(line: str) -> bool:
        for section_leads in Section.LEADS:
            if line.startswith(section_leads):
                return False
        return True

    def append_line(self, line: str, line_no: int) -> "Section":
        if Section.is_content_line(line):
            if not self._accepting_lines:
                raise ValueError(
                    f"Attempt to processing new line {line} at {line_no}"
                    "- Cannot add content line to section after new section "
                    f"was started: {self.describe()}")
            # else
            # trim content-lines AFTER the lead-char is checked
            line = line.strip()
            if len(line) > 0:  # do not add empty lines to content
                self.content += ("" if self.lines == 0 else "\n") + line
            self.lines += 1  # count all lines, even empty ones
            return self
        # else
        self._accepting_lines = False
        return Section.create_new(self.parent, line, line_no)

    @abstractmethod
    def evaluate(self, context: dict, aggregate: list[str]) -> tuple[dict, bool, list[str]]:
        pass

    def lead(self) -> str:
        return self.LEAD

    def describe(self) -> str:
        return f"{self.__class__.__name__} in {self.parent.from_file}@{self.at_line},#{self.lines}"


class AssignSection(Section):
    LEAD = "="

    def evaluate(self, context: dict, aggregate: list[tuple[str, Section]]) -> tuple[dict, bool, list[tuple[str, Section]]]:
        # parse content as json, and update context with the resulting dict
        # return updated context, True, and the unchanged aggregate
        # if no content, return empty context, True, and unchanged aggregate
        # in case of errors, return context, False, and an aggregate with error-messages
        try:
            log.debug(f"parsing json from {self.describe()}:\n--\n{self.content}\n--")
            if len(self.content.strip()) == 0:
                return dict(BASE_CONTEXT), True, aggregate
            parsed = json.loads(self.content)
            return dict(BASE_CONTEXT, **parsed), True, aggregate
        except Exception as e:
            return None, False, [(f"error parsing assignment content as json\n--\n{self.content}\n--\n{e}\n", self)]


def evaluate_template(template_str: str, context: dict) -> str:
    j2sb: J2RDFSyntaxBuilder = J2RDFSyntaxBuilder(TPL_PATH)
    # log.debug(f"evaluating \n--\n{template_str}\n--\nwith {context=}")
    return j2sb.expand_syntax(template_str, **context)


class TemplateSection(Section):
    LEAD = "?"

    def evaluate(self, context: dict, aggregate: list[tuple[str, Section]]) -> tuple[dict, bool, list[tuple[str, Section]]]:
        # parse content with  J2RDFSyntaxBuilder using the context as variables
        # add the rendered text to the aggregate, and return context, True, and the updated aggregate
        # in case of errors, return context, False, and an aggregate with error-messages
        if len(self.content.strip()) == 0:
            return context, True, aggregate
        try:
            rendered: str = evaluate_template(self.content, context)
            aggregate.append((rendered, self))
            log.debug(
                f"rendered from {self.describe()} with content\n--\n"
                f"{self.content}\n--with {context=}--\n--into--\n"
                f"{rendered}\n--"
            )
            return context, True, aggregate
        except Exception as e:
            return context, False, [(f"error rendering from content\n--\n{self.content}\n--\n{e}", self)]


class ResultSection(Section):
    LEAD = "$"

    def evaluate(self, context: dict, aggregate: list[tuple[str, Section]]) -> tuple[dict, bool, list[tuple[str, Section]]]:
        # todo compare own content with each line in the aggregate
        # if all match, return context, True, and a fresh empty aggregate
        # else return context, False, and an aggregate with error-messages refering to faulty lines
        if len(aggregate) == 0:
            return context, False, ["no input sections to validate.", self]
        # else
        errors: list[tuple[str, Section]] = []
        for inp_text, inp_section in aggregate:
            if inp_text != self.content:
                errors.append((
                    f"unexpected result of {inp_section.describe()}\n--\n{inp_text}\n--\n"
                    f"does not match expected\n--\n{self.content}\n--\n",
                    self,
                ))
        log.debug(f"check of {self.describe()} to match\n--\n{self.content}\n--\nfound {len(errors)} errors")
        if len(errors) == 0:
            return context, True, []
        # else
        return context, False, errors


class CommentSection(Section):
    LEAD = "#"

    def evaluate(self, context: dict, aggregate: list[tuple[str, Section]]) -> tuple[dict, bool, list[tuple[str, Section]]]:
        # nothing to do
        return context, True, aggregate


Section.registerImplementation(CommentSection)
Section.registerImplementation(AssignSection)
Section.registerImplementation(TemplateSection)
Section.registerImplementation(ResultSection)


def test_compliance_checks() -> None:
    assert FNC_PATH.exists() and FNC_PATH.is_dir(), (
        f"the fn-compliance folder should be available "
        f"at {FNC_PATH !s}"
    )
    cc_files = getMatchingGlobPaths(FNC_PATH, ["**/*.test"], onlyFiles=True, makeRelative=False)
    assert len(cc_files) > 0, (
        f"the fn-compliance folder at {FNC_PATH !s} "
        f"should contain some compliance-files"
    )
    log.debug(
        f"the fn-compliance folder at {FNC_PATH !s} "
        f"contains {len(cc_files)} compliance-files"
    )

    for cc_file in sorted(cc_files):
        cc = ConformanceCheck.from_file(cc_file)
        log.debug(
            f"checking conformance to {cc_file !s} "
            f"with {len(cc.sections)} sections"
        )
        cc.check()
