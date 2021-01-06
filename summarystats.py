import json
from cnrelated import get_raw


class Edge:
    class Node:

        def __init__(self, node, side):
            self.id = node["@id"]
            self.term = node["term"].split("/")[-1]
            self.pos = node["sense_label"].split(", ")[0] if "sense_label" in node else None
            self.side = side

    def __init__(self, edge):
        self.start = self.Node(edge["start"], "start")
        self.end = self.Node(edge["end"], "end")
        self.relation = edge["rel"]["@id"].split("/")[-1]
        self.nodes = (self.start, self.end)


def conceptnet_pos_summary():
    summary = {"pos_summary": {"pos": {"a": 0, "r": 0, "v": 0, "n": 0}, "total": 0, "percentage": 0.0},
               "relation_summary": {"relations": {}}, "total_nodes": 0}
    seen_nodes = []
    start_end = ["start", "end"]
    with open("data/words_in_wordnet.json", "r") as file:
        words = json.load(file)
    num_of_words = len(words)
    for i, word in enumerate(words):
        if not i % 1000:
            print(f"{(i / num_of_words) * 100}% Complete")
        data = get_raw(word)
        if "error" in data:
            continue
        for edge_data in data["edges"]:
            if "language" in edge_data["start"] and "language" in edge_data["end"] and edge_data["start"]["language"] == "en" and edge_data["end"]["language"] == "en":
                edge = Edge(edge_data)
                if edge.relation not in summary["relation_summary"]["relations"]:
                    summary["relation_summary"]["relations"][edge.relation] = {}
                    summary["relation_summary"]["relations"][edge.relation]["start"] = {}
                    summary["relation_summary"]["relations"][edge.relation]["start"]["pos"] = {}
                    summary["relation_summary"]["relations"][edge.relation]["start"]["pos"]["n"] = 0
                    summary["relation_summary"]["relations"][edge.relation]["start"]["pos"]["a"] = 0
                    summary["relation_summary"]["relations"][edge.relation]["start"]["pos"]["r"] = 0
                    summary["relation_summary"]["relations"][edge.relation]["start"]["pos"]["v"] = 0
                    summary["relation_summary"]["relations"][edge.relation]["start"]["total"] = 0
                    summary["relation_summary"]["relations"][edge.relation]["end"] = {}
                    summary["relation_summary"]["relations"][edge.relation]["end"]["pos"] = {}
                    summary["relation_summary"]["relations"][edge.relation]["end"]["pos"]["v"] = 0
                    summary["relation_summary"]["relations"][edge.relation]["end"]["pos"]["r"] = 0
                    summary["relation_summary"]["relations"][edge.relation]["end"]["pos"]["a"] = 0
                    summary["relation_summary"]["relations"][edge.relation]["end"]["pos"]["n"] = 0
                    summary["relation_summary"]["relations"][edge.relation]["end"]["total"] = 0
                    summary["relation_summary"]["relations"][edge.relation]["count"] = 0
                summary["relation_summary"]["relations"][edge.relation]["count"] += 1
                for node in edge.nodes:
                    if node.id not in seen_nodes:
                        summary["total_nodes"] += 1
                        if node.pos is not None:
                            summary["pos_summary"]["pos"][node.pos] += 1
                            summary["pos_summary"]["total"] += 1
                        seen_nodes.append(node.id)
                    if node.pos is not None:
                        summary["relation_summary"]["relations"][edge.relation][node.side]["pos"][node.pos] += 1
                        summary["relation_summary"]["relations"][edge.relation][node.side]["total"] += 1
    summary["pos_summary"]["percentage"] = summary["pos_summary"]["total"] / summary["total_nodes"]
    with open("data/pos_summary.json", "w") as file:
        json.dump(summary, file)


if __name__ == '__main__':
    conceptnet_pos_summary()
