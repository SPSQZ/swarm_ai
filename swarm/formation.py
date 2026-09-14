"""Formation control for coordinated multi-drone flight patterns."""


class FormationController:
    def __init__(self, formation_type="line", spacing=2.0):
        self.formation_type = formation_type
        self.spacing = spacing

    def get_formation_offsets(self, num_drones=3):
        """Generate formation offsets for a specified number of drones."""
        if self.formation_type == "line":
            return self._line_formation(num_drones)
        elif self.formation_type == "wedge":
            return self._wedge_formation(num_drones)
        elif self.formation_type == "arc":
            return self._arc_formation(num_drones)
        elif self.formation_type == "diamond":
            return self._diamond_formation(num_drones)
        else:
            return [(0, 0)] * num_drones

    def _line_formation(self, num_drones):
        """Offset drones in a straight line."""
        offsets = []
        for i in range(num_drones):
            offset = (i * self.spacing, 0)
            offsets.append(offset)
        return offsets

    def _wedge_formation(self, num_drones):
        """Offset drones in a wedge/V formation."""
        offsets = [(0, 0)]
        for i in range(1, num_drones):
            side = -1 if i % 2 == 1 else 1
            row = (i + 1) // 2
            offset = (row * self.spacing, side * row * self.spacing / 2)
            offsets.append(offset)
        return offsets[:num_drones]

    def _arc_formation(self, num_drones):
        """Offset drones in an arc formation."""
        offsets = []
        radius = self.spacing * 2
        for i in range(num_drones):
            angle = (i / max(1, num_drones - 1)) * 3.14159
            x = radius * __import__("math").cos(angle)
            y = radius * __import__("math").sin(angle)
            offsets.append((x, y))
        return offsets

    def _diamond_formation(self, num_drones):
        """Offset drones in a diamond formation."""
        if num_drones < 4:
            return self._line_formation(num_drones)

        offsets = [
            (0, 0),
            (-self.spacing, -self.spacing),
            (self.spacing, -self.spacing),
            (0, -2 * self.spacing),
        ]
        return offsets[:num_drones]
