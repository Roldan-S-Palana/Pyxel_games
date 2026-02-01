import pyxel
import random

# =====================
# CONSTANTS
# =====================
TILE = 8
CHAR_SIZE = 16
WIDTH_TILES = 20
HEIGHT_TILES = 15

STATE_SELECT = 0
STATE_PLAY = 1

# =====================
# CHARACTER DATA
# =====================
CHARACTERS = [
    {"name": "Archer", "row_y": 0,  "proj_y": 64},
    {"name": "Knight", "row_y": 16, "proj_y": 80},
    {"name": "Wizard", "row_y": 32, "proj_y": 96},
    {"name": "Barbarian", "row_y": 48, "proj_y": 80},
]

# =====================
# PROJECTILE DATA
# =====================
DIR_VEL = {
    "right": (2, 0),
    "left": (-2, 0),
    "up": (0, -2),
    "down": (0, 2),
    "up-left": (-1.5, -1.5),
    "up-right": (1.5, -1.5),
    "down-left": (-1.5, 1.5),
    "down-right": (1.5, 1.5)
}

# Correct per-character per-direction sprite mapping
PROJECTILE_SPRITES = {
    "Archer": {
        "right": (0, 64),
        "left":  (16, 64),
        "up":    (32, 64),
        "down":  (48, 64),
        "down-left": (64,64),
        "down-right": (80,64),
        "up-left": (96,64),
        "up-right": (112,64)
    },
    "Knight": {
        "right": (16,80),
        "left":  (0,80),
        "up":    (32,80),
        "down":  (48,80),
        "down-left": (64,80),
        "down-right": (80,80),
        "up-left": (96,80),
        "up-right": (112,80)
    },
    "Barbarian": {
        "right": (16,80),
        "left":  (0,80),
        "up":    (32,80),
        "down":  (48,80),
        "down-left": (64,80),
        "down-right": (80,80),
        "up-left": (96,80),
        "up-right": (112,80)
    },
    "Wizard": {
        "right": (16,96),
        "left":  (0,96),
        "up":    (48,96),
        "down":  (32,96),
        "down-left": (64,96),
        "down-right": (80,96),
        "up-left": (96,96),
        "up-right": (112,96)
    }
}

