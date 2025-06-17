import sys
import inspect
import importlib
from pathlib import Path


def calculate(base_path: Path, base_package: str):
    results = []

    for path in base_path.rglob("*.py"):
        module_path = path.relative_to(base_path).with_suffix("")
        module_name = ".".join(module_path.parts)
        module_name = f"{base_package}.{module_name}"

        module = importlib.import_module(module_name)
        for class_name, class_obj in inspect.getmembers(module, inspect.isclass):
            if class_obj.__module__ == module.__name__:
                metric = len(class_obj.__mro__) - 1
                results.append((f"{module_name}.{class_name}", metric))

    return results


def main():
    root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(root))

    base_path = root / "suspectral"
    base_package = "suspectral"

    results = calculate(base_path, base_package)
    results = [(class_name, str(metric)) for class_name, metric in results]

    header = ("Class", "DIT")
    widths = [max(len(row[i]) for row in [header] + results) for i in range(2)]

    print(f"{header[0]:<{widths[0]}} {header[1]:>{widths[1]}}")
    print("-" * (sum(widths) + 1))
    for class_name, metric in results:
        print(f"{class_name:<{widths[0]}} {metric:>{widths[1]}}")


if __name__ == "__main__":
    main()
