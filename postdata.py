import json
import os

# Simple Python script to create the postdata JSON files.
# Chris Joakim, Microsoft, September 2021
#
# Use:
# $ python postdata.py > postdata/body1.json

if __name__ == "__main__":
    postdata = dict()
    queries = list()
    postdata['queries'] = queries

    q1 = dict()
    q1['sql'] = "select * from c where c.pk = 'ANC:OKO' offset 0 limit 1"
    q1['count'] = 4 

    q2 = dict()
    q2['sql'] = "select * from c where c.route = 'ANC:OKO'"
    q2['count'] = 2 

    queries.append(q1)
    queries.append(q2)

    print(json.dumps(postdata, sort_keys=False, indent=2))
