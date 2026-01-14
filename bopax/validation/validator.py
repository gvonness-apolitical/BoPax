"""Validation for packing solutions."""
import json
import csv
import math
from typing import Dict, Tuple


def load_original_boxes(filename: str) -> Dict[str, Dict]:
    """Load original box data from CSV."""
    boxes_by_label = {}

    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            label = row['Box Label']
            count = int(row['Count'])
            dim1 = math.ceil(float(row['Dim 1 (mm)']))
            dim2 = math.ceil(float(row['Dim 2.  (mm)']))
            dim3 = math.ceil(float(row['Dim 3 (mm)']))

            boxes_by_label[label] = {
                'count': count,
                'dimensions': (dim1, dim2, dim3),
                'volume': dim1 * dim2 * dim3
            }

    return boxes_by_label


def check_box_overlap(box1: Dict, box2: Dict) -> bool:
    """Check if two placed boxes overlap."""
    x1, y1, z1 = box1['position']
    w1, d1, h1 = box1['placed_dimensions']

    x2, y2, z2 = box2['position']
    w2, d2, h2 = box2['placed_dimensions']

    x_overlap = x1 < x2 + w2 and x1 + w1 > x2
    y_overlap = y1 < y2 + d2 and y1 + d1 > y2
    z_overlap = z1 < z2 + h2 and z1 + h1 > z2

    return x_overlap and y_overlap and z_overlap


def is_valid_rotation(original_dims: Tuple[int, int, int],
                      placed_dims: Tuple[int, int, int]) -> bool:
    """Check if placed dimensions are a valid rotation of original dimensions."""
    orig_sorted = tuple(sorted(original_dims))
    placed_sorted = tuple(sorted(placed_dims))
    return orig_sorted == placed_sorted


