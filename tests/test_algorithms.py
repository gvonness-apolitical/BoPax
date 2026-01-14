"""Tests for BoPax packing algorithms."""
import pytest
from bopax.models import Box
from bopax.algorithms import (
    BasePacker,
    ExhaustivePacker,
    GreedyPacker,
    OptimalPacker,
    HybridPacker
)


# Test fixtures
@pytest.fixture
def simple_boxes():
    """Create a simple set of boxes for testing."""
    return [
        Box("Small", (50, 50, 50), box_id=1),
        Box("Small", (50, 50, 50), box_id=2),
        Box("Medium", (100, 100, 100), box_id=3),
    ]


@pytest.fixture
def single_box():
    """Create a single box for testing."""
    return [Box("Test", (100, 100, 100), box_id=1)]


@pytest.fixture
def containers():
    """Create container types for testing."""
    return [
        ("Small", (150, 150, 150)),
        ("Medium", (300, 300, 300)),
        ("Large", (500, 500, 500)),
    ]


@pytest.fixture
def small_container():
    """Create a small container for tight packing tests."""
    return [("Small", (100, 100, 100))]


class TestGreedyPacker:
    """Tests for the GreedyPacker algorithm."""

    def test_pack_single_box(self, single_box, containers):
        """Test packing a single box."""
        packer = GreedyPacker(single_box, containers)
        result = packer.pack()

        assert result is not None
        assert result['total_containers'] == 1
        assert len(result['containers'][0]['boxes']) == 1

    def test_pack_multiple_boxes(self, simple_boxes, containers):
        """Test packing multiple boxes."""
        packer = GreedyPacker(simple_boxes, containers)
        result = packer.pack()

        assert result is not None
        total_boxes = sum(len(c['boxes']) for c in result['containers'])
        assert total_boxes == 3

    def test_pack_result_structure(self, single_box, containers):
        """Test that result has expected structure."""
        packer = GreedyPacker(single_box, containers)
        result = packer.pack()

        assert 'containers' in result
        assert 'total_containers' in result
        assert 'container_counts' in result
        assert 'total_volume_used' in result
        assert 'total_volume_available' in result
        assert 'overall_utilization' in result

    def test_pack_container_info(self, single_box, containers):
        """Test that container info has expected structure."""
        packer = GreedyPacker(single_box, containers)
        result = packer.pack()

        container = result['containers'][0]
        assert 'id' in container
        assert 'type' in container
        assert 'dimensions' in container
        assert 'volume' in container
        assert 'used_volume' in container
        assert 'utilization' in container
        assert 'boxes' in container

    def test_pack_box_info(self, single_box, containers):
        """Test that packed box info has expected structure."""
        packer = GreedyPacker(single_box, containers)
        result = packer.pack()

        box = result['containers'][0]['boxes'][0]
        assert 'label' in box
        assert 'box_id' in box
        assert 'original_dimensions' in box
        assert 'placed_dimensions' in box
        assert 'position' in box
        assert 'volume' in box

    def test_pack_utilization_calculation(self, single_box, small_container):
        """Test utilization calculation is correct."""
        packer = GreedyPacker(single_box, small_container)
        result = packer.pack()

        assert result is not None
        # Box is 100x100x100 = 1,000,000 mm³
        # Container is 100x100x100 = 1,000,000 mm³
        # Utilization should be 100%
        assert result['overall_utilization'] == 1.0

    def test_pack_empty_boxes(self, containers):
        """Test packing with no boxes."""
        packer = GreedyPacker([], containers)
        result = packer.pack()

        assert result is not None
        assert result['total_containers'] == 0

    def test_pack_box_too_large(self):
        """Test when box doesn't fit in any container."""
        boxes = [Box("Huge", (1000, 1000, 1000), box_id=1)]
        containers = [("Tiny", (100, 100, 100))]

        packer = GreedyPacker(boxes, containers)
        result = packer.pack()

        assert result is None

    def test_pack_exact_fit(self):
        """Test box that exactly fits container."""
        boxes = [Box("Exact", (100, 100, 100), box_id=1)]
        containers = [("Exact", (100, 100, 100))]

        packer = GreedyPacker(boxes, containers)
        result = packer.pack()

        assert result is not None
        assert result['total_containers'] == 1
        assert result['overall_utilization'] == 1.0


class TestOptimalPacker:
    """Tests for the OptimalPacker algorithm."""

    def test_pack_single_box(self, single_box, containers):
        """Test packing a single box."""
        packer = OptimalPacker(single_box, containers)
        result = packer.pack()

        assert result is not None
        assert result['total_containers'] == 1

    def test_pack_multiple_boxes(self, simple_boxes, containers):
        """Test packing multiple boxes."""
        packer = OptimalPacker(simple_boxes, containers)
        result = packer.pack()

        assert result is not None
        total_boxes = sum(len(c['boxes']) for c in result['containers'])
        assert total_boxes == 3

    def test_pack_tries_multiple_strategies(self, simple_boxes, containers):
        """Test that OptimalPacker produces a result."""
        packer = OptimalPacker(simple_boxes, containers)
        result = packer.pack()

        # Should find some solution
        assert result is not None
        assert result['overall_utilization'] > 0

    def test_pack_empty_boxes(self, containers):
        """Test packing with no boxes."""
        packer = OptimalPacker([], containers)
        result = packer.pack()

        assert result is not None
        assert result['total_containers'] == 0


