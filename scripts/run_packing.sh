#!/bin/bash

# BoPax Packing Pipeline
# Runs the complete packing solution workflow

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "================================="
echo "BoPax Packing Pipeline"
echo "================================="
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found. Please install Python 3."
    exit 1
fi

# Check for data files
BOXES_FILE="${PROJECT_DIR}/examples/sample_boxes.csv"
CONTAINERS_FILE="${PROJECT_DIR}/examples/sample_containers.csv"

if [ ! -f "$BOXES_FILE" ]; then
    echo "Error: $BOXES_FILE not found"
    exit 1
fi

if [ ! -f "$CONTAINERS_FILE" ]; then
    echo "Error: $CONTAINERS_FILE not found"
    exit 1
fi

cd "$PROJECT_DIR"

# Step 1: Run the packing algorithm
echo "Step 1: Running packing algorithm..."
echo "-------------------------------------"
python3 -c "
import json
from bopax import load_boxes_from_csv, load_containers_from_csv, HybridPacker

boxes = load_boxes_from_csv('examples/sample_boxes.csv')
containers = load_containers_from_csv('examples/sample_containers.csv')

print(f'Loaded {len(boxes)} boxes')
print(f'Available {len(containers)} container types')

packer = HybridPacker(boxes, containers)
result = packer.pack()

if result:
    with open('packing_result.json', 'w') as f:
        json.dump(result, f, indent=2)
    print(f'\nSaved results to packing_result.json')
else:
    print('Failed to find solution')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "Error: Packing algorithm failed"
    exit 1
fi
echo ""

# Step 2: Validate the solution
echo "Step 2: Validating packing solution..."
echo "---------------------------------------"
python3 -c "
from bopax import validate_solution
validate_solution('packing_result.json', 'examples/sample_boxes.csv', 'examples/sample_containers.csv')
"

if [ $? -ne 0 ]; then
    echo "Error: Validation failed"
    exit 1
fi
echo ""

# Step 3: Generate visualizations
echo "Step 3: Generating visualizations..."
echo "------------------------------------"
python3 -c "
from bopax import visualize_packing
visualize_packing('packing_result.json')
"

if [ $? -ne 0 ]; then
    echo "Error: Visualization failed"
    exit 1
fi
echo ""

echo "================================="
echo "Pipeline completed successfully!"
echo "================================="
echo ""
echo "Generated files:"
echo "  - packing_result.json (detailed packing configuration)"
echo "  - packing_summary.png (summary statistics)"
echo "  - container_XX_viewX.png (3D visualization for each container)"
echo ""
