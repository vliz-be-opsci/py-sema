from sema.subyt import Source, SourceFactory
from sema.subyt.sources import EmptySource
from tests.conftest import TEST_FOLDER


def test_unexisting_source() -> None:
    UNEXISTING = TEST_FOLDER / "resources" / "unexisting.file.csv"
    emptySource: Source = SourceFactory.make_source(UNEXISTING, fake_empty=True)
    assert isinstance(emptySource, EmptySource)
    with emptySource as items:
        data = list(items)
        assert len(data) == 0
