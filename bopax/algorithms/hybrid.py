"""Hybrid exhaustive-greedy packing algorithm."""
import sys
import random
from copy import deepcopy
from typing import Dict, List, Tuple, Optional, Set

from ..models import Box, PackingContainer
from .base import BasePacker


class HybridPacker(BasePacker):
    """Hybrid exhaustive-greedy packing algorithm.

    For each container, exhaustively searches for best packing using multiple
    strategies (layer-based, greedy best-fit, random search), then greedily
    selects the container with highest utilization.

    Best for:
        - Medium to large datasets (50-200 boxes)
        - Good balance of quality and speed
        - When high utilization is important
    """

    def __init__(
        self,
        boxes: List[Box],
        container_types: List[Tuple[str, Tuple[int, int, int]]],
        max_attempts_per_container: int = 50000
    ):
        super().__init__(boxes, container_types)
        self.max_attempts = max_attempts_per_container

    def pack(self) -> Optional[Dict]:
        """Pack boxes using hybrid approach."""
        print(f"Hybrid exhaustive-greedy packing for {len(self.boxes)} boxes...")
        print(f"Container types: {[label for label, _ in self.container_types]}\n")

        sorted_boxes = sorted(self.boxes, key=lambda b: b.volume(), reverse=True)

        remaining_boxes = sorted_boxes.copy()
        result_containers = []
        iteration = 1

        while remaining_boxes:
            print(f"Iteration {iteration}: {len(remaining_boxes)} boxes remaining")

            best_container = None
            best_utilization = 0
            best_packed_indices = set()

            for container_label, container_dims in self.container_types:
                print(f"  Trying {container_label} ({container_dims})...", end="")
                sys.stdout.flush()

                packer = _ExhaustiveContainerPacker(
                    container_label, container_dims, remaining_boxes,
                    max_attempts=self.max_attempts
                )

                container, packed_indices = packer.find_best_packing()

                if container and packed_indices:
                    util = container.utilization()
                    print(f" {len(packed_indices)} boxes, {util:.1%} utilization")

                    if util > best_utilization:
                        best_utilization = util
                        best_container = container
                        best_packed_indices = packed_indices
                else:
                    print(" No packing found")

            if best_container and best_packed_indices:
                result_containers.append(best_container)
                print(f"  -> Selected: {len(best_packed_indices)} boxes, "
                      f"{best_utilization:.1%}\n")

                remaining_boxes = [box for i, box in enumerate(remaining_boxes)
                                 if i not in best_packed_indices]
                iteration += 1
            else:
                print("  Could not pack remaining boxes!\n")
                if not self._greedy_fallback(remaining_boxes, result_containers):
                    return None
                break

        print(f"Packed all boxes into {len(result_containers)} containers")
        return self._format_result(result_containers)

    def _greedy_fallback(self, remaining_boxes: List[Box],
                         result_containers: List[PackingContainer]) -> bool:
        """Fallback greedy packing for remaining boxes."""
        print("  Using greedy fallback...")

        for box in remaining_boxes:
            placed = False

            for container in result_containers:
                if self._try_place_in_container(box, container):
                    placed = True
                    break

            if not placed:
                for label, dims in self.container_types:
                    new_container = PackingContainer(label, dims)
                    if self._try_place_in_container(box, new_container):
                        result_containers.append(new_container)
                        placed = True
                        break

            if not placed:
                print(f"    Could not place: {box.label}")
                return False

        print(f"    Placed {len(remaining_boxes)} boxes with fallback")
        return True


