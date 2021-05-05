from typing import Mapping,Union

import numpy as np
import pandas as pd

from diagrams import Edge

# executed in order with subsequent values overriding
default_edge_color = 'grey'

edge_color_lookup = {
    ('Standard','Human translation'): 'red',
    ('Standard',np.NaN): 'red',
    ('Parallel model', 1): 'darkgreen',
    ('Centralized model', 1): 'darkgreen',
}

# executed in order with subsequent values overriding
default_edge_style = 'solid'

edge_style_lookup = {
    ('Standard','Human translation'): 'dotted',
    ('Mechanism','Intra-product'): 'dotted',
}

def define_edge(edge: Union[Mapping,pd.Series]) -> Edge:
    """[summary]

    Args:
        edge (Union[Mapping,pd.Series]): [description]

    Returns:
        Edge: [description]
    """    
    edge_label=f"{edge.get('Mechanism','')} : {edge.get('Standard','')}"
    
    edge_color = default_edge_color
    for (field,value),color in edge_color_lookup.items():
        if edge.get(field) == value: 
            edge_color = color
    
    edge_style=default_edge_style
    for (field,value),style in edge_style_lookup.items():
        if edge.get(field) == value: 
            edge_style = style
            
    e = Edge(
        color=edge_color, 
        style=edge_style, 
        label=edge_label,
        #labelfontsize = 24,
        #labelfontname = 'courier',
        #labelfontcolor = edge_color,
    )
    return e


def relationships_to_edges(relationships_df: pd.DataFrame)-> Mapping[tuple,Edge]:
    edges_s = relationships_df.apply(define_edge, axis=1)
    relationship_edges = dict(
        zip(
            list(zip(relationships_df["Component A"],relationships_df["Component B"])),
            edges_s
        )
    )
    return relationship_edges

