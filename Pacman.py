import pyxel
import random

# =====================
# CONSTANTS
# =====================
TILE = 8
WIDTH_TILES = 20
HEIGHT_TILES = 15
WALL_PROB = 0.1

# =====================
# GHOST CLASS
# =====================
class Ghost:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dir_x, self.dir_y = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
        self.speed = 1
        self.alive = True

    def can_move(self, x, y, tilemap):
        for dx in (0, TILE-1):
            for dy in (0, TILE-1):
                if tilemap[(y+dy)//TILE][(x+dx)//TILE] == 1:
                    return False
        return True

    def update(self, tilemap):
        if not self.alive:
            return

        nx = self.x + self.dir_x * self.speed
        ny = self.y + self.dir_y * self.speed

        if self.can_move(nx, ny, tilemap):
            self.x = nx
            self.y = ny
        else:
            random.shuffle(DIRS := [(1,0), (-1,0), (0,1), (0,-1)])
            for dx, dy in DIRS:
                if self.can_move(self.x+dx, self.y+dy, tilemap):
                    self.dir_x, self.dir_y = dx, dy
                    break

    def draw(self, frightened=False):
        if not self.alive:
            return
        u = 8 if frightened else 0
        pyxel.blt(self.x, self.y, 0, u, 8, 8, 8, 0)

# =====================
# MAIN GAME
# =====================
class App:
    def __init__(self):
        pyxel.init(160, 120, title="Pac-Man Sprite Edition")
        pyxel.load("pacman.pyxres")

        self.score = 0
        self.lives = 3

        self.powered = False
        self.power_start = 0
        self.power_duration = 5 * 30

        self.invincible = False
        self.inv_start = 0

        self.generate_maze()
        self.reset_player()

        # Spawn ghosts SAFELY
        self.ghosts = [
            Ghost(*self.find_empty_tile()),
            Ghost(*self.find_empty_tile())
        ]

        # =====================
        # MUSIC (NEW PYXEL API)
        # =====================
        pyxel.sounds[0].set(
            notes="c3d3e3g3 c4g3e3c3",
            tones="SSSSSSSS",
            volumes="77777777",
            effects="NNNNNNNN",
            speed=7
        )
        pyxel.musics[0].set([0, 0, 0, 0])
        pyxel.playm(0, loop=True)

        pyxel.run(self.update, self.draw)

    # =====================
    # HELPERS
    # =====================
    def find_empty_tile(self):
        while True:
            x = random.randint(1, WIDTH_TILES-2)
            y = random.randint(1, HEIGHT_TILES-2)
            if self.tilemap[y][x] == 0:
                return x*TILE, y*TILE

    def reset_player(self):
        self.x = TILE
        self.y = TILE
        self.dir_x = 0
        self.dir_y = 0
        self.next_dir_x = 0
        self.next_dir_y = 0

    def generate_maze(self):
        self.tilemap = []
        for y in range(HEIGHT_TILES):
            row = []
            for x in range(WIDTH_TILES):
                if x == 0 or y == 0 or x == WIDTH_TILES-1 or y == HEIGHT_TILES-1:
                    row.append(1)
                else:
                    row.append(1 if random.random() < WALL_PROB else 0)
            self.tilemap.append(row)

        self.tilemap[1][1] = 0

        self.dots = {
            (x*TILE+4, y*TILE+4)
            for y in range(HEIGHT_TILES)
            for x in range(WIDTH_TILES)
            if self.tilemap[y][x] == 0
        }

        self.power_pellets = set(random.sample(list(self.dots), min(4, len(self.dots))))

    def can_move(self, x, y):
        for dx in (0, TILE-1):
            for dy in (0, TILE-1):
                if self.tilemap[(y+dy)//TILE][(x+dx)//TILE] == 1:
                    return False
        return True

    def centered(self):
        return self.x % TILE == 0 and self.y % TILE == 0

    # =====================
    # GAME LOGIC
    # =====================
    def eat(self):
        pos = (self.x+4, self.y+4)
        if pos in self.dots:
            self.dots.remove(pos)
            self.score += 10
        if pos in self.power_pellets:
            self.power_pellets.remove(pos)
            self.powered = True
            self.power_start = pyxel.frame_count

    def check_ghosts(self):
        for g in self.ghosts:
            if not g.alive:
                continue
            if abs(self.x-g.x) < TILE and abs(self.y-g.y) < TILE:
                if self.powered:
                    g.alive = False
                    self.score += 50
                elif not self.invincible:
                    self.lives -= 1
                    self.invincible = True
                    self.inv_start = pyxel.frame_count
                    self.reset_player()
                    if self.lives <= 0:
                        pyxel.quit()

    # =====================
    # UPDATE
    # =====================
    def update(self):
        if pyxel.btn(pyxel.KEY_LEFT):  self.next_dir_x, self.next_dir_y = -1,0
        if pyxel.btn(pyxel.KEY_RIGHT): self.next_dir_x, self.next_dir_y = 1,0
        if pyxel.btn(pyxel.KEY_UP):    self.next_dir_x, self.next_dir_y = 0,-1
        if pyxel.btn(pyxel.KEY_DOWN):  self.next_dir_x, self.next_dir_y = 0,1

        if self.centered() and self.can_move(self.x+self.next_dir_x, self.y+self.next_dir_y):
            self.dir_x, self.dir_y = self.next_dir_x, self.next_dir_y

        if self.can_move(self.x+self.dir_x, self.y+self.dir_y):
            self.x += self.dir_x
            self.y += self.dir_y

        self.eat()
        for g in self.ghosts:
            g.update(self.tilemap)
        self.check_ghosts()

        if self.powered and pyxel.frame_count - self.power_start > self.power_duration:
            self.powered = False

        if self.invincible and pyxel.frame_count - self.inv_start > 60:
            self.invincible = False

    # =====================
    # DRAW
    # =====================
    def draw(self):
        pyxel.cls(0)

        for y in range(HEIGHT_TILES):
            for x in range(WIDTH_TILES):
                if self.tilemap[y][x] == 1:
                    # Draw your wall sprite at 0,16 instead of rectangle
                    pyxel.blt(x*TILE, y*TILE, 0, 0, 16, TILE, TILE, 0)

        for d in self.dots:
            pyxel.circ(d[0], d[1], 1, 11)
        for p in self.power_pellets:
            pyxel.circ(p[0], p[1], 2, 14)

        pacman = {
            "right": (0, 8),
            "left":  (16, 24),
            "up":    (32, 40),
            "down":  (48, 56)
        }

        if self.dir_x > 0:   direction = "right"
        elif self.dir_x < 0: direction = "left"
        elif self.dir_y < 0: direction = "up"
        elif self.dir_y > 0: direction = "down"
        else:               direction = "right"

        mouth = (pyxel.frame_count // 5) % 2
        u_closed, u_open = pacman[direction]
        u = u_open if mouth else u_closed

        pyxel.blt(self.x, self.y, 0, u, 0, 8, 8, 0)

        for g in self.ghosts:
            g.draw(self.powered)

        pyxel.text(5, 5, f"SCORE {self.score}", 7)
        pyxel.text(5, 14, f"LIVES {self.lives}", 8)


# =====================
App()
