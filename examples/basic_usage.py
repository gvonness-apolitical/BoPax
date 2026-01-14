#!/usr/bin/env python3
"""Basic usage example for BoPax.

This example demonstrates the simplest way to use BoPax to pack boxes
into containers using the greedy algorithm.
"""
import json
import os
import sys

# Add parent directory to path for running without installation
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bopax import (
    load_boxes_from_csv,
    load_containers_from_csv,
    GreedyPacker
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
    print(f"Available {len(containers)} container types")
    print(f"Total volume: {sum(b.volume() for b in boxes):,} mm3\n")

    # Run packing algorithm
    packer = GreedyPacker(boxes, containers)
    result = packer.pack()

    # Print summary
    if result:
        print("\n" + "="*60)
        print("PACKING RESULT")
        print("="*60)
        print(f"\nContainers used: {result['total_containers']}")
        print(f"Overall utilization: {result['overall_utilization']:.1%}")

        print("\nContainer breakdown:")
        for ctype, count in result['container_counts'].items():
            print(f"  - {ctype}: {count}")

        # Save result
        output_file = os.path.join(script_dir, 'packing_result.json')
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\nResults saved to {output_file}")
    else:
        print("Failed to find a packing solution!")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
