
import os

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'info.sparql')
with open(path) as f:
    QUERY_INFO = f.read()
