# platformer game
__author__ = 'Simon Lee: Game Developer, simonlee711@gmail.com'


import pygame
from pygame import mixer
import random
import csv
import button

from pygame import draw 

mixer.init()
pygame.init()


# Screen size - adjustable
SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)


# Building the screen and caption
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("私のパンはどこですか?")

# set frame rate
clock = pygame.time.Clock()
FPS = 60

#define game variables
GRAVITY = 0.5
SCROLL_THRESH = 300
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 42
screen_scroll = 0
bg_scroll = 0
level = 1
start_game = False
controls_menu = False
credits_menu = False
leaderboards = False

# define player action variables. Essentially initialize player movement
moving_left = False
moving_right = False
shoot = False

#load images
# button images
start_img = pygame.image.load('start.png').convert_alpha()
controls_img = pygame.image.load('controls.png').convert_alpha()
credits_img = pygame.image.load('credits.png').convert_alpha()
back_img = pygame.image.load('back.png').convert_alpha()
potato = pygame.image.load('1.png').convert_alpha()

# actual background
sky_img = pygame.image.load('img/Background/sky.png').convert_alpha()
skyline_img = pygame.image.load('img/Background/skyline.png').convert_alpha()
mountain_img = pygame.image.load('img/Background/mountain.png').convert_alpha()
tower_img = pygame.image.load('img/Background/tower.png').convert_alpha()
tower_img = pygame.transform.scale(tower_img, (int(tower_img.get_width() * 2) , int(tower_img.get_height() * 2)))

#store tiles in a list
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'img/tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

#extra images
bullet_img = pygame.image.load('img/icons/bullet.png').convert_alpha()
bread_img = pygame.image.load('img/icons/bread/0.png').convert_alpha()
bread_img = pygame.transform.scale(bread_img, (int(bread_img.get_width() * 2) , int(bread_img.get_height() * 2)))
bread2_img = pygame.image.load('img/icons/bread/1.png').convert_alpha()
bread2_img = pygame.transform.scale(bread2_img, (int(bread2_img.get_width() * 2) , int(bread2_img.get_height() * 2)))
item_boxes = {
    'Bread': bread_img,
    'Bread2': bread2_img
}

# load music and sounds
pygame.mixer.music.load('audio/background.mp3')
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1,0.5,10000)


# defining colors
BG = (130, 181, 210) # background color RGB (currently set at black)
BLUE = (0,0,255)
WHITE = (255,255,255)
RED = (255,0,0)

font = pygame.font.SysFont('Futura', 30)

def draw_text(text, font, text_col,x,y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x,y))

def draw_bg():
    '''
    function that colors in the background
    '''
    screen.fill(BG)
    width = sky_img.get_width()
    for x in range(2):
        screen.blit(sky_img,((width * x) - bg_scroll * 0.25,0))
        screen.blit(mountain_img,((x * width) -  bg_scroll * 0.05, SCREEN_HEIGHT - mountain_img.get_height() - 70))
        screen.blit(skyline_img,((x * width) - bg_scroll * 0.1 , SCREEN_HEIGHT - skyline_img.get_height() - 60))

    #pygame.draw.line(screen, BLUE , (0,500), (SCREEN_WIDTH, 500))

def draw_menu():
    screen.fill(BG)
    screen.blit(sky_img,(0,0))
    screen.blit(tower_img,(460, (0 - 145)))

def draw_controls():
    screen.fill(BG)
    screen.blit(sky_img,(0,0))
    screen.blit(tower_img,(460, (0 - 145)))

def draw_credits():
    screen.fill(BG)
    screen.blit(sky_img,(0,0))
    screen.blit(tower_img,(460, (0 - 145)))

def draw_leaderboards():
    screen.fill(BG)
    screen.blit(sky_img,(0,0))
    screen.blit(tower_img,(460, (0 - 145)))

# function to reset level
def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    car_group.empty()
    #item_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()

    #create empty tile list
    # create empty tile list
    data = [] #constructing a list of lists of a 16 x 150 map
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)
    
    return data