def validate_solution(json_file: str, boxes_csv: str, containers_csv: str) -> bool:
    """Validate the packing solution.

    Args:
        json_file: Path to packing result JSON
        boxes_csv: Path to boxes CSV file
        containers_csv: Path to containers CSV file

    Returns:
        True if solution is valid, False otherwise
    """
    print("="*60)
    print("VALIDATING PACKING SOLUTION")
    print("="*60)

    # Load data
    print("\n1. Loading data...")
    with open(json_file, 'r') as f:
        result = json.load(f)

    original_boxes = load_original_boxes(boxes_csv)

    with open(containers_csv, 'r') as f:
        reader = csv.DictReader(f)
        container_types = {
            row['Box Label']: (
                int(row['Dim 1 (mm)']),
                int(row['Dim 2.  (mm)']),
                int(row['Dim 3 (mm)'])
            )
            for row in reader
        }

    print(f"   Loaded {len(original_boxes)} box types")
    print(f"   Loaded {len(container_types)} container types")
    print(f"   Loaded solution with {result['total_containers']} containers")

    all_valid = True
    total_boxes_in_solution = 0
    boxes_in_solution = {}

    print("\n2. Checking each container...")
    for i, container in enumerate(result['containers'], 1):
        print(f"\n   Container #{i}: {container['type']}")
        container_valid = True

        if container['type'] not in container_types:
            print(f"      ERROR: Unknown container type '{container['type']}'")
            all_valid = False
            container_valid = False
            continue

        container_dims = container_types[container['type']]

        if tuple(container['dimensions']) != container_dims:
            print(f"      ERROR: Container dimensions mismatch")
            print(f"         Expected: {container_dims}")
            print(f"         Got: {container['dimensions']}")
            all_valid = False
            container_valid = False

        boxes_in_container = container['boxes']
        total_boxes_in_solution += len(boxes_in_container)

        for j, box in enumerate(boxes_in_container):
            label = box['label']
            if label not in boxes_in_solution:
                boxes_in_solution[label] = 0
            boxes_in_solution[label] += 1

            if label not in original_boxes:
                print(f"      ERROR: Box #{j+1} has unknown label '{label}'")
                all_valid = False
                container_valid = False
                continue

            orig_dims = original_boxes[label]['dimensions']

            if not is_valid_rotation(orig_dims, tuple(box['placed_dimensions'])):
                print(f"      ERROR: Box #{j+1} ({label}) has invalid rotation")
                print(f"         Original: {orig_dims}")
                print(f"         Placed: {box['placed_dimensions']}")
                all_valid = False
                container_valid = False

            x, y, z = box['position']
            w, d, h = box['placed_dimensions']

            if (x < 0 or y < 0 or z < 0 or
                x + w > container_dims[0] or
                y + d > container_dims[1] or
                z + h > container_dims[2]):
                print(f"      ERROR: Box #{j+1} ({label}) extends outside container")
                all_valid = False
                container_valid = False

            expected_volume = orig_dims[0] * orig_dims[1] * orig_dims[2]
            if box['volume'] != expected_volume:
                print(f"      ERROR: Box #{j+1} ({label}) has incorrect volume")
                all_valid = False
                container_valid = False

        # Check for overlaps
        print(f"      Checking for overlaps among {len(boxes_in_container)} boxes...")
        overlaps_found = False

        for j in range(len(boxes_in_container)):
            for k in range(j + 1, len(boxes_in_container)):
                if check_box_overlap(boxes_in_container[j], boxes_in_container[k]):
                    print(f"      ERROR: Overlap between boxes #{j+1} and #{k+1}")
                    all_valid = False
                    container_valid = False
                    overlaps_found = True

        if not overlaps_found:
            print(f"      No overlaps detected")

        calculated_used_volume = sum(b['volume'] for b in boxes_in_container)
        if calculated_used_volume != container['used_volume']:
            print(f"      ERROR: Used volume mismatch")
            all_valid = False
            container_valid = False

        if container_valid:
            print(f"      Container #{i} is valid ({len(boxes_in_container)} boxes, "
                  f"{container['utilization']:.1%} utilized)")

    # Check if all original boxes are packed
    print("\n3. Checking if all boxes are packed...")
    all_boxes_packed = True

    for label, data in original_boxes.items():
        expected_count = data['count']
        actual_count = boxes_in_solution.get(label, 0)

        if actual_count < expected_count:
            print(f"   ERROR: Missing boxes for '{label}'")
            print(f"      Expected: {expected_count}, Found: {actual_count}")
            all_valid = False
            all_boxes_packed = False
        elif actual_count > expected_count:
            print(f"   ERROR: Too many boxes for '{label}'")
            print(f"      Expected: {expected_count}, Found: {actual_count}")
            all_valid = False
            all_boxes_packed = False
        else:
            print(f"   '{label}': {actual_count}/{expected_count} boxes")

    total_expected = sum(data['count'] for data in original_boxes.values())
    print(f"\n   Total boxes: {total_boxes_in_solution}/{total_expected}")

    if all_boxes_packed:
        print("   All boxes accounted for")

    # Validate summary statistics
    print("\n4. Validating summary statistics...")

    calculated_total_volume = sum(c['used_volume'] for c in result['containers'])
    if calculated_total_volume != result['total_volume_used']:
        print(f"   ERROR: Total volume used mismatch")
        all_valid = False
    else:
        print(f"   Total volume used: {result['total_volume_used']:,} mm3")

    calculated_total_available = sum(c['volume'] for c in result['containers'])
    if calculated_total_available != result['total_volume_available']:
        print(f"   ERROR: Total volume available mismatch")
        all_valid = False
    else:
        print(f"   Total volume available: {result['total_volume_available']:,} mm3")

    expected_utilization = (calculated_total_volume / calculated_total_available
                           if calculated_total_available > 0 else 0)
    if abs(expected_utilization - result['overall_utilization']) > 0.0001:
        print(f"   ERROR: Overall utilization mismatch")
        all_valid = False
    else:
        print(f"   Overall utilization: {result['overall_utilization']:.1%}")

    # Final verdict
    print("\n" + "="*60)
    if all_valid:
        print("VALIDATION PASSED - Solution is valid!")
    else:
        print("VALIDATION FAILED - Errors found in solution")
    print("="*60)

    return all_valid
