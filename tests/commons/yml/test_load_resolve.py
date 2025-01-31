from sema.commons.yml import LoaderBuilder
import pytest
import yaml


def test_resolve_loader():
    context = {"a": "1", "b": "2"}

    yml_text = "value: !resolve '{a}.{b}'"
    # 0. with std resolver we get an error for not ignoring unknown tags
    with pytest.raises(yaml.constructor.ConstructorError):
        out = yaml.load(yml_text, Loader=yaml.SafeLoader)

    # 1. with ignore_unknown resolver we get out without expansion applied
    ignoring_loader = LoaderBuilder().ignore_unknown().build()
    out = yaml.load(yml_text, Loader=ignoring_loader)
    assert out['value'] == '{a}.{b}'

    # 2. previous approach should not affect the SafeLoader
    #    in other words, the 1st test should still fail
    with pytest.raises(yaml.constructor.ConstructorError):
        out = yaml.load(yml_text, Loader=yaml.SafeLoader)

    # 3. with custom resolver we get resolved output
    resolving_loader = LoaderBuilder().to_resolve(context).build()
    out = yaml.load(yml_text, Loader=resolving_loader)
    assert out['value'] == '1.2'

    # 4. when refering to unknown key we get no resolution - keyerror will be logged
    err_text = "value: !resolve '{a}.{c}'"
    out = yaml.load(err_text, Loader=resolving_loader)
    assert out['value'] == '{a}.{c}'
