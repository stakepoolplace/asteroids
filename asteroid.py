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
fire_sound = pygame.mixer.Sound("fire.mp3")
thrust_sound = pygame.mixer.Sound("thrust.wav")
intro_sound = pygame.mixer.Sound("intro.wav")
powerup_sound = pygame.mixer.Sound("powerup.wav")

# Constantes du jeu
BACKGROUND_COLOR = (0, 0, 0)
FONT = pygame.font.SysFont("Arial", 24)

# Charger et redimensionner les images
SHIP_IMAGE = pygame.transform.scale(pygame.image.load("ship.png"), (80, 120))
BULLET_IMAGE = pygame.transform.scale(pygame.image.load("bullet.png"), (80, 80))
BACKGROUND_IMAGE = pygame.transform.scale(pygame.image.load("background.jpg"), (WIDTH, HEIGHT))

# Paramètres du défilement du fond
bg_x = 0

# Vitesse et paramètres des objets
BULLET_SPEED = 10
BULLET_LIFETIME = 200

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

class Explosion:
    def __init__(self, x, y):
        explosion_sound.play()
        self.frame_index = 0
        self.x, self.y = x - frame_width / 2, y - frame_height / 2

    def explode(self):
        self.frame_index += 1


class Ship:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.image = SHIP_IMAGE
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.angle = -90
        self.velocity_x = 0
        self.velocity_y = 0
        self.angular_velocity = 0
        self.acceleration = 0.3
        self.rotation_acceleration = 0.35
        self.friction = 0.99
        self.angular_friction = 0.95
        self.update_graphics()

    def update_graphics(self):
        self.rotated_image = pygame.transform.rotate(self.image, -self.angle - 90)
        self.rotated_rect = self.rotated_image.get_rect(center=(self.x, self.y))

    def accelerate(self, direction):
        rad_angle = math.radians(self.angle)
        self.velocity_x += math.cos(rad_angle) * self.acceleration * direction
        self.velocity_y += math.sin(rad_angle) * self.acceleration * direction

    def rotate(self, direction):
        self.angular_velocity += self.rotation_acceleration * direction

    def update(self):
        self.velocity_x *= self.friction
        self.velocity_y *= self.friction
        self.angular_velocity *= self.angular_friction
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.angle += self.angular_velocity
        self.angle %= 360
        self.x %= WIDTH
        self.y %= HEIGHT
        self.rect.center = (self.x, self.y)
        # Mise à jour pour déplacer le fond d'écran
        global bg_x
        bg_x -= self.velocity_x * 0.5  # Vitesse du défilement adaptée à celle du vaisseau
        # Ralentissement du vaisseau et accélération du défilement du fond
        global scroll_speed
        if self.x > WIDTH * 0.85:
            scroll_speed = 2  # Accélération du défilement du fond
        else:
            scroll_speed = 0.5  # Réinitialisation de la vitesse de défilement

        self.x = max(50, min(self.x, WIDTH * 0.95))  # Limite la position x pour ne pas dépasser 95% de la largeur

        self.update_graphics()

class Asteroid:
    def __init__(self, x, y, size):
        self.x, self.y = x, y
        self.size = size
        self.image = pygame.transform.scale(pygame.image.load("asteroid.png"), (self.size, self.size))
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.angle = random.randint(0, 360)
        self.speed = random.randint(2, 4)
        self.rotation_speed = random.uniform(-0.5, 0.5)
        self.mask = pygame.mask.from_surface(self.image)

    def move(self):
        self.x += math.cos(math.radians(self.angle)) * self.speed
        self.y += math.sin(math.radians(self.angle)) * self.speed
        self.x %= WIDTH
        self.y %= HEIGHT
        self.rect.center = (self.x, self.y)

    def rotate(self):
        self.angle += self.rotation_speed
        self.angle %= 360

class Bullet:
    def __init__(self, x, y, angle):
        self.x, self.y = x, y
        self.image = BULLET_IMAGE
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.angle = angle
        self.lifetime = 0
        self.mask = pygame.mask.from_surface(self.image)

    def move(self):
        self.x += math.cos(math.radians(self.angle)) * BULLET_SPEED
        self.y += math.sin(math.radians(self.angle)) * BULLET_SPEED
        self.rect.center = (self.x, self.y)
        self.lifetime += 1
        if self.lifetime > BULLET_LIFETIME:
            return True
        return False

