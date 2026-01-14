"""Greedy first-fit decreasing packing algorithm."""
import sys
from typing import Dict, List, Tuple, Optional

from ..models import Box, FreeSpace, PlacedBox, PackingContainer
from .base import BasePacker


class GreedyPacker(BasePacker):
    """Greedy first-fit decreasing packing algorithm.

    This algorithm sorts boxes by volume (largest first) and places each
    box in the first available position. Fast but may not find optimal solution.

    Best for:
        - Large datasets (100+ boxes)
        - When speed is important
        - When near-optimal solution is acceptable
    """

    def __init__(
        self,
        boxes: List[Box],
        container_types: List[Tuple[str, Tuple[int, int, int]]]
    ):
        super().__init__(boxes, container_types)
        self.container_types = sorted(
            container_types,
            key=lambda x: x[1][0] * x[1][1] * x[1][2],
            reverse=True
        )

    def pack(self) -> Optional[Dict]:
        """Pack all boxes using greedy first-fit decreasing."""
        print(f"Using greedy first-fit decreasing for {len(self.boxes)} boxes...")
        print(f"Available containers: {[label for label, _ in self.container_types]}\n")

        sorted_boxes = sorted(self.boxes, key=lambda b: b.volume(), reverse=True)

        containers = []
        packed_count = 0

        for i, box in enumerate(sorted_boxes):
            if (i + 1) % 10 == 0 or i == 0:
                sys.stdout.write(f"\rPacking box {i + 1}/{len(sorted_boxes)} "
                               f"({((i+1)/len(sorted_boxes)*100):.1f}%) | "
                               f"Containers: {len(containers)}")
                sys.stdout.flush()

            placed = False

            for container in containers:
                if self._try_place_greedy(box, container):
                    placed = True
                    packed_count += 1
                    break

            if not placed:
                new_container = self._create_best_container(box)
                if new_container and self._try_place_greedy(box, new_container):
                    containers.append(new_container)
                    placed = True
                    packed_count += 1

            if not placed:
                print(f"\nERROR: Could not place box {box.label} (ID: {box.box_id})")
                print(f"   Dimensions: {box.dimensions}")
                return None

        sys.stdout.write(f"\r  Packed all {len(sorted_boxes)} boxes!" + " " * 30 + "\n")
        sys.stdout.flush()

        print(f"\nPacked {packed_count} boxes into {len(containers)} containers")

        return self._format_result(containers)

    def _try_place_greedy(self, box: Box, container: PackingContainer) -> bool:
        """Try to place a box using simplified free space management."""
        rotations = box.get_rotations()

        for rotation in rotations:
            for space in sorted(container.free_spaces,
                              key=lambda s: (s.position[2], s.position[1], s.position[0])):
                if space.can_fit(rotation):
                    if self._place_with_simple_update(box, container, space.position, rotation):
                        return True

        return False

    def _place_with_simple_update(self, box: Box, container: PackingContainer,
                                   position: Tuple[int, int, int],
                                   dimensions: Tuple[int, int, int]) -> bool:
        """Place box and update free spaces with simplified splitting."""
        if not container.can_place_box(dimensions, position):
            return False

        placed_box = PlacedBox(box, position, dimensions)
        container.placed_boxes.append(placed_box)

        self._update_free_spaces_simple(container, placed_box)
        return True

    def _update_free_spaces_simple(self, container: PackingContainer,
                                    placed_box: PlacedBox):
        """Simplified free space update (3-direction split)."""
        px, py, pz = placed_box.position
        pw, pd, ph = placed_box.dimensions

        new_spaces = []
        for space in container.free_spaces:
            sx, sy, sz = space.position
            sw, sd, sh = space.dimensions

            if not (px >= sx + sw or px + pw <= sx or
                   py >= sy + sd or py + pd <= sy or
                   pz >= sz + sh or pz + ph <= sz):
                # Space overlaps - split it
                if sz + sh > pz + ph:
                    new_spaces.append(FreeSpace(
                        (sx, sy, pz + ph),
                        (sw, sd, sz + sh - (pz + ph))
                    ))
                if sx + sw > px + pw:
                    new_spaces.append(FreeSpace(
                        (px + pw, sy, sz),
                        (sx + sw - (px + pw), sd, sh)
                    ))
                if sy + sd > py + pd:
                    new_spaces.append(FreeSpace(
                        (sx, py + pd, sz),
                        (sw, sy + sd - (py + pd), sh)
                    ))
            else:
                new_spaces.append(space)

        new_spaces.sort(key=lambda s: s.volume(), reverse=True)
        container.free_spaces = new_spaces[:20]

    def _create_best_container(self, box: Box) -> Optional[PackingContainer]:
        """Create the largest container that can fit the box."""
        for label, dims in self.container_types:
            for rotation in box.get_rotations():
                if (rotation[0] <= dims[0] and
                    rotation[1] <= dims[1] and
                    rotation[2] <= dims[2]):
                    return PackingContainer(label, dims)

        return None
