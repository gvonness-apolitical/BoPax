"""Pack a compact Packrift ecommerce carton fixture with BoPax.

Fixture source:
https://packrift.github.io/packaging-optimization-benchmark-corpus/cartonization-solver-fixtures.html
"""

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from bopax import HybridPacker, load_boxes_from_csv, load_containers_from_csv  # noqa: E402


def main():
    example_dir = Path(__file__).resolve().parent
    boxes = load_boxes_from_csv(example_dir / "packrift_boxes.csv")
    containers = load_containers_from_csv(example_dir / "packrift_containers.csv")

    result = HybridPacker(boxes, containers).pack()
    if result is None:
        raise RuntimeError("Packrift ecommerce fixture could not be packed")

    packed_boxes = sum(len(container["boxes"]) for container in result["containers"])
    print("Packrift ecommerce carton fixture")
    print(f"Packed boxes: {packed_boxes}/{len(boxes)}")
    print(f"Containers used: {result['total_containers']}")
    print(f"Overall utilization: {result['overall_utilization']:.1%}")
    print("Container counts:")
    for label, count in result["container_counts"].items():
        print(f"- {label}: {count}")


if __name__ == "__main__":
    main()
