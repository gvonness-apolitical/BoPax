"""Tests for BoPax model classes."""
import pytest
from bopax.models import Box, PlacedBox, FreeSpace, PackingContainer


class TestBox:
    """Tests for the Box class."""

    def test_box_creation(self):
        """Test basic box creation."""
        box = Box("Test Box", (100, 200, 300), box_id=1)
        assert box.label == "Test Box"
        assert box.dimensions == (100, 200, 300)
        assert box.box_id == 1

    def test_box_volume(self):
        """Test volume calculation."""
        box = Box("Test", (10, 20, 30))
        assert box.volume() == 6000

    def test_box_volume_cube(self):
        """Test volume for a cube."""
        box = Box("Cube", (100, 100, 100))
        assert box.volume() == 1000000

    def test_box_rotations_unique(self):
        """Test that rotations returns unique orientations."""
        box = Box("Test", (100, 200, 300))
        rotations = box.get_rotations()
        assert len(rotations) == 6
        assert len(set(rotations)) == 6  # All unique

    def test_box_rotations_cube(self):
        """Test that cube has only 1 unique rotation."""
        box = Box("Cube", (100, 100, 100))
        rotations = box.get_rotations()
        assert len(rotations) == 1
        assert rotations[0] == (100, 100, 100)

    def test_box_rotations_square_prism(self):
        """Test that square prism has 3 unique rotations."""
        box = Box("Square Prism", (100, 100, 200))
        rotations = box.get_rotations()
        assert len(rotations) == 3

    def test_box_default_id(self):
        """Test default box_id is 0."""
        box = Box("Test", (10, 20, 30))
        assert box.box_id == 0


class TestPlacedBox:
    """Tests for the PlacedBox class."""

    def test_placed_box_creation(self):
        """Test basic PlacedBox creation."""
        box = Box("Test", (100, 200, 300), box_id=1)
        placed = PlacedBox(box, (0, 0, 0), (100, 200, 300))
        assert placed.box == box
        assert placed.position == (0, 0, 0)
        assert placed.dimensions == (100, 200, 300)

    def test_get_bounds(self):
        """Test bounds calculation."""
        box = Box("Test", (100, 200, 300))
        placed = PlacedBox(box, (10, 20, 30), (100, 200, 300))
        bounds = placed.get_bounds()
        assert bounds == ((10, 110), (20, 220), (30, 330))

    def test_get_bounds_at_origin(self):
        """Test bounds at origin."""
        box = Box("Test", (100, 200, 300))
        placed = PlacedBox(box, (0, 0, 0), (100, 200, 300))
        bounds = placed.get_bounds()
        assert bounds == ((0, 100), (0, 200), (0, 300))

    def test_overlaps_true(self):
        """Test overlap detection when boxes overlap."""
        box1 = Box("Box1", (100, 100, 100))
        box2 = Box("Box2", (100, 100, 100))
        placed1 = PlacedBox(box1, (0, 0, 0), (100, 100, 100))
        placed2 = PlacedBox(box2, (50, 50, 50), (100, 100, 100))
        assert placed1.overlaps(placed2)
        assert placed2.overlaps(placed1)

    def test_overlaps_false_adjacent(self):
        """Test no overlap when boxes are adjacent."""
        box1 = Box("Box1", (100, 100, 100))
        box2 = Box("Box2", (100, 100, 100))
        placed1 = PlacedBox(box1, (0, 0, 0), (100, 100, 100))
        placed2 = PlacedBox(box2, (100, 0, 0), (100, 100, 100))
        assert not placed1.overlaps(placed2)
        assert not placed2.overlaps(placed1)

    def test_overlaps_false_separated(self):
        """Test no overlap when boxes are separated."""
        box1 = Box("Box1", (100, 100, 100))
        box2 = Box("Box2", (100, 100, 100))
        placed1 = PlacedBox(box1, (0, 0, 0), (100, 100, 100))
        placed2 = PlacedBox(box2, (200, 200, 200), (100, 100, 100))
        assert not placed1.overlaps(placed2)

    def test_overlaps_same_position(self):
        """Test overlap when boxes are at same position."""
        box1 = Box("Box1", (100, 100, 100))
        box2 = Box("Box2", (50, 50, 50))
        placed1 = PlacedBox(box1, (0, 0, 0), (100, 100, 100))
        placed2 = PlacedBox(box2, (0, 0, 0), (50, 50, 50))
        assert placed1.overlaps(placed2)


class TestFreeSpace:
    """Tests for the FreeSpace class."""

    def test_free_space_creation(self):
        """Test basic FreeSpace creation."""
        space = FreeSpace((0, 0, 0), (100, 200, 300))
        assert space.position == (0, 0, 0)
        assert space.dimensions == (100, 200, 300)

    def test_volume(self):
        """Test volume calculation."""
        space = FreeSpace((0, 0, 0), (10, 20, 30))
        assert space.volume() == 6000

    def test_can_fit_exact(self):
        """Test can_fit with exact dimensions."""
        space = FreeSpace((0, 0, 0), (100, 100, 100))
        assert space.can_fit((100, 100, 100))

    def test_can_fit_smaller(self):
        """Test can_fit with smaller box."""
        space = FreeSpace((0, 0, 0), (100, 100, 100))
        assert space.can_fit((50, 50, 50))

    def test_can_fit_too_large(self):
        """Test can_fit with box too large."""
        space = FreeSpace((0, 0, 0), (100, 100, 100))
        assert not space.can_fit((150, 100, 100))
        assert not space.can_fit((100, 150, 100))
        assert not space.can_fit((100, 100, 150))

    def test_can_fit_one_dimension_too_large(self):
        """Test can_fit when only one dimension is too large."""
        space = FreeSpace((0, 0, 0), (100, 200, 300))
        assert not space.can_fit((101, 100, 100))


