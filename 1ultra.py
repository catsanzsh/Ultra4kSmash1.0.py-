import asyncio
import pygame
import platform
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60

# Set up display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Smash Melee Pygame')

# Clock for FPS control
clock = pygame.time.Clock()

class Character:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 50
        self.color = color
        self.velocity_x = 0
        self.velocity_y = 0
        self.is_jumping = False
        self.jump_power = -10
        self.gravity = 0.5
        self.damage = 0  # Starts at 0%
        self.lives = 3

    def update(self, platforms):
        # Apply gravity
        self.velocity_y += self.gravity
        self.y += self.velocity_y

        # Update horizontal position
        self.x += self.velocity_x

        # Check for ground collision
        if self.y >= SCREEN_HEIGHT - self.height:
            self.y = SCREEN_HEIGHT - self.height
            self.velocity_y = 0
            self.is_jumping = False

        # Check for platform collisions
        for platform in platforms:
            if self.is_colliding_with_platform(platform):
                if self.velocity_y > 0:  # Falling down
                    self.y = platform.y - self.height
                    self.velocity_y = 0
                    self.is_jumping = False

    def draw(self, screen):
        draw_character(screen, self.x, self.y, self.color)

    def jump(self):
        if not self.is_jumping:
            self.velocity_y = self.jump_power
            self.is_jumping = True

    def move_left(self):
        self.velocity_x = -5

    def move_right(self):
        self.velocity_x = 5

    def stop(self):
        self.velocity_x = 0

    def attack(self, other):
        if self.is_colliding_with(other):
            other.damage += 10
            # Apply knockback based on damage
            knockback_force = 5 + other.damage / 10
            if self.x < other.x:
                other.velocity_x += knockback_force
            else:
                other.velocity_x -= knockback_force
            other.velocity_y -= 5 + other.damage / 20

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

class Platform:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), (self.x, self.y, self.width, self.height))

def draw_character(screen, x, y, color):
    # Body
    pygame.draw.rect(screen, color, (x + 20, y + 20, 10, 30))
    # Head
    pygame.draw.circle(screen, color, (x + 25, y + 15), 10)
    # Arms
    pygame.draw.line(screen, color, (x + 15, y + 25), (x + 35, y + 25), 5)
    # Legs
    pygame.draw.line(screen, color, (x + 20, y + 50), (x + 20, y + 70), 5)
    pygame.draw.line(screen, color, (x + 30, y + 50), (x + 30, y + 70), 5)

# Create characters
player1 = Character(100, SCREEN_HEIGHT - 50, (255, 0, 0))  # Red
player2 = Character(600, SCREEN_HEIGHT - 50, (0, 0, 255))  # Blue

# Create platforms
platform = Platform(300, 400, 200, 20)
platforms = [platform]

running = True

def setup():
    global running
    running = True

def update_loop():
    global running
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player1.move_left()
            elif event.key == pygame.K_RIGHT:
                player1.move_right()
            elif event.key == pygame.K_UP:
                player1.jump()
            elif event.key == pygame.K_a:
                player2.move_left()
            elif event.key == pygame.K_d:
                player2.move_right()
            elif event.key == pygame.K_w:
                player2.jump()
            elif event.key == pygame.K_SPACE:
                player1.attack(player2)
            elif event.key == pygame.K_LSHIFT:
                player2.attack(player1)
        elif event.type == pygame.KEYUP:
            if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                player1.stop()
            elif event.key in [pygame.K_a, pygame.K_d]:
                player2.stop()

    # Update characters with platforms
    player1.update(platforms)
    player2.update(platforms)

    # Check for falling off the screen
    if player1.y > SCREEN_HEIGHT:
        player1.lives -= 1
        if player1.lives <= 0:
            print("Player 2 wins!")
            running = False
        else:
            player1.x = 100
            player1.y = SCREEN_HEIGHT - 50
            player1.velocity_x = 0
            player1.velocity_y = 0
            player1.damage = 0
    if player2.y > SCREEN_HEIGHT:
        player2.lives -= 1
        if player2.lives <= 0:
            print("Player 1 wins!")
            running = False
        else:
            player2.x = 600
            player2.y = SCREEN_HEIGHT - 50
            player2.velocity_x = 0
            player2.velocity_y = 0
            player2.damage = 0

    # Clear the screen
    screen.fill((0, 0, 0))

    # Draw platforms
    for plat in platforms:
        plat.draw(screen)

    # Draw characters
    player1.draw(screen)
    player2.draw(screen)

    # Draw HUD
    font = pygame.font.Font(None, 36)
    player1_damage_text = font.render(f"P1 Damage: {player1.damage}%", True, (255, 255, 255))
    player2_damage_text = font.render(f"P2 Damage: {player2.damage}%", True, (255, 255, 255))
    screen.blit(player1_damage_text, (10, 10))
    screen.blit(player2_damage_text, (SCREEN_WIDTH - 200, 10))

    # Update display
    pygame.display.flip()

    # Maintain FPS
    clock.tick(FPS)

async def main():
    setup()
    while running:
        update_loop()
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