# class to generate the protagnist a.k.a playable character
class Player(pygame.sprite.Sprite):
    '''
    Class instance to make playable astronaut
    '''
    def __init__(self, char_type, x, y, scale, speed):
        '''
        creates a character and plots them on the screen. 
        * y-axis moves from top to bottom (e.g 1 is very top, 500 is below 1 on the graph)
        
        :param char_type - differentiates player or enemy
        :param x - x-coordinate spawn
        :param y - y-coordinate spawn
        :param scale - size of character (default 1)
        :param speed - how fast player is able to move
        '''
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.shoot_cooldown = 0
        self.health = 1000
        self.bread_collected = 0
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0 # velocity in the y axis
        self.jump = False
        self.squat = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

        # ai specific variables
        self.move_counter = 0
        self.vision = pygame.Rect(0,0,150,20)
        self.idling = False
        self.idling_counter = 0
        
        if self.char_type == 'player1':
            # idle animation
            temp_list = []
            for i in range(2): # loads a sequence of images making an animation
                img = pygame.image.load(f'img/{self.char_type}/idle/{i}.png').convert_alpha()    # import player 
                img = pygame.transform.scale(img, (int(img.get_width() * scale) , int(img.get_height() * scale)))    # size (scale) of player
                temp_list.append(img)
            self.animation_list.append(temp_list)
            
            # moving animation
            temp_list = []
            for i in range(12): # loads a sequence of images making an animation
                img = pygame.image.load(f'img/{self.char_type}/run/{i}.png').convert_alpha()    # import player 
                img = pygame.transform.scale(img, (int(img.get_width() * scale) , int(img.get_height() * scale)))    # size (scale) of player
                temp_list.append(img)
            self.animation_list.append(temp_list)

            # falling animation
            temp_list = []
            for i in range(5): # loads a sequence of images making an animation
                img = pygame.image.load(f'img/{self.char_type}/jump/{i}.png').convert_alpha()    # import player 
                img = pygame.transform.scale(img, (int(img.get_width() * scale) , int(img.get_height() * scale)))    # size (scale) of player
                temp_list.append(img)
            self.animation_list.append(temp_list)

            # squatting animation
            temp_list = []
            for i in range(2): # loads a sequence of images making an animation
                img = pygame.image.load(f'img/{self.char_type}/duck/{i}.png').convert_alpha()    # import player 
                img = pygame.transform.scale(img, (int(img.get_width() * scale) , int(img.get_height() * scale)))    # size (scale) of player
                temp_list.append(img)
            self.animation_list.append(temp_list)

            # death animation
            temp_list = []
            for i in range(6): # loads a sequence of images making an animation
                img = pygame.image.load(f'img/{self.char_type}/death/{i}.png').convert_alpha()    # import player 
                img = pygame.transform.scale(img, (int(img.get_width() * scale) , int(img.get_height() * scale)))    # size (scale) of player
                temp_list.append(img)
            self.animation_list.append(temp_list)

            # respawn animation
            temp_list = []
            for i in range(4): # loads a sequence of images making an animation
                img = pygame.image.load(f'img/{self.char_type}/respawn/{i}.png').convert_alpha()    # import player 
                img = pygame.transform.scale(img, (int(img.get_width() * scale) , int(img.get_height() * scale)))    # size (scale) of player
                temp_list.append(img)
            self.animation_list.append(temp_list)
        
        # mafia man
        if self.char_type == 'enemy2':
            temp_list = []
            for i in range(2): # loads a sequence of images making an animation
                img = pygame.image.load(f'img/{self.char_type}/move/{i}.png').convert_alpha()    # import player 
                img = pygame.transform.scale(img, (int(img.get_width() * scale) , int(img.get_height() * scale)))    # size (scale) of player
                temp_list.append(img)
            self.animation_list.append(temp_list)

            temp_list = []
            for i in range(2): # loads a sequence of images making an animation
                img = pygame.image.load(f'img/{self.char_type}/attack/{i}.png').convert_alpha()    # import player 
                img = pygame.transform.scale(img, (int(img.get_width() * scale) , int(img.get_height() * scale)))    # size (scale) of player
                temp_list.append(img)
            self.animation_list.append(temp_list)
            
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect() # rectangle is the hitbox of the player
        self.rect.center = (x,y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
    
    def update(self):
        self.update_animation()
        self.check_alive()
        # update cool down
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        '''
        tracking movement, sees if movement keys have been activated
        
        :param moving_left - checks to see if moving left key has been activated
        :param moving_right - checks to see if moving right key has been activated
        '''
        # reset movement variables
        screen_scroll = 0
        dx = 0
        dy = 0

        # assign movements variables if moving left and right
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1
        
        #jumping movement
        if self.jump == True and self.in_air == False:
            self.vel_y = -9
            self.jump = False
            self.in_air = True
        
        # apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        #check for collision
        for tile in world.obstacle_list:
            # check collision in the left and right direction
            if tile [1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                # if ai has hit wall make it turn around
                if self.char_type == 'enemy2':
                    self.direction *=-1
                    self.move_counter = 0
            #check for collision in the y direction
            if tile [1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # check if below the ground, i.e jumping
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                # check if above the ground, i.e falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        # check for collision with water
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0

        # check for collision with exit
        time_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            time_complete = True
        
        # check if fallen off the map
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0

        #check if going off the edges of the screen
        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        # update rectangle (hitbox's) position
        self.rect.x += dx
        self.rect.y += dy 

        #update scroll based on player position
        if self.char_type == 'player1':
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH)\
				or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx
        
        return screen_scroll, time_complete

    def shoot(self):
        if self.shoot_cooldown == 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.6 * self.rect.size[0] * self.direction), (self.rect.centery), self.direction)
            bullet_group.add(bullet)

    def ai(self):
        '''
        computer controlled characters
        '''
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.idling = True
                self.idling_counter = 500
            #check if ai is near the player
            if self.vision.colliderect(player.rect):
                #stop running and face the player
                self.shoot()
            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    if self.direction == -1:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.move_counter += 1
                    # update ai vision as the enemy moves
                    self.vision.center = (self.rect.centerx + 50 * self.direction, self.rect.centery)
                    pygame.draw.rect(screen, RED, self.vision, 1) # draw vision rectangle

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling -= 1
                    if self.idling_counter <= 0:
                        self.idling = False
        #scroll
        self.rect.x += screen_scroll
    
    def update_animation(self):
        '''
        updates animation making animation like thing
        '''
        # update animation
        ANIMATION_COOLDOWN = 120
        #update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        # check if enough time has passed since last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # if animation has run out then loop it back to the beginning of the loop
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 2 or self.action == 4 or self.action == 5:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0
    
    def update_action(self, new_action):
        '''
        check if new action is different from previous one
        '''
        if new_action != self.action:
            self.action = new_action
            # update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(4)

    def draw(self):
        '''
        Method that draws character from the __init__()
        '''
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        pygame.draw.rect(screen, BLUE, self.rect,1) # hit box
        

