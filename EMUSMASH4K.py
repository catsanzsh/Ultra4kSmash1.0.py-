import asyncio
import platform
import pygame
import random
import math

# Constants
FPS = 60
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
GRAVITY = 0.5
JUMP_STRENGTH = -10
PLAYER_SPEED = 4
AI_SPEED = 2.5
ATTACK_DURATION = 15
ATTACK_COOLDOWN = 30
ATTACK_RANGE = 30
ATTACK_SIZE = (60, 50)

# Advanced mechanics constants
DASH_SPEED = 7
DASH_DURATION = 15
AIR_ACCELERATION = 0.2
AIR_FRICTION = 0.05
GROUND_FRICTION = 0.15
FASTFALL_MULTIPLIER = 2
SHIELD_HEALTH_MAX = 100
SHIELD_DECAY_RATE = 0.5
SHIELD_REGEN_RATE = 0.2
SHIELD_STUN = 10
HITSTUN_MULTIPLIER = 0.4
DI_INFLUENCE = 0.2
L_CANCEL_REDUCTION = 0.5
LEDGE_GRAB_RANGE = 20
TECH_WINDOW = 20
TECH_COOLDOWN = 40

# Character stats (simplified from Melee)
CHARACTER_STATS = {
    "fox": {
        "weight": 75,
        "fall_speed": 0.7,
        "jump_height": -12,
        "air_speed": 0.25,
        "dash_speed": 8,
        "color": (255, 128, 0),  # Orange
        "moves": {
            "jab": {"damage": 3, "knockback": 2, "angle": 45, "frame_data": {"startup": 2, "active": 2, "cooldown": 10}},
            "ftilt": {"damage": 7, "knockback": 5, "angle": 30, "frame_data": {"startup": 5, "active": 3, "cooldown": 15}},
            "fsmash": {"damage": 15, "knockback": 12, "angle": 45, "frame_data": {"startup": 10, "active": 3, "cooldown": 25}},
            "nair": {"damage": 5, "knockback": 3, "angle": 45, "frame_data": {"startup": 4, "active": 5, "cooldown": 15}},
            "fair": {"damage": 9, "knockback": 6, "angle": 30, "frame_data": {"startup": 6, "active": 4, "cooldown": 20}},
            "upb": {"damage": 15, "knockback": 8, "angle": 80, "frame_data": {"startup": 8, "active": 5, "cooldown": 30}},
            "shine": {"damage": 5, "knockback": 1, "angle": 0, "frame_data": {"startup": 1, "active": 1, "cooldown": 15}}
        }
    },
    "falco": {
        "weight": 80,
        "fall_speed": 0.65,
        "jump_height": -13,
        "air_speed": 0.2,
        "dash_speed": 7.5,
        "color": (0, 0, 255),  # Blue
        "moves": {
            "jab": {"damage": 3, "knockback": 2, "angle": 45, "frame_data": {"startup": 2, "active": 2, "cooldown": 10}},
            "ftilt": {"damage": 8, "knockback": 6, "angle": 30, "frame_data": {"startup": 5, "active": 3, "cooldown": 15}},
            "fsmash": {"damage": 14, "knockback": 13, "angle": 45, "frame_data": {"startup": 11, "active": 3, "cooldown": 25}},
            "nair": {"damage": 6, "knockback": 4, "angle": 45, "frame_data": {"startup": 4, "active": 5, "cooldown": 15}},
            "fair": {"damage": 10, "knockback": 7, "angle": 30, "frame_data": {"startup": 6, "active": 4, "cooldown": 20}},
            "upb": {"damage": 14, "knockback": 7, "angle": 80, "frame_data": {"startup": 9, "active": 5, "cooldown": 30}},
            "shine": {"damage": 6, "knockback": 0, "angle": 90, "frame_data": {"startup": 1, "active": 1, "cooldown": 15}}
        }
    },
    "marth": {
        "weight": 85,
        "fall_speed": 0.5,
        "jump_height": -11,
        "air_speed": 0.18,
        "dash_speed": 7,
        "color": (0, 0, 128),  # Dark blue
        "moves": {
            "jab": {"damage": 4, "knockback": 2, "angle": 45, "frame_data": {"startup": 4, "active": 2, "cooldown": 10}},
            "ftilt": {"damage": 9, "knockback": 6, "angle": 30, "frame_data": {"startup": 7, "active": 3, "cooldown": 15}},
            "fsmash": {"damage": 16, "knockback": 14, "angle": 45, "frame_data": {"startup": 12, "active": 3, "cooldown": 25}},
            "nair": {"damage": 6, "knockback": 4, "angle": 45, "frame_data": {"startup": 6, "active": 5, "cooldown": 15}},
            "fair": {"damage": 11, "knockback": 8, "angle": 30, "frame_data": {"startup": 7, "active": 4, "cooldown": 20}},
            "upb": {"damage": 13, "knockback": 6, "angle": 80, "frame_data": {"startup": 10, "active": 5, "cooldown": 30}},
            "counter": {"damage": 8, "knockback": 7, "angle": 45, "frame_data": {"startup": 5, "active": 6, "cooldown": 30}}
        }
    }
}

