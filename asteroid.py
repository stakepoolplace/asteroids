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
rythme_sound = pygame.mixer.Sound("thrust.wav")
intro_sound = pygame.mixer.Sound("intro.wav")
powerup_sound = pygame.mixer.Sound("powerup.wav")
congratulations_sound = pygame.mixer.Sound("congratulations.wav")
win_sound = pygame.mixer.Sound("win.wav")


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


sprite_sheet_flame = pygame.image.load('rocket.png')

# Dimensions de chaque frame de flamme
frame_width_flame = 85.3
frame_height_flame = 259
num_cols_flame = 8  # Nombre de colonnes dans le sprite sheet pour les flammes
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
        offset_x = frame_width_flame * 1.2
        offset_y = 0
        
        # Calcul de la position derrière le vaisseau
        flame_x = x + offset_x * math.cos(rad_angle) - offset_y * math.sin(rad_angle)
        flame_y = y + offset_x * math.sin(rad_angle) + offset_y * math.cos(rad_angle)
        
        # Rotation de l'image de la flamme pour qu'elle suive l'orientation du vaisseau
        rotated_flame_image = pygame.transform.rotate(frames_flame[self.flame_index], -angle + 90)  # Le "+90" est nécessaire si l'image de base de la flamme est verticale

        # Réduction de taille de 10%
        current_width = rotated_flame_image.get_width()
        current_height = rotated_flame_image.get_height()
        new_width = int(current_width * 0.5)  # 90% de la largeur actuelle
        new_height = int(current_height * 0.5)  # 90% de la hauteur actuelle
        scaled_flame_image = pygame.transform.scale(rotated_flame_image, (new_width, new_height))


        # Mise à jour de l'index de la frame pour l'animation
        if self.flame_index >= len(frames_flame) - 1:
            self.flame_index = 0
        else:
            self.flame_index += 1

        return flame_x, flame_y, scaled_flame_image


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

    def init(self):
        self.center()
        self.angle = -90
        self.velocity_x = 0
        self.velocity_y = 0
        self.angular_velocity = 0
        self.update()

    def center(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2

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
        self.image = pygame.transform.scale(ASTEROID_IMAGE, (self.size, self.size))
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
        
# Fonction pour afficher le texte du niveau
def display_level_text(screen, text, duration_ms, clock, ship):
    global BACKGROUND_IMAGE
    start_time = pygame.time.get_ticks()
    font_size = 30  # Taille initiale de la police
    color = pygame.Color(255, 255, 255)  # Couleur blanche initiale
    background_color = pygame.Color(0, 0, 0)
    alpha = 255  # Opacité initiale

    while pygame.time.get_ticks() - start_time < duration_ms:
        screen.fill(background_color)
        screen.blit(BACKGROUND_IMAGE, (0, 0))  # Redessiner le fond à chaque frame
        screen.blit(ship.rotated_image, ship.rotated_rect.topleft)

        font = pygame.font.SysFont("Arial", font_size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))

        # Modifier la taille de la police pour l'effet de zoom
        font_size += 1 if font_size < 100 else 0  # Augmenter la taille jusqu'à 100

        # Effet de fade-in (décommenter pour utiliser)
        alpha = max(0, alpha - 1)  # Réduire l'opacité
        text_surface.set_alpha(alpha)  # Appliquer l'opacité

        screen.blit(text_surface, text_rect)  # Afficher le texte
        pygame.display.flip()  # Mettre à jour l'écran
        clock.tick(60)  # Limiter à 30 FPS

    # Pause avant de continuer
    pygame.time.wait(3000)

