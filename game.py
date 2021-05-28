2# Imports
import pygame
import random
import json

# Window settings
GRID_SIZE = 64
WIDTH = 25 * GRID_SIZE
HEIGHT = 13 * GRID_SIZE
TITLE = "Twisted Dreams and Fortune"
FPS = 60


# Create window
pygame.init()
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()


# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (0, 150, 255)
GRAY = (175, 175, 175)
RED = (252, 28, 3)

#STAGEs
START = 0
PLAYING = 1
LOSE = 2
LEVEL_COMPLETE = 3

#Settings
gravity = 1.0
terminal_velocity = 24

# Load fonts
font_xs = pygame.font.Font(None, 14)
font_x1 = pygame.font.Font('assets/fonts/Thanks_Autumn.ttf', 80)
font_q1 = pygame.font.Font('assets/fonts/Thanks_Autumn.ttf',40)

# Load images
hero_idle_imgs_rt = [pygame.image.load('assets/images/Players_Enemies/Player/Blue/alienBlue_walk3.png').convert_alpha()]
hero_walk_imgs_rt = [pygame.image.load('assets/images/Players_Enemies/Player/Blue/alienBlue_walk2.png').convert_alpha(),
                     pygame.image.load('assets/images/Players_Enemies/Player/Blue/alienBlue_walk1.png').convert_alpha()]
hero_jump_imgs_rt = [pygame.image.load('assets/images/Players_Enemies/Player/Blue/alienBlue_jump.png').convert_alpha()]

hero_idle_imgs_lt = [pygame.transform.flip(img, True, False) for img in hero_idle_imgs_rt ]
hero_walk_imgs_lt = [pygame.transform.flip(img, True, False) for img in hero_walk_imgs_rt ]
hero_jump_imgs_lt = [pygame.transform.flip(img, True, False) for img in hero_jump_imgs_rt ]

worm_imgs_rt = [pygame.image.load('assets/images/Players_Enemies/Enemies/worm/PINK/wormPink.png').convert_alpha(),
                pygame.image.load('assets/images/Players_Enemies/Enemies/worm/PINK/wormPink_move.png').convert_alpha()]
worm_imgs_lt = [pygame.transform.flip(img, True, False) for img in worm_imgs_rt ]


sand_img = pygame.image.load('assets/images/Ground/Sand/sand.png').convert_alpha()
brigde_img = pygame.image.load('assets/images/Objects/Set_up_objects/bridge/bridgeA.png').convert_alpha()
platform_img = pygame.image.load('assets/images/Ground/Sand/sandHalf_mid.png').convert_alpha()
backgroud_img = pygame.image.load('assets/images/Backgrounds/blue_land2.png').convert_alpha()
gem_img = pygame.image.load('assets/images/Objects/Jewel/hudJewel_blue.png').convert_alpha()
cactus_img = pygame.image.load('assets/images/Objects/Set_up_objects/plant/cactus.png').convert_alpha()
start_img = pygame.image.load('assets/images/Backgrounds/start_screen.jpg').convert_alpha()
end_img = pygame.image.load('assets/images/Backgrounds/end_screen.jpg').convert_alpha()
heart_img = pygame.image.load('assets/images/Objects/Heart/hudHeart_full.png').convert_alpha()
tundra_img = pygame.image.load('assets/images/Ground/Tundra/tundraCenter.png').convert_alpha()
door_img = pygame.image.load('assets/images/Objects/Set_up_objects/door/iglooDoor.png').convert_alpha()
pole_img = pygame.image.load('assets/images/Objects/Flag/flagPole.png').convert_alpha()
flag_img = pygame.image.load('assets/images/Objects/Flag/flagYellow2.png').convert_alpha()
levelScreen_img = pygame.image.load('assets/images/Backgrounds/level.png').convert_alpha()


# Load sounds

#levels

levels = ['assets/levels/world-1.json','assets/levels/world-2.json','assets/levels/world-3.json']
# Game classes
class Entity(pygame.sprite.Sprite):
    
    def __init__(self, x, y, image):
        super().__init__()
        
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.centerx = x * GRID_SIZE + GRID_SIZE // 2
        self.rect.centery = y * GRID_SIZE + GRID_SIZE // 2

        self.vx = 0
        self.vy = 0

    def apply_gravity(self):
        self.vy += gravity
        if self.vy > terminal_velocity:
            self.vy = terminal_velocity