class TestHybridPacker:
    """Tests for the HybridPacker algorithm."""

    def test_pack_single_box(self, single_box, containers):
        """Test packing a single box."""
        packer = HybridPacker(single_box, containers)
        result = packer.pack()

        assert result is not None
        assert result['total_containers'] == 1

    def test_pack_multiple_boxes(self, simple_boxes, containers):
        """Test packing multiple boxes."""
        packer = HybridPacker(simple_boxes, containers)
        result = packer.pack()

        assert result is not None
        total_boxes = sum(len(c['boxes']) for c in result['containers'])
        assert total_boxes == 3

    def test_pack_with_max_attempts(self, simple_boxes, containers):
        """Test packing with custom max_attempts."""
        packer = HybridPacker(simple_boxes, containers, max_attempts_per_container=1000)
        result = packer.pack()

        assert result is not None


class TestExhaustivePacker:
    """Tests for the ExhaustivePacker algorithm."""

    def test_pack_single_box(self, single_box, containers):
        """Test packing a single box."""
        packer = ExhaustivePacker(single_box, containers)
        result = packer.pack()

        assert result is not None
        assert result['total_containers'] == 1

    def test_pack_few_boxes(self):
        """Test packing a few boxes (exhaustive is slow)."""
        boxes = [
            Box("A", (50, 50, 50), box_id=1),
            Box("B", (50, 50, 50), box_id=2),
        ]
        containers = [("Medium", (200, 200, 200))]

        packer = ExhaustivePacker(boxes, containers)
        result = packer.pack()

        assert result is not None
        assert result['total_containers'] == 1


class TestPackerComparison:
    """Tests comparing different packer algorithms."""

    def test_all_packers_find_solution(self, simple_boxes, containers):
        """Test that all packers can solve the same problem."""
        packers = [
            GreedyPacker(simple_boxes, containers),
            OptimalPacker(simple_boxes, containers),
            HybridPacker(simple_boxes, containers),
        ]

        for packer in packers:
            result = packer.pack()
            assert result is not None, f"{packer.__class__.__name__} failed"
            total_boxes = sum(len(c['boxes']) for c in result['containers'])
            assert total_boxes == 3

    def test_all_packers_valid_utilization(self, simple_boxes, containers):
        """Test that all packers report valid utilization."""
        packers = [
            GreedyPacker(simple_boxes, containers),
            OptimalPacker(simple_boxes, containers),
            HybridPacker(simple_boxes, containers),
        ]

        for packer in packers:
            result = packer.pack()
            assert 0 <= result['overall_utilization'] <= 1.0


class TestNoOverlaps:
    """Tests to verify no box overlaps in packing results."""

    def test_greedy_no_overlaps(self, simple_boxes, containers):
        """Test that GreedyPacker produces no overlapping boxes."""
        packer = GreedyPacker(simple_boxes, containers)
        result = packer.pack()
        self._check_no_overlaps(result)

    def test_optimal_no_overlaps(self, simple_boxes, containers):
        """Test that OptimalPacker produces no overlapping boxes."""
        packer = OptimalPacker(simple_boxes, containers)
        result = packer.pack()
        self._check_no_overlaps(result)

    def test_hybrid_no_overlaps(self, simple_boxes, containers):
        """Test that HybridPacker produces no overlapping boxes."""
        packer = HybridPacker(simple_boxes, containers)
        result = packer.pack()
        self._check_no_overlaps(result)

    def _check_no_overlaps(self, result):
        """Helper to check for overlaps in a result."""
        if result is None:
            return

        for container in result['containers']:
            boxes = container['boxes']
            for i, box1 in enumerate(boxes):
                for j, box2 in enumerate(boxes):
                    if i >= j:
                        continue

                    # Check overlap
                    x1, y1, z1 = box1['position']
                    w1, d1, h1 = box1['placed_dimensions']
                    x2, y2, z2 = box2['position']
                    w2, d2, h2 = box2['placed_dimensions']

                    x_overlap = x1 < x2 + w2 and x1 + w1 > x2
                    y_overlap = y1 < y2 + d2 and y1 + d1 > y2
                    z_overlap = z1 < z2 + h2 and z1 + h1 > z2

                    overlaps = x_overlap and y_overlap and z_overlap
                    assert not overlaps, \
                        f"Boxes {box1['box_id']} and {box2['box_id']} overlap"
