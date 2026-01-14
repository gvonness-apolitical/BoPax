"""Optimal mix search packing algorithm."""
import sys
from typing import Dict, List, Tuple, Optional

from ..models import Box, FreeSpace, PlacedBox, PackingContainer
from .base import BasePacker


class OptimalPacker(BasePacker):
    """Optimal mix search packing algorithm.

    This algorithm tries multiple strategies (largest containers first,
    smallest first, best-fit, mixed) and returns the best result.

    Best for:
        - Medium datasets (20-100 boxes)
        - When you want to compare different strategies
        - When good utilization is important
    """

    def __init__(
        self,
        boxes: List[Box],
        container_types: List[Tuple[str, Tuple[int, int, int]]]
    ):
        super().__init__(boxes, container_types)
        self.container_types_sorted = sorted(
            container_types,
            key=lambda x: x[1][0] * x[1][1] * x[1][2],
            reverse=True
        )

    def pack(self) -> Optional[Dict]:
        """Find optimal packing by trying different strategies."""
        print(f"Finding optimal packing for {len(self.boxes)} boxes...")
        print(f"Available containers: {[label for label, _ in self.container_types]}\n")

        # Handle empty boxes case
        if not self.boxes:
            return self._format_result([])

        sorted_boxes = sorted(self.boxes, key=lambda b: b.volume(), reverse=True)

        best_result = None
        best_utilization = 0

        # Strategy 1: Prefer largest containers
        print("Strategy 1: Largest containers first...")
        result1 = self._pack_with_preference(sorted_boxes, "largest")
        if result1:
            util1 = result1['overall_utilization']
            print(f"  Result: {result1['total_containers']} containers, "
                  f"{util1:.1%} utilization\n")
            if util1 > best_utilization:
                best_result = result1
                best_utilization = util1

        # Strategy 2: Prefer smallest containers
        print("Strategy 2: Smallest containers first...")
        result2 = self._pack_with_preference(sorted_boxes, "smallest")
        if result2:
            util2 = result2['overall_utilization']
            print(f"  Result: {result2['total_containers']} containers, "
                  f"{util2:.1%} utilization\n")
            if util2 > best_utilization:
                best_result = result2
                best_utilization = util2

        # Strategy 3: Best-fit
        print("Strategy 3: Best-fit strategy...")
        result3 = self._pack_with_preference(sorted_boxes, "bestfit")
        if result3:
            util3 = result3['overall_utilization']
            print(f"  Result: {result3['total_containers']} containers, "
                  f"{util3:.1%} utilization\n")
            if util3 > best_utilization:
                best_result = result3
                best_utilization = util3

        # Strategy 4: Mixed approach
        print("Strategy 4: Mixed container sizes...")
        result4 = self._pack_with_mixed_strategy(sorted_boxes)
        if result4:
            util4 = result4['overall_utilization']
            print(f"  Result: {result4['total_containers']} containers, "
                  f"{util4:.1%} utilization\n")
            if util4 > best_utilization:
                best_result = result4
                best_utilization = util4

        if best_result:
            print(f"Best strategy achieved {best_utilization:.1%} utilization")
            return best_result
        else:
            print("No valid packing found")
            return None

    def _pack_with_preference(self, boxes: List[Box],
                               preference: str) -> Optional[Dict]:
        """Pack boxes with a specific container size preference."""
        containers = []

        for box in boxes:
            placed = False

            for container in containers:
                if self._try_place_optimal(box, container):
                    placed = True
                    break

            if not placed:
                if preference == "largest":
                    container_order = self.container_types_sorted
                elif preference == "smallest":
                    container_order = list(reversed(self.container_types_sorted))
                else:
                    container_order = self._get_best_fit_order(box)

                for label, dims in container_order:
                    new_container = PackingContainer(label, dims)
                    if self._try_place_optimal(box, new_container):
                        containers.append(new_container)
                        placed = True
                        break

            if not placed:
                return None

        return self._format_result(containers)

    def _pack_with_mixed_strategy(self, boxes: List[Box]) -> Optional[Dict]:
        """Pack using a mixed strategy that adapts container size."""
        containers = []
        remaining_boxes = boxes.copy()

        while remaining_boxes:
            best_container = None
            best_boxes = []
            best_utilization = 0

            for label, dims in self.container_types_sorted:
                container = PackingContainer(label, dims)
                packed_boxes = []

                for box in remaining_boxes:
                    if self._try_place_optimal(box, container):
                        packed_boxes.append(box)

                if packed_boxes:
                    util = container.utilization()
                    if util > best_utilization:
                        best_container = container
                        best_boxes = packed_boxes
                        best_utilization = util

            if best_container and best_boxes:
                containers.append(best_container)
                for box in best_boxes:
                    remaining_boxes.remove(box)
            else:
                return None

        return self._format_result(containers)

    def _get_best_fit_order(self, box: Box) -> List[Tuple[str, Tuple[int, int, int]]]:
        """Get container types ordered by best fit for the box."""
        box_vol = box.volume()
        container_with_fit = []

        for label, dims in self.container_types:
            container_vol = dims[0] * dims[1] * dims[2]
            can_fit = any(
                rot[0] <= dims[0] and rot[1] <= dims[1] and rot[2] <= dims[2]
                for rot in box.get_rotations()
            )
            if can_fit:
                waste = container_vol - box_vol
                container_with_fit.append((waste, label, dims))

        container_with_fit.sort(key=lambda x: x[0])
        return [(label, dims) for _, label, dims in container_with_fit]

    def _try_place_optimal(self, box: Box, container: PackingContainer) -> bool:
        """Try to place a box with simplified free space management."""
        rotations = box.get_rotations()

        for rotation in rotations:
            for space in sorted(container.free_spaces,
                              key=lambda s: (s.position[2], s.position[1], s.position[0])):
                if space.can_fit(rotation):
                    if self._place_with_simple_update(box, container,
                                                       space.position, rotation):
                        return True

        return False

    def _place_with_simple_update(self, box: Box, container: PackingContainer,
                                   position: Tuple[int, int, int],
                                   dimensions: Tuple[int, int, int]) -> bool:
        """Place box and update free spaces."""
        if not container.can_place_box(dimensions, position):
            return False

        placed_box = PlacedBox(box, position, dimensions)
        container.placed_boxes.append(placed_box)

        px, py, pz = position
        pw, pd, ph = dimensions

        new_spaces = []
        for space in container.free_spaces:
            sx, sy, sz = space.position
            sw, sd, sh = space.dimensions

            if not (px >= sx + sw or px + pw <= sx or
                   py >= sy + sd or py + pd <= sy or
                   pz >= sz + sh or pz + ph <= sz):
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

        return True
