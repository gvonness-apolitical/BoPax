# BoPax - 3D Bin Packing Optimization

A Python library for solving the 3D bin packing problem - efficiently packing items into containers while minimizing wasted space.

## Features

- **Multiple Algorithms**: Choose from exhaustive search, greedy heuristics, optimal mix, or hybrid approaches
- **All Rotations**: Boxes can be placed in any of 6 possible orientations
- **3D Visualization**: Generate visual representations of packing solutions
- **Validation**: Verify solutions for correctness (no overlaps, all items packed)
- **Flexible Input**: Load data from CSV files or create boxes programmatically

## Installation

### From Source

```bash
git clone https://github.com/gvonness-apolitical/BoPax.git
cd BoPax
pip install -e .
```

### Dependencies

- Python 3.8+
- numpy >= 1.20.0
- matplotlib >= 3.3.0

## Quick Start

```python
from bopax import Box, GreedyPacker, load_boxes_from_csv, load_containers_from_csv

# Load data from CSV files
boxes = load_boxes_from_csv('examples/sample_boxes.csv')
containers = load_containers_from_csv('examples/sample_containers.csv')

# Run packing algorithm
packer = GreedyPacker(boxes, containers)
result = packer.pack()

# Print results
print(f"Containers used: {result['total_containers']}")
print(f"Utilization: {result['overall_utilization']:.1%}")
```

### Creating Boxes Programmatically

```python
from bopax import Box, PackingContainer, GreedyPacker

# Create boxes manually
boxes = [
    Box("Small", (100, 150, 200), box_id=1),
    Box("Small", (100, 150, 200), box_id=2),
    Box("Large", (200, 250, 300), box_id=3),
]

# Define container types
containers = [
    ("Small Container", (300, 300, 300)),
    ("Large Container", (500, 500, 500)),
]

# Pack
packer = GreedyPacker(boxes, containers)
result = packer.pack()
```

## Available Algorithms

| Algorithm | Class | Use Case | Complexity |
|-----------|-------|----------|------------|
| Exhaustive | `ExhaustivePacker` | Small datasets (<50 boxes), optimal solution required | O(n! * rotations) |
| Hybrid | `HybridPacker` | Medium datasets, good balance of quality and speed | O(n^2 * containers) |
| Greedy | `GreedyPacker` | Large datasets, fast results | O(n * spaces) |
| Optimal | `OptimalPacker` | Tries multiple strategies, picks best | O(strategies * n^2) |

### Algorithm Selection Guide

- **ExhaustivePacker**: Guarantees optimal solution but slow for large datasets
- **GreedyPacker**: Fast first-fit decreasing heuristic, good for initial estimates
- **OptimalPacker**: Compares multiple strategies (largest-first, smallest-first, best-fit, mixed)
- **HybridPacker**: Exhaustive per-container search with greedy selection - recommended for most cases

## CLI Usage

### Run the Complete Pipeline

```bash
chmod +x scripts/run_packing.sh
./scripts/run_packing.sh
```

### Run Examples

```bash
# Basic usage
python examples/basic_usage.py

# Compare algorithms
python examples/compare_algorithms.py
```

### Python Commands

```python
# Pack boxes
from bopax import load_boxes_from_csv, load_containers_from_csv, HybridPacker
boxes = load_boxes_from_csv('examples/sample_boxes.csv')
containers = load_containers_from_csv('examples/sample_containers.csv')
packer = HybridPacker(boxes, containers)
result = packer.pack()

# Validate solution
from bopax import validate_solution
validate_solution('packing_result.json', 'examples/sample_boxes.csv', 'examples/sample_containers.csv')

# Visualize
from bopax import visualize_packing
visualize_packing('packing_result.json')
```

## Data Format

### Items to Pack (CSV)

```csv
Box Label,Count,Dim 1 (mm),Dim 2.  (mm),Dim 3 (mm)
Small Product Box,5,100,150,200
Large Product Box,2,300,350,400
```

### Container Types (CSV)

```csv
Box Label,Dim 1 (mm),Dim 2.  (mm),Dim 3 (mm)
Small Container,300,300,300
Large Container,500,500,500
```

## Project Structure

```
BoPax/
├── bopax/
│   ├── __init__.py           # Package exports
│   ├── models/               # Data models (Box, Container, etc.)
│   ├── loaders/              # CSV data loading
│   ├── algorithms/           # Packing algorithms
│   ├── visualization/        # 3D rendering
│   └── validation/           # Solution verification
├── examples/
│   ├── sample_boxes.csv      # Sample items
│   ├── sample_containers.csv # Sample containers
│   ├── basic_usage.py        # Basic example
│   └── compare_algorithms.py # Algorithm comparison
├── scripts/
│   └── run_packing.sh        # Pipeline script
├── tests/                    # Test suite
├── setup.py
├── pyproject.toml
├── LICENSE
└── README.md
```

## API Reference

### Models

- `Box(label, dimensions, box_id)` - Item to be packed
- `PlacedBox(box, position, dimensions)` - Placed item with location
- `PackingContainer(label, dimensions)` - Container for packing
- `FreeSpace(position, dimensions)` - Available space in container

### Loaders

- `load_boxes_from_csv(filename, exclude_labels=None)` - Load items from CSV
- `load_containers_from_csv(filename)` - Load container types from CSV

### Algorithms

All packers inherit from `BasePacker` and implement:
- `packer.pack()` - Returns result dictionary or None

### Visualization

- `visualize_packing(json_file, save_images=True)` - Generate visualizations
- `plot_container(container_data, container_id)` - Plot single container
- `create_summary_plot(result)` - Create summary statistics plot

### Validation

- `validate_solution(json_file, boxes_csv, containers_csv)` - Validate solution

## Output Format

The packing result is a dictionary containing:

```python
{
    'containers': [...],           # List of container details
    'total_containers': 3,         # Number of containers used
    'container_counts': {...},     # Count by container type
    'total_volume_used': 12500000, # Volume of packed boxes (mm³)
    'total_volume_available': 15000000,  # Total container volume
    'overall_utilization': 0.833   # Ratio (0.0 to 1.0)
}
```

## Algorithm Details

### Space Management

Uses **guillotine splitting** for free space management:
- When a box is placed, intersecting free spaces are split into up to 6 new spaces
- Spaces are pruned to remove duplicates and enclosed spaces
- Boxes are placed in free spaces sorted by position (bottom-to-top, back-to-front)

### Box Sorting

Boxes are sorted by volume (largest first) before packing - this first-fit decreasing
approach generally produces better results than processing in arbitrary order.

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## License

MIT License - see [LICENSE](LICENSE) file for details.
