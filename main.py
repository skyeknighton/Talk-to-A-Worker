import pygame
import sys
from pygame.locals import *
import math
import os
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Sprite loading function
def load_sprite(filename, size=(32, 32)):
    """Load and scale a sprite image, with fallback to colored rectangle"""
    try:
        sprite_path = os.path.join("sprites", filename)
        if os.path.exists(sprite_path):
            sprite = pygame.image.load(sprite_path)
            return pygame.transform.scale(sprite, size)
        else:
            # Create fallback colored rectangle
            surface = pygame.Surface(size)
            if "player" in filename:
                surface.fill(BLUE)
            elif "worker" in filename:
                surface.fill(GREEN)
            elif "protestor" in filename:
                surface.fill(YELLOW)
            elif "boss" in filename:
                surface.fill(RED)
            else:
                surface.fill(GRAY)
            return surface
    except:
        # Create fallback colored rectangle
        surface = pygame.Surface(size)
        if "player" in filename:
            surface.fill(BLUE)
        elif "worker" in filename:
            surface.fill(GREEN)
        elif "protestor" in filename:
            surface.fill(YELLOW)
        elif "boss" in filename:
            surface.fill(RED)
        else:
            surface.fill(GRAY)
        return surface

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = load_sprite("player.png", (75, 75))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 5
        self.trust_level = 0
        self.interaction_range = 50
        self.convinced_workers = 0

    def move(self, dx, dy, boss, convinced_workers):
        # Calculate new position
        new_x = self.rect.x + dx * self.speed
        new_y = self.rect.y + dy * self.speed
        
        # Check if boss is blocking movement
        boss_blocking = False
        if (abs(new_x - boss.rect.x) < 50 and 
            new_y < boss.rect.y + boss.rect.height and 
            new_y + self.rect.height > boss.rect.y):
            boss_blocking = True
        
        # Apply movement if not blocked
        if not boss_blocking:
            self.rect.x = new_x
            self.rect.y = new_y
        else:
            # Bounce off the boss like rubber
            # Calculate bounce direction based on collision side
            if abs(self.rect.x - boss.rect.x) < abs(self.rect.y - boss.rect.y):
                # Horizontal collision - bounce left or right
                if self.rect.x < boss.rect.x:
                    self.rect.x = boss.rect.x - self.rect.width - 5
                else:
                    self.rect.x = boss.rect.x + boss.rect.width + 5
            else:
                # Vertical collision - bounce up or down
                if self.rect.y < boss.rect.y:
                    self.rect.y = boss.rect.y - self.rect.height - 5
                else:
                    self.rect.y = boss.rect.y + boss.rect.height + 5
        
        # Keep player on screen
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

class Coworker(pygame.sprite.Sprite):
    def __init__(self, x, y, name):
        super().__init__()
        self.image = load_sprite("worker.png", (75, 75))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.name = name
        self.trust_level = 0
        self.convinced = False
        self.protesting = False
        self.target_x = x
        self.target_y = y
        self.speed = 2
        self.protest_angle = 0
        self.protest_radius = 60
        self.dialogue = [
            "Hey, how's it going?",
            "The boss has been really micromanaging lately...",
            "I think we should stick together on this.",
            "We deserve better working conditions."
        ]

    def update(self, boss, protesting_workers):
        if self.convinced and not self.protesting:
            # Move towards boss to protest
            dx = boss.rect.x - self.rect.x
            dy = boss.rect.y - self.rect.y
            distance = (dx**2 + dy**2)**0.5
            
            if distance > self.protest_radius + 10:
                # Normalize and move
                dx = dx / distance * self.speed
                dy = dy / distance * self.speed
                self.rect.x += dx
                self.rect.y += dy
            else:
                # Close enough to protest
                self.protesting = True
                self.image = load_sprite("protestor.png", (75, 75))
        
        elif self.protesting:
            # Surround the boss in a circle
            # Calculate position based on worker index and total protesting workers
            protesting_list = [c for c in protesting_workers if c.protesting]
            if self in protesting_list:
                index = protesting_list.index(self)
                angle = (360 / len(protesting_list)) * index + self.protest_angle
                angle_rad = math.radians(angle)
                
                target_x = boss.rect.centerx + math.cos(angle_rad) * self.protest_radius
                target_y = boss.rect.centery + math.sin(angle_rad) * self.protest_radius
                
                # Move towards target position
                dx = target_x - self.rect.centerx
                dy = target_y - self.rect.centery
                distance = (dx**2 + dy**2)**0.5
                
                if distance > 5:
                    dx = dx / distance * self.speed
                    dy = dy / distance * self.speed
                    self.rect.x += dx
                    self.rect.y += dy
            
            # Rotate the protest circle slowly
            self.protest_angle += 0.5