# Stage data
STAGE_DATA = {
    "battlefield": {
        "platforms": [
            {"rect": [0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40], "type": "main"},  # Main platform
            {"rect": [150, SCREEN_HEIGHT - 150, 300, 20], "type": "soft"},  # Middle platform
            {"rect": [50, SCREEN_HEIGHT - 250, 150, 20], "type": "soft"},  # Left platform
            {"rect": [SCREEN_WIDTH - 200, SCREEN_HEIGHT - 250, 150, 20], "type": "soft"}  # Right platform
        ],
        "blast_zones": {
            "left": -100,
            "right": SCREEN_WIDTH + 100,
            "top": -100,
            "bottom": SCREEN_HEIGHT + 150
        },
        "spawn_points": [[150, 100], [450, 100]],
        "background_color": (20, 20, 50)
    },
    "final_destination": {
        "platforms": [
            {"rect": [0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40], "type": "main"}  # Only main platform
        ],
        "blast_zones": {
            "left": -100,
            "right": SCREEN_WIDTH + 100,
            "top": -100,
            "bottom": SCREEN_HEIGHT + 150
        },
        "spawn_points": [[150, 100], [450, 100]],
        "background_color": (40, 0, 60)
    },
    "dreamland": {
        "platforms": [
            {"rect": [50, SCREEN_HEIGHT - 40, SCREEN_WIDTH - 100, 40], "type": "main"},  # Main platform
            {"rect": [200, SCREEN_HEIGHT - 160, 200, 20], "type": "soft"},  # Middle platform
            {"rect": [100, SCREEN_HEIGHT - 240, 120, 20], "type": "soft"},  # Left platform
            {"rect": [SCREEN_WIDTH - 220, SCREEN_HEIGHT - 240, 120, 20], "type": "soft"}  # Right platform
        ],
        "blast_zones": {
            "left": -120,
            "right": SCREEN_WIDTH + 120,
            "top": -120,
            "bottom": SCREEN_HEIGHT + 180
        },
        "spawn_points": [[150, 100], [450, 100]],
        "background_color": (100, 200, 255)
    }
}

# Utility functions
def calculate_knockback(base_kb, damage, weight, scaling=1.0):
    """Calculate knockback based on damage, weight and scaling"""
    return base_kb * (1 + (damage / 100)) * (1 / (weight / 100)) * scaling

def calculate_hitstun(knockback):
    """Calculate hitstun frames based on knockback"""
    return int(knockback * HITSTUN_MULTIPLIER)

def apply_di(kb_x, kb_y, di_x, di_y):
    """Apply directional influence to knockback"""
    magnitude = math.sqrt(kb_x**2 + kb_y**2)
    angle = math.atan2(kb_y, kb_x)
    di_influence = math.atan2(di_y, di_x) * DI_INFLUENCE
    new_angle = angle + di_influence
    return magnitude * math.cos(new_angle), magnitude * math.sin(new_angle)

