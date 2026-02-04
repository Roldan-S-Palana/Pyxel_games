import pyxel
import random

# ======================
# CONFIG
# ======================
TILE = 8
MAP_W = 16
MAP_H = 16

IMG_WORLD = 0  # Image bank for tiles
IMG_PLAYER = 1  # Image bank for player
IMG_ENEMY = 2   # Image bank for enemies

DIR_DOWN = 0
DIR_LEFT = 1
DIR_RIGHT = 2
DIR_UP = 3

STATE_IDLE = 0
STATE_WALK = 1
STATE_ATTACK = 2
STATE_SWIPE = 3

STATES_PER_DIR = 4

# ======================
# MAP MATH - Sprite positions in Image0
# ======================
MAP1_OFFSET = 0
MAP2_OFFSET = 16

SPRITE_FLOOR = 0
SPRITE_WALL = 1
SPRITE_WALL2 = 2
SPRITE_PELLET = 3

PORTAL_FRAMES = 4
SPRITE_PORTAL_FRONT = 4
SPRITE_PORTAL_LEFT = 5
SPRITE_PORTAL_RIGHT = 6

# ======================
# COLORS
# ======================
COLOR_FLOOR = 1      # Dark floor
COLOR_WALL = 6       # Stone gray wall
COLOR_WALL2 = 13     # Darker stone wall
COLOR_BORDER = 8     # Dark blue border
COLOR_PELLET = 10    # Yellow pellet
COLOR_PORTAL = 9     # Magenta portal

# ======================
# ENEMY SPRITE MATH (Image Bank 2)
# ======================
# Row 0: empty
# Row 1 (UP): Walk Walk2 Walk3 Walk4
# Row 2 (DOWN Idle): Idle Idle2 Idle3 Idle4
# Row 3 (DOWN Walk): Walk Walk2 Walk3 Walk4
# Row 4 (DOWN Attack): Attack Attack2 Attack3 Attack4
# Row 5 (DOWN Swipe): Swipe Swipe2 Swipe3 Swipe4
# Row 6 (LEFT Idle): Idle Idle2 Idle3 Idle4
# Row 7 (LEFT Walk): Walk Walk2 Walk3 Walk4
# Row 8 (LEFT Attack): Attack Attack2 Attack3 Attack4
# Row 9 (LEFT Swipe): Swipe Swipe2 Swipe3 Swipe4
# Row 10 (RIGHT Idle): Idle Idle2 Idle3 Idle4
# Row 11 (RIGHT Walk): Walk Walk2 Walk3 Walk4
# Row 12 (RIGHT Attack): Attack Attack2 Attack3 Attack4
# Row 13 (RIGHT Swipe): Swipe Swipe2 Swipe3 Swipe4

ENEMY_ROW_UP = 1
ENEMY_ROW_DOWN_IDLE = 2
ENEMY_ROW_DOWN_WALK = 3
ENEMY_ROW_DOWN_ATTACK = 4
ENEMY_ROW_DOWN_SWIPE = 5
ENEMY_ROW_LEFT_IDLE = 6
ENEMY_ROW_LEFT_WALK = 7
ENEMY_ROW_LEFT_ATTACK = 8
ENEMY_ROW_LEFT_SWIPE = 9
ENEMY_ROW_RIGHT_IDLE = 10
ENEMY_ROW_RIGHT_WALK = 11
ENEMY_ROW_RIGHT_ATTACK = 12
ENEMY_ROW_RIGHT_SWIPE = 13


