"""Base packer interface and shared utilities."""
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional

from ..models import Box, PackingContainer


class BasePacker(ABC):
    """Abstract base class for packing algorithms.

    All packing algorithms should inherit from this class and implement
    the pack() method.

    Attributes:
        boxes: List of boxes to pack
        container_types: List of available container types
    """

    def __init__(
        self,
        boxes: List[Box],
        container_types: List[Tuple[str, Tuple[int, int, int]]]
    ):
        """Initialize the packer.

        Args:
            boxes: List of Box objects to pack
            container_types: List of tuples (label, (width, depth, height))
        """
        self.boxes = boxes
        self.container_types = container_types

    @abstractmethod
    def pack(self) -> Optional[Dict]:
        """Execute the packing algorithm.

        Returns:
            Dictionary with packing results or None if no solution found.
            The dictionary contains:
                - containers: List of container details
                - total_containers: Number of containers used
                - container_counts: Dict of container type counts
                - total_volume_used: Total volume of packed boxes
                - total_volume_available: Total container volume
                - overall_utilization: Ratio of used to available volume
        """
        pass

    def _format_result(self, containers: List[PackingContainer]) -> Dict:
        """Format containers into standard result dictionary.

        Args:
            containers: List of PackingContainer objects

        Returns:
            Standardized result dictionary
        """
        result = {
            'containers': [],
            'total_containers': len(containers),
            'container_counts': {},
            'total_volume_used': 0,
            'total_volume_available': 0,
            'overall_utilization': 0.0
        }

        for i, container in enumerate(containers):
            container_info = {
                'id': i + 1,
                'type': container.label,
                'dimensions': container.dimensions,
                'volume': container.volume(),
                'used_volume': container.used_volume(),
                'utilization': container.utilization(),
                'boxes': []
            }

            for placed_box in container.placed_boxes:
                box_info = {
                    'label': placed_box.box.label,
                    'box_id': placed_box.box.box_id,
                    'original_dimensions': placed_box.box.dimensions,
                    'placed_dimensions': placed_box.dimensions,
                    'position': placed_box.position,
                    'volume': placed_box.box.volume()
                }
                container_info['boxes'].append(box_info)

            result['containers'].append(container_info)
            result['total_volume_used'] += container.used_volume()
            result['total_volume_available'] += container.volume()

            if container.label not in result['container_counts']:
                result['container_counts'][container.label] = 0
            result['container_counts'][container.label] += 1

        result['overall_utilization'] = (
            result['total_volume_used'] / result['total_volume_available']
            if result['total_volume_available'] > 0 else 0.0
        )

        return result

    def _try_place_in_container(self, box: Box, container: PackingContainer) -> bool:
        """Try to place a box in a container using free space management.

        Args:
            box: The box to place
            container: The container to place in

        Returns:
            True if placement succeeded, False otherwise
        """
        rotations = box.get_rotations()

        for rotation in rotations:
            for space in sorted(container.free_spaces,
                              key=lambda s: (s.position[2], s.position[1], s.position[0])):
                if space.can_fit(rotation):
                    if container.place_box(box, space.position, rotation):
                        return True

        return False