def main():
    
    global BACKGROUND_IMAGE
    global ASTEROID_IMAGE

    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("Asteroids")
    clock = pygame.time.Clock()
    fullscreen = True

    ship = Ship(WIDTH // 2, HEIGHT // 2)
    asteroids = []
    bullets = []
    explosions = []
    power_ups = []
    flame_index = 0

    score, bombs_remaining = 0, 3
    next_powerup_time = 0
    last_powerup_time = pygame.time.get_ticks()
    
    stage = 1
    new_stage = True
    end_game = False
    
    # Variables de contrôle

    intro_channel = pygame.mixer.find_channel()
    intro_channel.play(intro_sound)
    
    powerup_channel = pygame.mixer.find_channel()
    fire_channel = pygame.mixer.find_channel()
    win_channel = pygame.mixer.find_channel()
    congratulations_channel = pygame.mixer.find_channel()
    flame_channel  = pygame.mixer.find_channel()
    rythmics_channel = pygame.mixer.find_channel()

    # takeoff
    flame = Flame()
    
    running = True
    while running:
        
        gas = False
        current_time = pygame.time.get_ticks()
        
        if new_stage:
            ship.image = pygame.transform.scale(pygame.image.load(f"ship{stage}.png"), (250/4, 363/3))
            ship.init()
            bullets = []
            asteroids = []
            
            if stage > 1:
                win_channel.play(win_sound)

            BACKGROUND_IMAGE = pygame.transform.scale(pygame.image.load(f"background{stage}.jpg"), (WIDTH, HEIGHT))

            ASTEROID_IMAGE = pygame.image.load(f"asteroid{stage}.png")
            asteroids.extend([Asteroid(random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100), random.randint(30, 100)) for _ in range(15)])
            
            display_level_text(screen, f"Stage {stage}", 1000, clock, ship)

            new_stage = False
            
        if end_game:            
            congratulations_channel.play(congratulations_sound)
            display_level_text(screen, "Congratulations !", 2000, clock, ship)
            end_game = False
            stage = 0
        
        if current_time - last_powerup_time > next_powerup_time:
            power_ups.append(PowerUp())
            last_powerup_time = current_time
            next_powerup_time = random.randint(5000, 15000)  # Power-ups appear every 5 to 15 seconds
        
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_z:
                    #if not flame_channel.get_busy():
                    flame_channel.play(flame_sound)
                    if not rythmics_channel.get_busy():
                        rythmics_channel.play(rythme_sound)


                if event.key == pygame.K_F11 or event.key == pygame.K_ESCAPE:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((WIDTH, HEIGHT))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_z]:
            ship.accelerate(1)
            gas = True
        if keys[pygame.K_LEFT] or keys[pygame.K_q]:
            ship.rotate(-1)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            ship.rotate(1)
        if keys[pygame.K_SPACE] and bombs_remaining > 0:
            #if not fire_channel.get_busy():
            if stage == 2:
                fire_channel.play(fire_sound)
            else:
                fire_channel.play(laser_sound)

            bullets.append(Bullet(ship.x, ship.y, ship.angle))
            bombs_remaining -= 1  # Decrement the bomb count each time one is fired

        screen.fill(BACKGROUND_COLOR)

        ship.update()
        
    
        # Défilement du fond, pensez à placer les autres élements graphiques après
        bg_x_shift = bg_x - scroll_speed
        real_bg_x = bg_x_shift % WIDTH
        screen.blit(BACKGROUND_IMAGE, (real_bg_x - WIDTH, 0))
        if real_bg_x < WIDTH:
            screen.blit(BACKGROUND_IMAGE, (real_bg_x, 0))

        if gas:
            flame_x, flame_y, rotated_flame_image = flame.thrust(ship.x, ship.y, ship.angle - 180)
            flame_rect = rotated_flame_image.get_rect(center=(flame_x, flame_y))
            screen.blit(rotated_flame_image, flame_rect)

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
                    break

        if len(asteroids) == 0:
            stage += 1
            if stage >= 5:
                end_game = True
            else:
                new_stage = True



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
            if ship.rect.colliderect(power_up.rect):
                #if not powerup_channel.get_busy():
                powerup_channel.play(powerup_sound)
                power_ups.remove(power_up)
                bombs_remaining += 100  # Add 100 bombs when a power-up is collected

                


        # Display the score and bombs remaining
        stage_text = FONT.render(f"Stage: {stage}", True, (255, 0, 0))
        score_text = FONT.render(f"Score: {score}", True, (255, 0, 0))
        bombs_text = FONT.render(f"Bombs: {bombs_remaining}", True, (255, 255, 255))
        screen.blit(stage_text, (WIDTH / 2 - score_text.get_width() / 2, HEIGHT - 75))
        screen.blit(score_text, (WIDTH / 2 - score_text.get_width() / 2, HEIGHT - 50))
        screen.blit(bombs_text, (WIDTH / 2 - bombs_text.get_width() / 2, HEIGHT - 25))

        screen.blit(ship.rotated_image, ship.rotated_rect.topleft)



        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
