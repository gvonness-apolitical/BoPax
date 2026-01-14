#!/usr/bin/env python3
"""Compare different packing algorithms.

This example runs multiple packing algorithms on the same data
and compares their results.
"""
import os
import sys
import time

# Add parent directory to path for running without installation
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bopax import (
    load_boxes_from_csv,
    load_containers_from_csv,
    GreedyPacker,
    OptimalPacker,
    HybridPacker
)


def main():
    # Get path to sample data
    script_dir = os.path.dirname(os.path.abspath(__file__))
    boxes_file = os.path.join(script_dir, 'sample_boxes.csv')
    containers_file = os.path.join(script_dir, 'sample_containers.csv')

    # Load data
    print("Loading data...")
    boxes = load_boxes_from_csv(boxes_file)
    containers = load_containers_from_csv(containers_file)

    print(f"Loaded {len(boxes)} boxes to pack")
    print(f"Available {len(containers)} container types\n")

    # Define algorithms to compare
    algorithms = [
        ("Greedy", GreedyPacker),
        ("Optimal", OptimalPacker),
        ("Hybrid", HybridPacker),
    ]

    results = []

    # Run each algorithm
    for name, packer_class in algorithms:
        print("="*60)
        print(f"Running {name} Algorithm")
        print("="*60 + "\n")

        start_time = time.time()
        packer = packer_class(boxes, containers)
        result = packer.pack()
        elapsed = time.time() - start_time

        if result:
            results.append({
                'name': name,
                'containers': result['total_containers'],
                'utilization': result['overall_utilization'],
                'time': elapsed
            })
            print(f"\nResult: {result['total_containers']} containers, "
                  f"{result['overall_utilization']:.1%} utilization")
        else:
            results.append({
                'name': name,
                'containers': None,
                'utilization': None,
                'time': elapsed
            })
            print("\nFailed to find a solution")

        print(f"Time: {elapsed:.2f} seconds\n")

    # Print comparison table
    print("\n" + "="*60)
    print("COMPARISON SUMMARY")
    print("="*60)
    print(f"\n{'Algorithm':<15} {'Containers':<12} {'Utilization':<15} {'Time (s)':<10}")
    print("-"*52)

    for r in results:
        containers = str(r['containers']) if r['containers'] else "N/A"
        utilization = f"{r['utilization']:.1%}" if r['utilization'] else "N/A"
        print(f"{r['name']:<15} {containers:<12} {utilization:<15} {r['time']:.2f}")

    # Find best algorithm
    valid_results = [r for r in results if r['containers'] is not None]
    if valid_results:
        best_by_containers = min(valid_results, key=lambda x: x['containers'])
        best_by_utilization = max(valid_results, key=lambda x: x['utilization'])

        print(f"\nBest by containers: {best_by_containers['name']} "
              f"({best_by_containers['containers']} containers)")
        print(f"Best by utilization: {best_by_utilization['name']} "
              f"({best_by_utilization['utilization']:.1%})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
