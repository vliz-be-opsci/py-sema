import argparse
import logging
import logging.config
import sys
from pathlib import Path

import validators
from rdflib import Graph

from sema.commons.cli import SemaArgsParser
from sema.commons.fileformats import format_from_filepath
from sema.commons.glob import getMatchingGlobPaths
from sema.harvest import Harvest
from sema.harvest.store import RDFStore, RDFStoreAccess
from sema.harvest.url_to_graph import get_graph_for_format

log = logging.getLogger(__name__)


def get_arg_parser() -> SemaArgsParser:
    """
    Get the argument parser for the sema-harvest module.

    This parser includes arguments for configuration file paths,
    initial context loading, store endpoints, and output dumping.
    """
    parser = SemaArgsParser(
        "sema-harvest",
        "harvesting service for traversing and asserting paths",
    )

    DEFAULT_CONFIG_FOLDER = Path.cwd() / "config"

    parser.add_argument(
        "-c",
        "--config",
        nargs=1,
        action="store",
        type=str,
        required=False,
        default=str(DEFAULT_CONFIG_FOLDER),
        help=(
            "Path to folder containing configuration files "
            "or to a single configuration path "
            "in both cases relative to the working directory. "
            "Defaults to ./config "
        ),
    )

    parser.add_argument(
        "-d",
        "--dump",
        type=str,
        default=None,
        action="store",
        nargs=1,
        required=False,
        help=(
            "Path of file to dump the harvested resulting graph to "
            "use '-' to have output to stdout"
        ),
    )

    parser.add_argument(
        "-i",
        "--init",
        nargs="+",
        action="store",
        required=False,
        default=None,
        help=(
            "List of paths to files or folders (containing files) "
            "that will be loaded into the store at the start."
        ),
    )

    parser.add_argument(
        "-s",
        "--store",
        nargs=2,
        action="store",
        required=False,
        help=(
            "Pair of read_uri and write_uri describing the "
            "SPARQL endpoint to use as store. "
        ),
    )

    return parser


def enable_logging(args: argparse.Namespace):
    if args.logconf is None:
        return
    # conditional dependency -- we only need this (for now)
    #   when logconf needs to be read
    import yaml

    print(f"args.logconf = {args.logconf}")
    logconf_location = Path.cwd() / args.logconf[0]

    with open(logconf_location, "r") as yml_logconf:
        logging.config.dictConfig(
            yaml.load(yml_logconf, Loader=yaml.SafeLoader)
        )
    log.info(f"Logging enabled according to config in {args.logconf}")


def load_resource_into_graph(graph: Graph, resource: str | Path, format: str):
    """
    Insert a resource into a graph.
    """
    # resource can be a path or a URI

    # check if resource is a URI
    if validators.url(resource):
        # get triples from the uri and add them
        formats = ["text/turtle", "application/ld+json"]
        to_add_graph = get_graph_for_format(str(resource), formats=formats)
        if to_add_graph:
            return graph + to_add_graph

    # else
    resource_path: Path = Path(resource)

    # check if resource is a file
    if resource_path.is_file():
        # get triples from the file
        # determine the format of the file and use the correct parser
        format = format_from_filepath(resource_path, "turtle")
        graph.parse(resource, format=format)
        return graph

    # else
    # check if resource is a folder
    if resource_path.is_dir():
        for sub in getMatchingGlobPaths(resource_path, onlyFiles=True):
            format = format_from_filepath(sub, "turtle")
            load_resource_into_graph(graph, sub, format)
        return graph

    # if resource is neither a URI nor a file then raise an error
    raise ValueError(f"Resource is not a valid URI or file path: {resource}")


def init_load(args: argparse.Namespace, store: RDFStore):
    """
    loads the suggested input into the store prior to execution
    """
    if args.init is None:
        log.debug("no initial context to load")
        return  # nothing to do
    # else
    log.debug(f"loading initial context from {len(args.init)=} files")
    graph: Graph = Graph()
    for inputfile in args.init:
        load_resource_into_graph(graph, inputfile, format="text/turtle")
    store.insert(graph, "urn:harvest:context")


def make_service(args: argparse.Namespace) -> Harvest:
    store_info: list = args.store or []
    log.debug(f"{store_info=}")
    if store_info is not None:
        log.debug(f"make service for target store {store_info}")
    else:
        log.debug("make service for target store with no store_info provided")
    config = args.config[0]
    config = Path.cwd() / config
    new_service = Harvest(config, store_info)
    return new_service


def final_dump(args: argparse.Namespace, store: RDFStoreAccess):
    if args.dump is None:
        log.debug("no dump expected")
        return  # nothing to do
    # else
    format = "turtle"
    outgraph = Graph()
    alltriples = store.all_triples()
    # NOTE alternatively pass Graph() as arg
    if not alltriples:
        log.debug("nothing to dump")
        return
    # else
    for triple in alltriples:
        try:
            outgraph.add(triple)  # type: ignore
        except Exception as e:
            log.error(f"failed to add {triple} to output graph: {e}")

    if args.dump == "-":
        log.debug("dump to stdout")
        ser: str = outgraph.serialize(format=format)
        print(ser)
    else:
        # derive format from file extension
        log.debug(f"dump to file {args.dump}")
        dest = args.dump[0]
        output_path = Path.cwd() / dest
        format = format_from_filepath(output_path, format)
        # then save there
        outgraph.serialize(destination=output_path, format=format)


def _main(*cli_args):
    # parse cli args
    args: argparse.Namespace = get_arg_parser().parse_args(cli_args)

    # TODO remove this when using the SemaArgsParser
    # it already does this logging & the logconf setup
    log.debug(f"cli called with {args=}")
    # build the core service
    new_service = make_service(args)
    # load the store initially
    init_load(args, new_service.target_store)
    # do what needs to be done
    new_service.process()
    # dump the output
    final_dump(args, new_service.target_store)


def main():
    _main(*sys.argv[1:])


if __name__ == "__main__":
    main()
