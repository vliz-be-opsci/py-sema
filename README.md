# py-sema

Overall parent of all packages involving semantic manipulation of RDF data.

## Installation

TDB

## Architecture

```mermaid
graph TD
    py-sema --> | readme.md | sema
    click sema "https://github.com/vliz-be-opsci/py-sema/blob/main/sema/README.md"
    sema --> | readme.md | bench
    click bench "https://github.com/vliz-be-opsci/py-sema/blob/main/sema/bench/README.md"
    sema --> commons
    sema --> | readme.md | harvest
    click harvest "https://github.com/vliz-be-opsci/py-sema/blob/main/sema/harvest/README.md"
    sema --> | readme.md | query
    click query "https://github.com/vliz-be-opsci/py-sema/blob/main/sema/query/README.md"
    sema --> | readme.md | subyt
    click subyt "https://github.com/vliz-be-opsci/py-sema/blob/main/sema/subyt/README.md"
    sema --> | readme.md | syncfs
    click syncfs "https://github.com/vliz-be-opsci/py-sema/blob/main/sema/syncfs/README.md"
    sema --> | readme.md | discovery
    click discovery "https://github.com/vliz-be-opsci/py-sema/blob/main/sema/discovery/README.md"
```

```mermaid
graph TD
    commons --> | readme.md | clean
    click clean "https://github.com/vliz-be-opsci/py-sema/blob/main/sema/commons/clean/README.md"
    commons --> | readme.md | cli
    click cli "https://github.com/vliz-be-opsci/py-sema/blob/main/sema/commons/cli/README.md"
    commons --> | readme.md | env
    click env "https://github.com/vliz-be-opsci/py-sema/blob/main/sema/commons/env/README.md"
    commons --> | readme.md | j2
    click j2 "https://github.com/vliz-be-opsci/py-sema/blob/main/sema/commons/j2/README.md"
    commons --> | readme.md | j2-template
    click j2-template "https://github.com/vliz-be-opsci/py-sema/blob/main/sema/commons/j2-template/README.md"
    commons --> | readme.md | log
    click log "https://github.com/vliz-be-opsci/py-sema/blob/main/sema/commons/log/README.md"
    commons --> | readme.md | path
    click path "https://github.com/vliz-be-opsci/py-sema/blob/main/sema/commons/path/README.md"
    commons --> | readme.md | prov
    click prov "https://github.com/vliz-be-opsci/py-sema/blob/main/sema/commons/prov/README.md"
```

General migration info can be found here: [migration](https://docs.google.com/document/d/11T16tZ4w2-UVToDZfy3QhGrcAlIAdrt-F3WLt576x5g/edit)