class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = load_sprite("boss.png", (75, 75))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.base_speed = 5
        self.speed = self.base_speed
        self.detection_range = 150
        self.protesting_workers = 0
        self.target_x = x

    def update(self, protesting_workers, player):
        self.protesting_workers = protesting_workers
        
        # Slow down boss based on protesting workers
        # Each worker reduces speed by 1, minimum speed is 1
        self.speed = max(self.base_speed - protesting_workers, 1)
        
        # Move to block player if not stopped
        if self.speed > 0:
            # Always try to block the player horizontally
            self.target_x = player.rect.x
            
            # Move towards target to block player
            dx = self.target_x - self.rect.x
            if abs(dx) > 5:
                if dx > 0:
                    self.rect.x += self.speed
                else:
                    self.rect.x -= self.speed
                
                # Keep boss on screen
                if self.rect.x < 0:
                    self.rect.x = 0
                elif self.rect.x > SCREEN_WIDTH - self.rect.width:
                    self.rect.x = SCREEN_WIDTH - self.rect.width

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Talk To A Worker")
        self.clock = pygame.time.Clock()
        
        # Load background
        self.background = load_sprite("background.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.coworkers = pygame.sprite.Group()
        self.bosses = pygame.sprite.Group()
        
        # Create player
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.all_sprites.add(self.player)
        
        # Create coworkers
        coworker_positions = [(100, 100), (600, 100), (100, 500), (600, 500)]
        for i, pos in enumerate(coworker_positions):
            coworker = Coworker(pos[0], pos[1], f"Coworker {i+1}")
            self.coworkers.add(coworker)
            self.all_sprites.add(coworker)
        
        # Create boss
        self.boss = Boss(400, 350)
        self.bosses.add(self.boss)
        self.all_sprites.add(self.boss)
        
        # Game state
        self.running = True
        self.paused = False
        self.current_dialogue = None
        self.dialogue_font = pygame.font.Font(None, 32)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.paused = not self.paused
                elif event.key == K_e and not self.paused:
                    self.try_interaction()
                elif event.key == K_SPACE and self.current_dialogue:
                    self.current_dialogue = None

    def try_interaction(self):
        for coworker in self.coworkers:
            distance = pygame.math.Vector2(self.player.rect.center).distance_to(
                pygame.math.Vector2(coworker.rect.center))
            if distance < self.player.interaction_range and not coworker.convinced:
                coworker.trust_level += 1
                if coworker.trust_level >= 3:
                    coworker.convinced = True
                    self.player.convinced_workers += 1
                    self.current_dialogue = f"{coworker.name} is now convinced! ({self.player.convinced_workers}/4 workers)"
                else:
                    self.current_dialogue = f"{coworker.name}: {random.choice(coworker.dialogue)} ({coworker.trust_level}/3)"
                break

    def update(self):
        if self.paused:
            return

        # Handle player movement
        keys = pygame.key.get_pressed()
        dx = keys[K_d] - keys[K_a]
        dy = keys[K_s] - keys[K_w]
        self.player.move(dx, dy, self.boss, self.player.convinced_workers)

        # Update coworkers
        protesting_count = 0
        protesting_workers = []
        for coworker in self.coworkers:
            if coworker.protesting:
                protesting_count += 1
                protesting_workers.append(coworker)
        
        for coworker in self.coworkers:
            coworker.update(self.boss, protesting_workers)

        # Update boss
        self.boss.update(protesting_count, self.player)

        # Check for boss detection
        distance_to_boss = pygame.math.Vector2(self.player.rect.center).distance_to(
            pygame.math.Vector2(self.boss.rect.center))
        if distance_to_boss < self.boss.detection_range and not self.current_dialogue:
            self.current_dialogue = "The boss is watching! Be careful!"

    def draw(self):
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Draw all sprites
        self.all_sprites.draw(self.screen)
        
        # Draw dialogue if present
        if self.current_dialogue:
            text = self.dialogue_font.render(self.current_dialogue, True, BLACK)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            pygame.draw.rect(self.screen, GRAY, text_rect.inflate(20, 20))
            self.screen.blit(text, text_rect)
        
        # Draw stats
        trust_text = self.dialogue_font.render(f"Convinced Workers: {self.player.convinced_workers}/4", True, BLACK)
        self.screen.blit(trust_text, (10, 10))
        
        protesting_count = sum(1 for c in self.coworkers if c.protesting)
        protest_text = self.dialogue_font.render(f"Protesting: {protesting_count}", True, BLACK)
        self.screen.blit(protest_text, (10, 40))
        
        boss_speed_text = self.dialogue_font.render(f"Boss Speed: {self.boss.speed}", True, BLACK)
        self.screen.blit(boss_speed_text, (10, 70))
        
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
    sys.exit() 