class _ExhaustiveContainerPacker:
    """Helper class for exhaustive single-container packing."""

    def __init__(self, container_label: str, container_dims: Tuple[int, int, int],
                 boxes: List[Box], max_attempts: int = 50000):
        self.container_label = container_label
        self.container_dims = container_dims
        self.boxes = boxes
        self.max_attempts = max_attempts

    def find_best_packing(self) -> Tuple[Optional[PackingContainer], Set[int]]:
        """Find the best packing using multiple strategies."""
        result1 = self._try_layer_packing()
        result2 = self._try_greedy_best_fit()
        result3 = self._try_random_search(num_starts=10)

        best_container = None
        best_indices = set()
        best_util = 0

        for container, indices in [result1, result2, result3]:
            if container and container.utilization() > best_util:
                best_util = container.utilization()
                best_container = container
                best_indices = indices

        return best_container, best_indices

    def _try_layer_packing(self) -> Tuple[Optional[PackingContainer], Set[int]]:
        """Layer-based packing strategy."""
        container = PackingContainer(self.container_label, self.container_dims)
        packed_indices = set()

        current_z = 0
        max_layer_height = 0

        while current_z < self.container_dims[2]:
            current_y = 0

            while current_y < self.container_dims[1]:
                current_x = 0
                row_height = 0

                while current_x < self.container_dims[0]:
                    best_box_idx = None
                    best_rotation = None
                    best_fit_score = 0

                    for i, box in enumerate(self.boxes):
                        if i in packed_indices:
                            continue

                        for rotation in box.get_rotations():
                            w, d, h = rotation

                            if (current_x + w <= self.container_dims[0] and
                                current_y + d <= self.container_dims[1] and
                                current_z + h <= self.container_dims[2]):

                                fit_score = w * 1000 + d * 10 + h

                                if fit_score > best_fit_score:
                                    best_fit_score = fit_score
                                    best_box_idx = i
                                    best_rotation = rotation

                    if best_box_idx is not None:
                        box = self.boxes[best_box_idx]
                        w, d, h = best_rotation

                        if container.can_place_box(best_rotation,
                                                   (current_x, current_y, current_z)):
                            container.place_box(box,
                                              (current_x, current_y, current_z),
                                              best_rotation)
                            packed_indices.add(best_box_idx)
                            current_x += w
                            row_height = max(row_height, h)
                            max_layer_height = max(max_layer_height, h)
                        else:
                            break
                    else:
                        break

                current_y += row_height if row_height > 0 else self.container_dims[1]

            if max_layer_height == 0:
                break
            current_z += max_layer_height
            max_layer_height = 0

        return container, packed_indices

    def _try_greedy_best_fit(self) -> Tuple[Optional[PackingContainer], Set[int]]:
        """Greedy best-fit strategy."""
        container = PackingContainer(self.container_label, self.container_dims)
        packed_indices = set()

        while True:
            positions = self._get_placement_positions(container)

            best_placement = None
            best_util_gain = 0

            for i, box in enumerate(self.boxes):
                if i in packed_indices:
                    continue

                for rotation in box.get_rotations():
                    for pos in positions:
                        if container.can_place_box(rotation, pos):
                            util_gain = (box.volume() /
                                        (self.container_dims[0] *
                                         self.container_dims[1] *
                                         self.container_dims[2]))

                            if util_gain > best_util_gain:
                                best_util_gain = util_gain
                                best_placement = (i, box, pos, rotation)

            if best_placement:
                idx, box, pos, rotation = best_placement
                container.place_box(box, pos, rotation)
                packed_indices.add(idx)
            else:
                break

        return container, packed_indices

    def _try_random_search(self, num_starts: int) -> Tuple[Optional[PackingContainer],
                                                           Set[int]]:
        """Random ordering search strategy."""
        best_container = None
        best_indices = set()
        best_util = 0

        box_indices = list(range(len(self.boxes)))

        for _ in range(num_starts):
            random.shuffle(box_indices)

            container = PackingContainer(self.container_label, self.container_dims)
            packed_indices = set()

            for i in box_indices:
                box = self.boxes[i]
                positions = self._get_placement_positions(container)

                placed = False
                for rotation in box.get_rotations():
                    for pos in positions:
                        if container.can_place_box(rotation, pos):
                            container.place_box(box, pos, rotation)
                            packed_indices.add(i)
                            placed = True
                            break
                    if placed:
                        break

            if container.utilization() > best_util:
                best_util = container.utilization()
                best_container = deepcopy(container)
                best_indices = packed_indices.copy()

        return best_container, best_indices

    def _get_placement_positions(self, container: PackingContainer) -> List[Tuple[int, int, int]]:
        """Get candidate positions based on placed boxes."""
        positions = [(0, 0, 0)]

        for placed in container.placed_boxes:
            px, py, pz = placed.position
            pw, pd, ph = placed.dimensions

            positions.extend([
                (px + pw, py, pz),
                (px, py + pd, pz),
                (px, py, pz + ph),
                (px + pw, py + pd, pz),
                (px + pw, py, pz + ph),
                (px, py + pd, pz + ph),
            ])

        valid_positions = []
        seen = set()
        for pos in positions:
            if (pos not in seen and
                pos[0] < self.container_dims[0] and
                pos[1] < self.container_dims[1] and
                pos[2] < self.container_dims[2]):
                valid_positions.append(pos)
                seen.add(pos)

        return sorted(valid_positions, key=lambda p: (p[2], p[1], p[0]))