class DataLoader:
    def __init__(self, name, is_char=True):
        self.name = name
        self.is_char = is_char

    def load_data(self):
        if self.is_char:
            if self.name in CHARACTER_STATS:
                char_stats = CHARACTER_STATS[self.name]
                position = [100 if self.name == "fox" else 450, SCREEN_HEIGHT - 100]
                return {
                    'position': position,
                    'velocity': [0, 0],
                    'health': 0,
                    'stocks': 4,
                    'width': 40,
                    'height': 50,
                    'on_ground': False,
                    'attacking': False,
                    'attack_timer': 0,
                    'attack_cooldown_timer': 0,
                    'facing_right': True,
                    'character': self.name,
                    'weight': char_stats['weight'],
                    'fall_speed': char_stats['fall_speed'],
                    'jump_height': char_stats['jump_height'],
                    'air_speed': char_stats['air_speed'],
                    'dash_speed': char_stats['dash_speed'],
                    'color': char_stats['color'],
                    'moves': char_stats['moves'],
                    'jumps_left': 2,
                    'dash_timer': 0,
                    'shield_health': SHIELD_HEALTH_MAX,
                    'shielding': False,
                    'shield_stun': 0,
                    'hitstun': 0,
                    'fastfalling': False,
                    'tech_window': 0,
                    'tech_cooldown': 0,
                    'ledge_grab': False,
                    'ledge_cooldown': 0,
                    'current_move': None,
                    'move_frame': 0,
                    'l_canceling': False,
                    'di_direction': [0, 0]
                }
            else:
                return {
                    'position': [100, SCREEN_HEIGHT - 100],
                    'velocity': [0, 0],
                    'health': 0,
                    'stocks': 4,
                    'width': 40,
                    'height': 50,
                    'on_ground': False,
                    'attacking': False,
                    'attack_timer': 0,
                    'attack_cooldown_timer': 0,
                    'facing_right': True,
                    'character': "generic",
                    'weight': 80,
                    'fall_speed': 0.6,
                    'jump_height': -11,
                    'air_speed': 0.2,
                    'dash_speed': 7,
                    'color': (255, 0, 0),
                    'jumps_left': 2,
                    'dash_timer': 0,
                    'shield_health': SHIELD_HEALTH_MAX,
                    'shielding': False,
                    'shield_stun': 0,
                    'hitstun': 0,
                    'fastfalling': False,
                    'tech_window': 0,
                    'tech_cooldown': 0,
                    'ledge_grab': False,
                    'ledge_cooldown': 0,
                    'current_move': None,
                    'move_frame': 0,
                    'l_canceling': False,
                    'di_direction': [0, 0]
                }
        else:
            if self.name in STAGE_DATA:
                stage_data = STAGE_DATA[self.name]
                platforms = [{'rect': pygame.Rect(p['rect']), 'type': p['type']} for p in stage_data['platforms']]
                return {
                    'platforms': platforms,
                    'blast_zones': stage_data['blast_zones'],
                    'spawn_points': stage_data['spawn_points'],
                    'background_color': stage_data['background_color']
                }
            else:
                return {
                    'platforms': [{'rect': pygame.Rect(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40), 'type': 'main'}],
                    'blast_zones': {'left': -100, 'right': SCREEN_WIDTH + 100, 'top': -100, 'bottom': SCREEN_HEIGHT + 150},
                    'spawn_points': [[150, 100], [450, 100]],
                    'background_color': (20, 20, 50)
                }

def train_simple_ai_model():
    class MeleeAI:
        def __init__(self):
            self.decision_cooldown = 0
            self.current_strategy = "approach"
            self.strategy_timer = 0

        def predict(self, game_state):
            player = game_state['player']
            ai = game_state['ai']
            if self.decision_cooldown > 0:
                self.decision_cooldown -= 1
            if self.strategy_timer > 0:
                self.strategy_timer -= 1
            else:
                self.current_strategy = random.choice(["approach", "retreat", "defend"]) if random.random() < 0.7 else "approach"
                self.strategy_timer = random.randint(30, 120)
            dist_x = player.rect.centerx - ai.rect.centerx
            dist_y = player.rect.centery - ai.rect.centery
            dist = math.sqrt(dist_x**2 + dist_y**2)
            actions = {'move_left': False, 'move_right': False, 'jump': False, 'attack': False, 'shield': False, 'dash': False, 'special': False}
            if self.current_strategy == "approach":
                if dist_x < -20:
                    actions['move_left'] = True
                    ai.facing_right = False
                elif dist_x > 20:
                    actions['move_right'] = True
                    ai.facing_right = True
                if dist_y < -50 and ai.on_ground and random.random() < 0.05:
                    actions['jump'] = True
                if abs(dist_x) < ATTACK_RANGE + player.width and abs(dist_y) < ai.height:
                    actions['attack'] = True
                if abs(dist_x) > 100 and random.random() < 0.02:
                    actions['dash'] = True
            elif self.current_strategy == "retreat":
                if dist_x < 0:
                    actions['move_right'] = True
                    ai.facing_right = True
                else:
                    actions['move_left'] = True
                    ai.facing_right = False
                if random.random() < 0.1:
                    actions['jump'] = True
                if player.attacking and dist < 100:
                    actions['shield'] = True
            elif self.current_strategy == "defend":
                if dist < 150 and random.random() < 0.3:
                    actions['shield'] = True
                if random.random() < 0.2:
                    actions['move_left' if random.random() < 0.5 else 'move_right'] = True
                    ai.facing_right = not actions['move_left']
                if dist < 60:
                    actions['attack'] = True
            if random.random() < 0.02:
                actions['special'] = True
            return actions
    return MeleeAI()

