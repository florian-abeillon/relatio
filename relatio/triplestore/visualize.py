
from rdflib import URIRef
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph
from typing import List, Tuple

import matplotlib.pyplot as plt
import networkx as nx

from .namespaces import PREFIXES
from .resources import Triple


def prettify(iri: str) -> Triple:
    """ Prettify IRI with prefix form of namespace """
    for namespace, prefix in PREFIXES.items():
        iri = iri.replace(str(namespace), prefix + ":")
    return iri


def get_triples(res) -> List[Triple]:
    """ Prettify list of triples """
    triples = []
    for triple in res:
        triple = [ el.toPython() for el in triple ]
        triple[1] = prettify(triple[1])
        triples.append(Triple(*triple))
    return triples


def plot_graph(res, figsize: Tuple[int, int] = ( 10, 8 )) -> None:
    """ Plot graph from list of triples """

    # Turn rdflib graph into networkx graph
    G = rdflib_to_networkx_multidigraph(res)
    pos = nx.spring_layout(G, scale=2)

    # Format nodes
    node_color = []
    for node in G.nodes():
        if isinstance(node, URIRef):
            node = node.toPython()

        if not node or node.startswith('re:'):
            node_color.append('purple')
        elif node.startswith('rehd:'):
            node_color.append('red')
        elif node.startswith('reld:'):
            node_color.append('blue')
        elif node.startswith('sp:'):
            node_color.append('turquoise')
        elif node.startswith('wd:'):
            node_color.append('green')
        elif node.startswith('wn:'):
            node_color.append('orange')
        else:
            raise ValueError

    # Format edge labels
    edge_labels = {
        edge: prettify(list(G.get_edge_data(*edge).keys())[0])
        for edge in G.edges()
    }
        
    # Create figure
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot()

    # Plot edge labels
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax)
    # Plot graph
    nx.draw(G, pos=pos, node_color=node_color, with_labels=True, ax=ax)
