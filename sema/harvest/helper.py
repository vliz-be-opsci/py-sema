import re
from datetime import datetime, timezone
from typing import Dict, List

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import NamespaceManager

from sema.commons.clean import check_valid_uri


def timestamp():
    return datetime.now(timezone.utc)


def makeNSM(pfx_declarations: Dict[str, str]) -> Dict[str, Namespace]:
    pfxs = {k: Namespace(v) for k, v in pfx_declarations.items()}
    print(f"{pfxs=}")

    nsm = NamespaceManager(Graph(), bind_namespaces="none")
    for pf, ns in pfxs.items():
        nsm.bind(pf, ns, override=True)
    print(f"{list(nsm.namespaces())=}")
    return nsm


def resolve_uri(uri: str, nsm: NamespaceManager) -> URIRef:
    return URIRef(uri) if check_valid_uri(uri) else nsm.expand_curie(uri)


def resolve_literals(
    literal_uris: List[str], nsm: NamespaceManager
) -> List[URIRef]:
    return [resolve_uri(u, nsm) for u in literal_uris]


def resolve_sparql(sparql, nsm):
    pfxlines: str = "\n".join(
        (f"PREFIX {p}: {u.n3()}" for p, u in nsm.namespaces())
    )
    return f"{pfxlines}\n{sparql}"


PPATH_RE: str = (
    r"(([^<>\/\s]+)|<([^>]+)>)\s*\/"  # how to match parts of property-paths
)


def ppath_split(ppath: str) -> List[str]:
    return (
        m.group(2) or m.group(3)
        for m in re.finditer(pattern=PPATH_RE, string=ppath + "/")
    )


def resolve_ppaths(ppaths: List[str], nsm: NamespaceManager):
    return [
        " / ".join(resolve_uri(part, nsm).n3() for part in ppath_split(ppath))
        for ppath in ppaths
    ]
