# Should I cover who_reference cases?
# Should list all posible cases

import json
import re
from typing import Dict, List, Tuple

import networkx as nx


example = {
    "a.py": [
        {
            "name": "A",
            "code_start_line": 0,
            "code_end_line": 100,
            "reference_who": [
                "a.py/A/method"
            ],
            "who_reference": []
        },
        {
            "name": "method",
            "code_start_line": 20,
            "code_end_line": 30,
            "reference_who": [
                "b.py/B",
                "b.py/B/method",
            ],
            "who_reference": []
        },
    ],
    "b.py": [
        {
            "name": "B",
            "code_start_line": 0,
            "code_end_line": 100,
            "reference_who": [
                "b.py/B/method"
            ],
            "who_reference": []
        },
        {
            "name": "method",
            "code_start_line": 20,
            "code_end_line": 30,
            "reference_who": [
                "c.py/C",
                "c.py/C/method",
            ],
            "who_reference": []
        },
    ],
    "c.py": [
        {
            "name": "C",
            "code_start_line": 0,
            "code_end_line": 100,
            "reference_who": [
                "c.py/C/method"
            ],
            "who_reference": []
        },
        {
            "name": "method",
            "code_start_line": 20,
            "code_end_line": 30,
            "reference_who": [
                "d.py/D",
                "d.py/D/method",
            ],
            "who_reference": []
        },
    ],
    "d.py": [
        {
            "name": "D",
            "code_start_line": 0,
            "code_end_line": 100,
            "reference_who": [
                "d.py/D/method"
            ],
            "who_reference": []
        },
        {
            "name": "method",
            "code_start_line": 20,
            "code_end_line": 30,
            "reference_who": [
                "b.py/B",
                "b.py/B/method",
            ],
            "who_reference": []
        },
    ],
}


def extract_who_reference(file: Dict) -> Dict:
    pass


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


def add_father(file: Dict) -> Dict:
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
    return file


def add_path(file: Dict) -> Dict:
    for path in list(file):
        for item_id in range(len(file[path])):
            file[path][item_id].update({"path": path})
    return file


def parse_relation_node(file: Dict) -> List:
    nodes = []

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


def construct_graph(file: Dict, relation_nodes: List) -> nx.DiGraph:
    graph = nx.DiGraph()

    # Add nodes
    for path in list(file):
        for item in file[path]:
            if item['father']:
                graph.add_node(f"{path}/{item['father']}/{item['name']}", attributes=item)
            else:
                graph.add_node(f"{path}/{item['name']}", attributes=item)
    # Add edges
    for relation_node in relation_nodes:
        item_1 = relation_node[0]
        item_2 = relation_node[1]

        if item_1['father']:
            node_1 = f"{item_1['path']}/{item_1['father']}/{item_1['name']}"
        else:
            node_1 = f"{item_1['path']}/{item_1['name']}"

        if item_2['father']:
            node_2 = f"{item_2['path']}/{item_2['father']}/{item_2['name']}"
        else:
            node_2 = f"{item_2['path']}/{item_2['name']}"

        graph.add_edge(node_1, node_2)

    return graph


def get_loop(graph: nx.DiGraph) -> List:
    try:
        loop = list(nx.find_cycle(graph, orientation='original'))
        print(f"Loop: {loop}")
        return loop
    except:
        return []


def remove_loop_from_json(graph, loop: List, file: Dict) -> Tuple[Dict, nx.DiGraph]:
    must_remove_relationship: Tuple = loop[-1]
    print(f"Removed relation: {must_remove_relationship}")
    
    first_item: str = must_remove_relationship[0]
    second_item: str = must_remove_relationship[1]

    # Delete reference_who
    first_item_path = find_python_path(first_item)

    first_item_remain = first_item_path.replace(f"{first_item_path}/", "")
    first_item_splitted_remain = first_item_remain.split("/")
    
    if len(first_item_splitted_remain) == 1:
        for item_id in range(len(file[first_item_path])):
            if file[first_item_path][item_id]['name'] == first_item_splitted_remain[0]:
                try:
                    file[first_item_path][item_id]['reference_who'].remove(second_item)
                except:
                    pass
                break
    
    # Delete who_reference
    second_item_path = find_python_path(second_item)

    second_item_remain = second_item_path.replace(f"{second_item_path}/", "")
    second_item_splitted_remain = second_item_remain.split("/")
    
    if len(second_item_splitted_remain) == 1:
        for item_id in range(len(file[second_item_path])):
            if file[second_item_path][item_id]['name'] == second_item_splitted_remain[0]:
                try:
                    file[second_item_path][item_id]['who_reference'].remove(first_item)
                except:
                    pass
                break
    
    # Delete edges
    graph.remove_edge(first_item, second_item)
    
    return file, graph


def remove_all_loops(graph, file: Dict) -> Dict:
    contain_loop = True

    while contain_loop:
        loop = get_loop(graph)

        if loop:
            file, graph = remove_loop_from_json(graph, loop, file)
        else:
            contain_loop = False
    return file


if __name__ == "__main__":
    file = example

    file = add_path(file)

    file = add_father(file)

    relation_nodes = parse_relation_node(file)

    print(json.dumps(relation_nodes, indent=2))

    graph = construct_graph(file, relation_nodes)

    print(get_loop(graph))

    file = remove_all_loops(graph, file)

    print(json.dumps(file, indent=2))