import json
from io import StringIO

"""
Json converter for big query database.
"""

with open("input/data.json", "r") as infile:
    in_json = StringIO(infile.read())

with open("output/dataNL.json", "wb") as outfile:
    for record in json.load(in_json):
        outfile.write(json.dumps(record).encode("utf-8"))
        outfile.write("\n".encode("utf-8"))