class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.screen_x = x * TILE
        self.screen_y = y * TILE
        self.dir = DIR_DOWN
        self.state = STATE_IDLE
        self.speed = 1
        self.hp = 3
        self.alive = True
        self.move_timer = 0
        self.move_delay = 30  # frames between moves
        self.attack_cooldown = 0
        self.attacking = False  # Currently performing swipe attack
        self.attack_timer = 0
        self.attack_duration = 15  # frames swipe lasts
        self.damage_cooldown = 0  # 1000ms = 60 frames (at 60fps)
        self.damage_cooldown_time = 60
        
    def get_enemy_row(self):
        """Math: Get sprite row based on direction and state"""
        rows = {
            (DIR_UP, STATE_IDLE): ENEMY_ROW_UP,
            (DIR_UP, STATE_WALK): ENEMY_ROW_UP,
            (DIR_DOWN, STATE_IDLE): ENEMY_ROW_DOWN_IDLE,
            (DIR_DOWN, STATE_WALK): ENEMY_ROW_DOWN_WALK,
            (DIR_DOWN, STATE_ATTACK): ENEMY_ROW_DOWN_ATTACK,
            (DIR_DOWN, STATE_SWIPE): ENEMY_ROW_DOWN_SWIPE,
            (DIR_LEFT, STATE_IDLE): ENEMY_ROW_LEFT_IDLE,
            (DIR_LEFT, STATE_WALK): ENEMY_ROW_LEFT_WALK,
            (DIR_LEFT, STATE_ATTACK): ENEMY_ROW_LEFT_ATTACK,
            (DIR_LEFT, STATE_SWIPE): ENEMY_ROW_LEFT_SWIPE,
            (DIR_RIGHT, STATE_IDLE): ENEMY_ROW_RIGHT_IDLE,
            (DIR_RIGHT, STATE_WALK): ENEMY_ROW_RIGHT_WALK,
            (DIR_RIGHT, STATE_ATTACK): ENEMY_ROW_RIGHT_ATTACK,
            (DIR_RIGHT, STATE_SWIPE): ENEMY_ROW_RIGHT_SWIPE,
        }
        return rows.get((self.dir, self.state), ENEMY_ROW_DOWN_IDLE)
    
    def get_attack_pos(self):
        """Get the tile position for the swipe attack (1 tile in front)"""
        if self.dir == DIR_LEFT:
            return (self.x - 1, self.y)
        elif self.dir == DIR_RIGHT:
            return (self.x + 1, self.y)
        elif self.dir == DIR_UP:
            return (self.x, self.y - 1)
        elif self.dir == DIR_DOWN:
            return (self.x, self.y + 1)
        return (self.x, self.y)
    
    def update(self, player_x, player_y, walls, enemies):
        if not self.alive:
            return
        
        # Update damage cooldown
        if self.damage_cooldown > 0:
            self.damage_cooldown -= 1
        
        # Handle attack animation timer
        if self.attacking:
            self.attack_timer -= 1
            if self.attack_timer <= 0:
                self.attacking = False
                self.state = STATE_IDLE
            return
        
        # Move towards player
        self.move_timer += 1
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            self.state = STATE_IDLE
        elif self.move_timer >= self.move_delay:
            self.move_timer = 0
            
            # Calculate direction to player
            if player_x < self.x:
                self.dir = DIR_LEFT
            elif player_x > self.x:
                self.dir = DIR_RIGHT
            elif player_y < self.y:
                self.dir = DIR_UP
            elif player_y > self.y:
                self.dir = DIR_DOWN
            
            # Check if player is 1 tile away - ATTACK!
            dist = abs(player_x - self.x) + abs(player_y - self.y)
            if dist == 1:
                # Player is in attack range - SWIPE!
                self.state = STATE_SWIPE
                self.attacking = True
                self.attack_timer = self.attack_duration
                return
            
            # Try to move
            dx = dy = 0
            if self.dir == DIR_LEFT:
                dx = -1
            elif self.dir == DIR_RIGHT:
                dx = 1
            elif self.dir == DIR_UP:
                dy = -1
            elif self.dir == DIR_DOWN:
                dy = 1
            
            # Check collision
            new_x = self.x + dx
            new_y = self.y + dy
            
            if not self.is_wall(new_x, new_y, walls):
                self.x = new_x
                self.y = new_y
                self.state = STATE_WALK
            else:
                self.state = STATE_IDLE
        
        # Smooth screen movement
        target_x = self.x * TILE
        target_y = self.y * TILE
        if self.screen_x < target_x:
            self.screen_x = min(self.screen_x + self.speed, target_x)
        elif self.screen_x > target_x:
            self.screen_x = max(self.screen_x - self.speed, target_x)
        if self.screen_y < target_y:
            self.screen_y = min(self.screen_y + self.speed, target_y)
        elif self.screen_y > target_y:
            self.screen_y = max(self.screen_y - self.speed, target_y)
    
    def is_wall(self, x, y, walls):
        if x < 0 or y < 0 or x >= MAP_W or y >= MAP_H:
            return True
        return (x, y) in walls
    
    def player_in_attack_range(self, px, py):
        """Check if player is in the swipe attack zone"""
        ax, ay = self.get_attack_pos()
        return px == ax and py == ay
    
    def can_damage_player(self):
        """Check if enemy can damage player (1000ms cooldown)"""
        return self.damage_cooldown <= 0
    
    def reset_damage_cooldown(self):
        """Reset damage cooldown after dealing damage"""
        self.damage_cooldown = self.damage_cooldown_time


