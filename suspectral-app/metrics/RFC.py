import ast
import sys
from pathlib import Path


class RFCVisitor(ast.NodeVisitor):
    def __init__(self, module_name: str):
        self._current_class: str | None = None
        self._module_name = module_name
        self.data_: dict[str, set[str]] = {}

    def visit_ClassDef(self, node):
        class_name = f"{self._module_name}.{node.name}"
        self._current_class = class_name
        self.data_[class_name] = set()

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                self.data_[class_name].add(item.name)
                self.visit(item)

    def visit_Call(self, node):
        if self._current_class:
            if isinstance(node.func, ast.Name):
                self.data_[self._current_class].add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                self.data_[self._current_class].add(self._attr_to_str(node.func))
        self.generic_visit(node)

    def _attr_to_str(self, node):
        if isinstance(node, ast.Attribute):
            return self._attr_to_str(node.value) + "." + node.attr
        elif isinstance(node, ast.Name):
            return node.id
        return ""


def analyze_file(filepath: Path, module_name: str):
    with filepath.open("r", encoding="utf-8") as file:
        tree = ast.parse(file.read(), filename=str(filepath))

    visitor = RFCVisitor(module_name)
    visitor.visit(tree)

    return [(class_name, len(uses)) for class_name, uses in visitor.data_.items()]


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

    header = ("Class", "RFC")
    widths = [max(len(row[i]) for row in [header] + results) for i in range(2)]

    print(f"{header[0]:<{widths[0]}} {header[1]:>{widths[1]}}")
    print("-" * (sum(widths) + 1))
    for class_name, metric in results:
        print(f"{class_name:<{widths[0]}} {metric:>{widths[1]}}")


if __name__ == "__main__":
    main()