class PowerUp:
    def __init__(self):
        self.x, self.y = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.size = 30
        self.size_orig = random.randint(5, 30) 
        self.rect = pygame.Rect(self.x - self.size // 2, self.y - self.size // 2, self.size, self.size)

    def draw(self, surface, tick):
        self.size = self.size_orig * abs(math.sin(tick))
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.size + 5)

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("Asteroids")
    clock = pygame.time.Clock()
    fullscreen = True

    player = Ship(WIDTH // 2, HEIGHT // 2)
    asteroids = [Asteroid(random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100), random.randint(30, 100)) for _ in range(5)]
    bullets = []
    explosions = []
    power_ups = []

    score, bombs_remaining = 0, 3
    next_powerup_time = 0
    last_powerup_time = pygame.time.get_ticks()
    
    # Variables de contrôle
    thrust_channel = pygame.mixer.find_channel()

    intro_channel = pygame.mixer.find_channel()
    intro_channel.play(intro_sound)
    
    powerup_channel = pygame.mixer.find_channel()
    fire_channel = pygame.mixer.find_channel()


    running = True
    while running:
        current_time = pygame.time.get_ticks()
        if current_time - last_powerup_time > next_powerup_time:
            power_ups.append(PowerUp())
            last_powerup_time = current_time
            next_powerup_time = random.randint(5000, 15000)  # Power-ups appear every 5 to 15 seconds
        
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    if not thrust_channel.get_busy():
                        thrust_channel.play(thrust_sound)


                if event.key == pygame.K_F11 or event.key == pygame.K_ESCAPE:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((WIDTH, HEIGHT))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            player.accelerate(1)
        if keys[pygame.K_LEFT]:
            player.rotate(-1)
        if keys[pygame.K_RIGHT]:
            player.rotate(1)
        if keys[pygame.K_SPACE] and bombs_remaining > 0:
            if not fire_channel.get_busy():
                fire_channel.play(fire_sound)
            bullets.append(Bullet(player.x, player.y, player.angle))
            bombs_remaining -= 1  # Decrement the bomb count each time one is fired

        screen.fill(BACKGROUND_COLOR)

        player.update()
        
    
        # Défilement du fond
        bg_x_shift = bg_x - scroll_speed
        real_bg_x = bg_x_shift % WIDTH
        screen.blit(BACKGROUND_IMAGE, (real_bg_x - WIDTH, 0))
        if real_bg_x < WIDTH:
            screen.blit(BACKGROUND_IMAGE, (real_bg_x, 0))

        for asteroid in asteroids:
            asteroid.move()
            asteroid.rotate()

        bullets = [bullet for bullet in bullets if not bullet.move()]

        for bullet in bullets:
            for asteroid in asteroids:
                if pygame.sprite.collide_mask(bullet, asteroid):
                    explosions.append(Explosion(bullet.rect.left, bullet.rect.top))
                    bullets.remove(bullet)
                    asteroids.remove(asteroid)
                    score += 10  # Increment score for each asteroid destroyed
                    bombs_remaining += 10
                    new_size = random.randint(30, 100)
                    asteroids.append(Asteroid(random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100), new_size))
                    break



        for asteroid in asteroids:
            asteroid_rotated = pygame.transform.rotate(asteroid.image, asteroid.angle)
            asteroid_rect = asteroid_rotated.get_rect(center=(asteroid.x, asteroid.y))
            screen.blit(asteroid_rotated, asteroid_rect.topleft)

        for bullet in bullets:
            bullet_rotated = pygame.transform.rotate(bullet.image, bullet.angle)
            bullet_rect = bullet_rotated.get_rect(center=(bullet.x, bullet.y))
            screen.blit(bullet_rotated, bullet_rect.topleft)

        for explosion in explosions:
            explosion.explode()
            screen.blit(frames[explosion.frame_index], (explosion.x, explosion.y))
            if explosion.frame_index >= len(frames) - 1:
                explosions.remove(explosion)
                    
        for power_up in power_ups:
            power_up.draw(screen, current_time)
            if player.rect.colliderect(power_up.rect):
                powerup_channel.play(powerup_sound)
                power_ups.remove(power_up)
                bombs_remaining += 100  # Add 100 bombs when a power-up is collected

                


        # Display the score and bombs remaining
        score_text = FONT.render(f"Score: {score}", True, (255, 0, 0))
        bombs_text = FONT.render(f"Bombs: {bombs_remaining}", True, (255, 255, 255))
        screen.blit(score_text, (WIDTH / 2 - score_text.get_width() / 2, HEIGHT - 50))
        screen.blit(bombs_text, (WIDTH / 2 - bombs_text.get_width() / 2, HEIGHT - 25))

        screen.blit(player.rotated_image, player.rotated_rect.topleft)




        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
