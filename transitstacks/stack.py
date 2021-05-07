from typing import Mapping, Any, List, Collection

import pandas as pd
from diagrams import Cluster, Diagram

from .node import define_node
from .edge import relationships_to_edges
from .color import bg_colors

UNKNOWN_VALUE = "TO CONFIRM"
EXCLUDE_PREFIX = "_"

class Stack:
    def __init__(self, stack_dict):
        _exclude = [f for f in stack_dict["components"].columns if f.startswith(EXCLUDE_PREFIX)]

        self.components_df = stack_dict["components"].drop(_exclude, axis=1)

        self.components_df = add_df(
            self.components_df,
            stack_dict["key component"],
            "Component",
        )

        self.components_df = add_df(
            self.components_df,
            stack_dict["key product"],
            "Product",
        )

        self.components_df = add_df(
            self.components_df,
            stack_dict["contracts"],
            "Contract ID",
        )

        self.relationships_df = stack_dict["relationships"]

        # Dataframes with cluster attributes
        self.clusters = {}


    @property
    def providers(self) -> List[str]:
        x = self.components_df["Transit Provider"].dropna().unique().tolist()
        if UNKNOWN_VALUE in x:
            x.remove(UNKNOWN_VALUE)
        return x

    @property
    def contract_vendors(self) -> List[str]:
        x = self.components_df["Contract Vendor"].dropna().unique().tolist()
        if UNKNOWN_VALUE in x:
            x.remove(UNKNOWN_VALUE)
        return x

    @property
    def vendors(self) -> List[str]:
        x = self.components_df["Vendor"].dropna().unique().tolist()
        if UNKNOWN_VALUE in x:
            x.remove(UNKNOWN_VALUE)
        return x

    @property
    def products(self) -> List[str]:
        x = self.components_df["Product"].dropna().unique().tolist()
        if UNKNOWN_VALUE in x:
            x.remove(UNKNOWN_VALUE)
        return x

    @property
    def components(self) -> List[str]:
        x = self.components_df["Component"].dropna().unique().tolist()
        if UNKNOWN_VALUE in x:
            x.remove(UNKNOWN_VALUE)
        return x

    @property
    def function_group(self) -> List[str]:
        x = self.relationships_df["Function Group"].dropna().unique().tolist()
        if UNKNOWN_VALUE in x:
            x.remove(UNKNOWN_VALUE)
        return x

    @property
    def location(self) -> List[str]:
        x = self.relationships_df["Location"].dropna().unique().tolist()
        if UNKNOWN_VALUE in x:
            x.remove(UNKNOWN_VALUE)
        return x

    @property
    def standards(self) -> List[str]:
        x = self.relationships_df["Standard"].dropna().unique().tolist()
        if UNKNOWN_VALUE in x:
            x.remove(UNKNOWN_VALUE)
        return x

    @property
    def mechanisms(self) -> List[str]:
        x = self.relationships_df["Mechanism"].dropna().unique().tolist()
        if UNKNOWN_VALUE in x:
            x.remove(UNKNOWN_VALUE)
        return x

    def __repr__(self) -> str:
        PROPERTY_LIST = ["providers", "vendors", "components"]
        MAX_N = 10

        def _str_from_list(
            _list: Collection[Any], _max_n: int = MAX_N, _list_delim: str = "\n - "
        ) -> str:

            if len(_list) <= _max_n:
                return _list_delim + _list_delim.join(_list)
            else:
                return f"{len(_list)}"

        def _property_summary(prop_name: str, _name_str_len: int) -> str:
            _name = " " + prop_name.capitalize().format(width=_name_str_len) + ": "
            _values = f"{_str_from_list(getattr(self,prop_name))}"

            return _name + _values

        len_prop = max([len(x) for x in PROPERTY_LIST])

        _s = "Stack Object:\n" + "\n".join(
            [_property_summary(x, len_prop) for x in PROPERTY_LIST]
        )
        return _s

    def add_cluster(self, cluster_field: str):
        if cluster_field in self.clusters.keys():
            raise ValueError(f"{cluster_field} already a cluster.")

        _cluster = pd.DataFrame(
            self.components_df[cluster_field].dropna().unique(),
            columns=["category"],
        )

        _cluster["bg_color"] = bg_colors(quantity=len(_cluster))

        _cluster.set_index("category")

        self.clusters[cluster_field] = _cluster