class AnimatedEntity(Entity):
    def __init__(self, x , y, images):
        super().__init__(x, y, images[0])

        self.images = images
        self.image_index = 0
        self.ticks = 0
        self.animation_speed = 10
        self.facing_right = True

    def check_world_edge(self):
        if self.rect.left < 0:
            self.rect.left = 0
            self.vx = self.speed
        elif self.rect.right > world_width:
            self.rect.right = world_width
            self.vx = -1 * self.speed
            
    def move_and_check_blocks(self):
        self.rect.x += self.vx
        hits = pygame.sprite.spritecollide(self, platforms, False)

        for block in hits:
            if self.vx > 0:
                self.rect.right = block.rect.left
            elif self.vx < 0:
                self.rect.left = block.rect.right

        self.rect.y += self.vy
        hits = pygame.sprite.spritecollide(self, platforms, False)

        for block in hits:
            if self.vy > 0:
                self.rect.bottom = block.rect.top
                self.jumping = False
            elif self.vy < 0:
                self.rect.top = block.rect.bottom

            self.vy = 0

    def set_image_list(self):
        self.images = self.images

    def animate(self):
        self.set_image_list()
        self.ticks += 1

        if self.ticks % self.animation_speed == 0:
            self.image_index += 1

            if self.image_index >= len(self.images):
                self.image_index = 0
                
            self.image = self.images[self.image_index]
        
class Hero(AnimatedEntity):
    
    def __init__(self, x, y, images):
        super().__init__(x, y, images)
        
        self.speed = 5
        self.jump_power = 24

        self.vx = 0
        self.vy = 0
        self.hurt_timer = 0
        self.hearts = 3
        self.gems = 0
        self.score = 0
        self.jumping = False

    def move_to(self, x, y):
        self.rect.centerx = x * GRID_SIZE + GRID_SIZE // 2
        self.rect.centery = y * GRID_SIZE + GRID_SIZE // 2

        
    def move_right(self):
        self.vx = self.speed
        self.facing_right = True
        
    def move_left(self):
        self.vx = -1 * self.speed
        self.facing_right = False

    def stop(self):
        self.vx = 0
    
    def jump(self):
        self.rect.y += 1
        hits = pygame.sprite.spritecollide(self, platforms, False)
        self.rect.y -= 1

        if len(hits) > 0:
            self.vy = -1 * self.jump_power
            self.jumping = True
    def move_and_check_blocks(self):
        self.rect.x += self.vx
        hits = pygame.sprite.spritecollide(self, platforms, False)

        for block in hits:
            if self.vx > 0:
                self.rect.right = block.rect.left
            elif self.vx < 0:
                self.rect.left = block.rect.right

        self.rect.y += self.vy
        hits = pygame.sprite.spritecollide(self, platforms, False)

        for block in hits:
            if self.vy > 0:
                self.rect.bottom = block.rect.top
                self.jumping = False
            elif self.vy < 0:
                self.rect.top = block.rect.bottom

            self.vy = 0

    def check_world_edges(self):
        if self.rect.left < 0:
            self.rect.left = 0
            self.vx = self.speed
        elif self.rect.right > world_width:
            self.rect.right = world_width
            self.vx = -1 * self.speed

    def check_items(self):
        hits = pygame.sprite.spritecollide(self, items, True)

        for item in hits:
            item.apply(self)

    def check_enemies(self):
            hits = pygame.sprite.spritecollide(self, enemies, False)

            for enemy in hits:
                if self.hurt_timer == 0:
                    for enemy in hits:
                        self.hearts -= 1
                        self.hurt_timer = 1.0 * FPS

                if self.rect.centerx < enemy.rect.centerx:
                    self.rect.right = enemy.rect.left
                elif self.rect.centerx > enemy.rect.centerx:
                    self.rect.left = enemy.rect.right

                if self.rect.centery < enemy.rect.centery:
                    self.rect.bottom = enemy.rect.top
                elif self.rect.centery > enemy.rect.centery:
                    self.rect.top = enemy.rect.bottom


            self.hurt_timer -= 1

            if self.hurt_timer < 0:
                self.hurt_timer = 0

    def reached_goal(self):
        return pygame.sprite.spritecollideany(self, goal)

    def set_image_list(self):
        if self.facing_right:
            if self.jumping:
                self.images = hero_jump_imgs_rt
            if self.vx != 0:
                self.images = hero_walk_imgs_rt
            else:
                self.images = hero_idle_imgs_rt
        else:
            if self.jumping:
                self.images = hero_jump_imgs_lt
            elif self.vx == 0:
                self.images = hero_idle_imgs_lt
            else:
                self.images = hero_walk_imgs_lt
        
    def update(self):
        self.apply_gravity()
        self.move_and_check_blocks()
        self.check_world_edges()
        self.check_items()
        self.check_enemies()
        self.animate()

