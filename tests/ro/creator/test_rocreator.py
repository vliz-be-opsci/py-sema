from sema.ro.creator import ROCreator

def test_object_graph_mapper():
    roc = ROCreator(
        blueprint_path="./tests/ro/creator/data/katoomba-rainfall/roc-me.yml",
        blueprint_env={"SESSIONNAME": "ApiConsole"},
        rocrate_path="./tests/ro/creator/data/katoomba-rainfall",
    )
    roc.process()
