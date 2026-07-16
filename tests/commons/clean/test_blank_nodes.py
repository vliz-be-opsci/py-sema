import pytest
import json
from rdflib import Graph, BNode, URIRef, Literal
from sema.commons.clean import clean_graph, default_cleaner

# We will test how py-sema's clean_graph handles various @id and property formats.
# Under JSON-LD 1.1, any string starting with "_:" is a valid blank node identifier,
# and relative path IDs are valid relative IRIs.

TEST_CASES = [
    # 1. Standard blank node (should pass)
    {
        "name": "standard_blank_node",
        "id": "_:b0",
        "should_fail_parse": False,
        "should_fail_clean": False,
    },
    # 2. Blank node with dot (should pass)
    {
        "name": "blank_node_with_dot",
        "id": "_:b0.dot",
        "should_fail_parse": False,
        "should_fail_clean": False,
    },
    # 3. Blank node with hyphen (should pass)
    {
        "name": "blank_node_with_hyphen",
        "id": "_:b0-hyphen",
        "should_fail_parse": False,
        "should_fail_clean": False,
    },
    # 4. Blank node with underscore (should pass)
    {
        "name": "blank_node_with_underscore",
        "id": "_:b0_underscore",
        "should_fail_parse": False,
        "should_fail_clean": False,
    },
    # 5. Blank node with @ sign (reported issue)
    {
        "name": "blank_node_with_at_sign",
        "id": "_:help@embrc.org",
        "should_fail_parse": False,
        "should_fail_clean": False, # This should now clean successfully
    },
    # 6. Blank node with slash
    {
        "name": "blank_node_with_slash",
        "id": "_:b0/slash",
        "should_fail_parse": False,
        "should_fail_clean": False, # This should now clean successfully
    },
    # 7. Blank node with percent
    {
        "name": "blank_node_with_percent",
        "id": "_:b0%percent",
        "should_fail_parse": False,
        "should_fail_clean": False, # This should now clean successfully
    },
    # 8. Blank node with dollar
    {
        "name": "blank_node_with_dollar",
        "id": "_:b0$dollar",
        "should_fail_parse": False,
        "should_fail_clean": False, # This should now clean successfully
    },
    # 9. Non-blank node: http URI
    {
        "name": "http_uri",
        "id": "http://example.org/node",
        "should_fail_parse": False,
        "should_fail_clean": False,
    },
    # 10. Non-blank node: http URI with @ sign
    {
        "name": "http_uri_with_at_sign",
        "id": "http://example.org/contact@domain.com",
        "should_fail_parse": False,
        "should_fail_clean": False,
    },
    # 11. Non-blank node: mailto URI
    {
        "name": "mailto_uri",
        "id": "mailto:help@embrc.org",
        "should_fail_parse": False,
        "should_fail_clean": False,
    },
]

@pytest.mark.parametrize("case", TEST_CASES)
def test_jsonld_node_interactions(case):
    name = case["name"]
    node_id = case["id"]
    should_fail_parse = case["should_fail_parse"]
    should_fail_clean = case["should_fail_clean"]

    # Scaffolding JSON-LD
    json_ld_data = {
        "@context": {
            "ContactPoint": "http://schema.org/ContactPoint",
            "email": "http://schema.org/email",
            "name": "http://schema.org/name"
        },
        "@graph": [
            {
                "@id": node_id,
                "@type": "ContactPoint",
                "email": "mailto:info@example.org",
                "name": "Test Node"
            }
        ]
    }

    g = Graph()
    
    if should_fail_parse:
        with pytest.raises(Exception):
            g.parse(data=json.dumps(json_ld_data), format="json-ld")
        return
    
    # Parse should succeed
    g.parse(data=json.dumps(json_ld_data), format="json-ld")
    assert len(g) > 0

    cleaner = default_cleaner()
    
    if should_fail_clean:
        with pytest.raises(Exception):
            clean_graph(g, cleaner)
    else:
        cleaned_g = clean_graph(g, cleaner)
        assert len(cleaned_g) == len(g)
