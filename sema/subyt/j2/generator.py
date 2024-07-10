import os
from typing import Callable

from jinja2 import select_autoescape

from sema.commons.j2 import Filters, J2RDFSyntaxBuilder
from sema.subyt.api import Generator


class JinjaBasedGenerator(Generator):
    """
    Core class for the jinja based LD Templating service.
    """

    def __init__(self, templates_folder: str = "."):
        """
        Builds the generator that produces LD output from datasources

        :param templates_folder: Location of the templates defaults to "."
        """
        self._templates_folder = templates_folder
        ttl_filter = {"ttl": Filters.all()["xsd"]}

        self.syntax_builder = J2RDFSyntaxBuilder(
            templates_folder,
            extra_filters=ttl_filter,
            jinja_env_variables={
                "autoescape": select_autoescape(
                    disabled_extensions=(
                        "ttl",
                        "txt",
                        "ldt",
                        "json",
                        "jsonld",
                    ),
                    default_for_string=True,
                    default=True,
                )
            },
        )

    def __repr__(self):
        abs_folder = os.path.abspath(self._templates_folder)
        return "JinjaBasedGenerator('%s')" % abs_folder

    def make_render_fn(self, template_name: str) -> Callable:
        return self.syntax_builder._get_rdfsyntax_template(
            template_name
        ).render
