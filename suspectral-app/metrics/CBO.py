import ast
import sys
from pathlib import Path


class CBOVisitor(ast.NodeVisitor):
    def __init__(self, module_name: str):
        self._module_name = module_name
        self._current_class: str | None = None
        self._dependencies: set[str] = set()
        self.data_: dict[str, set[str]] = {}

    def visit_ClassDef(self, node):
        class_name = f"{self._module_name}.{node.name}"
        self._current_class = class_name
        self._dependencies = set()

        for base in node.bases:
            if isinstance(base, ast.Name):
                self._dependencies.add(base.id)
            elif isinstance(base, ast.Attribute):
                self._dependencies.add(self._attr_to_str(base))

        self.generic_visit(node)

        self.data_[class_name] = self._dependencies.copy()
        self._current_class = None
        self._dependencies = set()

    def visit_AnnAssign(self, node):
        if self._current_class:
            ann = node.annotation
            if isinstance(ann, ast.Name):
                self._dependencies.add(ann.id)
            elif isinstance(ann, ast.Attribute):
                self._dependencies.add(self._attr_to_str(ann))
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        if self._current_class:
            for arg in node.args.args:
                if ann := arg.annotation:
                    if isinstance(ann, ast.Name):
                        self._dependencies.add(ann.id)
                    elif isinstance(ann, ast.Attribute):
                        self._dependencies.add(self._attr_to_str(ann))

            if ret := node.returns:
                if isinstance(ret, ast.Name):
                    self._dependencies.add(ret.id)
                elif isinstance(ret, ast.Attribute):
                    self._dependencies.add(self._attr_to_str(ret))

        self.generic_visit(node)

    def visit_Call(self, node):
        if self._current_class:
            func = node.func
            if isinstance(func, ast.Name):
                if self._is_constructor(func.id):
                    self._dependencies.add(func.id)
            elif isinstance(func, ast.Attribute):
                name = self._get_first_attr_after_self(func)
                if self._is_constructor(name):
                    self._dependencies.add(name)
        self.generic_visit(node)

    def _attr_to_str(self, node) -> str:
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return self._attr_to_str(node.value) + "." + node.attr
        return ""

    @staticmethod
    def _is_constructor(name: str | None) -> bool:
        return bool(name and name[0].isupper())

    @staticmethod
    def _get_first_attr_after_self(node) -> str | None:
        if isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name) and node.value.id == "self":
                return node.attr
            else:
                return CBOVisitor._get_first_attr_after_self(node.value)
        elif isinstance(node, ast.Name):
            return node.id

        return None


def analyze_file(filepath: Path, module_name: str):
    with filepath.open("r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=str(filepath))

    visitor = CBOVisitor(module_name)
    visitor.visit(tree)

    builtin_ignore = {
        "int", "str", "float", "bool", "list", "dict",
        "set", "tuple", "self", ".__init__", "super",
    }

    results = []
    for class_name, deps in visitor.data_.items():
        filtered = {d for d in deps if d not in builtin_ignore}
        results.append((class_name, filtered))

    return results


def analyze_package(base_path: Path, base_package: str):
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

    results = analyze_package(base_path, base_package)
    results_str = [(class_name, str(len(deps))) for class_name, deps in results]

    header = ("Class", "CBO")
    widths = [max(len(row[i]) for row in [header] + results_str) for i in range(2)]

    print(f"{header[0]:<{widths[0]}} {header[1]:>{widths[1]}}")
    print("-" * (sum(widths) + 1))
    for class_name, metric in results_str:
        print(f"{class_name:<{widths[0]}} {metric:>{widths[1]}}")


if __name__ == "__main__":
    main()
