"""Container model classes for 3D bin packing."""
from dataclasses import dataclass, field
from typing import List, Tuple

from .box import Box, PlacedBox


@dataclass
class FreeSpace:
    """Represents a rectangular free space in a container.

    Attributes:
        position: Tuple of (x, y, z) coordinates for the corner
        dimensions: Tuple of (width, depth, height) in mm
    """
    position: Tuple[int, int, int]
    dimensions: Tuple[int, int, int]

    def volume(self) -> int:
        """Calculate the volume of this free space."""
        return self.dimensions[0] * self.dimensions[1] * self.dimensions[2]

    def can_fit(self, box_dims: Tuple[int, int, int]) -> bool:
        """Check if a box with given dimensions can fit in this space.

        Args:
            box_dims: Tuple of (width, depth, height) to check

        Returns:
            True if the box fits, False otherwise
        """
        return (box_dims[0] <= self.dimensions[0] and
                box_dims[1] <= self.dimensions[1] and
                box_dims[2] <= self.dimensions[2])


@dataclass
class PackingContainer:
    """Represents a container (packing box) with placed boxes.

    Attributes:
        label: Name/identifier for the container type
        dimensions: Tuple of (width, depth, height) in mm
        placed_boxes: List of boxes placed in this container
        free_spaces: List of available free spaces
    """
    label: str
    dimensions: Tuple[int, int, int]
    placed_boxes: List[PlacedBox] = field(default_factory=list)
    free_spaces: List[FreeSpace] = field(default_factory=list)

    def __post_init__(self):
        if not self.free_spaces:
            self.free_spaces = [FreeSpace((0, 0, 0), self.dimensions)]

    def volume(self) -> int:
        """Calculate the total volume of the container."""
        return self.dimensions[0] * self.dimensions[1] * self.dimensions[2]

    def used_volume(self) -> int:
        """Calculate the volume used by placed boxes."""
        return sum(pb.box.volume() for pb in self.placed_boxes)

    def utilization(self) -> float:
        """Calculate the utilization ratio (0.0 to 1.0)."""
        return self.used_volume() / self.volume() if self.volume() > 0 else 0.0

    def can_place_box(self, box_dims: Tuple[int, int, int],
                      position: Tuple[int, int, int]) -> bool:
        """Check if a box can be placed at the given position.

        Args:
            box_dims: Dimensions of the box (width, depth, height)
            position: Position to place at (x, y, z)

        Returns:
            True if placement is valid, False otherwise
        """
        x, y, z = position
        w, d, h = box_dims

        if (x + w > self.dimensions[0] or
            y + d > self.dimensions[1] or
            z + h > self.dimensions[2]):
            return False

        if x < 0 or y < 0 or z < 0:
            return False

        temp_box = Box("temp", box_dims)
        temp_placed = PlacedBox(temp_box, position, box_dims)

        for placed_box in self.placed_boxes:
            if temp_placed.overlaps(placed_box):
                return False

        return True

    def place_box(self, box: Box, position: Tuple[int, int, int],
                  dimensions: Tuple[int, int, int]) -> bool:
        """Attempt to place a box at the given position.

        Args:
            box: The Box to place
            position: Position (x, y, z) for placement
            dimensions: Dimensions after rotation (width, depth, height)

        Returns:
            True if placement succeeded, False otherwise
        """
        if not self.can_place_box(dimensions, position):
            return False

        placed_box = PlacedBox(box, position, dimensions)
        self.placed_boxes.append(placed_box)
        self._update_free_spaces(placed_box)
        return True

    def remove_last(self):
        """Remove the last placed box (for backtracking)."""
        if self.placed_boxes:
            self.placed_boxes.pop()

    def _update_free_spaces(self, placed_box: PlacedBox):
        """Update free spaces after placing a box using guillotine splitting."""
        new_free_spaces = []
        px, py, pz = placed_box.position
        pw, pd, ph = placed_box.dimensions

        for free_space in self.free_spaces:
            fx, fy, fz = free_space.position
            fw, fd, fh = free_space.dimensions

            if not self._boxes_intersect(
                (px, py, pz, pw, pd, ph),
                (fx, fy, fz, fw, fd, fh)
            ):
                new_free_spaces.append(free_space)
                continue

            # Space to the right (positive x)
            if fx + fw > px + pw:
                new_space = FreeSpace(
                    (px + pw, fy, fz),
                    (fx + fw - (px + pw), fd, fh)
                )
                if new_space.volume() > 0:
                    new_free_spaces.append(new_space)

            # Space to the left (negative x)
            if fx < px:
                new_space = FreeSpace(
                    (fx, fy, fz),
                    (px - fx, fd, fh)
                )
                if new_space.volume() > 0:
                    new_free_spaces.append(new_space)

            # Space to the front (positive y)
            if fy + fd > py + pd:
                new_space = FreeSpace(
                    (fx, py + pd, fz),
                    (fw, fy + fd - (py + pd), fh)
                )
                if new_space.volume() > 0:
                    new_free_spaces.append(new_space)

            # Space to the back (negative y)
            if fy < py:
                new_space = FreeSpace(
                    (fx, fy, fz),
                    (fw, py - fy, fh)
                )
                if new_space.volume() > 0:
                    new_free_spaces.append(new_space)

            # Space above (positive z)
            if fz + fh > pz + ph:
                new_space = FreeSpace(
                    (fx, fy, pz + ph),
                    (fw, fd, fz + fh - (pz + ph))
                )
                if new_space.volume() > 0:
                    new_free_spaces.append(new_space)

            # Space below (negative z)
            if fz < pz:
                new_space = FreeSpace(
                    (fx, fy, fz),
                    (fw, fd, pz - fz)
                )
                if new_space.volume() > 0:
                    new_free_spaces.append(new_space)

        self.free_spaces = self._prune_free_spaces(new_free_spaces)

    def _boxes_intersect(self, box1: Tuple, box2: Tuple) -> bool:
        """Check if two boxes (x, y, z, w, d, h) intersect."""
        x1, y1, z1, w1, d1, h1 = box1
        x2, y2, z2, w2, d2, h2 = box2

        return (x1 < x2 + w2 and x1 + w1 > x2 and
                y1 < y2 + d2 and y1 + d1 > y2 and
                z1 < z2 + h2 and z1 + h1 > z2)

    def _prune_free_spaces(self, spaces: List[FreeSpace]) -> List[FreeSpace]:
        """Remove enclosed and duplicate spaces."""
        pruned = []

        for i, space1 in enumerate(spaces):
            is_enclosed = False

            for j, space2 in enumerate(spaces):
                if i == j:
                    continue

                s1x, s1y, s1z = space1.position
                s1w, s1d, s1h = space1.dimensions
                s2x, s2y, s2z = space2.position
                s2w, s2d, s2h = space2.dimensions

                if (s2x <= s1x and s2y <= s1y and s2z <= s1z and
                    s2x + s2w >= s1x + s1w and
                    s2y + s2d >= s1y + s1d and
                    s2z + s2h >= s1z + s1h and
                    (s2x < s1x or s2y < s1y or s2z < s1z or
                     s2x + s2w > s1x + s1w or
                     s2y + s2d > s1y + s1d or
                     s2z + s2h > s1z + s1h)):
                    is_enclosed = True
                    break

            if not is_enclosed:
                is_duplicate = False
                for existing in pruned:
                    if (space1.position == existing.position and
                        space1.dimensions == existing.dimensions):
                        is_duplicate = True
                        break

                if not is_duplicate:
                    pruned.append(space1)

        return pruned