class Move:
    def __init__(self, name, data, owner):
        self.name = name
        self.damage = data['damage']
        self.knockback = data['knockback']
        self.angle = data['angle'] * (math.pi / 180)
        self.frame_data = data['frame_data']
        self.owner = owner
        self.current_frame = 0
        self.hitboxes = []
        self.hit_targets = set()

    def update(self):
        self.current_frame += 1
        self.hitboxes = []
        if self.frame_data['startup'] <= self.current_frame < self.frame_data['startup'] + self.frame_data['active']:
            if self.name == "jab":
                width, height = 40, 30
                x = self.owner.rect.right if self.owner.facing_right else self.owner.rect.left - width
                y = self.owner.rect.centery - height // 2
                self.hitboxes.append(pygame.Rect(x, y, width, height))
            elif self.name == "ftilt":
                width, height = 60, 40
                x = self.owner.rect.right if self.owner.facing_right else self.owner.rect.left - width
                y = self.owner.rect.centery - height // 2
                self.hitboxes.append(pygame.Rect(x, y, width, height))
            elif self.name == "fsmash":
                width, height = 80, 50
                x = self.owner.rect.right if self.owner.facing_right else self.owner.rect.left - width
                y = self.owner.rect.centery - height // 2
                self.hitboxes.append(pygame.Rect(x, y, width, height))
            elif self.name == "nair":
                radius = 50
                self.hitboxes.append(pygame.Rect(self.owner.rect.centerx - radius, self.owner.rect.centery - radius, radius * 2, radius * 2))
            elif self.name == "fair":
                width, height = 60, 40
                x = self.owner.rect.right if self.owner.facing_right else self.owner.rect.left - width
                y = self.owner.rect.centery - height // 2
                self.hitboxes.append(pygame.Rect(x, y, width, height))
            elif self.name == "upb":
                width, height = 50, 70
                x = self.owner.rect.centerx - width // 2
                y = self.owner.rect.top - height
                self.hitboxes.append(pygame.Rect(x, y, width, height))
            elif self.name == "shine":
                radius = 40
                self.hitboxes.append(pygame.Rect(self.owner.rect.centerx - radius, self.owner.rect.centery - radius, radius * 2, radius * 2))
            elif self.name == "counter":
                width, height = 60, 80
                x = self.owner.rect.centerx - width // 2
                y = self.owner.rect.centery - height // 2
                self.hitboxes.append(pygame.Rect(x, y, width, height))
        return self.current_frame >= self.frame_data['startup'] + self.frame_data['active'] + self.frame_data['cooldown']

    def draw(self, screen):
        for hitbox in self.hitboxes:
            pygame.draw.rect(screen, (255, 255, 0), hitbox, 2)

