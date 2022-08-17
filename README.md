# Msc_project_python

The aim of this part is implementing ontology learning and query mapping mentioned in the dissertation.

## Scripts
Our main script is 'generateSQL.py', which has the function of ontology learning and query mapping. The functions inside are well-defined, together with comments. We supprot differernt input with database, policy and query, and their form are shown in the data file as an example for further using.

The outputs of generateSQL.py includes two files, 'ontology.json' and 'test_data/policy_query.json'. 'ontology.json' stores the key information for OWLAPI to initialize the ontology. 'test_data/policy_query.json' stores the EL expression of query and policy, which are mapped from SQL select statement.
## Data

'data/' includes the data that is used ontology learning.

'testdata/' keeps the EL expression of query and policy.
