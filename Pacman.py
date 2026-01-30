import pyxel
import math


class App:
    def __init__(self):
        pyxel.init(160, 120, title="Pac-Man Waka Waka")

        self.x = 80
        self.y = 60
        self.speed = 2

        self.dx = 0
        self.dy = 0

        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btn(pyxel.KEY_LEFT):
            self.dx, self.dy = -1, 0
        elif pyxel.btn(pyxel.KEY_RIGHT):
            self.dx, self.dy = 1, 0
        elif pyxel.btn(pyxel.KEY_UP):
            self.dx, self.dy = 0, -1
        elif pyxel.btn(pyxel.KEY_DOWN):
            self.dx, self.dy = 0, 1

        self.x += self.dx * self.speed
        self.y += self.dy * self.speed

        self.x = max(0, min(self.x, pyxel.width - 8))
        self.y = max(0, min(self.y, pyxel.height - 8))

    def draw(self):
        pyxel.cls(0)

        # Mouth animation (0.2 = slow, 0.5 = fast)
        mouth_open = abs(math.sin(pyxel.frame_count * 0.2)) * 45

        # Direction angle
        if self.dx == 1:
            angle = 0
        elif self.dx == -1:
            angle = 180
        elif self.dy == -1:
            angle = 270
        elif self.dy == 1:
            angle = 90
        else:
            angle = 0

        # Draw Pac-Man
        pyxel.circ(self.x + 4, self.y + 4, 4, 10)

        # Mouth cut
        pyxel.tri(
            self.x + 4,
            self.y + 4,
            self.x + 4 + math.cos(math.radians(angle - mouth_open)) * 6,
            self.y + 4 + math.sin(math.radians(angle - mouth_open)) * 6,
            self.x + 4 + math.cos(math.radians(angle + mouth_open)) * 6,
            self.y + 4 + math.sin(math.radians(angle + mouth_open)) * 6,
            0
        )


App()
