# Should I cover who_reference cases?
# Should list all posible cases

import re
from typing import Dict, List

import networkx as nx


example = {
    "a.py": [
        {
            "name": "A",
            "code_start_line": 0,
            "code_end_line": 100,
            "reference_who": [
                "a.py/A/method"
            ]
        },
        {
            "name": "method",
            "code_start_line": 20,
            "code_end_line": 30,
            "reference_who": [
                "b.py/B",
                "b.py/B/method",
            ]
        },
    ],
    "b.py": [
        {
            "name": "B",
            "code_start_line": 0,
            "code_end_line": 100,
            "reference_who": [
                "b.py/B/method"
            ]
        },
        {
            "name": "method",
            "code_start_line": 20,
            "code_end_line": 30,
            "reference_who": [
                "c.py/C",
                "c.py/C/method",
            ]
        },
    ],
    "c.py": [
        {
            "name": "C",
            "code_start_line": 0,
            "code_end_line": 100,
            "reference_who": [
                "c.py/C/method"
            ]
        },
        {
            "name": "method",
            "code_start_line": 20,
            "code_end_line": 30,
            "reference_who": [
                "d.py/D",
                "d.py/D/method",
            ]
        },
    ],
    "d.py": [
        {
            "name": "D",
            "code_start_line": 0,
            "code_end_line": 100,
            "reference_who": [
                "d.py/D/method"
            ]
        },
        {
            "name": "method",
            "code_start_line": 20,
            "code_end_line": 30,
            "reference_who": [
                "b.py/B",
                "b.py/B/method",
            ]
        },
    ],
}





def code_contain(item, other_item) -> bool:
    if other_item["code_end_line"] == item["code_end_line"] and other_item["code_start_line"] == item["code_start_line"]:
        return False
    if other_item["code_end_line"] < item["code_end_line"] or other_item["code_start_line"] > item["code_start_line"]:
        return False
    return True


def find_python_path(string: str) -> str:

    pattern = r".*\.py"

    match = re.search(pattern, string)

    if match:
        return match.group()
    else:
        return ""


def parse_node(file: Dict) -> List:
    nodes = []
    
    for path in list(file):
        potential_father = None
        # Should find exactly father in law
        for item_id in range(len(file[path])):
            item = file[path][item_id]
            for other_item in file[path]:
                if code_contain(item, other_item):
                    if potential_father == None or ((other_item["code_end_line"] - other_item["code_start_line"]) < (potential_father["code_end_line"] - potential_father["code_start_line"])):
                        potential_father = other_item
            if potential_father:
                file[path][item_id].update({"father": potential_father["name"]})
            else:
                file[path][item_id].update({"father": ""})

    for path in list(file):
        for item in file[path]:
            for referenced_item in item["reference_who"]:
                # seach referenced node
                referenced_path = find_python_path(referenced_item)
                remain = referenced_item.replace(f"{referenced_path}/", "")
                splitted_remain = remain.split("/")
                # either a class method or class
                if len(splitted_remain) == 1:
                    for other_item in file[referenced_path]:
                        if other_item['name'] == splitted_remain[0]:
                            nodes.append((item, other_item))
                            break
                else:
                    for other_item in file[referenced_path]:
                        if other_item['name'] == splitted_remain[1] and other_item['father'] == splitted_remain[0]:
                            nodes.append((item, other_item))
                            break

    return nodes


def construct_graph(node_list: List) -> nx.DiGraph:
    graph = nx.DiGraph()

    graph.add_edges_from(node_list)

    return graph


def get_loop(graph: nx.DiGraph) -> List:
    return list(nx.find_cycle(graph, orientation='original'))


def remove_loop_from_json(loops: List, file) -> List:
    must_remove_relationships = [loop[-1] for loop in loops]

    for must_remove_relationship in must_remove_relationships:
        try:
            pass

        except:
            pass






if __name__ == "__main__":
    file = example

    print(parse_node(file))


