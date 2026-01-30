import pyxel
import random

# =====================
# CONSTANTS
# =====================
TILE = 8
WIDTH_TILES = 20        # 160px
HEIGHT_TILES = 15       # 120px
WALL_PROB = 0.1

# =====================
# GHOST CLASS
# =====================
class Ghost:
    def __init__(self, x, y):
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = y
        # Pick a random direction but never (0,0)
        self.dir_x, self.dir_y = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
        self.speed = 1
        self.alive = True

    def can_move(self, x, y, tilemap):
        for dx in (0, TILE-1):
            for dy in (0, TILE-1):
                tx = (x + dx) // TILE
                ty = (y + dy) // TILE
                if tilemap[ty][tx] == 1:
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
            # Pick a new direction
            dirs = [(1,0), (-1,0), (0,1), (0,-1)]
            random.shuffle(dirs)
            for dx, dy in dirs:
                if self.can_move(self.x + dx * self.speed, self.y + dy * self.speed, tilemap):
                    self.dir_x, self.dir_y = dx, dy
                    break

    def respawn(self):
        self.x = self.start_x
        self.y = self.start_y
        self.dir_x, self.dir_y = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
        self.alive = True

    def draw(self, frightened=False):
        if not self.alive:
            return

        u = 8 if frightened else 0
        v = 8
        pyxel.blt(self.x, self.y, 0, u, v, 8, 8, 0)


# =====================
# MAIN GAME
# =====================
class App:
    def __init__(self):
        pyxel.init(160, 120, title="Pac-Man Sprite Edition")
        pyxel.load("pacman.pyxres")

        self.level = 1
        self.score = 0
        self.lives = 3

        self.powered = False
        self.power_start = 0
        self.power_duration = 5 * 30

        self.invincible = False
        self.inv_start = 0

        self.generate_maze()
        self.reset_player()

        # Ghosts spawn
        self.ghosts = [
            Ghost(9*TILE, 7*TILE),
            Ghost(10*TILE, 7*TILE)
        ]

        pyxel.run(self.update, self.draw)

    # =====================
    # SETUP
    # =====================
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
                # Borders are always walls
                if x == 0 or y == 0 or x == WIDTH_TILES-1 or y == HEIGHT_TILES-1:
                    row.append(1)
                else:
                    row.append(1 if random.random() < WALL_PROB else 0)
            self.tilemap.append(row)

        self.tilemap[1][1] = 0  # starting position

        self.dots = set()
        for y in range(HEIGHT_TILES):
            for x in range(WIDTH_TILES):
                if self.tilemap[y][x] == 0:
                    self.dots.add((x*TILE+4, y*TILE+4))

        # Make sure no dot is completely boxed by walls
        safe_dots = set()
        for x, y in self.dots:
            tx, ty = x//TILE, y//TILE
            neighbors = [
                self.tilemap[ty-1][tx],
                self.tilemap[ty+1][tx],
                self.tilemap[ty][tx-1],
                self.tilemap[ty][tx+1]
            ]
            if neighbors.count(1) < 4:
                safe_dots.add((x, y))
        self.dots = safe_dots

        # Power pellets
        self.power_pellets = set(random.sample(list(self.dots), min(4, len(self.dots))))

    # =====================
    # COLLISION
    # =====================
    def can_move(self, x, y):
        for dx in (0, TILE-1):
            for dy in (0, TILE-1):
                tx = (x + dx) // TILE
                ty = (y + dy) // TILE
                if self.tilemap[ty][tx] == 1:
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
            if abs(self.x - g.x) < TILE and abs(self.y - g.y) < TILE:
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

        if self.centered():
            nx = self.x + self.next_dir_x
            ny = self.y + self.next_dir_y
            if self.can_move(nx, ny):
                self.dir_x = self.next_dir_x
                self.dir_y = self.next_dir_y

        nx = self.x + self.dir_x
        ny = self.y + self.dir_y
        if self.can_move(nx, ny):
            self.x = nx
            self.y = ny

        self.eat()

        for g in self.ghosts:
            g.update(self.tilemap)

        self.check_ghosts()

        if self.powered and pyxel.frame_count - self.power_start > self.power_duration:
            self.powered = False

        if self.invincible and pyxel.frame_count - self.inv_start > 60:
            self.invincible = False

        if not self.dots:
            self.level += 1
            self.generate_maze()
            self.reset_player()
            for g in self.ghosts:
                g.respawn()

        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

    # =====================
    # DRAW
    # =====================
    def draw(self):
        pyxel.cls(0)

        # Draw walls
        for y in range(HEIGHT_TILES):
            for x in range(WIDTH_TILES):
                if self.tilemap[y][x] == 1:
                    pyxel.rect(x*TILE, y*TILE, TILE, TILE, 9)

        # Draw dots
        for d in self.dots:
            pyxel.circ(d[0], d[1], 1, 11)

        for p in self.power_pellets:
            pyxel.circ(p[0], p[1], 2, 14)
            
        # =====================
        # Pac-Man sprite
        # =====================
        pacman_sprites = {
            "right": (0, 8, 0),
            "left":  (16, 24, 0),
            "up":    (32, 40, 0),
            "down":  (48, 56, 0)
        }

        if self.dir_x > 0:
            direction = "right"
        elif self.dir_x < 0:
            direction = "left"
        elif self.dir_y < 0:
            direction = "up"
        elif self.dir_y > 0:
            direction = "down"
        else:
            direction = "right"

        mouth_frame = (pyxel.frame_count // 5) % 2
        u_closed, u_open, v = pacman_sprites[direction]
        u = u_open if mouth_frame else u_closed
        pyxel.blt(self.x, self.y, 0, u, v, 8, 8, 0)

        # =====================
        # Ghosts
        # =====================
        for g in self.ghosts:
            g.draw(self.powered)

        # =====================
        # UI
        # =====================
        pyxel.text(5, 5, f"SCORE {self.score}", 7)
        pyxel.text(5, 14, f"LIVES {self.lives}", 8)
        pyxel.text(120, 5, f"LV {self.level}", 7)


# =====================
App()
