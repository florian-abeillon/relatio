
import os

from .utils import URL, query_triplestore

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'query.sparql')
with open(path) as f:
    QUERY = f.read()
