import pygame
import random
import math

from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    K_SPACE,
    KEYDOWN,
    QUIT,
    RLEACCEL,
    K_w,
    K_s,
    K_a,
    K_d,
    K_e,
    K_q,
    K_r
)





SCREEN_HEIGHT = 600
SCREEN_WIDTH = 700
pygame.mixer.init()
pygame.init()

screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])

clock = pygame.time.Clock()
CLOCK_TICK = pygame.USEREVENT + 2
pygame.time.set_timer(CLOCK_TICK, 1000)
seconds = 0
level = 1

ADD_ENEMY = pygame.USEREVENT + 1
enemy_frequency = 500
pygame.time.set_timer(ADD_ENEMY, random.randint(max(1, enemy_frequency - 300), enemy_frequency))
font = pygame.font.Font("freesansbold.ttf", 32)
large_font = pygame.font.Font(None, 72)
level_up_time = 0
amo_cooldown = 0
ADD_CLOUD = pygame.USEREVENT + 3
pygame.time.set_timer(ADD_CLOUD, random.randint(300, 1000))
ADD_Powerup_Twin_Pain = pygame.USEREVENT + 5
pygame.time.set_timer(ADD_Powerup_Twin_Pain, random.randint(3000, 10000))

def increase_freq():
    global enemy_frequency
    enemy_frequency = int(enemy_frequency * 1.000000000000000000001)
    pygame.time.set_timer(ADD_ENEMY, random.randint(max(1, enemy_frequency - 300), enemy_frequency))


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.surf = pygame.image.load("fighter pilot update.png").convert_alpha()
        self.rect = self.surf.get_rect()
        self.lives = 10

    def update(self, pressed_keys):
        if pressed_keys[K_UP]:
            self.rect.move_ip(0, -3)
            move_up_sound = pygame.mixer.Sound("Rising_putter.ogg")
            move_up_sound.play()
        if pressed_keys[K_DOWN]:
            self.rect.move_ip(0, 3)
            move_down_sound = pygame.mixer.Sound("Falling_putter.ogg")
            move_down_sound.play()
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-3, 0)
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(3, 0)

        # Keep player within screen bounds - prevents passing through walls
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

class Twin_Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Twin_Player, self).__init__()
        self.surf = pygame.image.load("Twin Plane.png").convert_alpha()
        self.rect = self.surf.get_rect()
        self.lives = 1

    def update(self, pressed_keys):
        if pressed_keys[K_w] and self.rect.top >= 0:
            self.rect.move_ip(0, -1)
            move_up_sound = pygame.mixer.Sound("Rising_putter.ogg")
            move_up_sound.play()
        if pressed_keys[K_s] and self.rect.bottom <= SCREEN_HEIGHT:
            self.rect.move_ip(0, 1)
            move_down_sound = pygame.mixer.Sound("Falling_putter.ogg")
            move_down_sound.play()

class Bullet_X4_Powerup(pygame.sprite.Sprite):
    def __init__(self):
        super(Bullet_X4_Powerup, self).__init__()
        self.surf = pygame.image.load("Bullet_X4.png").convert_alpha()
        self.rect = self.surf.get_rect(
            center=(
                random.randint(SCREEN_WIDTH - 506, SCREEN_WIDTH - 168),
                random.randint(10, SCREEN_HEIGHT - 10),
            )
        )
        if pressed_keys[K_s] and self.rect.bottom <= SCREEN_HEIGHT:
            self.rect.move_ip(0, 1)
            move_down_sound = pygame.mixer.Sound("Falling_putter.ogg")
            move_down_sound.play()
        if pressed_keys[K_a] and self.rect.left >= 0:
            self.rect.move_ip(-1, 0)
        if pressed_keys[K_d] and self.rect.right <= SCREEN_WIDTH:
            self.rect.move_ip(1, 0)