def cluster_attrs(cluster: pd.DataFrame, category: Any) -> Mapping[str, Any]:
    """
    Given a clustering field name and category, return a dictionary of attributes.

    Args:
        cluster ([type]): Cluster dataframe
        category ([type]): Category within the cluster

    Returns:
        Dictionary of attributes for GraphViz
    """

    _attrs = cluster[category].to_dict("records")[0]
    del _attrs["category"]

    return _attrs


def stack_diagram(
    stack: Stack,
    cluster_level_1: str = None,
    cluster_level_2: str = None,
    verbose: bool = True,
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
    clusters = {}

    stack.add_cluster(cluster_level_1)
    stack.add_cluster(cluster_level_2)

    c1_df = stack.clusters[cluster_level_1]
    c2_df = stack.clusters[cluster_level_2]

    _comp_df = stack.components_df.copy()
    _comp_df["in diagram"] = False

    with Diagram("Stack Diagram - Functional View", direction="LR") as _stack_d:

        for c1 in c1_df.category.tolist():
            if verbose:
                print(f"CLUSTER 1: {c1}")
            # cluster_components[c1] = {}
            _comp_c1_df = _comp_df.loc[_comp_df[cluster_level_1] == c1]

            with Cluster(c1) as clusters[c1]:
                clusters[c1].dot.attr(**cluster_attrs(c1_df, c1))
                for c2 in _comp_c1_df[cluster_level_2].dropna().unique().tolist():

                    if verbose:
                        print(f"CLUSTER 2: {c2}")

                    # cluster_components[c1][c2] = {}
                    _dfc2 = _dfc1.loc[stack.components_df[cluster_level_2] == c2]

                    with Cluster(c2) as clusters[(c1, c2)]:
                        clusters[(c1, c2)].dot.attr(**cluster_attrs(c1_df, c2))
                        for _, row in _dfc2.iterrows():
                            _n = define_node(row)
                            cluster_components[c1][c2] = _n
                            components[row.Component] = _n
                        if verbose:
                            print(f"//CLUSTER 2: {c2}")

                if verbose:
                    print(f"CLUSTER 1 - NO CLUSTER 2: {c1}")

                for _, row in _dfc1.loc[_dfc1[cluster_level_2].isna()].iterrows():

                    _n = define_node(row=_c_end)
                    cluster_components[c1][None] = _n
                    components[row.Component] = _n

                if verbose:
                    print(f"//CLUSTER 1: {c1}")

        unclustered_c = list(
            set(stack.components_df.Component.dropna().unique().tolist())
            - set(components.keys())
        )
        _df_no_c = stack.components_df.loc[
            stack.components_df.Component.isin(unclustered_c)
        ]
        for _, row in _df_no_c.iterrows():
            components[row.Component] = define_node(row)

        for (a, b), edge in relationships_to_edges(stack.relationships_df).items():
            components[a] >> edge >> components[b]

        return _stack_d


def add_df(base_df,add_df,key,exclude_prefix = EXCLUDE_PREFIX,exclude=[]):
    """[summary]

    Args:
        base_df ([type]): [description]
        add_df ([type]): [description]
        key ([type]): [description]
        exclude_prefix (str, optional): [description]. Defaults to "_".
        exclude (list, optional): [description]. Defaults to [].
    """        
    key_list = [key] if type(key)==str else key

    #don't add fields already there
    _exclude = [f for f in base_df.columns if f in add_df.columns and f not in key_list]

    #don't add fields marked as private
    _exclude += [f for f in add_df.columns if f.startswith(exclude_prefix)]

    #don't add explicitly excluded fields
    _exclude += exclude

    return base_df.merge(
        add_df.drop(_exclude,axis=1), on=key, how="left"
    )