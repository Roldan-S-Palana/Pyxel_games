import pyxel
import math
import random

TILE = 8
WIDTH_TILES = 20
HEIGHT_TILES = 7
WALL_PROB = 0.2  # 20% chance a tile becomes a wall

class Ghost:
    def __init__(self, x, y, color=8):
        self.x = x
        self.y = y
        self.dir_x = random.choice([-1,0,1])
        self.dir_y = random.choice([-1,0,1])
        self.color = color
        self.speed = 1
        self.alive = True

    def can_move(self, x, y, tilemap):
        tile_x = x // TILE
        tile_y = y // TILE
        if tile_y < 0 or tile_y >= len(tilemap):
            return False
        if tile_x < 0 or tile_x >= len(tilemap[0]):
            return False
        return tilemap[tile_y][tile_x] == 0

    def update(self, tilemap):
        if not self.alive:
            return
        next_x = self.x + self.dir_x * self.speed
        next_y = self.y + self.dir_y * self.speed
        if self.can_move(next_x, next_y, tilemap):
            self.x = next_x
            self.y = next_y
        else:
            directions = [(-1,0),(1,0),(0,-1),(0,1)]
            random.shuffle(directions)
            for dx, dy in directions:
                if self.can_move(self.x + dx*self.speed, self.y + dy*self.speed, tilemap):
                    self.dir_x, self.dir_y = dx, dy
                    break

    def draw(self):
        if self.alive:
            pyxel.rect(self.x, self.y, TILE, TILE, self.color)

class App:
    def __init__(self):
        pyxel.init(160, 120, title="Pac-Man Random Maze")
        self.level = 1
        self.generate_maze()
        self.x = 1 * TILE
        self.y = 1 * TILE
        self.dir_x = 0
        self.dir_y = 0
        self.next_dir_x = 0
        self.next_dir_y = 0
        self.speed = 1

        # Ghosts
        self.ghosts = [Ghost(9*TILE, 3*TILE, color=8), Ghost(10*TILE, 3*TILE, color=12)]

        # Power-up
        self.powered_up = False
        self.power_timer = 0
        self.power_duration = 5

        pyxel.run(self.update, self.draw)

    def generate_maze(self):
        self.tilemap = []
        for y in range(HEIGHT_TILES):
            row = []
            for x in range(WIDTH_TILES):
                if x==0 or y==0 or x==WIDTH_TILES-1 or y==HEIGHT_TILES-1:
                    row.append(1)  # border
                else:
                    # Keep start area free
                    if (x,y) in [(1,1),(2,1),(1,2)]:
                        row.append(0)
                    else:
                        row.append(1 if random.random() < WALL_PROB else 0)
            self.tilemap.append(row)

        # Food dots and power pellets
        self.dots = set()
        self.power_pellets = set()
        for row_idx, row in enumerate(self.tilemap):
            for col_idx, tile in enumerate(row):
                if tile == 0:
                    self.dots.add((col_idx*TILE + TILE//2, row_idx*TILE + TILE//2))
        # Pick 4 random power pellets
        open_tiles = list(self.dots)
        self.power_pellets = set(random.sample(open_tiles, min(4, len(open_tiles))))

    def is_centered(self):
        return self.x % TILE == 0 and self.y % TILE == 0

    def can_move(self, x, y):
        tile_x = x // TILE
        tile_y = y // TILE
        if tile_y < 0 or tile_y >= len(self.tilemap):
            return False
        if tile_x < 0 or tile_x >= len(self.tilemap[0]):
            return False
        return self.tilemap[tile_y][tile_x] == 0

    def eat_dot(self):
        pac_center = (self.x + TILE//2, self.y + TILE//2)
        if pac_center in self.dots:
            self.dots.remove(pac_center)
        if pac_center in self.power_pellets:
            self.power_pellets.remove(pac_center)
            self.powered_up = True
            self.power_timer = pyxel.frame_count

    def check_collision(self):
        for ghost in self.ghosts:
            if not ghost.alive:
                continue
            if abs(self.x - ghost.x) < TILE and abs(self.y - ghost.y) < TILE:
                if self.powered_up:
                    ghost.alive = False
                else:
                    print("Pac-Man got caught!")
                    pyxel.quit()

    def update(self):
        if pyxel.btn(pyxel.KEY_LEFT): self.next_dir_x, self.next_dir_y = -1,0
        elif pyxel.btn(pyxel.KEY_RIGHT): self.next_dir_x, self.next_dir_y = 1,0
        elif pyxel.btn(pyxel.KEY_UP): self.next_dir_x, self.next_dir_y = 0,-1
        elif pyxel.btn(pyxel.KEY_DOWN): self.next_dir_x, self.next_dir_y = 0,1

        if self.is_centered():
            next_x = self.x + self.next_dir_x*self.speed
            next_y = self.y + self.next_dir_y*self.speed
            if self.can_move(next_x, next_y):
                self.dir_x = self.next_dir_x
                self.dir_y = self.next_dir_y

        next_x = self.x + self.dir_x*self.speed
        next_y = self.y + self.dir_y*self.speed
        if self.can_move(next_x, next_y):
            self.x = next_x
            self.y = next_y

        self.eat_dot()

        for ghost in self.ghosts:
            ghost.update(self.tilemap)

        self.check_collision()

        # Power-up timer
        if self.powered_up:
            if (pyxel.frame_count - self.power_timer)/30 >= 5:
                self.powered_up = False

        # Level up when dots cleared
        if not self.dots:
            self.level += 1
            print(f"Level {self.level}!")
            self.generate_maze()
            self.x = 1*TILE
            self.y = 1*TILE
            for ghost in self.ghosts:
                ghost.alive = True
                ghost.x = 9*TILE
                ghost.y = 3*TILE

        if pyxel.btnp(pyxel.KEY_Q): pyxel.quit()

    def draw(self):
        pyxel.cls(0)
        # Draw walls
        for row_idx, row in enumerate(self.tilemap):
            for col_idx, tile in enumerate(row):
                if tile == 1:
                    pyxel.rect(col_idx*TILE, row_idx*TILE, TILE, TILE, 9)

        # Draw dots
        for dot_x, dot_y in self.dots:
            pyxel.circ(dot_x, dot_y, 1, 11)
        # Draw power pellets
        for px, py in self.power_pellets:
            pyxel.circ(px, py, 2, 14)

        # Draw Pac-Man
        pac_radius = TILE//2
        cx = self.x + pac_radius
        cy = self.y + pac_radius
        mouth_open = math.sin(pyxel.frame_count*0.2)*0.25
        if self.dir_x==1: start=-mouth_open; end=mouth_open
        elif self.dir_x==-1: start=math.pi-mouth_open; end=math.pi+mouth_open
        elif self.dir_y==-1: start=-math.pi/2-mouth_open; end=-math.pi/2+mouth_open
        elif self.dir_y==1: start=math.pi/2-mouth_open; end=math.pi/2+mouth_open
        else: start=-mouth_open; end=mouth_open
        pyxel.circ(cx,cy,pac_radius,10)
        pyxel.tri(cx,cy,
                  cx + pac_radius*math.cos(start),
                  cy + pac_radius*math.sin(start),
                  cx + pac_radius*math.cos(end),
                  cy + pac_radius*math.sin(end),
                  0)

        # Draw ghosts
        for ghost in self.ghosts:
            ghost.draw()

App()