# =====================
# MAIN APP
# =====================
class App:
    def __init__(self):
        pyxel.init(WIDTH_TILES * TILE, HEIGHT_TILES * TILE, title="Roguelite")
        pyxel.load("DungeonSlice.pyxres")

        self.state = STATE_SELECT
        self.selected = 0
        self.character = None

        self.player = {}
        self.projectiles = []
        self.dots = set()
        self.tick = 0

        pyxel.run(self.update, self.draw)

    # =====================
    # START GAME
    # =====================
    def start_game(self):
        self.character = CHARACTERS[self.selected]

        self.player = {
            "x": TILE,
            "y": TILE,
            "speed": 1,
            "dir": "down",
            "hp": 10,
            "max_hp": 10,
            "atk": 1,
            "level": 1,
            "xp": 0,
            "xp_need": 10,
            "moving": False,
            "anim": 0,
        }

        self.projectiles = []
        self.tick = 0
        self.dots = self.spawn_dots()
        self.state = STATE_PLAY

    # =====================
    # HELPERS
    # =====================
    def spawn_dots(self):
        return {
            (x * TILE + 4, y * TILE + 4)
            for y in range(HEIGHT_TILES)
            for x in range(WIDTH_TILES)
            if random.random() < 0.12
        }

    def level_up(self):
        self.player["level"] += 1
        self.player["xp"] = 0
        self.player["xp_need"] = int(self.player["xp_need"] * 1.4)
        self.player["atk"] += 1

    def fire_projectile(self, direction=None):
        dir = direction if direction else self.player["dir"]
        dx, dy = DIR_VEL[dir]
        u, v = PROJECTILE_SPRITES[self.character["name"]][dir]

        self.projectiles.append({
            "x": self.player["x"] + CHAR_SIZE//2 - 8,
            "y": self.player["y"] + CHAR_SIZE//2 - 8,
            "dx": dx,
            "dy": dy,
            "u": u,
            "v": v
        })

    # =====================
    # UPDATE
    # =====================
    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        if self.state == STATE_SELECT:
            self.update_select()
        else:
            self.update_game()

    def update_select(self):
        if pyxel.btnp(pyxel.KEY_LEFT):
            self.selected = (self.selected - 1) % len(CHARACTERS)
        if pyxel.btnp(pyxel.KEY_RIGHT):
            self.selected = (self.selected + 1) % len(CHARACTERS)
        if pyxel.btnp(pyxel.KEY_RETURN):
            self.start_game()

    def update_game(self):
        dx = dy = 0
        self.player["moving"] = False

        if pyxel.btn(pyxel.KEY_LEFT):
            dx = -self.player["speed"]
            self.player["dir"] = "left"
            self.player["moving"] = True
        elif pyxel.btn(pyxel.KEY_RIGHT):
            dx = self.player["speed"]
            self.player["dir"] = "right"
            self.player["moving"] = True
        elif pyxel.btn(pyxel.KEY_UP):
            dy = -self.player["speed"]
            self.player["dir"] = "up"
            self.player["moving"] = True
        elif pyxel.btn(pyxel.KEY_DOWN):
            dy = self.player["speed"]
            self.player["dir"] = "down"
            self.player["moving"] = True

        self.player["x"] += dx
        self.player["y"] += dy
        self.player["x"] = max(0, min(self.player["x"], WIDTH_TILES*TILE - CHAR_SIZE))
        self.player["y"] = max(0, min(self.player["y"], HEIGHT_TILES*TILE - CHAR_SIZE))

        # animation
        if self.player["moving"]:
            self.player["anim"] = (pyxel.frame_count // 8) % 2
        else:
            self.player["anim"] = 0

        self.tick += 1

        # idle XP
        if self.tick % 60 == 0:
            self.player["xp"] += self.player["atk"]

        if self.player["xp"] >= self.player["xp_need"]:
            self.level_up()

        # auto fire
        if self.tick % 20 == 0:
            self.fire_projectile()

        # move projectiles
        for p in self.projectiles:
            p["x"] += p["dx"]
            p["y"] += p["dy"]

        self.projectiles = [
            p for p in self.projectiles
            if 0 <= p["x"] <= WIDTH_TILES*TILE and 0 <= p["y"] <= HEIGHT_TILES*TILE
        ]

    # =====================
    # DRAW
    # =====================
    def draw(self):
        pyxel.cls(0)
        if self.state == STATE_SELECT:
            self.draw_select()
        else:
            self.draw_game()

    def draw_select(self):
        pyxel.text(50, 10, "SELECT CHARACTER", 7)
        for i, c in enumerate(CHARACTERS):
            x = 30 + i*32
            y = 40
            pyxel.blt(x, y, 0, 0, c["row_y"], 16, 16, 0)
            pyxel.text(x, y+20, c["name"], 11)
            if i == self.selected:
                pyxel.rectb(x-2, y-2, 20, 20, 10)
        pyxel.text(40, 90, "LEFT/RIGHT", 6)
        pyxel.text(48, 100, "ENTER", 6)

    def draw_game(self):
        for d in self.dots:
            pyxel.circ(d[0], d[1], 1, 11)
        self.draw_player()
        for p in self.projectiles:
            pyxel.blt(p["x"], p["y"], 0, p["u"], p["v"], 16, 16, 0)
        pyxel.text(5,5,f"LV {self.player['level']} XP {self.player['xp']}/{self.player['xp_need']}",7)

    def draw_player(self):
        x = self.player["x"]
        y = self.player["y"]
        row = self.character["row_y"]
        anim = self.player["anim"]
        dir = self.player["dir"]

        if dir == "right":
            u = 16 if anim==0 else 48
        elif dir == "left":
            u = 32 if anim==0 else 64
        else:
            u = 0

        pyxel.blt(x, y, 0, u, row, 8, 8, 0)
        pyxel.blt(x+8, y, 0, u+8, row, 8, 8, 0)
        pyxel.blt(x, y+8, 0, u, row+8, 8, 8, 0)
        pyxel.blt(x+8, y+8, 0, u+8, row+8, 8, 8, 0)

App()