class Game:
    def __init__(self):
        pyxel.init(MAP_W * TILE, MAP_H * TILE, title="Dungeon Crawler")
        pyxel.load("Dungeon.pyxres")
        
        self.level = 1
        self.score = 0
        
        # Generate first level
        self.generate_level()
        
        pyxel.run(self.update, self.draw)
    
    def generate_level(self):
        """Generate random dungeon level"""
        # Initialize empty map
        self.walls = set()
        
        # Add border walls
        for x in range(MAP_W):
            self.walls.add((x, 0))
            self.walls.add((x, MAP_H - 1))
        for y in range(MAP_H):
            self.walls.add((0, y))
            self.walls.add((MAP_W - 1, y))
        
        # Add random internal walls
        num_walls = random.randint(20, 40)
        for _ in range(num_walls):
            x = random.randint(1, MAP_W - 2)
            y = random.randint(1, MAP_H - 2)
            self.walls.add((x, y))
        
        # Initialize collections before finding spots
        self.enemies = []
        self.pellet_positions = []
        
        # Place player (find empty spot)
        self.px, self.py = self.find_empty_spot()
        self.screen_x = self.px * TILE
        self.screen_y = self.py * TILE
        self.dir = DIR_DOWN
        self.state = STATE_IDLE
        self.speed = 2
        
        self.portal_x, self.portal_y = self.find_empty_spot(min_dist=5)
        self.portal_active = False
        
        # Place enemies
        num_enemies = 2 + self.level  # More enemies per level
        for _ in range(num_enemies):
            ex, ey = self.find_empty_spot(min_dist=3)
            self.enemies.append(Enemy(ex, ey))
        
        # Count pellets (optional objective)
        self.pellets = 0
        self.pellet_positions = []
        for _ in range(5 + self.level):
            px, py = self.find_empty_spot()
            self.pellet_positions.append((px, py))
            self.pellets += 1
    
    def find_empty_spot(self, min_dist=0):
        """Find random empty tile, optionally far from player"""
        while True:
            x = random.randint(1, MAP_W - 2)
            y = random.randint(1, MAP_H - 2)
            if (x, y) not in self.walls:
                # Check distance from player
                if min_dist > 0:
                    dist = abs(x - self.px) + abs(y - self.py)
                    if dist < min_dist:
                        continue
                
                # Check distance from other objects
                too_close = False
                for ex, ey in self.pellet_positions:
                    if abs(x - ex) + abs(y - ey) < 2:
                        too_close = True
                        break
                for enemy in self.enemies:
                    if abs(x - enemy.x) + abs(y - enemy.y) < 2:
                        too_close = True
                        break
                if not too_close:
                    return (x, y)
    
    def update(self):
        # Player movement
        self.update_player()
        
        # Check pellets
        self.check_pellets()
        
        # Update portal
        self.check_portal()
        
        # Update enemies
        for enemy in self.enemies:
            enemy.update(self.px, self.py, self.walls, self.enemies)
        
        # Smooth screen movement
        self.update_screen_pos()
        
        # Check enemy collisions
        self.check_enemy_collisions()
    
    def update_player(self):
        # Only move if player has reached center of tile
        if self.screen_x == self.px * TILE and self.screen_y == self.py * TILE:
            dx, dy = 0, 0
            if pyxel.btn(pyxel.KEY_UP):
                dx, dy = 0, -1
                self.dir = DIR_UP
            elif pyxel.btn(pyxel.KEY_DOWN):
                dx, dy = 0, 1
                self.dir = DIR_DOWN
            elif pyxel.btn(pyxel.KEY_LEFT):
                dx, dy = -1, 0
                self.dir = DIR_LEFT
            elif pyxel.btn(pyxel.KEY_RIGHT):
                dx, dy = 1, 0
                self.dir = DIR_RIGHT
            elif pyxel.btn(pyxel.KEY_SPACE):
                # Attack
                self.state = STATE_ATTACK
                self.attack_enemies()
                return
            elif pyxel.btn(pyxel.KEY_Z):
                # Swipe
                self.state = STATE_SWIPE
                self.attack_enemies()
                return
            
            # Check wall collision
            if dx != 0 or dy != 0:
                if not self.is_wall(self.px + dx, self.py + dy):
                    self.px += dx
                    self.py += dy
                    self.state = STATE_WALK
                else:
                    self.state = STATE_IDLE
            else:
                self.state = STATE_IDLE
        else:
            # Player is still moving
            self.state = STATE_WALK
    
    def attack_enemies(self):
        """Attack enemies in front of player"""
        attack_range = 1
        for enemy in self.enemies:
            if not enemy.alive:
                continue
            
            # Calculate enemy position relative to player
            ex, ey = enemy.x, enemy.y
            dx = ex - self.px
            dy = ey - self.py
            
            # Check if enemy is in attack range and direction
            in_range = abs(dx) <= attack_range and abs(dy) <= attack_range
            if not in_range:
                continue
            
            # Check direction match
            if self.dir == DIR_UP and dy < 0 and abs(dx) <= 1:
                enemy.hp -= 1
            elif self.dir == DIR_DOWN and dy > 0 and abs(dx) <= 1:
                enemy.hp -= 1
            elif self.dir == DIR_LEFT and dx < 0 and abs(dy) <= 1:
                enemy.hp -= 1
            elif self.dir == DIR_RIGHT and dx > 0 and abs(dy) <= 1:
                enemy.hp -= 1
            
            # Check if enemy died
            if enemy.hp <= 0:
                enemy.alive = False
                self.score += 100
                # Remove dead enemies
                self.enemies = [e for e in self.enemies if e.alive]
    
    def check_enemy_collisions(self):
        """Check if player is in enemy attack range"""
        for enemy in self.enemies:
            if enemy.alive:
                # Check if player is on same tile (collision)
                if self.px == enemy.x and self.py == enemy.y:
                    if enemy.can_damage_player():
                        self.score -= 10
                        enemy.reset_damage_cooldown()
                    # Push enemy away
                    if enemy.x < self.px:
                        enemy.x -= 1
                    else:
                        enemy.x += 1
                # Check if player is in swipe attack zone
                elif enemy.attacking and enemy.player_in_attack_range(self.px, self.py):
                    if enemy.can_damage_player():
                        self.score -= 5
                        enemy.reset_damage_cooldown()
    
    def update_screen_pos(self):
        target_x = self.px * TILE
        target_y = self.py * TILE

        if self.screen_x < target_x:
            self.screen_x = min(self.screen_x + self.speed, target_x)
        elif self.screen_x > target_x:
            self.screen_x = max(self.screen_x - self.speed, target_x)

        if self.screen_y < target_y:
            self.screen_y = min(self.screen_y + self.speed, target_y)
        elif self.screen_y > target_y:
            self.screen_y = max(self.screen_y - self.speed, target_y)

    def is_wall(self, tx, ty):
        if tx < 0 or ty < 0 or tx >= MAP_W or ty >= MAP_H:
            return True
        return (tx, ty) in self.walls
    
    def check_pellets(self):
        """Check if player collected pellet"""
        for i, (px, py) in enumerate(self.pellet_positions):
            if px == self.px and py == self.py:
                self.pellet_positions.pop(i)
                self.pellets -= 1
                self.score += 10
                
                # Activate portal when all pellets collected
                if self.pellets == 0:
                    self.portal_active = True
                break
    
    def update_portal_dir(self):
        """Math: determine portal direction based on player position"""
        if self.py < self.portal_y:
            return 0  # Player above portal → front
        elif self.px < self.portal_x:
            return 1  # Player left of portal → left
        elif self.px > self.portal_x:
            return 2  # Player right of portal → right
        return 0

    def check_portal(self):
        if self.portal_active and self.px == self.portal_x and self.py == self.portal_y:
            # Next level!
            self.level += 1
            self.score += 500
            self.generate_level()
    
    def draw(self):
        pyxel.cls(0)
        
        # Draw tilemap with pixel dimensions
        # bltm(x, y, tilemap_index, u, v, width, height)
        # 16 tiles * 8 pixels = 128 pixels
        pyxel.bltm(0, 0, 0, 0, 0, MAP_W * TILE, MAP_H * TILE)
        
        # Draw pellets with sprite texture
        for (px, py) in self.pellet_positions:
            sx = SPRITE_PELLET * TILE
            sy = SPRITE_PELLET * TILE
            pyxel.blt(px * TILE, py * TILE, IMG_WORLD, sx, sy, TILE, TILE, 0)
        
        # Draw portal if active with sprite
        if self.portal_active:
            frame = (pyxel.frame_count // 8) % PORTAL_FRAMES
            portal_rows = [SPRITE_PORTAL_FRONT, SPRITE_PORTAL_LEFT, SPRITE_PORTAL_RIGHT]
            portal_row = portal_rows[self.update_portal_dir()]
            sx = (MAP2_OFFSET + frame) * TILE
            sy = portal_row * TILE
            pyxel.blt(self.portal_x * TILE, self.portal_y * TILE, IMG_WORLD, sx, sy, TILE, TILE, 0)
        
        # Draw enemies
        for enemy in self.enemies:
            if enemy.alive:
                # Draw swipe attack if attacking (separate from enemy sprite)
                if enemy.attacking:
                    ax, ay = enemy.get_attack_pos()
                    frame = (enemy.attack_timer // 4) % 4
                    swipe_row = {
                        DIR_UP: ENEMY_ROW_UP,
                        DIR_DOWN: ENEMY_ROW_DOWN_SWIPE,
                        DIR_LEFT: ENEMY_ROW_LEFT_SWIPE,
                        DIR_RIGHT: ENEMY_ROW_RIGHT_SWIPE,
                    }
                    row = swipe_row.get(enemy.dir, ENEMY_ROW_DOWN_SWIPE)
                    u = frame * TILE
                    v = row * TILE
                    pyxel.blt(ax * TILE, ay * TILE, IMG_ENEMY, u, v, TILE, TILE, 0)
                
                # Draw enemy sprite (keeps idle/walk sprite while attacking)
                if enemy.state == STATE_WALK:
                    frame = (pyxel.frame_count // 6) % 4
                else:
                    frame = 0
                
                # Get row based on direction (idle animation only, no attack sprite on enemy)
                row = {
                    DIR_UP: ENEMY_ROW_UP,
                    DIR_DOWN: ENEMY_ROW_DOWN_IDLE,
                    DIR_LEFT: ENEMY_ROW_LEFT_IDLE,
                    DIR_RIGHT: ENEMY_ROW_RIGHT_IDLE,
                }.get(enemy.dir, ENEMY_ROW_DOWN_IDLE)
                
                u = frame * TILE
                v = row * TILE
                
                pyxel.blt(enemy.screen_x, enemy.screen_y, IMG_ENEMY, u, v, TILE, TILE, 0)
        
        # Draw player
        self.draw_player()
        
        # UI
        pyxel.text(5, 5, f"LEVEL: {self.level}", 7)
        pyxel.text(5, 15, f"SCORE: {self.score}", 7)
        pyxel.text(5, 25, f"PELLETS: {self.pellets}", 7)
        pyxel.text(5, 35, f"ENEMIES: {len(self.enemies)}", 7)
    
    def draw_player(self):
        if self.state == STATE_WALK:
            frame = (pyxel.frame_count // 6) % 4
        elif self.state in (STATE_ATTACK, STATE_SWIPE):
            frame = (pyxel.frame_count // 8) % 4
        else:
            frame = 0

        u = frame * TILE

        BASE_ROW = 2

        v = (BASE_ROW +
             self.dir * STATES_PER_DIR +
             self.state) * TILE

        pyxel.blt(
            self.screen_x,
            self.screen_y,
            IMG_PLAYER,
            u, v,
            TILE, TILE, 0
        )


Game()
