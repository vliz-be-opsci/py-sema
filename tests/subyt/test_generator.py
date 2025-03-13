import logging
from pathlib import Path

from sema.subyt.api import GeneratorSettings, Sink
from sema.subyt.j2.generator import JinjaBasedGenerator
from sema.subyt.sources import SourceFactory

log = logging.getLogger(__name__)


class AssertingSink(Sink):
    def __init__(self, parts: list = None):
        super().__init__()
        self._parts = parts
        self._index = 0
        self._already_open = False
        self._already_closed = False

    def _assert_count(self):
        assert self._index == len(self._parts), "not all parts were rendered"

    def add(self, part: str, item: dict = None, source_mtime: float = None):
        assert self._already_open, "sink.add called before sink.open"
        assert not self._already_closed, "sink.add called after sink.close"

        log.debug(f"part received no. {self._index}:\n--\n{part}\n--")
        expected = self._parts[self._index].strip()
        part = part.strip()
        log.debug(f"expected part == \n{expected}\n")
        log.debug(f"actual part == \n{part}\n")
        log.debug(f"expectations ok: {bool(part == expected)}")
        assert expected == part, (
            f"unexpected rendering for part at index {self._index}",
        )
        self._index += 1

    def open(self):
        assert not self._already_open, "sink.open called twice"
        self._already_open = True

    def close(self):
        assert not self._already_closed, "sink.close called twice"
        self._already_closed = True

    def evaluate(self):
        self._assert_count()


def get_expected_parts(outfile):
    parts = [""]
    n = 0
    with open(outfile, "r") as content:
        for line in content:
            if not line.startswith("#"):
                parts[n] = parts[n] + line
            else:
                if len(parts[n]) > 0:
                    parts.append("")
                    n += 1
    return parts


def get_indicator_from_name(
    name: str, splitter: str = "_", fallback: str = None
):
    known_cases = {"data_glob/*.json": "glob"}
    if name in known_cases.keys():
        return known_cases[name]
    stem = Path(name).stem
    indicator = (
        stem[stem.index(splitter) + 1 :] if splitter in stem else fallback
    )
    return indicator


def test_templates():
    base: Path = Path(__file__).parent.relative_to(Path(".").absolute())
    log.debug(f"beginning test_templates in {base !s}")
    tpl_path: Path = base / "templates"
    out_path: Path = base / "out"
    inp_path: Path = base / "in"

    g = JinjaBasedGenerator(tpl_path)

    inputs = dict()
    inp_names = [p.name for p in inp_path.iterdir()]  # the stuff in the folder
    inp_names = [
        nm for nm in inp_names if nm != "data_glob"
    ]  # filter "data_glob" folder source out to avoid FolderSource for it
    inp_names.extend(
        ["data_glob/*.json"]
    )  # insert "glob pattern" glob source for that folder in stead
    for inp_name in inp_names:
        key = get_indicator_from_name(inp_name, fallback="_")
        assert key not in inputs, (
            f"duplicate key '{key}' for input '"
            f"{inp_name}' --> object[{inputs[key]}]"
        )
        inputs[key] = SourceFactory.make_source(str(inp_path / inp_name))

    assert "_" in inputs, "the base set should be available"

    # read all names (files) in the tpl_path
    tpl_names = [p.name for p in tpl_path.iterdir() if p.is_file()]

    for tpl_name in tpl_names:
        # load the expected parts from the matching output-file in the sink
        sink = AssertingSink(get_expected_parts(out_path / tpl_name))
        generator_settings = GeneratorSettings(
            get_indicator_from_name(tpl_name)
        )

        # process
        log.debug(f"processing test-template: {tpl_path / tpl_name !s}")
        try:
            g.process(
                tpl_name,
                inputs,
                generator_settings,
                sink,
                vars_dict={"my_domain": "realexample.org"},
            )
        except Exception:
            log.exception("failed to process template")
            raise

        # assure all records were passed
        sink.evaluate()
    log.debug("ending test_templates")
