"""Exhaustive search packing algorithm with backtracking."""
import sys
from copy import deepcopy
from typing import Dict, List, Tuple, Optional

from ..models import Box, PackingContainer
from .base import BasePacker


class ExhaustivePacker(BasePacker):
    """Exhaustive search packing algorithm using backtracking.

    This algorithm guarantees finding an optimal solution (minimum containers)
    if one exists, but may be slow for large datasets.

    Best for:
        - Small to medium datasets (<50 boxes)
        - When optimal solution is required
        - When time is not a constraint
    """

    def __init__(
        self,
        boxes: List[Box],
        container_types: List[Tuple[str, Tuple[int, int, int]]]
    ):
        super().__init__(boxes, container_types)
        self.attempts = 0

    def pack(self) -> Optional[Dict]:
        """Find optimal packing configuration using exhaustive search."""
        print(f"Starting exhaustive search for packing {len(self.boxes)} boxes...")
        print(f"Available containers: {[label for label, _ in self.container_types]}")

        sorted_boxes = sorted(self.boxes, key=lambda b: b.volume(), reverse=True)

        for max_containers in range(1, len(self.boxes) + 1):
            print(f"\nTrying with up to {max_containers} containers...")

            result = self._try_packing_with_limit(sorted_boxes, max_containers)

            if result:
                print(f"\nFound solution with {len(result['containers'])} containers!")
                return result
            else:
                print(f"  No solution with {max_containers} containers "
                      f"(tried {self.attempts:,} placements)")

        return None

    def _try_packing_with_limit(self, boxes: List[Box],
                                max_containers: int) -> Optional[Dict]:
        """Try to pack all boxes using at most max_containers."""
        containers = []
        self.attempts = 0

        def backtrack(box_index: int) -> bool:
            if box_index >= len(boxes):
                sys.stdout.write(f"\r  Successfully packed all {len(boxes)} boxes!" +
                               " " * 50 + "\n")
                sys.stdout.flush()
                return True

            self.attempts += 1
            if self.attempts % 50 == 0:
                progress_pct = (box_index / len(boxes)) * 100
                box_label = boxes[box_index].label[:20]
                sys.stdout.write(f"\r  Box {box_index + 1}/{len(boxes)} "
                               f"({progress_pct:.1f}%) | '{box_label}' | "
                               f"Containers: {len(containers)} | "
                               f"Attempts: {self.attempts:,}" + " " * 10)
                sys.stdout.flush()

            if len(containers) >= max_containers:
                return False

            box = boxes[box_index]
            rotations = box.get_rotations()

            for container in containers:
                for rotation in rotations:
                    for free_space in sorted(container.free_spaces,
                                           key=lambda fs: (fs.position[2],
                                                          fs.position[1],
                                                          fs.position[0])):
                        if free_space.can_fit(rotation):
                            saved_state = self._save_container_state(container)

                            if container.place_box(box, free_space.position, rotation):
                                if backtrack(box_index + 1):
                                    return True
                                self._restore_container_state(container, saved_state)

            if len(containers) < max_containers:
                for box_type_label, box_type_dims in self.container_types:
                    new_container = PackingContainer(box_type_label, box_type_dims)

                    for rotation in rotations:
                        if new_container.can_place_box(rotation, (0, 0, 0)):
                            new_container.place_box(box, (0, 0, 0), rotation)
                            containers.append(new_container)

                            if backtrack(box_index + 1):
                                return True

                            containers.pop()
                            break

            return False

        result = backtrack(0)
        sys.stdout.write("\r" + " " * 100 + "\r")
        sys.stdout.flush()

        if result:
            return self._format_result(containers)

        return None

    def _save_container_state(self, container: PackingContainer) -> Tuple:
        """Save container state for backtracking."""
        return (
            deepcopy(container.placed_boxes),
            deepcopy(container.free_spaces)
        )

    def _restore_container_state(self, container: PackingContainer, state: Tuple):
        """Restore container state from saved state."""
        container.placed_boxes, container.free_spaces = state
