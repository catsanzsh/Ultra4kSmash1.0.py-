import pygame
import random
import asyncio
import platform

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60

# Set up display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Cool Smash Melee Pygame Engine')

# Clock for FPS
clock = pygame.time.Clock()

class Platform:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), (self.x, self.y, self.width, self.height))

class Character:
    def __init__(self, x, y, color, speed, jump_power):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 50
        self.color = color
        self.velocity_x = 0
        self.velocity_y = 0
        self.is_jumping = False
        self.jump_power = jump_power
        self.gravity = 0.5
        self.damage = 0
        self.lives = 3
        self.speed = speed
        self.walk_frame = 0
        self.speed_boost_timer = 0
        self.power_boost_timer = 0
        self.hit_timer = 0

    def update(self, platforms, particles):
        self.velocity_y += self.gravity
        self.y += self.velocity_y
        self.x += self.velocity_x
        if self.x < 0:
            self.x = 0
        elif self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width
        if self.velocity_x != 0:
            self.walk_frame = (self.walk_frame + 1) % 20
        else:
            self.walk_frame = 0
        if self.y >= SCREEN_HEIGHT - self.height:
            self.y = SCREEN_HEIGHT - self.height
            self.velocity_y = 0
            self.is_jumping = False
            if self.velocity_x != 0:
                particles.append(Particle(self.x + self.width / 2, self.y + self.height, (200, 200, 200), random.uniform(-1, 1), -1))
        for platform in platforms:
            if self.is_colliding_with_platform(platform) and self.velocity_y > 0:
                self.y = platform.y - self.height
                self.velocity_y = 0
                self.is_jumping = False
                if self.velocity_x != 0:
                    particles.append(Particle(self.x + self.width / 2, self.y + self.height, (200, 200, 200), random.uniform(-1, 1), -1))
        if self.speed_boost_timer > 0:
            self.speed_boost_timer -= 1
            if self.speed_boost_timer == 0:
                self.speed /= 1.5
        if self.power_boost_timer > 0:
            self.power_boost_timer -= 1
        if self.hit_timer > 0:
            self.hit_timer -= 1

    def draw(self, screen):
        draw_color = (255, 0, 0) if self.hit_timer > 0 else self.color
        pygame.draw.rect(screen, draw_color, (self.x + 20, self.y + 20, 10, 30))
        pygame.draw.circle(screen, draw_color, (self.x + 25, self.y + 15), 10)
        if self.walk_frame < 10:
            pygame.draw.line(screen, draw_color, (self.x + 15, self.y + 25), (self.x + 35, self.y + 25), 5)
            pygame.draw.line(screen, draw_color, (self.x + 20, self.y + 50), (self.x + 20, self.y + 70), 5)
            pygame.draw.line(screen, draw_color, (self.x + 30, self.y + 50), (self.x + 30, self.y + 70), 5)
        else:
            pygame.draw.line(screen, draw_color, (self.x + 10, self.y + 30), (self.x + 40, self.y + 30), 5)
            pygame.draw.line(screen, draw_color, (self.x + 15, self.y + 50), (self.x + 15, self.y + 70), 5)
            pygame.draw.line(screen, draw_color, (self.x + 35, self.y + 50), (self.x + 35, self.y + 70), 5)

    def jump(self):
        if not self.is_jumping:
            self.velocity_y = self.jump_power
            self.is_jumping = True

    def move_left(self):
        self.velocity_x = -self.speed

    def move_right(self):
        self.velocity_x = self.speed

    def stop(self):
        self.velocity_x = 0

    def attack(self, other, particles):
        if self.is_colliding_with(other):
            damage = 10 if self.power_boost_timer == 0 else 15
            other.damage += damage
            other.hit_timer = 10
            knockback = 5 + other.damage / 10
            if self.x < other.x:
                other.velocity_x += knockback
            else:
                other.velocity_x -= knockback
            other.velocity_y -= 5 + other.damage / 20
            for _ in range(5):
                particles.append(Particle(self.x + self.width / 2, self.y + self.height / 2, self.color, random.uniform(-2, 2), random.uniform(-2, 2)))

    def is_colliding_with(self, other):
        return (self.x < other.x + other.width and
                self.x + self.width > other.x and
                self.y < other.y + other.height and
                self.y + self.height > other.y)

    def is_colliding_with_platform(self, platform):
        return (self.x < platform.x + platform.width and
                self.x + self.width > platform.x and
                self.y + self.height > platform.y and
                self.y < platform.y + platform.height)

class RedCharacter(Character):
    def __init__(self, x, y):
        super().__init__(x, y, (255, 0, 0), speed=5, jump_power=-10)

