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
explosion_sound = pygame.mixer.Sound("assets/explosion.mp3")
flame_sound = pygame.mixer.Sound("assets/thrust.mp3")
fire_sound = pygame.mixer.Sound("assets/fire.mp3")
laser_sound = pygame.mixer.Sound("assets/laser-2.mp3")
rythme_sound = pygame.mixer.Sound("assets/thrust.wav")
intro_sound = pygame.mixer.Sound("assets/intro.wav")
powerup_sound = pygame.mixer.Sound("assets/powerup.wav")
congratulations_sound = pygame.mixer.Sound("assets/congratulations.wav")
win_sound = pygame.mixer.Sound("assets/win.wav")


# Constantes du jeu
BACKGROUND_COLOR = (0, 0, 0)
FONT = pygame.font.SysFont("Arial", 24)

# Charger et redimensionner les images
SHIP_IMAGE = pygame.transform.scale(pygame.image.load("assets/ship1.png"), (62, 151))
BULLET_IMAGE = pygame.transform.scale(pygame.image.load("assets/bullet.png"), (80, 80))
BACKGROUND_IMAGE = pygame.transform.scale(pygame.image.load("assets/background1.jpg"), (WIDTH, HEIGHT))
ASTEROID_IMAGE = pygame.image.load("assets/asteroid1.png")
ALIEN_IMAGE = pygame.image.load("assets/alien1.png") #pygame.transform.scale(, (690, 257))

# Paramètres du défilement du fond
bg_x = 0

# Vitesse et paramètres des objets
BULLET_SPEED = 10
BULLET_LIFETIME = 200

# Charger l'image du sprite sheet
sprite_sheet = pygame.image.load('assets/explosion.png')

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


sprite_sheet_flame = pygame.image.load('assets/rocket.png')

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


sprite_sheet_shield = pygame.image.load('assets/shield.png')

# Dimensions de chaque frame de shield
frame_width_shield = 161
frame_height_shield = 157
num_cols_shield = 5  # Nombre de colonnes dans le sprite sheet pour shield
num_rows_shield = 4  # Nombre de lignes dans le sprite sheet pour shield

# Liste pour stocker chaque frame découpée pour shield
frames_shield = []

# Découper le sprite sheet pour les shield
for row in range(num_rows_shield):
    for col in range(num_cols_shield):
        frame = sprite_sheet_shield.subsurface(pygame.Rect(col * frame_width_shield, row * frame_height_shield, frame_width_shield, frame_height_shield))
        frames_shield.append(frame)

 
class Shield:
    def __init__(self):
        self.shield_index = 0
        self.shield_remaining_tick = 0
        self.active = False

    def activate(self):
        self.active = True
        self.shield_remaining_tick = 500
        
    def deactivate(self):
        self.active = False
        self.shield_remaining_tick = 0

    def is_active(self):
       return self.active
   
    def update(self, x, y, angle):
        rad_angle = math.radians(angle)
        offset_x = 40
        offset_y = 0

        # Calcul de la position sur le vaisseau
        shield_x = x + offset_x * math.cos(rad_angle) - offset_y * math.sin(rad_angle)
        shield_y = y + offset_x * math.sin(rad_angle) + offset_y * math.cos(rad_angle)
        
        
        shield_image = frames_shield[self.shield_index]
        
        # Rotation de l'image du bouclier pour qu'il suive l'orientation du vaisseau
        rotated_flame_image = pygame.transform.rotate(shield_image, -angle +90)  # Le "+90" est nécessaire si l'image de base de la flamme est verticale

        
        # Réduction de taille de 10%
        # current_width = rotated_flame_image.get_width()
        # current_height = rotated_flame_image.get_height()
        # new_width = int(current_width * 1.2)  # 90% de la largeur actuelle
        # new_height = int(current_height * 1.2)  # 90% de la hauteur actuelle
        # scaled_shield_image = pygame.transform.scale(rotated_flame_image, (new_width, new_height))


        # Mise à jour de l'index de la frame pour l'animation
        if self.shield_index >= len(frames_shield) - 1:
            self.shield_index = 0
        else:
            self.shield_index += 1
            
        self.shield_remaining_tick -= 1
        if self.shield_remaining_tick <= 0:
            self.active = False

        return shield_x, shield_y, rotated_flame_image