class Character:
    def __init__(self, data):
        self.position = list(data['position'])
        self.velocity = list(data['velocity'])
        self.damage = data['health']
        self.stocks = data['stocks']
        self.width = data['width']
        self.height = data['height']
        self.rect = pygame.Rect(self.position[0], self.position[1], self.width, self.height)
        self.on_ground = data['on_ground']
        self.attacking = data['attacking']
        self.attack_timer = data['attack_timer']
        self.attack_cooldown_timer = data['attack_cooldown_timer']
        self.facing_right = data['facing_right']
        self.character = data['character']
        self.weight = data['weight']
        self.fall_speed = data['fall_speed']
        self.jump_height = data['jump_height']
        self.air_speed = data['air_speed']
        self.dash_speed = data['dash_speed']
        self.color = data['color']
        self.moves = data['moves']
        self.jumps_left = data['jumps_left']
        self.dash_timer = data['dash_timer']
        self.shield_health = data['shield_health']
        self.shielding = data['shielding']
        self.shield_stun = data['shield_stun']
        self.hitstun = data['hitstun']
        self.fastfalling = data['fastfalling']
        self.tech_window = data['tech_window']
        self.tech_cooldown = data['tech_cooldown']
        self.ledge_grab = data['ledge_grab']
        self.ledge_cooldown = data['ledge_cooldown']
        self.current_move = None
        self.move_frame = data['move_frame']
        self.l_canceling = data['l_canceling']
        self.di_direction = data['di_direction']
        self.respawn_timer = 0
        self.respawn_invincibility = 0
        self.shield_broken = False
        self.shield_break_timer = 0
        self.is_cpu = False

    def move(self, dx, dy):
        if self.hitstun > 0 or self.shield_stun > 0 or self.shield_broken:
            return
        if self.dash_timer > 0:
            if self.facing_right:
                dx = self.dash_speed
            else:
                dx = -self.dash_speed
            self.dash_timer -= 1
        if self.on_ground:
            if not self.attacking and not self.shielding:
                if dx > 0:
                    self.facing_right = True
                elif dx < 0:
                    self.facing_right = False
                self.position[0] += dx
        else:
            if not self.attacking:
                if dx > 0:
                    self.velocity[0] = min(self.velocity[0] + self.air_speed, self.dash_speed * 0.8)
                    self.facing_right = True
                elif dx < 0:
                    self.velocity[0] = max(self.velocity[0] - self.air_speed, -self.dash_speed * 0.8)
                    self.facing_right = False

    def jump(self):
        if self.hitstun > 0 or self.shield_stun > 0 or self.shield_broken:
            return
        if self.on_ground and not self.attacking and not self.shielding:
            self.velocity[1] = self.jump_height
            self.on_ground = False
            self.jumps_left = 1
        elif not self.on_ground and self.jumps_left > 0 and not self.attacking:
            self.velocity[1] = self.jump_height * 0.8
            self.jumps_left -= 1

    def dash(self):
        if self.on_ground and not self.attacking and not self.shielding and self.hitstun <= 0 and self.shield_stun <= 0 and not self.shield_broken:
            self.dash_timer = DASH_DURATION

    def shield(self, activate):
        if not self.on_ground or self.attacking or self.hitstun > 0 or self.shield_broken:
            return
        if activate and self.shield_health > 0:
            self.shielding = True
        else:
            self.shielding = False

    def fastfall(self):
        if not self.on_ground and self.velocity[1] > 0 and not self.fastfalling:
            self.velocity[1] *= FASTFALL_MULTIPLIER
            self.fastfalling = True

    def tech(self):
        if not self.on_ground and self.tech_cooldown <= 0:
            self.tech_window = TECH_WINDOW

    def l_cancel(self):
        if not self.on_ground and self.attacking:
            self.l_canceling = True

    def set_di(self, x, y):
        magnitude = math.sqrt(x**2 + y**2)
        if magnitude > 0:
            self.di_direction = [x / magnitude, y / magnitude]
        else:
            self.di_direction = [0, 0]

    def perform_move(self, move_name):
        if self.hitstun > 0 or self.shield_stun > 0 or self.shield_broken:
            return
        if move_name in self.moves:
            if self.shielding:
                self.shielding = False
            self.current_move = Move(move_name, self.moves[move_name], self)
            self.attacking = True
            if move_name == "upb":
                self.velocity[1] = self.jump_height * 1.2
                self.velocity[0] = 5 if self.facing_right else -5
            elif move_name == "shine":
                self.velocity = [0, 0]

    def update(self, stage):
        if self.respawn_timer > 0:
            self.respawn_timer -= 1
            if self.respawn_timer <= 0:
                spawn_point = random.choice(stage.spawn_points)
                self.position = list(spawn_point)
                self.velocity = [0, 0]
                self.damage = 0
                self.respawn_invincibility = 120
                self.hitstun = 0
                self.shield_stun = 0
                self.shield_health = SHIELD_HEALTH_MAX
                self.shield_broken = False
                self.jumps_left = 1
            return
        if self.respawn_invincibility > 0:
            self.respawn_invincibility -= 1
        if self.shield_broken:
            self.shield_break_timer -= 1
            if self.shield_break_timer <= 0:
                self.shield_broken = False
                self.shield_health = SHIELD_HEALTH_MAX * 0.3
            return
        if self.hitstun > 0:
            self.hitstun -= 1
        if self.shield_stun > 0:
            self.shield_stun -= 1
        if self.tech_window > 0:
            self.tech_window -= 1
        if self.tech_cooldown > 0:
            self.tech_cooldown -= 1
        if self.shielding:
            self.shield_health -= SHIELD_DECAY_RATE
            if self.shield_health <= 0:
                self.shield_broken = True
                self.shield_break_timer = 300
                self.shielding = False
        else:
            self.shield_health = min(self.shield_health + SHIELD_REGEN_RATE, SHIELD_HEALTH_MAX)
        if not self.on_ground:
            max_fall_speed = self.fall_speed * 10 * (FASTFALL_MULTIPLIER if self.fastfalling else 1)
            self.velocity[1] = min(self.velocity[1] + GRAVITY * self.fall_speed, max_fall_speed)
        else:
            self.fastfalling = False
        self.velocity[0] *= (1 - (GROUND_FRICTION if self.on_ground else AIR_FRICTION))
        if not (self.shielding and self.on_ground):
            self.position[0] += self.velocity[0]
            self.position[1] += self.velocity[1]
        self.rect.topleft = (int(self.position[0]), int(self.position[1]))
        if self.current_move:
            if self.current_move.update():
                self.current_move = None
                self.attacking = False
                if not self.on_ground and self.l_canceling:
                    self.attack_cooldown_timer = int(self.attack_cooldown_timer * L_CANCEL_REDUCTION)
                    self.l_canceling = False
        self.on_ground = False
        for platform in stage.platforms:
            if self.rect.colliderect(platform['rect']) and self.velocity[1] > 0 and self.rect.bottom <= platform['rect'].top + self.velocity[1] + 1:
                self.rect.bottom = platform['rect'].top
                self.position[1] = self.rect.top
                self.velocity[1] = 0
                self.on_ground = True
                if self.hitstun > 0 and self.tech_window > 0:
                    self.hitstun = 0
                    self.tech_window = 0
                    self.tech_cooldown = TECH_COOLDOWN
                break
            elif self.velocity[1] < 0 and self.rect.top >= platform['rect'].bottom + self.velocity[1] - 1:
                self.rect.top = platform['rect'].bottom
                self.position[1] = self.rect.top
                self.velocity[1] = 0
        if not self.on_ground and not self.ledge_grab and self.ledge_cooldown <= 0 and self.velocity[1] > 0:
            for platform in stage.platforms:
                if platform['type'] == 'main':
                    ledge_left = platform['rect'].left
                    ledge_right = platform['rect'].right
                    ledge_top = platform['rect'].top
                    if (abs(self.rect.right - ledge_left) < LEDGE_GRAB_RANGE and abs(self.rect.bottom - ledge_top) < LEDGE_GRAB_RANGE and not self.facing_right) or \
                       (abs(self.rect.left - ledge_right) < LEDGE_GRAB_RANGE and abs(self.rect.bottom - ledge_top) < LEDGE_GRAB_RANGE and self.facing_right):
                        self.ledge_grab = True
                        self.position = [ledge_left - self.width if not self.facing_right else ledge_right, ledge_top - self.height]
                        self.velocity = [0, 0]
                        self.hitstun = 0
                        break
        if self.ledge_grab and self.velocity[1] > 0:
            self.ledge_grab = False
            self.ledge_cooldown = 30
            self.velocity[1] = 2
        if self.ledge_grab and self.jumps_left < 1:
            self.jumps_left = 1
        if self.ledge_cooldown > 0:
            self.ledge_cooldown -= 1
        if self.position[0] < stage.blast_zones['left'] or self.position[0] > stage.blast_zones['right'] or \
           self.position[1] < stage.blast_zones['top'] or self.position[1] > stage.blast_zones['bottom']:
            self.stocks -= 1
            if self.stocks > 0:
                self.respawn_timer = 60
        if self.rect.left < 0:
            self.rect.left = 0
            self.position[0] = self.rect.left
            if self.velocity[0] < 0:
                self.velocity[0] = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.position[0] = self.rect.left
            if self.velocity[0] > 0:
                self.velocity[0] = 0

    def draw(self, screen):
        if self.respawn_timer > 0:
            return
        color = (255, 255, 255) if self.respawn_invincibility > 0 and self.respawn_invincibility % 4 < 2 else self.color
        pygame.draw.rect(screen, color, self.rect)
        eye_x = self.rect.right - 10 if self.facing_right else self.rect.left + 10
        pygame.draw.circle(screen, (0, 0, 0), (eye_x, self.rect.top + 15), 5)
        if self.shielding:
            shield_size = int(20 * (self.shield_health / SHIELD_HEALTH_MAX) + 20)
            pygame.draw.circle(screen, (100, 200, 255, 128), self.rect.center, shield_size, 3)
        if self.current_move:
            self.current_move.draw(screen)
        if self.shield_broken:
            pygame.draw.line(screen, (255, 0, 0), (self.rect.centerx - 15, self.rect.top - 20), (self.rect.centerx + 15, self.rect.top - 5), 3)
            pygame.draw.line(screen, (255, 0, 0), (self.rect.centerx - 15, self.rect.top - 5), (self.rect.centerx + 15, self.rect.top - 20), 3)

