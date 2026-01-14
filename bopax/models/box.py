"""Box model classes for 3D bin packing."""
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class Box:
    """Represents a box to be packed.

    Attributes:
        label: Name/identifier for the box type
        dimensions: Tuple of (width, depth, height) in mm
        box_id: Unique identifier for this box instance
    """
    label: str
    dimensions: Tuple[int, int, int]
    box_id: int = 0

    def volume(self) -> int:
        """Calculate box volume in cubic mm."""
        return self.dimensions[0] * self.dimensions[1] * self.dimensions[2]

    def get_rotations(self) -> List[Tuple[int, int, int]]:
        """Return all unique rotations of the box (up to 6).

        Returns:
            List of dimension tuples representing unique orientations.
        """
        w, d, h = self.dimensions
        rotations = [
            (w, d, h), (w, h, d),
            (d, w, h), (d, h, w),
            (h, w, d), (h, d, w)
        ]
        seen = set()
        unique = []
        for rot in rotations:
            if rot not in seen:
                seen.add(rot)
                unique.append(rot)
        return unique


@dataclass
class PlacedBox:
    """Represents a box that has been placed in a container.

    Attributes:
        box: The original Box instance
        position: Tuple of (x, y, z) coordinates for placement
        dimensions: Actual dimensions after rotation (width, depth, height)
    """
    box: Box
    position: Tuple[int, int, int]
    dimensions: Tuple[int, int, int]

    def get_bounds(self) -> Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]]:
        """Get the bounding box coordinates.

        Returns:
            Tuple of ((x_min, x_max), (y_min, y_max), (z_min, z_max))
        """
        x, y, z = self.position
        w, d, h = self.dimensions
        return ((x, x + w), (y, y + d), (z, z + h))

    def overlaps(self, other: 'PlacedBox') -> bool:
        """Check if this box overlaps with another.

        Args:
            other: Another PlacedBox to check against

        Returns:
            True if the boxes overlap, False otherwise
        """
        b1 = self.get_bounds()
        b2 = other.get_bounds()

        x_overlap = b1[0][0] < b2[0][1] and b1[0][1] > b2[0][0]
        y_overlap = b1[1][0] < b2[1][1] and b1[1][1] > b2[1][0]
        z_overlap = b1[2][0] < b2[2][1] and b1[2][1] > b2[2][0]

        return x_overlap and y_overlap and z_overlap
