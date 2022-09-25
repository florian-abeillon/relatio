
from typing import Optional, Tuple

import matplotlib.pyplot as plt
import networkx as nx



def plot_graph(res:     dict, 
               lim:     Optional[int]   = None,
               figsize: Tuple[int, int] = ( 10, 8 )) -> None:
    """ 
    Plot graph from list of quad 
    """

    # Create directed graph
    DG = nx.DiGraph()
    edge_labels = {}

    if lim is not None:
        res = res[:lim]

    # Populate graph
    for r in res:
        
        edge1, edge2 = ( r['s1'], r['s2'] ), ( r['s2'], r['s3'] )
        
        DG.add_edge(*edge1)
        edge_labels[edge1] = r['p12']
        
        DG.add_edge(*edge2)
        edge_labels[edge2] = r['p23']


    # Create figure
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot()

    # Plot edge labels
    pos = nx.spring_layout(DG, scale=2)
    nx.draw_networkx_edge_labels(DG, pos, edge_labels=edge_labels, ax=ax)

    # Plot graph
    node_size = [ d * 250 for d in dict(DG.degree).values() ]
    nx.draw(DG, pos=pos, node_size=node_size, with_labels=True, ax=ax)
