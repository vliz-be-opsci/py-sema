from html.parser import HTMLParser


class LODAwareHTMLParser(HTMLParser):
    """
    HTMLParser that knows about LOD embedding and linking techniques.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.links = []
        self.scripts = []
        self.in_script = False
        self.type = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "link" and "rel" in attrs and attrs["rel"] == "describedby":
            if "href" in attrs:
                self.links.append(attrs["href"])
        elif (
            tag == "script"
            and "type" in attrs
            and (
                attrs["type"] == "application/ld+json"
                or attrs["type"] == "text/turtle"
            )
        ):
            self.in_script = True
            self.type = attrs["type"]

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_script = False

    def handle_data(self, data):
        if self.in_script:
            self.scripts.append({self.type: data})