class World():
    def __init__(self):
        self.obstacle_list = []
    
    def process_data(self,data):
        self.level_length = len(data[0])
        # iterate through each value in level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if (tile >= 0 and tile <= 2) or (tile == 4) or (tile == 29) or (tile == 30) or (tile == 10) or (tile >= 16 and tile <= 18) or (tile == 9) or (tile == 11) or (tile == 13) or (tile == 15) or (tile >= 19 and tile <= 27) or (tile >= 31 and tile <= 33) or (tile == 8) or (tile == 12) or (tile == 14):
                        self.obstacle_list.append(tile_data)
                    #elif (tile == 8) or (tile == 12) or (tile == 14):
                    #    self.obstacle_half.append(tile_data)
                    elif tile == 28: # water
                        water = Water(img,x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)
                    # decorative non interactive tiles
                    elif (tile >= 5 and tile <= 7) or (tile >= 35 and tile <= 37):
                        #screen.blit(img,(x * TILE_SIZE, y * TILE_SIZE))
                        decoration = Decoration(img,x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 38: # create player
                        player = Player('player1', x * TILE_SIZE, y * TILE_SIZE, 2, 4) # generating character at (x-coord, y-coord) [y - axis reverse]
                    elif tile == 39: # create enemy
                        enemy = Player('enemy2', x * TILE_SIZE, y * TILE_SIZE, 2, 1) # generating character at (x-coord, y-coord) [y - axis reverse]
                        enemy_group.add(enemy)
                    elif tile == 40: # red car
                        car = Car('car2', x * TILE_SIZE, y * TILE_SIZE, 2, 6) # generating character at (x-coord, y-coord) [y - axis reverse]
                        car_group.add(car)
                    elif tile == 41: # blue car
                        car2 = Car('car1', x * TILE_SIZE, y * TILE_SIZE, 2, 3)
                        car_group.add(car2)
                    elif tile == 34: # bread 
                        item_box = ItemBox('Bread', x * TILE_SIZE, y * TILE_SIZE)
                        item_group.add(item_box)
                    elif tile == 3: # exit game
                        exit = Exit(img,x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)
        return player
    
    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])


class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
    def update(self):
        self.rect.x += screen_scroll

class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
    def update(self):
        self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
    def update(self):
        self.rect.x += screen_scroll