class Enemy(AnimatedEntity):
    
    def __init__(self, x, y, images):
        super().__init__(x, y, images)

        self.speed = 2
        self.vx = -1 * self.speed
        self.vy = 0

    def reverse(self):
        self.vx *= -1

    def move_and_check_blocks(self):
        self.rect.x += self.vx
        hits = pygame.sprite.spritecollide(self, platforms, False)

        for block in hits:
            if self.vx > 0:
                self.rect.right = block.rect.left
            elif self.vx < 0:
                self.rect.left = block.rect.right

        self.rect.y += self.vy
        hits = pygame.sprite.spritecollide(self, platforms, False)

        for block in hits:
            if self.vy > 0:
                self.rect.bottom = block.rect.top
            elif self.vy < 0:
                self.rect.top = block.rect.bottom

            self.vy = 0

    def check_platform_edges(self):
        self.rect.y += 2
        hits = pygame.sprite.spritecollide(self, platforms, False)
        self.rect.y -= 2

        must_reverse = True

        for platform in hits:
            if self.vx < 0 and platform.rect.left <= self.rect.left:
                must_reverse = False
            elif self.vx > 0 and platform.rect.right >= self.rect.right:
                must_reverse = False

        if must_reverse:
            self.reverse()

    def check_world_edges(self):
        if self.rect.left < 0:
            self.rect.left = 0
            self.vx = self.speed
        elif self.rect.right > world_width:
            self.rect.right = world_width

       
    def update(self):
        self.move_and_check_blocks()
        self.check_world_edges()
        self.apply_gravity()
        self.check_platform_edges()
        
