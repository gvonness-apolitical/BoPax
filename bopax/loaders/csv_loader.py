"""CSV data loaders for BoPax."""
import csv
import math
from typing import List, Tuple, Optional

from ..models import Box


def load_boxes_from_csv(
    filename: str,
    exclude_labels: Optional[List[str]] = None
) -> List[Box]:
    """Load boxes to pack from a CSV file.

    Expected CSV format:
        Box Label,Count,Dim 1 (mm),Dim 2.  (mm),Dim 3 (mm)

    Args:
        filename: Path to the CSV file
        exclude_labels: Optional list of box labels to skip

    Returns:
        List of Box objects
    """
    boxes = []
    box_id = 1
    exclude_labels = exclude_labels or []

    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            label = row['Box Label']

            if label in exclude_labels:
                continue

            count = int(row['Count'])
            dim1 = math.ceil(float(row['Dim 1 (mm)']))
            dim2 = math.ceil(float(row['Dim 2.  (mm)']))
            dim3 = math.ceil(float(row['Dim 3 (mm)']))

            for _ in range(count):
                boxes.append(Box(label, (dim1, dim2, dim3), box_id))
                box_id += 1

    return boxes


def load_containers_from_csv(
    filename: str
) -> List[Tuple[str, Tuple[int, int, int]]]:
    """Load container types from a CSV file.

    Expected CSV format:
        Box Label,Dim 1 (mm),Dim 2.  (mm),Dim 3 (mm)

    Args:
        filename: Path to the CSV file

    Returns:
        List of tuples (label, (width, depth, height))
    """
    containers = []

    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            label = row['Box Label']
            dims = (
                int(row['Dim 1 (mm)']),
                int(row['Dim 2.  (mm)']),
                int(row['Dim 3 (mm)'])
            )
            containers.append((label, dims))

    return containers
