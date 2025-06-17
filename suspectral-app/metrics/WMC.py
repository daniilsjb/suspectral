import ast
import sys
from pathlib import Path


def analyze_file(filepath: Path):
    with filepath.open("r", encoding="utf-8") as file:
        tree = ast.parse(file.read(), filename=str(filepath))

    results = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            metric = sum(isinstance(node, ast.FunctionDef) for node in node.body)
            results.append((node.name, metric))

    return results


def calculate(base_path: Path, base_package: str):
    results = []

    for path in base_path.rglob("*.py"):
        module_path = path.relative_to(base_path).with_suffix("")
        module_name = ".".join(module_path.parts)
        module_name = f"{base_package}.{module_name}"

        for class_name, metric in analyze_file(path):
            results.append((f"{module_name}.{class_name}", metric))

    return results


def main():
    root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(root))

    base_path = root / "suspectral"
    base_package = "suspectral"

    results = calculate(base_path, base_package)
    results = [(class_name, str(metric)) for class_name, metric in results]

    header = ("Class", "WMC")
    widths = [max(len(row[i]) for row in [header] + results) for i in range(2)]

    print(f"{header[0]:<{widths[0]}} {header[1]:>{widths[1]}}")
    print("-" * (sum(widths) + 1))
    for class_name, metric in results:
        print(f"{class_name:<{widths[0]}} {metric:>{widths[1]}}")


if __name__ == "__main__":
    main()