class Car(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed) -> None:
        pygame.sprite.Sprite.__init__(self)
        self.char_type = char_type
        self.speed = speed
        self.update_time = pygame.time.get_ticks()
        self.animation_list = []
        self.action = 0
        self.jump = False
        self.frame_index = 0
        self.direction = 1
        self.vel_y = 0 # velocity in the y axis
        self.in_air = True

        #ai specific variables
        self.move_counter = 0
        self.vision = pygame.Rect(0,0,150,20)
        self.idling = False
        self.idling_counter = 0

        # red car
        if self.char_type == 'car2':
            temp_list = []
            for i in range(2): # loads a sequence of images making an animation
                img = pygame.image.load(f'img/{self.char_type}/{i}.png').convert_alpha()    # import player 
                img = pygame.transform.scale(img, (int(img.get_width() * scale) , int(img.get_height() * scale)))    # size (scale) of player
                temp_list.append(img)
            self.animation_list.append(temp_list)
        
        # blue car
        
        if self.char_type == 'car1':
            temp_list = []
            for i in range(2): # loads a sequence of images making an animation
                img = pygame.image.load(f'img/{self.char_type}/{i}.png').convert_alpha()    # import player 
                img = pygame.transform.scale(img, (int(img.get_width() * scale) , int(img.get_height() * scale)))    # size (scale) of player
                temp_list.append(img)
            self.animation_list.append(temp_list)
        
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect() # rectangle is the hitbox of the player
        self.rect.center = (x,y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
    
    def move(self, moving_left, moving_right):
        '''
        tracking movement, sees if movement keys have been activated
        
        :param moving_left - checks to see if moving left key has been activated
        :param moving_right - checks to see if moving right key has been activated
        '''
        # reset movement variables
        screen_scroll = 0
        dx = 0
        dy = 0

        # assign movements variables if moving left and right
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1
        
        #jumping movement
        if self.jump == True and self.in_air == False:
            self.vel_y = -9
            self.jump = False
            self.in_air = True
        
        # apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        #check for collision
        for tile in world.obstacle_list:
            # check collision in the left and right direction
            if tile [1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                # if ai has hit wall make it turn around
                if self.char_type == 'enemy2':
                    self.direction *=-1
                    self.move_counter = 0
            #check for collision in the y direction
            if tile [1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # check if below the ground, i.e jumping
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                # check if above the ground, i.e falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        # check for collision with water
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0

        # check for collision with exit
        time_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            time_complete = True
        
        # check if fallen off the map
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0

        #check if going off the edges of the screen
        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        # update rectangle (hitbox's) position
        self.rect.x += dx
        self.rect.y += dy 

        #update scroll based on player position
        if self.char_type == 'player1':
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH)\
				or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx
        
        return screen_scroll, time_complete


    def update_animation(self):
        '''
        updates animation making animation like thing
        '''
        # update animation
        ANIMATION_COOLDOWN = 120
        #update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        # check if enough time has passed since last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        
    def car_ai(self):
        '''
        computer controlled characters
        '''
        if self.alive and player.alive:
            if pygame.sprite.spritecollide(player, car_group, False):
                if player.alive:
                    player.health -= 1
            if self.idling == False and random.randint(1, 200) == 1:
                self.idling = True
                self.idling_counter = 500
            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    if self.direction == -1:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.move_counter += 1
                    # update ai vision as the enemy moves
                    #self.vision.center = (self.rect.centerx + 50 * self.direction, self.rect.centery)
                    #pygame.draw.rect(screen, RED, self.vision, 1) # draw vision rectangle

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling -= 1
                    if self.idling_counter <= 0:
                        self.idling = False
            
        #scroll
        self.rect.x += screen_scroll
    
    def update(self):
        #scroll
        self.rect.x += screen_scroll
        #check if the player has collected bread
        if pygame.sprite.collide_rect(self, player):
            # check what kind of box it was
            player.health -= 10000
    
    def draw(self):
        '''
        Method that draws character from the __init__()
        '''
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        pygame.draw.rect(screen, BLUE, self.rect,1) # hit box

        

class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE) - self.image.get_height())
    
    def update(self):
        #scroll
        self.rect.x += screen_scroll
        #check if the player has collected bread
        if pygame.sprite.collide_rect(self, player):
            # check what kind of box it was
            if self.item_type == 'Bread':
                player.bread_collected += 1
            elif self.item_type == 'Bread2':
                player.bread_collected += 1
            # delete the item box
            self.kill()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.direction = direction
    
    def update(self):
        #move bullet
        self.rect.x += (self.direction * self.speed) + screen_scroll
        #check if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        # check for collision with level
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()
        
        #check collision with characters
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 1
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 1
                    self.kill()


