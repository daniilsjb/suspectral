import ast
import sys
from pathlib import Path
from collections import defaultdict


class LCOM4Visitor(ast.NodeVisitor):
    def __init__(self, module_name: str):
        self._class_stack: list[str] = []
        self._module_name = module_name
        self.data_: dict[str, dict[str, set[str]]] = {}

    def visit_ClassDef(self, node):
        class_name = ".".join([self._module_name] + [c for c in self._class_stack] + [node.name])
        self._class_stack.append(node.name)
        self.data_[class_name] = {}

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                collector = InstanceVarCollector()
                collector.visit(item)
                self.data_[class_name][item.name] = collector.attributes

        self._class_stack.pop()


class InstanceVarCollector(ast.NodeVisitor):
    def __init__(self):
        self.attributes: set[str] = set()

    def visit_Attribute(self, node):
        if isinstance(node.value, ast.Name) and node.value.id == "self":
            self.attributes.add(node.attr)
        self.generic_visit(node)


def connected_components(graph: dict[str, set[str]]) -> int:
    visited = set()
    def dfs(node: str):
        stack = [node]
        while stack:
            current = stack.pop()
            if current not in visited:
                visited.add(current)
                stack.extend(graph[current] - visited)

    count = 0
    for node in graph:
        if node not in visited:
            count += 1
            dfs(node)

    return count


def analyze_file(filepath: Path, module_name: str):
    with filepath.open("r", encoding="utf-8") as file:
        tree = ast.parse(file.read(), filename=str(filepath))

    visitor = LCOM4Visitor(module_name)
    visitor.visit(tree)

    results = []
    for class_name, methods in visitor.data_.items():
        method_names = list(methods.keys())
        graph = defaultdict(set)

        for i in range(len(method_names)):
            for j in range(i + 1, len(method_names)):
                m1, m2 = method_names[i], method_names[j]
                if methods[m1] & methods[m2]:
                    graph[m1].add(m2)
                    graph[m2].add(m1)

        for m in method_names:
            if m not in graph:
                graph[m] = set()

        metric = connected_components(graph)
        results.append((class_name, metric))

    return results


def calculate(base_path: Path, base_package: str):
    results = []
    for path in base_path.rglob("*.py"):
        module_path = path.relative_to(base_path).with_suffix("")
        module_name = f"{base_package}." + ".".join(module_path.parts)
        results.extend(analyze_file(path, module_name))

    return results


def main():
    root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(root))

    base_path = root / "suspectral"
    base_package = "suspectral"

    results = calculate(base_path, base_package)
    results = [(class_name, str(metric)) for class_name, metric in results]

    header = ("Class", "LCOM4")
    widths = [max(len(row[i]) for row in [header] + results) for i in range(2)]

    print(f"{header[0]:<{widths[0]}} {header[1]:>{widths[1]}}")
    print("-" * (sum(widths) + 1))
    for class_name, metric in results:
        print(f"{class_name:<{widths[0]}} {metric:>{widths[1]}}")


if __name__ == "__main__":
    main()
