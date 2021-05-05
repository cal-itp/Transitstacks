from .node import define_node
from .edge import relationships_to_edges

from diagrams import Cluster, Diagram

class Stack():
    def __init__(self,stack_dict):
        self.components_df = stack_dict["components"]

        self.components_df = self.components_df.merge(
            stack_dict["key component"],on='Component',how='left'
        )

        self.components_df = self.components_df.merge(
            stack_dict["contracts"],on='Contract ID',how='left'
        )

        self.relationships_df = stack_dict["relationships"] 


def stack_diagram(
    stack: Stack, 
    cluster_level_1: str= None, 
    cluster_level_2: str=None, 
    verbose: bool = True
) -> Diagram:
    """[summary]

    Args:
        stack: Stack instance.
        cluster_level_1: First level cluster. Defaults to None.
        cluster_level_2: Second level cluster. Defaults to None.

    Returns:
        Diagram: [description]
    """    
    components = {}
    cluster_components = {}

    with Diagram("Stack Diagram - Functional View", direction = 'LR') as _stack_d:

        for c1 in stack.components_df[cluster_level_1].dropna().unique().tolist():
            if verbose: print(f"CLUSTER 1: {c1}")
            cluster_components[c1]={}
            _dfc1 = stack.components_df.loc[stack.components_df[cluster_level_1]==c1]
            
            with Cluster(c1):
                
                for c2 in _dfc1[cluster_level_2].dropna().unique().tolist():
        
                    if verbose: print(f"CLUSTER 2: {c2}")

                    cluster_components[c1][c2]={}
                    _dfc2 = _dfc1.loc[stack.components_df[cluster_level_2]==c2]
                    
                    with Cluster(c2):

                        for _,row in _dfc2.iterrows():
                            _n = define_node(row)
                            cluster_components[c1][c2]= _n
                            components[row.Component] = _n
                        if verbose: print(f"//CLUSTER 2: {c2}")
                
                if verbose: print(f"CLUSTER 1 - NO CLUSTER 2: {c1}")

                for _,row in _dfc1.loc[_dfc1[cluster_level_2].isna()].iterrows():
    
                    _n = define_node(row= _c_end)
                    cluster_components[c1][None]= _n
                    components[row.Component] = _n

                if verbose: print(f"//CLUSTER 1: {c1}")

                    
        unclustered_c = list(set(stack.components_df.Component.dropna().unique().tolist())-set(components.keys()))
        _df_no_c = stack.components_df.loc[stack.components_df.Component.isin(unclustered_c)]
        for _,row in _df_no_c.iterrows():
            components[row.Component] = define_node(row)
        
        for (a,b),edge in relationships_to_edges(stack.relationships_df).items():
            components[a] >> edge >> components[b]
        
        return _stack_d