class Powerup_Twin_Pain(pygame.sprite.Sprite):
    def __init__(self):
        super(Powerup_Twin_Pain, self).__init__()
        self.surf = pygame.image.load("Twin_Pain.png").convert_alpha()
        self.rect = self.surf.get_rect(
            center=(
                random.randint(SCREEN_WIDTH - 506, SCREEN_WIDTH - 168),
                random.randint(10, SCREEN_HEIGHT - 10),
            )
        )


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super(Enemy, self).__init__()
        self.surf = pygame.image.load("missle.png").convert_alpha()
        # self.surf = pygame.transform.scale(self.surf, (100, 70))
        self.rect = self.surf.get_rect(
            center=(
                random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),
                random.randint(10, SCREEN_HEIGHT - 10),
            )
        )
        self.speed = 1.5

    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()


class Boss(pygame.sprite.Sprite):
    def __init__(self, boss_level=1):
        super(Boss, self).__init__()
        # Load both boss images for animation
        self.boss_image1 = pygame.image.load("Boss.png").convert_alpha()
        self.boss_image2 = pygame.image.load("Boss2.png").convert_alpha()
        self.boss_image1 = pygame.transform.scale(self.boss_image1, (150, 150))
        self.boss_image2 = pygame.transform.scale(self.boss_image2, (150, 150))

        # Animation variables
        self.animation_timer = 0
        self.animation_speed = 60  # Frames to switch between images (slower animation)
        self.current_image = 0  # 0 for Boss.png, 1 for Boss2.png

        self.surf = self.boss_image1  # Start with first image
        self.rect = self.surf.get_rect()
        self.rect.centerx = SCREEN_WIDTH - 100
        self.rect.centery = SCREEN_HEIGHT // 2

        # Scale difficulty based on boss level
        self.boss_level = boss_level
        self.health = 30 + (boss_level - 1) * 25  # 50, 75, 100, 125, etc.
        self.max_health = self.health
        self.speed = 2 + (boss_level - 1) * 0.5  # 2, 2.5, 3, 3.5, etc.
        self.direction = 1
        self.shoot_timer = 0
        self.shoot_cooldown = max(30, 60 - (boss_level - 1) * 10)  # 60, 50, 40, 30 (faster shooting)
        self.movement_timer = 0
        self.movement_pattern = 0  # 0: vertical, 1: circular, 2: horizontal zigzag
        self.pattern_duration = max(120, 180 - (boss_level - 1) * 15)  # Faster pattern switching
        self.original_x = self.rect.centerx
        self.original_y = self.rect.centery
        self.angle = 0

    def update(self):
        # Handle animation
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_image = 1 - self.current_image  # Toggle between 0 and 1
            if self.current_image == 0:
                self.surf = self.boss_image1
            else:
                self.surf = self.boss_image2

        self.movement_timer += 1

        # Switch movement patterns every few seconds
        if self.movement_timer >= self.pattern_duration:
            self.movement_timer = 0
            self.movement_pattern = (self.movement_pattern + 1) % 3
            self.original_x = self.rect.centerx
            self.original_y = self.rect.centery
            self.angle = 0

        # Different movement patterns
        if self.movement_pattern == 0:  # Vertical movement
            self.rect.centery += self.speed * self.direction
            if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
                self.direction *= -1

        elif self.movement_pattern == 1:  # Circular movement
            self.angle += 0.05
            radius = 80
            self.rect.centerx = self.original_x + int(radius * math.cos(self.angle))
            self.rect.centery = self.original_y + int(radius * math.sin(self.angle))
            # Keep boss on screen
            self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

        elif self.movement_pattern == 2:  # Horizontal zigzag
            self.rect.centerx += self.speed * self.direction
            self.rect.centery += int(math.sin(self.movement_timer * 0.1) * 3)
            if self.rect.right >= SCREEN_WIDTH or self.rect.left <= SCREEN_WIDTH - 200:
                self.direction *= -1

        # Keep boss within reasonable bounds
        self.rect.clamp_ip(pygame.Rect(SCREEN_WIDTH - 250, 0, 250, SCREEN_HEIGHT))

        # Shooting logic
        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_cooldown:
            self.shoot_timer = 0
            return True  # Signal to create boss bullet
        return False

    def take_damage(self, damage=1):
        self.health -= damage
        if self.health <= 0:
            self.kill()
            return True  # Boss defeated
        return False


class BossBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(BossBullet, self).__init__()
        self.surf = pygame.image.load("missle.png").convert_alpha()
        self.surf = pygame.transform.scale(self.surf, (30, 20))
        self.rect = self.surf.get_rect(center=(x, y))
        self.speed = 3

    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()


class Ammo(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Ammo, self).__init__()
        self.surf = pygame.image.load("Bullet_X4.png").convert_alpha()
        self.rect = self.surf.get_rect(center=(x, y))
        self.speed = 3
        self.speed_x = self.speed
        self.speed_y = 0
        self.pierce_count = 3  # Number of enemies the bullet can pierce

    def update(self):
        self.rect.move_ip(self.speed_x, self.speed_y)
        if self.rect.left > SCREEN_WIDTH:
            self.kill()

class Background:
    def __init__(self):
        self.image = pygame.image.load("bbackground.png").convert()
        self.rect1 = self.image.get_rect(topleft=(0, 0))
        self.rect2 = self.image.get_rect(topleft=(self.rect1.width, 0))

    def draw(self, surface):
        surface.blit(self.image, self.rect1)
        surface.blit(self.image, self.rect2)


class EnergyPowerup(pygame.sprite.Sprite):
    def __init__(self):
        super(EnergyPowerup, self).__init__()
        self.surf = pygame.image.load("enegry.png").convert_alpha()
        self.rect = self.surf.get_rect(
            center=(
                random.randint(SCREEN_WIDTH - 506, SCREEN_WIDTH - 168),
                random.randint(10, SCREEN_HEIGHT - 10),
            )
        )

class RangeShooterPowerup(pygame.sprite.Sprite):
    def __init__(self):
        super(RangeShooterPowerup, self).__init__()
        self.surf = pygame.image.load("Range_shooter.png").convert_alpha()
        self.rect = self.surf.get_rect(
            center=(
                random.randint(SCREEN_WIDTH - 506, SCREEN_WIDTH - 168),
                random.randint(10, SCREEN_HEIGHT - 10),
            )
        )

class InvincibilityPowerup(pygame.sprite.Sprite):
    def __init__(self):
        super(InvincibilityPowerup, self).__init__()
        self.surf = pygame.image.load("invince.png").convert_alpha()
        self.rect = self.surf.get_rect(
            center=(
                random.randint(SCREEN_WIDTH - 506, SCREEN_WIDTH - 168),
                random.randint(10, SCREEN_HEIGHT - 10),
            )
        )

class EnergyBlast(pygame.sprite.Sprite):
    def __init__(self, center_x, center_y):
        super(EnergyBlast, self).__init__()
        self.surf = pygame.image.load("enegry.png").convert_alpha()
        self.rect = self.surf.get_rect(center=(center_x, center_y))
        self.radius = 10
        self.max_radius = SCREEN_WIDTH
        self.expansion_speed = 15

    def update(self):
        self.radius += self.expansion_speed
        scale = self.radius / (self.surf.get_width() / 2)
        self.surf = pygame.transform.scale(self.surf, 
            (int(self.surf.get_width() * scale), 
             int(self.surf.get_height() * scale)))
        self.rect = self.surf.get_rect(center=self.rect.center)
        if self.radius >= self.max_radius:
            self.kill()