class Ship:
    def __init__(self, x, y):
        self.alive = True
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

    def is_alive(self):
        return self.alive
    
    def destruct(self):
        self.alive = False
    
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
        
class Alien:
    def __init__(self, x, y, ratio):
        self.x, self.y = x, y
        self.image = pygame.transform.scale(ALIEN_IMAGE, (690 / ratio, 257 / ratio))
        #self.image = ALIEN_IMAGE
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.angle = 0
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
    
    global BACKGROUND_IMAGE
    global ASTEROID_IMAGE

    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("Asteroids")
    clock = pygame.time.Clock()
    fullscreen = True
    show_message = False
    show_message_tick = 0

    
    ship = Ship(WIDTH // 2, HEIGHT // 2)
    shield = Shield()
    asteroids = []
    bullets = []
    explosions = []
    power_ups = []

    score, bombs_remaining = 0, 3
    next_powerup_time = 0
    last_powerup_time = pygame.time.get_ticks()
    
    stage = 0
    new_stage = True
    win_game = False
    loose_game = False
    
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
        
        # Gestion des stages
        if new_stage:
            stage += 1
            font_size = 25  # Taille initiale de la police
            ship.image = pygame.transform.scale(pygame.image.load(f"assets/ship{stage}.png"), (250/4, 363/3))
            ship.init()
            shield.activate()
            bullets = []
            asteroids = []
            aliens = []
            
            if stage > 1:
                win_channel.play(win_sound)

            BACKGROUND_IMAGE = pygame.transform.scale(pygame.image.load(f"assets/background{stage}.jpg"), (WIDTH, HEIGHT))
            ASTEROID_IMAGE = pygame.image.load(f"assets/asteroid{stage}.png")
            text = f"Stage {stage}"
            show_message_tick = 100
            
            if stage == 1:
                asteroids.extend([Asteroid(random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100), random.randint(30, 100)) for _ in range(10)])
                aliens.extend([Alien(random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100), random.randint(4, 8)) for _ in range(1)])
            elif stage == 2:
                asteroids.extend([Asteroid(random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100), random.randint(30, 100)) for _ in range(10)])
            elif stage == 3:
                asteroids.extend([Asteroid(random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100), random.randint(30, 100)) for _ in range(2)])
                aliens.extend([Alien(random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100), random.randint(4, 8)) for _ in range(10)])
            else:
                asteroids.extend([Asteroid(random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100), random.randint(30, 100)) for _ in range(15)])

            new_stage = False
            
        if win_game:            
            congratulations_channel.play(congratulations_sound)
            text = "Congratulations ! <ENTER> to restart"
            font_size = 25
            show_message = True
            win_game = False
            
        if loose_game:            
            text = "Game Over. <ENTER> to restart"
            font_size = 25
            show_message = True
            loose_game = False
        
        if current_time - last_powerup_time > next_powerup_time:
            power_ups.append(PowerUp())
            last_powerup_time = current_time
            next_powerup_time = random.randint(5000, 15000)  # Power-ups appear every 5 to 15 seconds
        
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if not ship.is_alive() and event.key == pygame.K_RETURN:
                    ship.alive = True
                    shield.activate()
                    score, bombs_remaining = 0, 3
                    stage = 0
                    show_message = False
                    new_stage = True
                if ship.is_alive() and (event.key == pygame.K_UP or event.key == pygame.K_z):
                    #if not flame_channel.get_busy():
                    flame_channel.play(flame_sound)
                    if not rythmics_channel.get_busy():
                        rythmics_channel.play(rythme_sound)
                if ship.is_alive() and event.key == pygame.K_s:
                    shield.activate()
                if event.key == pygame.K_F11 or event.key == pygame.K_ESCAPE:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((WIDTH, HEIGHT))

        keys = pygame.key.get_pressed()
        if (keys[pygame.K_UP] or keys[pygame.K_z]) and ship.is_alive():
            ship.accelerate(1)
            gas = True
        if (keys[pygame.K_LEFT] or keys[pygame.K_q]) and ship.is_alive():
            ship.rotate(-1)
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and ship.is_alive():
            ship.rotate(1)
        if keys[pygame.K_SPACE] and ship.is_alive() and bombs_remaining > 0:
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
            if ship.is_alive() and not shield.is_active() and pygame.sprite.collide_mask(asteroid, ship): # ship.rect.colliderect(asteroid.rect):
                explosions.append(Explosion(ship.x, ship.y))
                ship.destruct()
                # Vous pouvez ajouter ici la logique pour terminer le jeu ou retirer une vie
                loose_game = True
                break  # Sortez de la boucle si vous voulez terminer le jeu immédiatement

            
        for alien in aliens:
            alien.move()
            if ship.is_alive() and not shield.is_active() and pygame.sprite.collide_mask(alien, ship): # ship.rect.colliderect(alien.rect):
                explosions.append(Explosion(ship.x, ship.y))
                ship.destruct()
                # Vous pouvez ajouter ici la logique pour terminer le jeu ou retirer une vie
                #display_level_text(screen, "That's one small step for man, one giant leap for alien kind!", 5000, clock, ship)
                loose_game = True
                break  # Sortez de la boucle si vous voulez terminer le jeu immédiatement




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

            for alien in aliens:
                if pygame.sprite.collide_mask(bullet, alien):
                    explosions.append(Explosion(bullet.rect.left, bullet.rect.top))
                    bullets.remove(bullet)
                    aliens.remove(alien)
                    score += 50  # Increment score for each asteroid destroyed
                    bombs_remaining += 50
                    break
            

        if len(asteroids) + len(aliens) == 0:
            if stage >= 4:
                ship.destruct()
                win_game = True
                new_stage = False
            else:
                new_stage = True



        for asteroid in asteroids:
            asteroid_rotated = pygame.transform.rotate(asteroid.image, asteroid.angle)
            asteroid_rect = asteroid_rotated.get_rect(center=(asteroid.x, asteroid.y))
            screen.blit(asteroid_rotated, asteroid_rect.topleft)
            
        for alien in aliens:
            alien_rotated = pygame.transform.rotate(alien.image, alien.angle)
            alien_rect = alien_rotated.get_rect(center=(alien.x, alien.y))
            screen.blit(alien_rotated, alien_rect.topleft)

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

                
        # Text messages
        if show_message_tick > 0 or show_message:
            color = pygame.Color(255, 255, 255)  # Couleur blanche initiale
            alpha = 255  # Opacité initiale

            font = pygame.font.SysFont("Arial", font_size)
            text_surface = font.render(text, True, color)
            text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))

            # Modifier la taille de la police pour l'effet de zoom
            font_size += 1 if font_size < 100 else 0  # Augmenter la taille jusqu'à 100

            # Effet de fade-in (décommenter pour utiliser)
            alpha = max(0, alpha - 1)  # Réduire l'opacité
            text_surface.set_alpha(alpha)  # Appliquer l'opacité

            screen.blit(text_surface, text_rect)  # Afficher le texte
            show_message_tick -= 1
            
        # Display the score and bombs remaining
        shield_text = FONT.render("SHIELD ON ", True, (0, 0, 255))
        stage_text = FONT.render(f"Stage: {stage}", True, (255, 0, 0))
        score_text = FONT.render(f"Score: {score}", True, (255, 0, 0))
        bombs_text = FONT.render(f"Bombs: {bombs_remaining}", True, (255, 255, 255))
       
        if shield.is_active():
            screen.blit(shield_text, (WIDTH / 2 - score_text.get_width() / 2, HEIGHT - 100))
        screen.blit(stage_text, (WIDTH / 2 - score_text.get_width() / 2, HEIGHT - 75))
        screen.blit(score_text, (WIDTH / 2 - score_text.get_width() / 2, HEIGHT - 50))
        screen.blit(bombs_text, (WIDTH / 2 - bombs_text.get_width() / 2, HEIGHT - 25))

        if ship.is_alive():
            screen.blit(ship.rotated_image, ship.rotated_rect.topleft)

        if shield.is_active():
            (shield_x, shield_y, rotated_shield_image) = shield.update(ship.x, ship.y, ship.angle)
            shield_rect = rotated_shield_image.get_rect(center=(shield_x, shield_y))
            screen.blit(rotated_shield_image, shield_rect)



        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