#PlatForms_Brigde
class platform(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
        
class blockTop(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
        
class blockBottom(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)        

class Brigde(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
        
class Block(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

class Tundra(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)



#plants_Gems_door
class Door(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

class Cactus(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)


class gem(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
        
    def apply(self, character):
        character.gems += 1
        character.score += 10
        print(character.gems)
class Flag(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
#Enemy        
class Worm(Enemy):
    
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
        self.rect.bottom = y * GRID_SIZE + GRID_SIZE

    def set_image_list(self):
        if self.vx > 0:
            self.images = worm_imgs_rt
        else:
            self.images = worm_imgs_lt

    def update(self):
        self.move_and_check_blocks()
        self.check_world_edges()
        self.apply_gravity()
        self.check_platform_edges()
        self.animate()


    def move_and_check_blocks(self):
        self.rect.x += self.vx
        hits = pygame.sprite.spritecollide(self,platforms, False)

        for block in hits:
            if self.vx > 0:
                self.rect.right = block.rect.left
                self.vx = -1 * self.speed
            elif self.vx < 0:
                self.rect.left = block.rect.right
                self.vx = self.speed

        self.rect.y += self.vy
        hits = pygame.sprite.spritecollide(self,platforms, False)

        for block in hits:
            if self.vy > 0:
                self.rect.bottom= block.rect.top
            elif self.vy <0:
                self.rect.top = block.rect.bottom
            self.vy = 0
    def check_world_edges(self):
        if self.rect.left <0:
            self.rect.left = 0
            self.vx = self.speed
        elif self.rect.right > WIDTH:
            self.rect.right = WIDTH
            self.vx = -1 * self.speed

    def update(self):
        self.move_and_check_blocks()
        self.check_world_edges()
        
# Helper functoins
def show_start_screen():
    screen.blit(start_img, [0, 0])
    text = font_x1.render(TITLE, True, BLACK)
    rect = text.get_rect()
    rect.center = WIDTH // 2.52, HEIGHT // 2.52 
    screen.blit(text, rect)

    text = font_x1.render("Press any key to start", True, BLACK)
    rect = text.get_rect()
    rect.center = WIDTH // 1.52, HEIGHT // 1.52 
    screen.blit(text, rect)

    text = font_x1.render(TITLE, True, WHITE)
    rect = text.get_rect()
    rect.center = WIDTH // 2.54, HEIGHT // 2.54
    screen.blit(text, rect)

    text = font_x1.render("Press any key to start", True, WHITE)
    rect = text.get_rect()
    rect.center = WIDTH // 1.53, HEIGHT // 1.53
    screen.blit(text, rect)


def show_lose_screen():
    screen.blit(end_img, [0, 0])
    text = font_x1.render('GAME OVER', True, BLACK)
    rect = text.get_rect()
    rect.center = WIDTH // 2.52, HEIGHT // 2.52
    screen.blit(text, rect)

    text = font_x1.render("Press \'r\' to restart", True, BLACK)
    rect = text.get_rect()
    rect.center = WIDTH // 1.52, HEIGHT // 1.52 
    screen.blit(text, rect)

    text = font_x1.render('GAME OVER', True, WHITE)
    rect = text.get_rect()
    rect.center = WIDTH // 2.54, HEIGHT // 2.54
    screen.blit(text, rect)

    text = font_x1.render("Press \'r\' to restart", True, WHITE)
    rect = text.get_rect()
    rect.center = WIDTH // 1.53, HEIGHT // 1.53
    screen.blit(text, rect)

def show_level_complete_screen():
    screen.blit(levelScreen_img, [0, 0])

    text = font_x1.render('Level Complete!', True, BLACK)
    rect = text.get_rect()
    rect.center = WIDTH // 2.54, HEIGHT // 2.54
    screen.blit(text, rect)
    
    text = font_x1.render('Level Complete!', True, WHITE)
    rect = text.get_rect()
    rect.center = WIDTH // 2.52, HEIGHT // 2.52
    screen.blit(text, rect)

    text = font_x1.render("Press \'c\' to restart", True, BLACK)
    rect = text.get_rect()
    rect.center = WIDTH // 1.52, HEIGHT // 1.52 
    screen.blit(text, rect)

    text = font_x1.render("Press \'c\' to restart", True, WHITE)
    rect = text.get_rect()
    rect.center = WIDTH // 1.53, HEIGHT // 1.53
    screen.blit(text, rect)

    
player = pygame.sprite.GroupSingle()
platforms = pygame.sprite.Group()
brigde = pygame.sprite.Group()
items = pygame.sprite.Group()
cactus = pygame.sprite.Group()
enemies = pygame.sprite.Group()
Entity = pygame.sprite.Group()
block = pygame.sprite.Group()
tundra = pygame.sprite.Group()
door = pygame.sprite.Group()

def show_hud():
    text = font_q1.render( str (hero.score), True, WHITE)
    rect = text.get_rect()
    rect.midtop = WIDTH // 2, 28
    screen.blit(text, rect)

    screen.blit(gem_img, [WIDTH - 128, 16])
    text = font_q1.render(str (hero.gems), True, WHITE)
    rect = text.get_rect()
    rect.topleft = WIDTH - 44, 28
    screen.blit(text, rect)

    text = font_q1.render('' , True, WHITE)
    rect = text.get_rect()
    rect.topleft = WIDTH - 70, 28
    screen.blit(text, rect)


    for i in range(hero.hearts):
        x = i * 36
        y = 16
        screen.blit(heart_img, [x,y])


#set up
def start_game():
    global hero, stage,current_level
    hero = Hero(0, 0, hero_idle_imgs_rt)
    current_level = 0
    stage = START

def start_level():
    global player, platforms, items, worm, goal, hero, grass,blockTop,blockBottom,brigde,cactus, gems, enemies,world_width,world_height,all_sprites

    
    grass = pygame.sprite.Group()
    blockTop = pygame.sprite.Group()
    blockBottom = pygame.sprite.Group()
    brigde = pygame.sprite.Group()
    cactus = pygame.sprite.Group()
    gems = pygame.sprite.Group()

    player = pygame.sprite.GroupSingle()
    platforms = pygame.sprite.Group()
    worm = pygame.sprite.Group()
    goal = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    items = pygame.sprite.Group()

    
    all_sprites = pygame.sprite.Group()
    
    with open('assets/levels/world-1.json') as f:
        data = json.load(f)
        
    world_width = data ['width'] * GRID_SIZE
    world_height = data ['height'] * GRID_SIZE
    
    hero.move_to(data["start"][0],data["start"][1])
    player.add(hero)

    for i, loc in enumerate(data["flag_locs"]):
            if i == 0:
                goal.add( Flag(loc[0], loc[1], flag_img) )
            else:
                goal.add( Flag(loc[0], loc[1], pole_img) )

    for loc in (data["door_locs"]):
        x = loc[0]
        y = loc[1]
        p = platform(x, y, door_img)
        platforms.add(p)

    for loc in (data["tundra_locs"]):
        x = loc[0]
        y = loc[1]
        p = platform(x, y, tundra_img)
        platforms.add(p)
    
    for loc in (data["grass_locs"]):
        x = loc[0]
        y = loc[1]
        p = platform(x, y, sand_img)
        platforms.add(p)

    for loc in (data["blockTop_locs"]):
        x = loc[0]
        y = loc[1]
        p = platform(x, y, platform_img)
        platforms.add(p)


    for loc in (data['blockBottom_locs']):
        x = loc[0]
        y = loc[1]
        p = platform(x, y, platform_img)
        platforms.add(p)

    for loc in (data["brigde_locs"]):
        x = loc[0]
        y = loc[1]
        b = Brigde(x, y, brigde_img)
        brigde.add(b)
        

    for loc in (data["cactus_locs"]):
        x = loc[0]
        y = loc[1]
        c = Cactus(x, y, cactus_img)
        cactus.add(c)

    for loc in (data["gems_locs"]):
        x =loc[0]
        y =loc[1]
        g = gem(x,y,gem_img)
        items.add(g)
    
    for loc in (data["worm_locs"]):
        x = loc[0]
        y = loc[1]
        w = Worm(x, y, worm_imgs_rt)
        enemies.add(w)

    for loc in (data["worm_locs"]):
        x = loc[0]
        y = loc[1]
        w = Worm(x, y, worm_imgs_lt)
        enemies.add(w)

    all_sprites.add(player,enemies)

def draw_grid(offset_x=0, offset_y=0):
    for x in range(0, WIDTH + GRID_SIZE, GRID_SIZE):
        adj_x = x - offset_x % GRID_SIZE
        pygame.draw.line(screen, GRAY, [adj_x, 0], [adj_x, HEIGHT], 1)

    for y in range(0, HEIGHT + GRID_SIZE, GRID_SIZE):
        adj_y = y - offset_y % GRID_SIZE
        pygame.draw.line(screen, GRAY, [0, adj_y], [WIDTH, adj_y], 1)

    for x in range(0, WIDTH + GRID_SIZE, GRID_SIZE):
        for y in range(0, HEIGHT + GRID_SIZE, GRID_SIZE):
            adj_x = x - offset_x % GRID_SIZE + 4
            adj_y = y - offset_y % GRID_SIZE + 4
            disp_x = x // GRID_SIZE + offset_x // GRID_SIZE
            disp_y = y // GRID_SIZE + offset_y // GRID_SIZE
            
            point = '(' + str(disp_x) + ',' + str(disp_y) + ')'
            text = font_xs.render(point, True, GRAY)
            screen.blit(text, [adj_x, adj_y])

# Game loop
running = True

grid_on = False
start_game()
start_level()
while running:
    # Input handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if stage == START:
                stage = PLAYING

            elif stage == PLAYING:
                if event.key == pygame.K_SPACE:
                    hero.jump()
                if event.key == pygame.K_g:
                    grid_on = not grid_on
                    
            elif stage == LEVEL_COMPLETE:
                 if event.key  == pygame.K_c:
                    start_game()
                    start_level()

            elif stage == LOSE:
                if event.key == pygame.K_r:
                    start_game()
                    start_level()
            


    pressed = pygame.key.get_pressed()

    if stage == PLAYING:

        if pressed[pygame.K_LEFT]:
            hero.move_left()
        elif pressed[pygame.K_RIGHT]:
            hero.move_right()
        else:
            hero.stop()

    # Game logic
    if stage == PLAYING:
        all_sprites.update()

        if hero.hearts <= 0:
            stage = LOSE

        elif hero.reached_goal():
            stage = LEVEL_COMPLETE
            countdown = 2 * FPS
    elif stage == LEVEL_COMPLETE:
        countdown -= 1
        if countdown <+ 0:
            current_level += 1

            if current_level < len(levels):
                start_level()
                stage = PLAYING
            else:
                stage = WIN

    if hero.rect.centerx < WIDTH // 2:
        offset_x = 0
    elif hero.rect.centerx > world_width - WIDTH // 2:
        offset_x = world_width - WIDTH
    else:
        offset_x = hero.rect.centerx - WIDTH  // 2

    # Drawing code
    screen.fill(SKY_BLUE)
    screen.blit(backgroud_img,[0,0])
    platforms.draw(screen)
    brigde.draw(screen)
    cactus.draw(screen)
    items.draw(screen)
    player.draw(screen)
    enemies.draw(screen)
    worm.draw(screen)
    tundra.draw(screen)
    door.draw(screen)
    goal.draw(screen)
    show_hud()
    if stage == START:
        show_start_screen()
    elif stage == LOSE:
        show_lose_screen()
    elif stage == LEVEL_COMPLETE:
        show_level_complete_screen()

    if grid_on:
        draw_grid(offset_x)
# Update screen
    pygame.display.update()


# Limit refresh rate of game loop 
    clock.tick(FPS)


# Close window and quit
pygame.quit()