# create module
start_button = button.Button(50, 400, start_img, 1)
controls_button = button.Button (50, 460, controls_img, 1)
credits_button = button.Button(50, 520, credits_img, 1)
back_button = button.Button(50, 570, back_img, 1)

# create sprite groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
item_group = pygame.sprite.Group()
car_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

# create empty tile list
world_data = [] #constructing a list of lists of a 16 x 150 map
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)

#load in level data and creates world
with open(f'level{level}_data.csv', newline='') as csvfile: #loads in csv file
    reader = csv.reader(csvfile, delimiter=',') #delimiter tells computer how to distinguish each tile by comma separation
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)


world = World()
player = world.process_data(world_data)


# main game loop
run = True
while run:
    clock.tick(FPS)
    if leaderboards == True and start_game == False:
        draw_leaderboards()
        if back_button.draw(screen):
            leaderboards = False
    elif controls_menu == True and start_game == False:
        draw_controls()
        if back_button.draw(screen):
            controls_menu = False
    elif credits_menu == True and start_game == False:
        draw_credits()
        if back_button.draw(screen):
            credits_menu = False
    elif start_game == False:
        #main menu
        draw_menu()
        # add buttons
        if start_button.draw(screen):
            start_game = True
        if controls_button.draw(screen):
            controls_menu = True
        if credits_button.draw(screen):
            credits_menu = True
    elif start_game == True:
        # draw background
        draw_bg()
        # draw map
        world.draw()
        # show bread collected
        draw_text(f'      COLLECTED: {player.bread_collected}', font, WHITE, 10, 35)
        screen.blit(bread_img, (10, 25))

        player.update()
        player.draw()
        
        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()
        
        for car in car_group:
            car.car_ai()
            car.update()
            car.draw()

        #update and draw groups
        bullet_group.update()
        item_group.update()
        car_group.update()
        decoration_group.update()
        water_group.update()
        exit_group.update()
        bullet_group.draw(screen)
        item_group.draw(screen)
        car_group.draw(screen)
        decoration_group.draw(screen)
        water_group.draw(screen)
        exit_group.draw(screen)

        RESPAWN_COOLDOWN = 20
        #update player actions
        if player.alive:
            #shoot bullets
            if shoot:
                player.shoot()
            if player.in_air:
                player.update_action(2) #2: jump and fall
            elif player.squat:
                player.update_action(3) #3: squat
            elif moving_left or moving_right:
                player.update_action(1) #1: run
            else: 
                player.update_action(0) #0: idle
            screen_scroll, time_complete = player.move(moving_left, moving_right)
            bg_scroll -= screen_scroll
            # check if player has reached the end:
            if time_complete:
                leaderboards = True
                start_game = False
        else:
            screen_scroll = 0
            if pygame.time.get_ticks() - player.update_time > RESPAWN_COOLDOWN:
                    player.update_time = pygame.time.get_ticks()
                    player.frame_index += 1
                    bg_scroll = 0
                    world_data = reset_level()
                    #load in level data and creates world
                    with open(f'level{level}_data.csv', newline='') as csvfile: #loads in csv file
                        reader = csv.reader(csvfile, delimiter=',') #delimiter tells computer how to distinguish each tile by comma separation
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                if int(tile) != 34:
                                    world_data[x][y] = int(tile)
                    world = World()
                    player = world.process_data(world_data)
                        

    for event in pygame.event.get():
        # quit game exit condition
        if event.type == pygame.QUIT:
            run = False
        #keyboard being used is detected
        if event.type == pygame.KEYDOWN: # KEYDOWN is how you know if a key is being pressed
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True
            if event.key == pygame.K_s and player.alive:
                player.squat = True
            #if event.key == pygame.K_SPACE:
            #    shoot = True
            #if event.key == pygame.K_ESCAPE:  # if you want to have escape button quit the game
            #    run = False

        #keyboard not being used is detected
        if event.type == pygame.KEYUP: # KEYUP is likewise how you know if key is not being pressed
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_s:
                player.squat = False
            if event.key == pygame.K_SPACE:
                shoot = False
            

    pygame.display.update()

pygame.quit()