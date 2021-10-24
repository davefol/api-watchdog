import itertools
from typing import Iterable, List, Literal, Tuple, Dict
from urllib.parse import urlparse

from pydantic import BaseModel, StrictStr

from api_watchdog.core import WatchdogResult


class WatchdogResultGroup(BaseModel):
    name: StrictStr
    results: List[WatchdogResult]
    groups: List["WatchdogResultGroup"]


WatchdogResultGroup.update_forward_refs()

collect_results_groupby = Literal["target"]


def collect_results(
    results: Iterable[WatchdogResult],
    groupby: collect_results_groupby = "target",
) -> WatchdogResultGroup:
    if groupby == "target":
        return group_results_by_target(results)
    else:
        raise NotImplementedError(f"Invalid groupby option {groupby}.")


def group_results_by_target(
    results: Iterable[WatchdogResult],
) -> WatchdogResultGroup:
    class GrouperNode:
        """
        Lightweight utility class for WatchdogResultGroup algorithms
        """

        def __init__(self, key):
            self.key = key
            self.children = list()

    def extract_key(result) -> Tuple[str, ...]:
        """
        Extract the top level of the url as well as the path
        these will be the keys for grouping
        """
        url_parts = urlparse(result.target)
        root = url_parts.scheme + "://" + url_parts.netloc
        rest = url_parts.path.split("/")
        rest = [x for x in rest if x not in ("", "/")]
        return tuple([root] + rest)

    def dfs_result_group(
        grouper_node: GrouperNode,
        keyed_results: Dict[Tuple[str, ...], List[WatchdogResult]],
    ) -> WatchdogResultGroup:
        """
        Recursively generate WatchdogResultGroup
        """
        return WatchdogResultGroup(
            name="/".join(grouper_node.key),
            results=keyed_results[grouper_node.key],
            groups=[
                dfs_result_group(child, keyed_results)
                for child in grouper_node.children
            ],
        )

    # Associate each result with a key that will determinine
    # its position in the hiearchy
    result_with_keys = [(result, extract_key(result)) for result in results]
    keyed_results = {
        k: [r for _, r in v]
        for k, v in itertools.groupby(
            sorted([(k, r) for (r, k) in result_with_keys], key=lambda x: x[0]),
            lambda x: x[0],
        )
    }

    # create a lighteight out-tree by iterating over the keys
    # in sorted order (ensures that a parent is present _before_ we add to it
    grouper_nodes: Dict[Tuple[str, ...], GrouperNode] = {(): GrouperNode(())}
    for key in sorted(set([key for _, key in result_with_keys])):
        node = GrouperNode(key=key)
        try:
            grouper_nodes[key[:-1]].children.append(node)
        except KeyError:
            grouper_nodes[()].children.append(node)
        grouper_nodes[key] = node

    # depth first search our out-tree to fill out our WatchdogResultGroup
    result_group = WatchdogResultGroup(
        name="<root>",
        results=[],
        groups=[
            dfs_result_group(child, keyed_results)
            for child in grouper_nodes[()].children
        ],
    )

    return result_group
