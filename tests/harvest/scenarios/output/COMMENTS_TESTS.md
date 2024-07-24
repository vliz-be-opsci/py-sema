# Comments on test output

## Test 1

### yml

```yaml
snooze-till-graph-age-minutes: 0
prefix:
  rdf: http://www.w3.org/1999/02/22-rdf-syntax-ns#
  ex: http://www.example.org/
assert:
  - subjects:
      literal:
        - http://localhost:8080/DOC1.ttl
    paths:
      - "ex:resource"
  - subjects:
      SPARQL: >
        SELECT DISTINCT ?o
        WHERE {
            ?s ex:subset ?bn .
            ?bn ex:id ?o .
        }
    paths:
      - "ex:p1"
      - "ex:p2"
      - "ex:p3"
```

### stop

The first task states that the first subject must be dereferenced and the paths ex:resource must be followed. This will result in the inclusion of DOC1 and DOC2.

The second task states that the first subject must be dereferenced and the paths ex:subset must be followed. This will result in the inclusion of DOC4 .

resulting in the inclusion of DOC1, DOC2 and DOC4.

### nostop

TBD but since the first subbjects of each task are the same the result will be the same as the stop case.

## Test 2

### yml

```yaml
snooze-till-graph-age-minutes: 0
prefix:
  rdf: http://www.w3.org/1999/02/22-rdf-syntax-ns#
  ex: http://www.example.org/
assert:
  - subjects:
      literal:
        - http://localhost:8080/DOC1.ttl
    paths:
      - "ex:resource / ex:subset"
      - "ex:resource / ex:part"
  - subjects:
      SPARQL: >
        SELECT DISTINCT ?o
        WHERE {
            ?s ex:id ?o .
        }
    paths:
      - "ex:p1"
      - "ex:p2"
      - "ex:p3"
```

### stop

The test2_fdoc_stop_expdocsincluded.ttl describes that after the first assertion of the first subject paths the following docs must be included DOC1, DOC2, DOC3, DOC8

However given that only the first resource will be dereference and no other one only the DOC2 will be included on top of DOC1 which is the primary literal subject.

Since only DOC2 and DOC1 are present the second part fo the first assertion can only get DOC4 which satisfies the assertion of ex:subset.

For the second assertion path nothing will be added since the first assertion did not dereference DOC8.

resulting in the inclusion of DOC1 and DOC2 and DOC4.

### nostop

Not implemented yet.

Some foreshadowing , since only DOC2 dereferenced bu the test will keep going until all subjects have been tested, the following docs will be included:

- DOC1 : primary dereference
- DOC2 : first assertion and first to be tested with ex:subset
- DOC3 : added since DOC2 will fail on "ex:resource / ex:part"
- DOC8 : added since DOC3 will fail on "ex:resource / ex:part"
- DOC4: since first subject to be caught of ex:id is from DOC2 stating DOC4

## Test 3

### yml

```yaml
snooze-till-graph-age-minutes: 0
prefix:
  rdf: http://www.w3.org/1999/02/22-rdf-syntax-ns#
  ex: http://www.example.org/
assert:
  - subjects:
      literal:
        - http://localhost:8080/DOC1.ttl
    paths:
      - "ex:resource / ex:subset"
      - "ex:part"
  - subjects:
      SPARQL: >
        SELECT DISTINCT ?o
        WHERE {
            ?s ex:id ?o .
        }
    paths:
      - "ex:p1"
      - "ex:p2"
      - "ex:p3"
```

### stop

The test3_fdoc_stop_expdocsincluded.ttl describes that after the first assertion of the first subject paths the following docs must be included DOC1, DOC2, DOC3, DOC8

However given that only the first resource will be dereference and no other one only the DOC2 will be included on top of DOC1 which is the primary literal subject.

Since only DOC2 and DOC1 are present the second part fo the first assertion can only get DOC4 which satisfies the assertion of ex:subset.

For the second assertion path the only doc that will be added is DOC4 since this is the only subject that has ex:id.

resulting in the inclusion of DOC1, DOC2 and DOC4.

### nostop

Not implemented yet.

## Test 4

### yml

```yaml
snooze-till-graph-age-minutes: 0
prefix:
  rdf: http://www.w3.org/1999/02/22-rdf-syntax-ns#
  ex: http://www.example.org/
assert:
  - subjects:
      literal:
        - http://localhost:8080/DOC1.ttl
    paths:
      - "ex:part"
      - "ex:resource / ex:subset"
  - subjects:
      SPARQL: >
        SELECT DISTINCT ?o
        WHERE {
            ?s ex:id ?o .
        }
    paths:
      - "ex:p1"
      - "ex:p2"
      - "ex:p3"
```

### stop

The test4_fdoc_stop_expdocsincluded.ttl describes that after the first assertion of the first subject paths the following docs must be included DOC1, DOC2, DOC3, DOC8

However given that only the first resource will be dereference and no other one only the DOC2 will be included on top of DOC1 which is the primary literal subject.

Since only DOC2 and DOC1 are present the second part fo the first assertion can only get DOC4 which satisfies the assertion of ex:subset.

For the second assertion path the only doc that will be added is DOC4 since this is the only subject that has ex:id.

resulting in the inclusion of DOC1, DOC2 and DOC4.

### nostop

Not implemented yet.

## Test 5

### yml

```yaml
snooze-till-graph-age-minutes: 0
prefix:
  rdf: http://www.w3.org/1999/02/22-rdf-syntax-ns#
  ex: http://www.example.org/
assert:
  - subjects:
      literal:
        - http://localhost:8080/DOC1.ttl
    paths:
      - "ex:resource / ex:subset"
      - "ex:part"
  - subjects:
      SPARQL: >
        SELECT DISTINCT ?o
        WHERE {
            ?s ex:id ?o .
        }
    paths:
      - "ex:p4"
```

### stop

The test5_fdoc_stop_expdocsincluded.ttl describes that after the first assertion of the first subject paths the following docs must be included DOC1, DOC2, DOC3

However given that only the first resource will be dereference and no other one only the DOC2 will be included on top of DOC1 which is the primary literal subject.

The second subject SPARQL query will find DOC4 since it is the only subject that has ex:id.

resulting in the inclusion of DOC1, DOC2 and DOC4.

### nostop

Not implemented yet.
