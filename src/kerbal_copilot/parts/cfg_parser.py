from dataclasses import dataclass, field

@dataclass
class Node:
    name: str
    values: list[tuple[str, str]] = field(default_factory=list)
    nodes: list["Node"] = field(default_factory=list)

    def get(self, key, default=None):
        return next((v for k, v in self.values if k == key), default)

    def get_all(self, key):
        return [v for k, v in self.values if k == key]

    def children(self, name):
        return [n for n in self.nodes if n.name == name]

def parse(text:str) -> Node:
    root, pending = Node("root"), None
    stack = [root]
    for raw in text.splitlines():
        line = raw.split("//", 1)[0].strip()
        while line:
            if line[0] == "{":
                node = Node(pending or "")
                stack[-1].nodes.append(node)
                stack.append(node)
                pending, line = None, line[1:].strip()
            elif line[0] == "}":
                if len(stack) > 1:
                    stack.pop()
                pending, line = None, line[1:].strip()
            elif "=" in line.split("{")[0].split("}")[0]:
                key, _, rest = line.partition("=")
                val, brace, tail = rest.partition("}")
                stack[-1].values.append((key.strip(), val.strip()))
                line = (brace + tail).strip()
            else:
                word, brace, tail = line.partition("{")
                pending, line = word.strip(), (brace + tail).strip()
    return root

def parse_file(path) -> Node:
    with open(path, encoding="utf-8-sig", errors="replace") as fh:
        return parse(fh.read())