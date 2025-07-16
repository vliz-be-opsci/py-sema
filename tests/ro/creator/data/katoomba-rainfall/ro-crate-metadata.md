---
"@blueprint":
  import: emo-bon-base-blueprint
  export: emo-bon-bpns-blueprint
  options:
    glob: true
  prototypes:
    organization:
      "@type": "schema:Organization"

"@context": "https://w3id.org/ro/crate/1.2/context"

"@graph":

"ro-crate-metadata.json":
  "@type": "CreativeWork"
  conformsTo: {"@id": "https://w3id.org/ro/crate/1.2"}
  about: *root
  
"./": &root
  "@type": "Dataset"
  name: "Example dataset for RO-Crate specification"
  description: "Official rainfall readings for Katoomba, NSW 2022, Australia"
  datePublished: "2022-12-01"
  publisher: {"@id": "https://ror.org/04dkp1p98"}
  license: {"@id": "http://spdx.org/licenses/CC0-1.0"}
  hasPart:
    - *data.csv

"data.csv": &data.csv
  "@type": "File"
  name: "Rainfall data for Katoomba, NSW Australia February 2022"
  encodingFormat: "text/csv"
  license: {"@id": "https://creativecommons.org/licenses/by-nc-sa/3.0/au/"}

"https://ror.org/04dkp1p98":
  "@prototype": organization
  name: "Bureau of Meteorology"
  description: "Australian Government Bureau of Meteorology"
  url: "http://www.bom.gov.au/"

"https://creativecommons.org/licenses/by-nc-sa/3.0/au/":
  "@type": "CreativeWork"
  name: "CC BY-NC-SA 3.0 AU"
  description: "Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Australia"
---
