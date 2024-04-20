import sys
import pygame
import random
import math
from pygame.locals import *

# Initialisation de Pygame
pygame.init()

if not pygame.font.get_init():
    pygame.font.init()

infoObject = pygame.display.Info()
WIDTH, HEIGHT = infoObject.current_w, infoObject.current_h
HEIGHT -= 60

# Charger les sons
explosion_sound = pygame.mixer.Sound("explosion.mp3")
fire_sound = pygame.mixer.Sound("fire.mp3")
thrust_sound = pygame.mixer.Sound("thrust.wav")
intro_sound = pygame.mixer.Sound("intro.wav")
powerup_sound = pygame.mixer.Sound("powerup.wav")

# Constantes du jeu
BACKGROUND_COLOR = (0, 0, 0)
FONT = pygame.font.SysFont("Arial", 24)
SHIP_IMAGE = pygame.transform.scale(pygame.image.load("ship.png"), (80, 120))
BULLET_IMAGE = pygame.transform.scale(pygame.image.load("bullet.png"), (80, 80))
BACKGROUND_IMAGE = pygame.transform.scale(pygame.image.load("background.jpg"), (WIDTH, HEIGHT))
bg_x = 0
scroll_speed = 0.5  # Vitesse initiale de défilement du fond

class Ship:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.image = SHIP_IMAGE
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.velocity_x = 0
        self.max_speed = 5
        self.friction = 0.98

    def update(self):
        self.x += self.velocity_x
        self.rect.center = (self.x, self.y)

        # Ralentissement du vaisseau et accélération du défilement du fond
        if self.x > WIDTH * 0.95:
            self.velocity_x *= self.friction  # Ralentissement progressif
            global scroll_speed
            scroll_speed = 2  # Accélération du défilement du fond
        else:
            scroll_speed = 0.5  # Réinitialisation de la vitesse de défilement

        self.x = min(self.x, WIDTH * 0.95)  # Limite la position x pour ne pas dépasser 95% de la largeur

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("Asteroids")
    clock = pygame.time.Clock()
    player = Ship(WIDTH // 2, HEIGHT // 2)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    player.velocity_x = player.max_speed
                elif event.key == pygame.K_LEFT:
                    player.velocity_x = -player.max_speed

        player.update()

        # Défilement du fond
        bg_x_shift = bg_x - scroll_speed
        real_bg_x = bg_x_shift % WIDTH
        screen.blit(BACKGROUND_IMAGE, (real_bg_x - WIDTH, 0))
        if real_bg_x < WIDTH:
            screen.blit(BACKGROUND_IMAGE, (real_bg_x, 0))

        # Affichage du vaisseau
        screen.blit(player.image, player.rect.topleft)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