class Stage:
    def __init__(self, data):
        self.platforms = data['platforms']
        self.blast_zones = data['blast_zones']
        self.spawn_points = data['spawn_points']
        self.background_color = data['background_color']

    def draw(self, screen):
        screen.fill(self.background_color)
        for platform in self.platforms:
            pygame.draw.rect(screen, (100, 100, 100) if platform['type'] == 'main' else (150, 150, 150), platform['rect'])

class GameState:
    def __init__(self):
        self.player = None
        self.ai = None
        self.stage = None
        self.game_timer = 0
        self.game_time_limit = 8 * 60 * 60
        self.game_over = False
        self.winner = None
        self.paused = False
        self.current_stage_name = "battlefield"
        self.player_character = "fox"
        self.ai_character = "falco"

    def reset(self):
        self.game_timer = 0
        self.game_over = False
        self.winner = None
        self.paused = False
        char_loader_player = DataLoader(self.player_character, is_char=True)
        char_loader_ai = DataLoader(self.ai_character, is_char=True)
        stage_loader = DataLoader(self.current_stage_name, is_char=False)
        player_data = char_loader_player.load_data()
        ai_data = char_loader_ai.load_data()
        stage_data = stage_loader.load_data()
        self.player = Character(player_data)
        self.ai = Character(ai_data)
        self.ai.is_cpu = True
        self.stage = Stage(stage_data)

    def update(self):
        if self.paused or self.game_over:
            return
        self.game_timer += 1
        if self.game_timer >= self.game_time_limit:
            self.game_over = True
            self.winner = "player" if self.player.stocks > self.ai.stocks or (self.player.stocks == self.ai.stocks and self.player.damage < self.ai.damage) else "ai"
            return
        if self.player.stocks <= 0:
            self.game_over = True
            self.winner = "ai"
            return
        if self.ai.stocks <= 0:
            self.game_over = True
            self.winner = "player"
            return
        self.player.update(self.stage)
        self.ai.update(self.stage)
        self.check_hits()

    def check_hits(self):
        for char, target, source in [(self.player, self.ai, "ai"), (self.ai, self.player, "player")]:
            if char.current_move and char.current_move.hitboxes:
                for hitbox in char.current_move.hitboxes:
                    if target.rect.colliderect(hitbox) and target not in char.current_move.hit_targets:
                        char.current_move.hit_targets.add(target)
                        if target.respawn_invincibility > 0:
                            continue
                        if target.shielding and not target.shield_broken:
                            target.shield_health -= char.current_move.damage * 0.7
                            target.shield_stun = int(char.current_move.knockback * 0.5)
                            if target.shield_health <= 0:
                                target.shield_broken = True
                                target.shield_break_timer = 300
                                target.shielding = False
                        else:
                            move = char.current_move
                            knockback = calculate_knockback(move.knockback, target.damage, target.weight)
                            kb_x = knockback * math.cos(move.angle) * (-1 if not char.facing_right else 1)
                            kb_y = knockback * math.sin(move.angle)
                            if target.di_direction != [0, 0]:
                                kb_x, kb_y = apply_di(kb_x, kb_y, target.di_direction[0], target.di_direction[1])
                            target.velocity = [kb_x, kb_y]
                            target.damage += move.damage
                            target.hitstun = calculate_hitstun(knockback)
                            target.current_move = None
                            target.attacking = False

    def draw(self, screen):
        self.stage.draw(screen)
        self.player.draw(screen)
        self.ai.draw(screen)
        self.draw_ui(screen)
        if self.game_over:
            self.draw_game_over(screen)

    def draw_ui(self, screen):
        font = pygame.font.Font(None, 30)
        player_text = font.render(f"P1: {int(self.player.damage)}%", True, (255, 255, 255))
        screen.blit(player_text, (20, 20))
        for i in range(self.player.stocks):
            pygame.draw.circle(screen, self.player.color, (30 + i * 20, 50), 8)
        ai_text = font.render(f"CPU: {int(self.ai.damage)}%", True, (255, 255, 255))
        screen.blit(ai_text, (SCREEN_WIDTH - ai_text.get_width() - 20, 20))
        for i in range(self.ai.stocks):
            pygame.draw.circle(screen, self.ai.color, (SCREEN_WIDTH - 30 - i * 20, 50), 8)
        minutes = (self.game_time_limit - self.game_timer) // (60 * 60)
        seconds = ((self.game_time_limit - self.game_timer) % (60 * 60)) // 60
        timer_text = font.render(f"{minutes}:{seconds:02d}", True, (255, 255, 255))
        screen.blit(timer_text, (SCREEN_WIDTH // 2 - timer_text.get_width() // 2, 20))

    def draw_game_over(self, screen):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        font_large = pygame.font.Font(None, 60)
        font_small = pygame.font.Font(None, 30)
        game_over_text = font_large.render("GAME!", True, (255, 255, 255))
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 3))
        winner_text = font_small.render("Player 1 Wins!" if self.winner == "player" else "CPU Wins!", True, (255, 255, 255))
        screen.blit(winner_text, (SCREEN_WIDTH // 2 - winner_text.get_width() // 2, SCREEN_HEIGHT // 2))
        restart_text = font_small.render("Press ENTER to play again", True, (255, 255, 255))
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT * 2 // 3))

# Global variables
screen = None
clock = None
game_state = None
ai_model = None

def setup():
    global screen, clock, game_state, ai_model
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Simplified Melee Engine")
    clock = pygame.time.Clock()
    game_state = GameState()
    game_state.reset()
    ai_model = train_simple_ai_model()

async def update_loop():
    global screen, clock, game_state, ai_model
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game_state.paused = not game_state.paused
            if event.key == pygame.K_RETURN and game_state.game_over:
                game_state.reset()
            if not game_state.paused and not game_state.game_over:
                if event.key in (pygame.K_UP, pygame.K_w):
                    game_state.player.jump()
                if event.key in (pygame.K_DOWN, pygame.K_s) and not game_state.player.on_ground:
                    game_state.player.fastfall()
                if event.key == pygame.K_j:
                    game_state.player.perform_move("jab" if game_state.player.on_ground else "nair")
                if event.key == pygame.K_k:
                    game_state.player.perform_move("fsmash" if game_state.player.on_ground else "fair")
                if event.key == pygame.K_u:
                    game_state.player.perform_move("upb")
                if event.key == pygame.K_i:
                    game_state.player.perform_move("shine" if game_state.player.character in ["fox", "falco"] else "counter")
                if event.key == pygame.K_LSHIFT:
                    game_state.player.dash()
                if event.key == pygame.K_SPACE:
                    game_state.player.shield(True) if game_state.player.on_ground else game_state.player.tech()
                if event.key == pygame.K_l:
                    game_state.player.l_cancel()
        if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
            game_state.player.shield(False)
    if game_state.paused:
        font = pygame.font.Font(None, 60)
        pause_text = font.render("PAUSED", True, (255, 255, 255))
        screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2))
        pygame.display.flip()
        await asyncio.sleep(0)
        clock.tick(FPS)
        return True
    if not game_state.game_over:
        keys = pygame.key.get_pressed()
        player_dx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player_dx -= PLAYER_SPEED
            game_state.player.set_di(-1, 0)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player_dx += PLAYER_SPEED
            game_state.player.set_di(1, 0)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            game_state.player.set_di(0, -1)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            game_state.player.set_di(0, 1)
        game_state.player.move(player_dx, 0)
        if ai_model and game_state.ai.is_cpu:
            ai_game_state = {'player': game_state.player, 'ai': game_state.ai}
            ai_actions = ai_model.predict(ai_game_state)
            ai_dx = 0
            if ai_actions['move_left']:
                ai_dx -= AI_SPEED
                game_state.ai.set_di(-1, 0)
            if ai_actions['move_right']:
                ai_dx += AI_SPEED
                game_state.ai.set_di(1, 0)
            game_state.ai.move(ai_dx, 0)
            if ai_actions['jump']:
                game_state.ai.jump()
            if ai_actions['attack']:
                game_state.ai.perform_move("fsmash" if game_state.ai.on_ground and random.random() < 0.3 else "jab" if game_state.ai.on_ground else "nair" if random.random() < 0.5 else "fair")
            game_state.ai.shield(ai_actions['shield'])
            if ai_actions['dash']:
                game_state.ai.dash()
            if ai_actions['special']:
                game_state.ai.perform_move("upb" if random.random() < 0.5 else "shine" if game_state.ai.character in ["fox", "falco"] else "counter")
        game_state.update()
    game_state.draw(screen)
    pygame.display.flip()
    await asyncio.sleep(0)
    clock.tick(FPS)
    return True

async def main():
    setup()
    running = True
    while running:
        running = await update_loop()
    pygame.quit()

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
