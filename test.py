import sys
import pygame
import random
import math
from pygame.locals import *

# Initialisation de Pygame
pygame.init()

# Vérifiez si le module de font est initialisé, sinon initialisez-le
if not pygame.font.get_init():
    pygame.font.init()

infoObject = pygame.display.Info()
WIDTH, HEIGHT = infoObject.current_w, infoObject.current_h  # Résolution complète de l'écran
HEIGHT -= 60

# Charger les sons
explosion_sound = pygame.mixer.Sound("explosion.mp3")
flame_sound = pygame.mixer.Sound("thrust.mp3")
fire_sound = pygame.mixer.Sound("fire.mp3")
laser_sound = pygame.mixer.Sound("laser-2.mp3")
thrust_sound = pygame.mixer.Sound("thrust.wav")
intro_sound = pygame.mixer.Sound("intro.wav")
powerup_sound = pygame.mixer.Sound("powerup.wav")
congratulations_sound = pygame.mixer.Sound("congratulations.mp3")
win_sound = pygame.mixer.Sound("win.mp3")

# Constantes du jeu
BACKGROUND_COLOR = (0, 0, 0)
FONT = pygame.font.SysFont("Arial", 24)

# Charger et redimensionner les images
SHIP_IMAGE = pygame.transform.scale(pygame.image.load("ship1.png"), (62, 151))
BULLET_IMAGE = pygame.transform.scale(pygame.image.load("bullet.png"), (80, 80))
BACKGROUND_IMAGE = pygame.transform.scale(pygame.image.load("background1.jpg"), (WIDTH, HEIGHT))
ASTEROID_IMAGE = pygame.image.load("asteroid1.png")

# Paramètres du défilement du fond
bg_x = 0

# Vitesse et paramètres des objets
BULLET_SPEED = 10
BULLET_LIFETIME = 200

# Charger l'image du sprite sheet pour les flammes
sprite_sheet_flame = pygame.image.load('rocket.png')

# Dimensions de chaque frame de flamme
frame_width_flame = 94.8
frame_height_flame = 288
num_cols_flame = 9  # Nombre de colonnes dans le sprite sheet pour les flammes
num_rows_flame = 1  # Nombre de lignes dans le sprite sheet pour les flammes

# Liste pour stocker chaque frame découpée pour les flammes
frames_flame = []

# Découper le sprite sheet pour les flammes
for row in range(num_rows_flame):
    for col in range(num_cols_flame):
        frame = sprite_sheet_flame.subsurface(pygame.Rect(col * frame_width_flame, row * frame_height_flame, frame_width_flame, frame_height_flame))
        frames_flame.append(frame)

class Flame:
    def __init__(self):
        self.flame_index = 0

    def thrust(self, x, y, angle):
        rad_angle = math.radians(angle)
        offset_x = -frame_width_flame / 2
        offset_y = 0
        # Positionner la flamme derrière le vaisseau en fonction de son angle
        flame_x = x + offset_x * math.cos(rad_angle) - offset_y * math.sin(rad_angle)
        flame_y = y + offset_x * math.sin(rad_angle) + offset_y * math.cos(rad_angle)
        
        # Incrémenter l'index de frame ou réinitialiser
        if self.flame_index >= len(frames_flame) - 1:
            self.flame_index = 0
        else:
            self.flame_index += 1
        
        return flame_x, flame_y, self.flame_index

class Ship:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.image = SHIP_IMAGE
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.angle = 0  # Angle initial du vaisseau
        self.velocity_x = 0
        self.velocity_y = 0
        self.acceleration = 0.3

    def update(self):
        rad_angle = math.radians(self.angle)
        self.velocity_x += math.cos(rad_angle) * self.acceleration
        self.velocity_y += math.sin(rad_angle) * self.acceleration
        self.x += self.velocity_x
        self.y += self.velocity_y
        # Mise à jour de l'image pivotée et du rect
        self.image = pygame.transform.rotate(SHIP_IMAGE, -self.angle)
        self.rect = self.image.get_rect(center=(self.x, self.y))

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    clock = pygame.time.Clock()
    running = True
    ship = Ship(WIDTH // 2, HEIGHT // 2)
    flame = Flame()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    flame_sound.play()
                    ship.acceleration = 1  # Accélérer
                elif event.key == pygame.K_LEFT:
                    ship.angle += 5  # Tourner à gauche
                elif event.key == pygame.K_RIGHT:
                    ship.angle -= 5  # Tourner à droite

        screen.fill(BACKGROUND_COLOR)
        ship.update()
        flame_x, flame_y, flame_index = flame.thrust(ship.x, ship.y, ship.angle)
        screen.blit(frames_flame[flame_index], (flame_x, flame_y))
        screen.blit(ship.image, ship.rect.topleft)
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
