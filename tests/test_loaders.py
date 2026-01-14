"""Tests for BoPax data loaders."""
import os
import tempfile
import pytest
from bopax.loaders import load_boxes_from_csv, load_containers_from_csv


class TestLoadBoxesFromCSV:
    """Tests for load_boxes_from_csv function."""

    def test_load_sample_boxes(self):
        """Test loading the sample boxes file."""
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        boxes_file = os.path.join(script_dir, 'examples', 'sample_boxes.csv')

        boxes = load_boxes_from_csv(boxes_file)
        assert len(boxes) > 0
        assert all(hasattr(box, 'label') for box in boxes)
        assert all(hasattr(box, 'dimensions') for box in boxes)

    def test_load_boxes_count(self):
        """Test that boxes are expanded by count."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Box Label,Count,Dim 1 (mm),Dim 2.  (mm),Dim 3 (mm)\n")
            f.write("Test Box,3,100,200,300\n")
            temp_file = f.name

        try:
            boxes = load_boxes_from_csv(temp_file)
            assert len(boxes) == 3
            assert all(box.label == "Test Box" for box in boxes)
        finally:
            os.unlink(temp_file)

    def test_load_boxes_unique_ids(self):
        """Test that each box gets a unique ID."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Box Label,Count,Dim 1 (mm),Dim 2.  (mm),Dim 3 (mm)\n")
            f.write("Box A,2,100,100,100\n")
            f.write("Box B,2,200,200,200\n")
            temp_file = f.name

        try:
            boxes = load_boxes_from_csv(temp_file)
            ids = [box.box_id for box in boxes]
            assert len(ids) == len(set(ids))  # All unique
            assert ids == [1, 2, 3, 4]
        finally:
            os.unlink(temp_file)

    def test_load_boxes_dimensions(self):
        """Test that dimensions are loaded correctly."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Box Label,Count,Dim 1 (mm),Dim 2.  (mm),Dim 3 (mm)\n")
            f.write("Test,1,100,200,300\n")
            temp_file = f.name

        try:
            boxes = load_boxes_from_csv(temp_file)
            assert len(boxes) == 1
            assert boxes[0].dimensions == (100, 200, 300)
        finally:
            os.unlink(temp_file)

    def test_load_boxes_float_dimensions(self):
        """Test that float dimensions are rounded up."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Box Label,Count,Dim 1 (mm),Dim 2.  (mm),Dim 3 (mm)\n")
            f.write("Test,1,100.5,200.1,300.9\n")
            temp_file = f.name

        try:
            boxes = load_boxes_from_csv(temp_file)
            assert boxes[0].dimensions == (101, 201, 301)
        finally:
            os.unlink(temp_file)

    def test_load_boxes_exclude_labels(self):
        """Test excluding specific box labels."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Box Label,Count,Dim 1 (mm),Dim 2.  (mm),Dim 3 (mm)\n")
            f.write("Include,2,100,100,100\n")
            f.write("Exclude,3,200,200,200\n")
            temp_file = f.name

        try:
            boxes = load_boxes_from_csv(temp_file, exclude_labels=["Exclude"])
            assert len(boxes) == 2
            assert all(box.label == "Include" for box in boxes)
        finally:
            os.unlink(temp_file)

    def test_load_boxes_zero_count(self):
        """Test that boxes with count 0 are not loaded."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Box Label,Count,Dim 1 (mm),Dim 2.  (mm),Dim 3 (mm)\n")
            f.write("Zero,0,100,100,100\n")
            f.write("One,1,200,200,200\n")
            temp_file = f.name

        try:
            boxes = load_boxes_from_csv(temp_file)
            assert len(boxes) == 1
            assert boxes[0].label == "One"
        finally:
            os.unlink(temp_file)

    def test_load_boxes_file_not_found(self):
        """Test that FileNotFoundError is raised for missing file."""
        with pytest.raises(FileNotFoundError):
            load_boxes_from_csv("nonexistent_file.csv")


class TestLoadContainersFromCSV:
    """Tests for load_containers_from_csv function."""

    def test_load_sample_containers(self):
        """Test loading the sample containers file."""
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        containers_file = os.path.join(script_dir, 'examples', 'sample_containers.csv')

        containers = load_containers_from_csv(containers_file)
        assert len(containers) > 0
        assert all(isinstance(c, tuple) for c in containers)
        assert all(len(c) == 2 for c in containers)

    def test_load_containers_format(self):
        """Test container tuple format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Box Label,Dim 1 (mm),Dim 2.  (mm),Dim 3 (mm)\n")
            f.write("Small,100,200,300\n")
            f.write("Large,400,500,600\n")
            temp_file = f.name

        try:
            containers = load_containers_from_csv(temp_file)
            assert len(containers) == 2
            assert containers[0] == ("Small", (100, 200, 300))
            assert containers[1] == ("Large", (400, 500, 600))
        finally:
            os.unlink(temp_file)

    def test_load_containers_dimensions(self):
        """Test that container dimensions are loaded correctly."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Box Label,Dim 1 (mm),Dim 2.  (mm),Dim 3 (mm)\n")
            f.write("Test Container,300,400,500\n")
            temp_file = f.name

        try:
            containers = load_containers_from_csv(temp_file)
            label, dims = containers[0]
            assert label == "Test Container"
            assert dims == (300, 400, 500)
        finally:
            os.unlink(temp_file)

    def test_load_containers_empty_file(self):
        """Test loading empty CSV (header only)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Box Label,Dim 1 (mm),Dim 2.  (mm),Dim 3 (mm)\n")
            temp_file = f.name

        try:
            containers = load_containers_from_csv(temp_file)
            assert len(containers) == 0
        finally:
            os.unlink(temp_file)

    def test_load_containers_file_not_found(self):
        """Test that FileNotFoundError is raised for missing file."""
        with pytest.raises(FileNotFoundError):
            load_containers_from_csv("nonexistent_file.csv")
