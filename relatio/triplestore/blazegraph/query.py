
from rdflib import Graph
from SPARQLWrapper import JSON, SPARQLWrapper
from typing import List, Union

from .server import URL_BLAZEGRAPH


def query_server(query: str) -> Union[List[dict], Graph]:
    """ 
    Query Blazegraph server
    """
    
    # BlazeGraph doesn't know 'turtle' format...
    # is_output_graph = "CONSTRUCT" in query 
    # return_format = TURTLE if is_output_graph else JSON

    # Initialize endpoint
    sparql = SPARQLWrapper(URL_BLAZEGRAPH, returnFormat=JSON)
    
    # Query Blazegraph
    sparql.setQuery(query)
    res = sparql.queryAndConvert()

    # Formatted results
    res = [
        { key: value['value'] for key, value in r.items() }
        for r in res["results"]["bindings"]
    ]

    return res