class BlueCharacter(Character):
    def __init__(self, x, y):
        super().__init__(x, y, (0, 0, 255), speed=6, jump_power=-12)

class Item:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

class SpeedItem(Item):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = (0, 255, 255)

    def apply_effect(self, character):
        character.speed *= 1.5
        character.speed_boost_timer = 300

class PowerItem(Item):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = (255, 0, 255)

    def apply_effect(self, character):
        character.power_boost_timer = 300

class Particle:
    def __init__(self, x, y, color, velocity_x, velocity_y):
        self.x = x
        self.y = y
        self.color = color
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.lifetime = 30

    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.lifetime -= 1

    def draw(self, screen):
        if self.lifetime > 0:
            radius = max(1, self.lifetime // 10)
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), radius)

class Game:
    def __init__(self):
        self.stages = [
            [Platform(300, 400, 200, 20)],
            [Platform(100, 300, 150, 20), Platform(550, 300, 150, 20)],
            [Platform(200, 500, 100, 20), Platform(500, 500, 100, 20), Platform(350, 350, 100, 20)]
        ]
        self.current_stage = random.choice(self.stages)
        self.characters = [RedCharacter(100, SCREEN_HEIGHT - 50), BlueCharacter(600, SCREEN_HEIGHT - 50)]
        self.items = []
        self.particles = []
        self.running = True
        self.start_time = pygame.time.get_ticks()

    def update(self):
        for character in self.characters:
            character.update(self.current_stage, self.particles)
        for character in self.characters:
            for item in self.items[:]:
                if character.is_colliding_with(item):
                    item.apply_effect(character)
                    self.items.remove(item)
        for particle in self.particles[:]:
            particle.update()
            if particle.lifetime <= 0:
                self.particles.remove(particle)
        if random.random() < 0.01:
            item_x = random.randint(0, SCREEN_WIDTH - 20)
            item_y = random.randint(0, SCREEN_HEIGHT - 100)
            self.items.append(random.choice([SpeedItem(item_x, item_y), PowerItem(item_x, item_y)]))
        for character in self.characters:
            if character.y > SCREEN_HEIGHT:
                character.lives -= 1
                if character.lives <= 0:
                    winner = "Player 2" if character == self.characters[0] else "Player 1"
                    print(f"{winner} wins!")
                    self.running = False
                else:
                    character.x = 100 if character == self.characters[0] else 600
                    character.y = SCREEN_HEIGHT - 50
                    character.velocity_x = 0
                    character.velocity_y = 0
                    character.damage = 0

    def draw(self, screen):
        for y in range(SCREEN_HEIGHT):
            blue = min(255, y * 255 // SCREEN_HEIGHT)
            pygame.draw.line(screen, (0, 100, blue), (0, y), (SCREEN_WIDTH, y))
        for platform in self.current_stage:
            platform.draw(screen)
        for character in self.characters:
            character.draw(screen)
        for item in self.items:
            item.draw(screen)
        for particle in self.particles:
            particle.draw(screen)
        font = pygame.font.Font(None, 36)
        p1_text = font.render(f"P1: {self.characters[0].damage}% Lives: {self.characters[0].lives}", True, (255, 255, 255))
        p2_text = font.render(f"P2: {self.characters[1].damage}% Lives: {self.characters[1].lives}", True, (255, 255, 255))
        time_text = font.render(f"Time: {(pygame.time.get_ticks() - self.start_time) / 1000:.1f}", True, (255, 255, 255))
        screen.blit(p1_text, (10, 10))
        screen.blit(p2_text, (SCREEN_WIDTH - 250, 10))
        screen.blit(time_text, (SCREEN_WIDTH // 2 - 50, 10))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.characters[0].move_left()
                elif event.key == pygame.K_RIGHT:
                    self.characters[0].move_right()
                elif event.key == pygame.K_UP:
                    self.characters[0].jump()
                elif event.key == pygame.K_SPACE:
                    self.characters[0].attack(self.characters[1], self.particles)
                elif event.key == pygame.K_a:
                    self.characters[1].move_left()
                elif event.key == pygame.K_d:
                    self.characters[1].move_right()
                elif event.key == pygame.K_w:
                    self.characters[1].jump()
                elif event.key == pygame.K_LSHIFT:
                    self.characters[1].attack(self.characters[0], self.particles)
            elif event.type == pygame.KEYUP:
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                    self.characters[0].stop()
                elif event.key in [pygame.K_a, pygame.K_d]:
                    self.characters[1].stop()

game = Game()

async def main():
    while game.running:
        game.handle_events()
        game.update()
        game.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
