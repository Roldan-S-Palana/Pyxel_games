import pyxel
import random
import math

# =====================
# CONSTANTS
# =====================
TILE = 8
CHAR_SIZE = 16
WIDTH_TILES = 20
HEIGHT_TILES = 15

STATE_SELECT = 0
STATE_PLAY = 1

# Joystick
JOY_CENTER_X = 40
JOY_CENTER_Y = HEIGHT_TILES * TILE - 40
JOY_RADIUS = 20
JOY_KNOB_RADIUS = 6

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

PROJECTILE_SPRITES = {
    "Archer": {
        "right": (0,64), "left": (16,64), "up": (32,64), "down": (48,64),
        "down-left": (64,64), "down-right": (80,64),
        "up-left": (96,64), "up-right": (112,64)
    },
    "Knight": {
        "right": (16,80), "left": (0,80), "up": (32,80), "down": (48,80),
        "down-left": (64,80), "down-right": (80,80),
        "up-left": (96,80), "up-right": (112,80)
    },
    "Barbarian": {
        "right": (16,80), "left": (0,80), "up": (32,80), "down": (48,80),
        "down-left": (64,80), "down-right": (80,80),
        "up-left": (96,80), "up-right": (112,80)
    },
    "Wizard": {
        "right": (16,96), "left": (0,96), "up": (48,96), "down": (32,96),
        "down-left": (64,96), "down-right": (80,96),
        "up-left": (96,96), "up-right": (112,96)
    }
}

# =====================
# MAIN APP
# =====================
class App:
    def __init__(self):
        pyxel.init(WIDTH_TILES*TILE, HEIGHT_TILES*TILE, title="Roguelite")
        pyxel.load("DungeonSlice.pyxres")
        pyxel.mouse(True)

        self.state = STATE_SELECT
        self.selected = 0
        self.character = None

        self.player = {}
        self.projectiles = []
        self.dots = set()
        self.tick = 0

        # joystick state
        self.joy_dx = 0
        self.joy_dy = 0

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
            (x*TILE+4, y*TILE+4)
            for y in range(HEIGHT_TILES)
            for x in range(WIDTH_TILES)
            if random.random() < 0.12
        }

    def level_up(self):
        self.player["level"] += 1
        self.player["xp"] = 0
        self.player["xp_need"] = int(self.player["xp_need"] * 1.4)
        self.player["atk"] += 1

    def fire_projectile(self):
        dir = self.player["dir"]
        dx, dy = DIR_VEL[dir]
        u, v = PROJECTILE_SPRITES[self.character["name"]][dir]

        self.projectiles.append({
            "x": self.player["x"] + 4,
            "y": self.player["y"] + 4,
            "dx": dx,
            "dy": dy,
            "u": u,
            "v": v
        })

    # =====================
    # JOYSTICK
    # =====================
    def joystick_direction(self):
        self.joy_dx = self.joy_dy = 0

        if not pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
            return None

        mx, my = pyxel.mouse_x, pyxel.mouse_y
        dx = mx - JOY_CENTER_X
        dy = my - JOY_CENTER_Y
        dist = math.sqrt(dx*dx + dy*dy)

        if dist > JOY_RADIUS:
            return None

        self.joy_dx = dx / JOY_RADIUS
        self.joy_dy = dy / JOY_RADIUS

        angle = math.degrees(math.atan2(-dy, dx)) % 360

        if 22.5 <= angle < 67.5: return "up-right"
        if 67.5 <= angle < 112.5: return "up"
        if 112.5 <= angle < 157.5: return "up-left"
        if 157.5 <= angle < 202.5: return "left"
        if 202.5 <= angle < 247.5: return "down-left"
        if 247.5 <= angle < 292.5: return "down"
        if 292.5 <= angle < 337.5: return "down-right"
        return "right"

    # =====================
    # UPDATE
    # =====================
    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        if self.state == STATE_SELECT:
            if pyxel.btnp(pyxel.KEY_LEFT):
                self.selected = (self.selected - 1) % len(CHARACTERS)
            if pyxel.btnp(pyxel.KEY_RIGHT):
                self.selected = (self.selected + 1) % len(CHARACTERS)
            if pyxel.btnp(pyxel.KEY_RETURN):
                self.start_game()
        else:
            self.update_game()

    def update_game(self):
        dir = self.joystick_direction()
        self.player["moving"] = False

        if dir:
            self.player["dir"] = dir
            vx, vy = DIR_VEL[dir]
            self.player["x"] += vx
            self.player["y"] += vy
            self.player["moving"] = True

        self.player["x"] = max(0, min(self.player["x"], WIDTH_TILES*TILE-CHAR_SIZE))
        self.player["y"] = max(0, min(self.player["y"], HEIGHT_TILES*TILE-CHAR_SIZE))

        self.player["anim"] = (pyxel.frame_count//8)%2 if self.player["moving"] else 0

        self.tick += 1

        if self.tick % 60 == 0:
            self.player["xp"] += self.player["atk"]

        if self.player["xp"] >= self.player["xp_need"]:
            self.level_up()

        if self.tick % 20 == 0:
            self.fire_projectile()

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
            pyxel.text(40,10,"SELECT CHARACTER",7)
            for i,c in enumerate(CHARACTERS):
                x = 30+i*32
                pyxel.blt(x,40,0,0,c["row_y"],16,16,0)
                pyxel.text(x,60,c["name"],11)
                if i == self.selected:
                    pyxel.rectb(x-2,38,20,20,10)
        else:
            for d in self.dots:
                pyxel.circ(d[0],d[1],1,11)

            for p in self.projectiles:
                pyxel.blt(p["x"],p["y"],0,p["u"],p["v"],16,16,0)

            pyxel.text(5,5,f"LV {self.player['level']} XP {self.player['xp']}/{self.player['xp_need']}",7)
            self.draw_player()
            self.draw_joystick()

    def draw_player(self):
        x,y = self.player["x"], self.player["y"]
        row = self.character["row_y"]
        anim = self.player["anim"]

        if self.player["dir"].endswith("right"):
            u = 16 if anim==0 else 48
        elif self.player["dir"].endswith("left"):
            u = 32 if anim==0 else 64
        else:
            u = 0

        for ox in (0,8):
            for oy in (0,8):
                pyxel.blt(x+ox,y+oy,0,u+ox,row+oy,8,8,0)

    def draw_joystick(self):
        pyxel.circ(JOY_CENTER_X,JOY_CENTER_Y,JOY_RADIUS,5)
        kx = JOY_CENTER_X + int(self.joy_dx*(JOY_RADIUS-6))
        ky = JOY_CENTER_Y + int(self.joy_dy*(JOY_RADIUS-6))
        pyxel.circ(kx,ky,JOY_KNOB_RADIUS,10)

App()
