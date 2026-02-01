import pyxel
import random

# =====================
# CONSTANTS
# =====================
TILE = 8
CHAR_SIZE = 16
WIDTH_TILES = 20
HEIGHT_TILES = 15

# =====================
# BUFF DEFINITIONS
# =====================
BUFFS = [
    ("+1 ATK", lambda p: p.__setitem__("atk", p["atk"] + 1)),
    ("+5 MAX HP", lambda p: p.__setitem__("max_hp", p["max_hp"] + 5)),
    ("Heal +3", lambda p: p.__setitem__("hp", min(p["max_hp"], p["hp"] + 3))),
    ("Attack Speed +1", lambda p: p.__setitem__("speed", p["speed"] + 1)),
]

# =====================
# MAIN GAME CLASS
# =====================
class App:
    def __init__(self):
        pyxel.init(WIDTH_TILES * TILE, HEIGHT_TILES * TILE, title="Idle Roguelite Demo")
        pyxel.load("DungeonSlice.pyxres")

        # -----------------
        # PLAYER
        # -----------------
        self.player = {
            "x": TILE,
            "y": TILE,
            "hp": 10,
            "max_hp": 10,
            "atk": 1,
            "speed": 1,
            "level": 1,
            "xp": 0,
            "xp_need": 10,
        }

        # idle timer
        self.tick = 0

        # dots = XP orbs
        self.dots = self.spawn_dots()

        # last buff text
        self.last_buff = ""

        pyxel.run(self.update, self.draw)

    # =====================
    # SPAWN DOTS
    # =====================
    def spawn_dots(self):
        return {
            (x * TILE + 4, y * TILE + 4)
            for y in range(HEIGHT_TILES)
            for x in range(WIDTH_TILES)
            if random.random() < 0.15
        }

    # =====================
    # LEVEL UP
    # =====================
    def level_up(self):
        self.player["level"] += 1
        self.player["xp"] = 0
        self.player["xp_need"] = int(self.player["xp_need"] * 1.4)

        buff = random.choice(BUFFS)
        buff[1](self.player)
        self.last_buff = buff[0]

    # =====================
    # UPDATE
    # =====================
    def update(self):
        self.tick += 1

        # -------- movement --------
        dx = dy = 0
        if pyxel.btn(pyxel.KEY_LEFT):  dx = -self.player["speed"]
        if pyxel.btn(pyxel.KEY_RIGHT): dx = self.player["speed"]
        if pyxel.btn(pyxel.KEY_UP):    dy = -self.player["speed"]
        if pyxel.btn(pyxel.KEY_DOWN):  dy = self.player["speed"]

        self.player["x"] += dx
        self.player["y"] += dy

        # clamp
        self.player["x"] = max(0, min(self.player["x"], WIDTH_TILES * TILE - CHAR_SIZE))
        self.player["y"] = max(0, min(self.player["y"], HEIGHT_TILES * TILE - CHAR_SIZE))

        # -------- collect dots --------
        px = self.player["x"] + CHAR_SIZE // 2
        py = self.player["y"] + CHAR_SIZE // 2

        collected = set()
        for d in self.dots:
            if abs(px - d[0]) < 8 and abs(py - d[1]) < 8:
                collected.add(d)

        if collected:
            self.player["xp"] += len(collected)
            self.dots -= collected

        # -------- idle tick (auto gain) --------
        if self.tick % 60 == 0:  # once per second
            self.player["xp"] += self.player["atk"]

        # -------- level up check --------
        if self.player["xp"] >= self.player["xp_need"]:
            self.level_up()

        # respawn dots if empty
        if not self.dots:
            self.dots = self.spawn_dots()

        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

    # =====================
    # DRAW
    # =====================
    def draw(self):
        pyxel.cls(0)

        # dots
        for d in self.dots:
            pyxel.circ(d[0], d[1], 1, 11)

        # character (16x16)
        x = self.player["x"]
        y = self.player["y"]
        pyxel.blt(x, y, 0, 0, 0, 8, 8, 0)
        pyxel.blt(x + 8, y, 0, 8, 0, 8, 8, 0)
        pyxel.blt(x, y + 8, 0, 0, 8, 8, 8, 0)
        pyxel.blt(x + 8, y + 8, 0, 8, 8, 8, 8, 0)

        # UI
        pyxel.text(5, 5, f"LV {self.player['level']}", 7)
        pyxel.text(5, 13, f"XP {self.player['xp']}/{self.player['xp_need']}", 6)
        pyxel.text(5, 21, f"ATK {self.player['atk']} SPD {self.player['speed']}", 11)

        if self.last_buff:
            pyxel.text(5, 29, f"Buff: {self.last_buff}", 10)


# =====================
App()
