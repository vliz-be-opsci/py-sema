from sema.ro.creator import Roc

roc = Roc(
    rocrate_path="./data/katoomba-rainfall",
    blueprint_path="./data/blueprint/katoomba-rainfall.yml",
)

print(roc)
