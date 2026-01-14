"""BoPax - 3D Bin Packing Optimization Library.

A Python library for solving the 3D bin packing problem using
multiple algorithmic approaches including exhaustive search,
greedy heuristics, and hybrid methods.

Example:
    >>> from bopax import Box, GreedyPacker, load_boxes_from_csv, load_containers_from_csv
    >>>
    >>> boxes = load_boxes_from_csv('boxes.csv')
    >>> containers = load_containers_from_csv('containers.csv')
    >>>
    >>> packer = GreedyPacker(boxes, containers)
    >>> result = packer.pack()
    >>> print(f"Used {result['total_containers']} containers")
"""

__version__ = "1.0.0"

from .models import Box, PlacedBox, FreeSpace, PackingContainer
from .loaders import load_boxes_from_csv, load_containers_from_csv
from .algorithms import (
    BasePacker,
    ExhaustivePacker,
    HybridPacker,
    GreedyPacker,
    OptimalPacker
)
from .visualization import visualize_packing
from .validation import validate_solution

__all__ = [
    # Version
    '__version__',
    # Models
    'Box',
    'PlacedBox',
    'FreeSpace',
    'PackingContainer',
    # Loaders
    'load_boxes_from_csv',
    'load_containers_from_csv',
    # Algorithms
    'BasePacker',
    'ExhaustivePacker',
    'HybridPacker',
    'GreedyPacker',
    'OptimalPacker',
    # Visualization
    'visualize_packing',
    # Validation
    'validate_solution',
]