class TestPackingContainer:
    """Tests for the PackingContainer class."""

    def test_container_creation(self):
        """Test basic container creation."""
        container = PackingContainer("Test", (300, 300, 300))
        assert container.label == "Test"
        assert container.dimensions == (300, 300, 300)
        assert len(container.placed_boxes) == 0

    def test_initial_free_space(self):
        """Test that container starts with full free space."""
        container = PackingContainer("Test", (300, 300, 300))
        assert len(container.free_spaces) == 1
        assert container.free_spaces[0].position == (0, 0, 0)
        assert container.free_spaces[0].dimensions == (300, 300, 300)

    def test_volume(self):
        """Test container volume calculation."""
        container = PackingContainer("Test", (100, 200, 300))
        assert container.volume() == 6000000

    def test_used_volume_empty(self):
        """Test used volume when empty."""
        container = PackingContainer("Test", (300, 300, 300))
        assert container.used_volume() == 0

    def test_utilization_empty(self):
        """Test utilization when empty."""
        container = PackingContainer("Test", (300, 300, 300))
        assert container.utilization() == 0.0

    def test_can_place_box_valid(self):
        """Test can_place_box with valid placement."""
        container = PackingContainer("Test", (300, 300, 300))
        assert container.can_place_box((100, 100, 100), (0, 0, 0))

    def test_can_place_box_outside_bounds(self):
        """Test can_place_box when box extends outside."""
        container = PackingContainer("Test", (300, 300, 300))
        assert not container.can_place_box((100, 100, 100), (250, 0, 0))

    def test_can_place_box_negative_position(self):
        """Test can_place_box with negative position."""
        container = PackingContainer("Test", (300, 300, 300))
        assert not container.can_place_box((100, 100, 100), (-10, 0, 0))

    def test_place_box_success(self):
        """Test successful box placement."""
        container = PackingContainer("Test", (300, 300, 300))
        box = Box("Box1", (100, 100, 100), box_id=1)
        result = container.place_box(box, (0, 0, 0), (100, 100, 100))
        assert result is True
        assert len(container.placed_boxes) == 1
        assert container.placed_boxes[0].box == box

    def test_place_box_failure(self):
        """Test failed box placement (outside bounds)."""
        container = PackingContainer("Test", (300, 300, 300))
        box = Box("Box1", (100, 100, 100), box_id=1)
        result = container.place_box(box, (250, 250, 250), (100, 100, 100))
        assert result is False
        assert len(container.placed_boxes) == 0

    def test_used_volume_after_placement(self):
        """Test used volume after placing a box."""
        container = PackingContainer("Test", (300, 300, 300))
        box = Box("Box1", (100, 100, 100), box_id=1)
        container.place_box(box, (0, 0, 0), (100, 100, 100))
        assert container.used_volume() == 1000000

    def test_utilization_after_placement(self):
        """Test utilization after placing a box."""
        container = PackingContainer("Test", (100, 100, 100))
        box = Box("Box1", (50, 50, 50), box_id=1)
        container.place_box(box, (0, 0, 0), (50, 50, 50))
        assert container.utilization() == 0.125  # 125000 / 1000000

    def test_place_multiple_boxes(self):
        """Test placing multiple boxes."""
        container = PackingContainer("Test", (300, 300, 300))
        box1 = Box("Box1", (100, 100, 100), box_id=1)
        box2 = Box("Box2", (100, 100, 100), box_id=2)

        container.place_box(box1, (0, 0, 0), (100, 100, 100))
        container.place_box(box2, (100, 0, 0), (100, 100, 100))

        assert len(container.placed_boxes) == 2
        assert container.used_volume() == 2000000

    def test_place_box_overlap_prevention(self):
        """Test that overlapping placements are prevented."""
        container = PackingContainer("Test", (300, 300, 300))
        box1 = Box("Box1", (100, 100, 100), box_id=1)
        box2 = Box("Box2", (100, 100, 100), box_id=2)

        container.place_box(box1, (0, 0, 0), (100, 100, 100))
        result = container.place_box(box2, (50, 50, 50), (100, 100, 100))

        assert result is False
        assert len(container.placed_boxes) == 1

    def test_remove_last(self):
        """Test removing last placed box."""
        container = PackingContainer("Test", (300, 300, 300))
        box = Box("Box1", (100, 100, 100), box_id=1)
        container.place_box(box, (0, 0, 0), (100, 100, 100))
        assert len(container.placed_boxes) == 1

        container.remove_last()
        assert len(container.placed_boxes) == 0

    def test_remove_last_empty(self):
        """Test remove_last on empty container doesn't crash."""
        container = PackingContainer("Test", (300, 300, 300))
        container.remove_last()  # Should not raise
        assert len(container.placed_boxes) == 0
