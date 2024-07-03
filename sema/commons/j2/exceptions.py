class NoTemplateFolder(Exception):
    """Raised when class no template folder is given"""

    def __init__(self):
        message = (
            "The J2RDFSyntaxBuilder object requires a templates_folder arg"
            " pointing to a folder with jinja templates"
        )
        super().__init__(message)