class Cloud(pygame.sprite.Sprite):
    def __init__(self):
        super(Cloud, self).__init__()
        self.surf = pygame.image.load("Cloud.png")
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.image = self.surf  # This line fixes the draw() error
        self.rect = self.surf.get_rect(
            center=(SCREEN_WIDTH + random.randint(50, 100), random.randint(0, SCREEN_HEIGHT // 2))
        )
        self.speed = 1

    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()


pygame.mixer.music.load("Apoxode_-_Electric_1.mp3")
pygame.mixer.music.play(loops=-1)
move_up_sound = pygame.mixer.Sound("Rising_putter.ogg")
move_down_sound = pygame.mixer.Sound("Falling_putter.ogg")
collision_sound = pygame.mixer.Sound("Collision.ogg")

player = Player()
player.has_energy_blast = False
enemies = pygame.sprite.Group()

ammo_group = pygame.sprite.Group()

energy_blasts = pygame.sprite.Group()

energy_powerups = pygame.sprite.Group()

all_sprites = pygame.sprite.Group()

all_sprites.add(player)
background = Background()

clouds = pygame.sprite.Group()

Twin_Pain = pygame.sprite.Group()

twin_players = pygame.sprite.Group()

Twin_Pain = pygame.sprite.Group()

bullet_x4_powerups = pygame.sprite.Group()

range_shooter_powerups = pygame.sprite.Group()
invincibility_powerups = pygame.sprite.Group()
boss_group = pygame.sprite.Group()

boss_bullets = pygame.sprite.Group()
boss_active = False

boss_defeated = False
boss_count = 0

piercing_bullets_end_time = 0
spread_shot_end_time = 0
invincibility_end_time = 0

ADD_BULLET_X4 = pygame.USEREVENT + 6
ADD_RANGE_SHOOTER = pygame.USEREVENT + 7

ADD_ENERGY = pygame.USEREVENT + 8
ADD_INVINCIBILITY = pygame.USEREVENT + 9
pygame.time.set_timer(ADD_BULLET_X4, random.randint(5000, 15000))
pygame.time.set_timer(ADD_RANGE_SHOOTER, random.randint(7000, 12000))
pygame.time.set_timer(ADD_ENERGY, random.randint(10000, 20000))
pygame.time.set_timer(ADD_INVINCIBILITY, random.randint(8000, 15000))

# Initialize game_active
game_active = True
running = True

while running:
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == ADD_ENEMY:
            # Only spawn regular enemies if boss is not active
            if not boss_active:
                new_enemy = Enemy()
                enemies.add(new_enemy)
                all_sprites.add(new_enemy)

        elif event.type == CLOCK_TICK and game_active:
            seconds += 1

            if seconds % 16 == 0:
                level += 1
                increase_freq()
                level_up_time = pygame.time.get_ticks()

                # Spawn boss at level 4
                if level % 4 == 0 and not boss_active and not boss_defeated:
                    boss_count += 1
                    boss = Boss(boss_count)  # Pass boss level for scaling difficulty
                    boss_group.add(boss)
                    all_sprites.add(boss)
                    boss_active = True
                    # Clear all existing enemies when boss spawns
                    for enemy in enemies:
                        enemy.kill()
                    enemies.empty()
                    # Stop spawning regular enemies during boss fight
                    pygame.time.set_timer(ADD_ENEMY, 0)

        elif event.type == KEYDOWN and event.key == K_SPACE:
            if pygame.time.get_ticks() < spread_shot_end_time:
                # Spread shot pattern
                angles = [-30, -15, 0, 15, 30]
                for angle in angles:
                    new_ammo = Ammo(player.rect.centerx + 20, player.rect.centery)
                    new_ammo.speed_x = new_ammo.speed * math.cos(math.radians(angle))
                    new_ammo.speed_y = new_ammo.speed * math.sin(math.radians(angle))
                    ammo_group.add(new_ammo)
                    all_sprites.add(new_ammo)
            else:
                new_ammo = Ammo(player.rect.centerx + 20, player.rect.centery)
                ammo_group.add(new_ammo)
                all_sprites.add(new_ammo)

        elif event.type == KEYDOWN and event.key == K_q:  # Q key for energy blast
            if player.has_energy_blast:
                blast = EnergyBlast(player.rect.centerx, player.rect.centery)
                energy_blasts.add(blast)
                all_sprites.add(blast)
                player.has_energy_blast = False

        elif event.type == ADD_ENERGY:
            if len(energy_powerups) == 0:
                new_powerup = EnergyPowerup()
                energy_powerups.add(new_powerup)
                all_sprites.add(new_powerup)

        elif event.type == KEYDOWN and event.key == K_e:
            # Shoot from all twin players
            for twin_player in twin_players:
                if pygame.time.get_ticks() < spread_shot_end_time:
                    # Spread shot pattern for twin player
                    angles = [-30, -15, 0, 15, 30]
                    for angle in angles:
                        new_ammo = Ammo(twin_player.rect.centerx + 20, twin_player.rect.centery)
                        new_ammo.speed_x = new_ammo.speed * math.cos(math.radians(angle))
                        new_ammo.speed_y = new_ammo.speed * math.sin(math.radians(angle))
                        ammo_group.add(new_ammo)
                        all_sprites.add(new_ammo)
                else:
                    new_ammo = Ammo(twin_player.rect.centerx + 20, twin_player.rect.centery)
                    ammo_group.add(new_ammo)
                    all_sprites.add(new_ammo)


        elif event.type == ADD_CLOUD:
            new_cloud = Cloud()
            clouds.add(new_cloud)
            all_sprites.add(new_cloud)

        elif event.type == ADD_BULLET_X4:
            if len(bullet_x4_powerups) == 0:
                new_powerup = Bullet_X4_Powerup()
                bullet_x4_powerups.add(new_powerup)
                all_sprites.add(new_powerup)

        elif event.type == ADD_RANGE_SHOOTER:
            if len(range_shooter_powerups) == 0:
                new_powerup = RangeShooterPowerup()
                range_shooter_powerups.add(new_powerup)
                all_sprites.add(new_powerup)

        elif event.type == ADD_Powerup_Twin_Pain:

            if len(Twin_Pain) == 0 and len(twin_players) == 0:
                new_powerup = Powerup_Twin_Pain()
                Twin_Pain.add(new_powerup)
                all_sprites.add(new_powerup)

        elif event.type == ADD_INVINCIBILITY:
            if len(invincibility_powerups) == 0:
                new_powerup = InvincibilityPowerup()
                invincibility_powerups.add(new_powerup)
                all_sprites.add(new_powerup)


    # Only update game when active
    if game_active:
        # screen.fill((135, 206, 235))
        background.draw(screen)
        clouds.update()
        clouds.draw(screen)

        # Check if player is invincible
        is_invincible = pygame.time.get_ticks() < invincibility_end_time

        for entity in all_sprites:
            if entity == player and is_invincible:
                # Flash player when invincible
                if (pygame.time.get_ticks() // 100) % 2:  # Flash every 100ms
                    screen.blit(entity.surf, entity.rect)
            else:
                screen.blit(entity.surf, entity.rect)

        # Check for invincibility powerup collision
        invincibility_collided = pygame.sprite.spritecollideany(player, invincibility_powerups)
        if invincibility_collided:
            invincibility_end_time = pygame.time.get_ticks() + 8000  # 8 seconds of invincibility
            invincibility_collided.kill()

        collided = pygame.sprite.spritecollideany(player, enemies)
        if collided and not is_invincible:
            player.lives -= 1
            collided.kill()
            if player.lives == 0:
                game_active = False
                collision_sound = pygame.mixer.Sound("Collision.ogg")
                collision_sound.play()
        elif collided and is_invincible:
            collided.kill()  # Destroy enemy but don't take damage

        for twin_player in twin_players:
            collided = pygame.sprite.spritecollideany(twin_player, enemies)
            if collided:
                twin_player.lives -= 1
                collided.kill()
                if twin_player.lives == 0:
                    twin_player.kill()
                    collision_sound = pygame.mixer.Sound("Collision.ogg")
                    collision_sound.play()

        # Boss bullet collisions with player
        boss_bullet_hit = pygame.sprite.spritecollideany(player, boss_bullets)
        if boss_bullet_hit and not is_invincible:
            player.lives -= 1
            boss_bullet_hit.kill()
            if player.lives == 0:
                game_active = False
                collision_sound = pygame.mixer.Sound("Collision.ogg")
                collision_sound.play()
        elif boss_bullet_hit and is_invincible:
            boss_bullet_hit.kill()  # Destroy bullet but don't take damage

        # Boss bullet collisions with twin players
        for twin_player in twin_players:
            boss_bullet_hit = pygame.sprite.spritecollideany(twin_player, boss_bullets)
            if boss_bullet_hit:
                twin_player.lives -= 1
                boss_bullet_hit.kill()
                if twin_player.lives == 0:
                    twin_player.kill()
                    collision_sound = pygame.mixer.Sound("Collision.ogg")
                    collision_sound.play()

        # Player collision with boss
        for boss in boss_group:
            if pygame.sprite.spritecollideany(player, boss_group) and not is_invincible:
                player.lives -= 2  # Boss does more damage
                if player.lives <= 0:
                    game_active = False
                    collision_sound = pygame.mixer.Sound("Collision.ogg")
                    collision_sound.play()

        bullet_x4_collided = pygame.sprite.spritecollideany(player, bullet_x4_powerups)
        if bullet_x4_collided:
            piercing_bullets_end_time = pygame.time.get_ticks() + 10000  # 10 seconds
            bullet_x4_collided.kill()

        range_shooter_collided = pygame.sprite.spritecollideany(player, range_shooter_powerups)
        if range_shooter_collided:
            spread_shot_end_time = pygame.time.get_ticks() + 10000  # 10 seconds
            range_shooter_collided.kill()

        energy_powerup_collided = pygame.sprite.spritecollideany(player, energy_powerups)
        if energy_powerup_collided:
            player.has_energy_blast = True
            energy_powerup_collided.kill()

        collided = pygame.sprite.spritecollideany(player, Twin_Pain)
        if collided:
            second_player = Twin_Player()
            second_player.rect.center = (player.rect.centerx + 50, player.rect.centery)
            twin_players.add(second_player)
            all_sprites.add(second_player)
            collided.kill()


        pressed_keys = pygame.key.get_pressed()
        player.update(pressed_keys)
        enemies.update()
        ammo_group.update()
        energy_blasts.update()
        boss_bullets.update()

        # Update boss and handle boss bullets
        for boss in boss_group:
            if boss.update():  # Boss is shooting
                boss_bullet = BossBullet(boss.rect.left, boss.rect.centery)
                boss_bullets.add(boss_bullet)
                all_sprites.add(boss_bullet)

        for blast in energy_blasts:
            # Energy blast vs boss
            boss_hit = pygame.sprite.spritecollideany(blast, boss_group)
            if boss_hit:
                if boss_hit.take_damage(5):  # Energy blast does more damage to boss
                    boss_active = False
                    boss_defeated = False  # Reset so next boss can spawn
                    player.lives += 10
                    pygame.time.set_timer(ADD_ENEMY, random.randint(max(1, enemy_frequency - 300), enemy_frequency))

            enemies_hit = pygame.sprite.spritecollide(blast, enemies, True)
            for enemy in enemies_hit:
                player.lives += 1

        for twin in twin_players:
            twin.update(pressed_keys)

        for ammo in ammo_group:
            # Check collision with boss first
            boss_hit = pygame.sprite.spritecollideany(ammo, boss_group)
            if boss_hit:
                if boss_hit.take_damage():  # Boss defeated
                    boss_active = False
                    boss_defeated = False  # Reset so next boss can spawn
                    player.lives += 10  # Reward for defeating boss
                    # Resume normal enemy spawning
                    pygame.time.set_timer(ADD_ENEMY, random.randint(max(1, enemy_frequency - 300), enemy_frequency))
                ammo.kill()
            elif pygame.time.get_ticks() < piercing_bullets_end_time:
                enemies_hit = pygame.sprite.spritecollide(ammo, enemies, True)
                for enemy in enemies_hit:
                    player.lives += 1
            else:
                enemy_hit = pygame.sprite.spritecollideany(ammo, enemies)
                if enemy_hit:
                    enemy_hit.kill()
                    player.lives += 1
                    ammo.kill()

        # Create smaller lives counter at top-left
        lives_text = font.render("Lives: " + str(player.lives), True, (255, 255, 255))  # White text
        lives_bg = pygame.Surface((lives_text.get_width() + 10, lives_text.get_height() + 5))
        lives_bg.fill((0, 0, 0))  # Black background
        lives_bg.set_alpha(128)   # Semi-transparent
        screen.blit(lives_bg, (5, 5))
        screen.blit(lives_text, (10, 8))

        clockText = font.render(str(seconds), True, (255, 255, 255))
        screen.blit(clockText, (SCREEN_WIDTH - 42, SCREEN_HEIGHT - 32))

        levelText = font.render("level: " + str(level), True, (255, 255, 255))
        screen.blit(levelText, (SCREEN_WIDTH // 2 - 40, 10))

        # Display invincibility status
        if is_invincible:
            invince_time_left = (invincibility_end_time - pygame.time.get_ticks()) // 1000 + 1
            invince_text = font.render(f"INVINCIBLE: {invince_time_left}s", True, (255, 255, 0))
            screen.blit(invince_text, (10, 40))

        # Draw boss health bar
        if boss_active and len(boss_group) > 0:
            boss = list(boss_group)[0]
            boss_text = font.render(f"BOSS LV.{boss.boss_level}", True, (255, 0, 0))
            screen.blit(boss_text, (SCREEN_WIDTH // 2 - 50, 50))

            # Health bar background
            health_bar_bg = pygame.Rect(SCREEN_WIDTH // 2 - 100, 80, 200, 20)
            pygame.draw.rect(screen, (255, 0, 0), health_bar_bg)

            # Health bar foreground
            health_percentage = boss.health / boss.max_health
            health_bar_fg = pygame.Rect(SCREEN_WIDTH // 2 - 100, 80, 200 * health_percentage, 20)
            pygame.draw.rect(screen, (0, 255, 0), health_bar_fg)

        if pygame.time.get_ticks() - level_up_time < 1:
            levelText = font.render("level: " + str(level), True, (255, 255, 255))
            screen.blit(levelText, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 36))
    else:
        # When game is not active, just draw a black screen
        screen.fill((0, 0, 0))

    # Display game over screen if game is not active
    if not game_active:
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Game Over text
        game_over_text = large_font.render("GAME OVER", True, (255, 0, 0))
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(game_over_text, game_over_rect)
        
        # Final stats
        final_level_text = font.render(f"Final Level: {level}", True, (255, 255, 255))
        final_level_rect = final_level_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(final_level_text, final_level_rect)
        
        final_time_text = font.render(f"Time Survived: {seconds} seconds", True, (255, 255, 255))
        final_time_rect = final_time_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        screen.blit(final_time_text, final_time_rect)
        
        # Restart instruction
        restart_text = font.render("Press R to restart or ESC to quit", True, (255, 255, 0))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
        screen.blit(restart_text, restart_rect)

    pygame.display.flip()

    # Handle restart when game is over
    if not game_active:
        keys = pygame.key.get_pressed()
        if keys[K_r]:  # Press R to restart
            # Restart the game (reset all relevant variables)
            game_active = True
            player = Player()
            player.has_energy_blast = False
            enemies = pygame.sprite.Group()
            ammo_group = pygame.sprite.Group()
            energy_blasts = pygame.sprite.Group()
            energy_powerups = pygame.sprite.Group()
            all_sprites = pygame.sprite.Group()
            all_sprites.add(player)
            clouds = pygame.sprite.Group()
            Twin_Pain = pygame.sprite.Group()
            twin_players = pygame.sprite.Group()
            Twin_Pain = pygame.sprite.Group()
            bullet_x4_powerups = pygame.sprite.Group()
            range_shooter_powerups = pygame.sprite.Group()
            boss_group = pygame.sprite.Group()
            boss_bullets = pygame.sprite.Group()
            boss_active = False
            boss_defeated = False
            boss_count = 0
            piercing_bullets_end_time = 0
            spread_shot_end_time = 0
            invincibility_end_time = 0
            invincibility_powerups = pygame.sprite.Group()
            seconds = 0
            level = 1
            enemy_frequency = 500
            pygame.time.set_timer(ADD_ENEMY, random.randint(max(1, enemy_frequency - 300), enemy_frequency))
            pygame.time.set_timer(ADD_INVINCIBILITY, random.randint(8000, 15000))
        elif keys[K_ESCAPE]:  # Press ESC to quit
            running = False

pygame.quit()