import pygame
import sys

# Initialisation de Pygame
pygame.init()

# Charger l'image du sprite sheet
sprite_sheet = pygame.image.load('explosion.png')

# Dimensions de chaque frame de l'explosion
frame_width = 192
frame_height = 192
num_cols = 5  # Nombre de colonnes dans le sprite sheet
num_rows = 4  # Nombre de lignes dans le sprite sheet

# Liste pour stocker chaque frame découpée
frames = []

# Découper le sprite sheet
for row in range(num_rows):
    for col in range(num_cols):
        frame = sprite_sheet.subsurface(pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height))
        frames.append(frame)

# Exemple pour afficher les frames
screen = pygame.display.set_mode((800, 600))
running = True
frame_index = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    screen.fill((0, 0, 0))  # Efface l'écran avec du noir
    if frame_index < len(frames):
        screen.blit(frames[frame_index], (100, 100))
        frame_index += 1
    else:
        frame_index = 0  # Recommencer l'animation

    pygame.display.flip()
    pygame.time.delay(50)  # Délai entre les frames pour ralentir l'animation

pygame.quit()
sys.exit()
