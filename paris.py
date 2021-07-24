# platformer game
__author__ = 'Simon Lee: Game Developer, simonlee711@gmail.com'


import pygame
from pygame import mixer
import os
import random

from pygame import draw 

mixer.init()
pygame.init()


# Screen size - adjustable
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)


# Building the screen and caption
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("私のパンはどこですか?")

# set frame rate
clock = pygame.time.Clock()
FPS = 60

#define game variables
GRAVITY = 0.5
TILE_SIZE = 40

# define player action variables. Essentially initialize player movement
moving_left = False
moving_right = False
shoot = False

#load images
#bullet
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
#pygame.mixer.music.load('audio/awake.mp3')
#pygame.mixer.music.set_volume(0.2)
#pygame.mixer.music.play(-1,0.5,10000)


# defining colors
BG = (0,0,0) # background color RGB (currently set at black)
BLUE = (0,0,255)
WHITE = (255,255,255)
RED = (255,0,0)

font = pygame.font.SysFont('Comic Sans', 30)

def draw_text(text, font, text_col,x,y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x,y))

def draw_bg():
    '''
    function that colors in the background
    '''
    screen.fill(BG)
    pygame.draw.line(screen, BLUE , (0,500), (SCREEN_WIDTH, 500))


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
        self.health = 1
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
        if self.char_type == 'car2':
            temp_list = []
            for i in range(2): # loads a sequence of images making an animation
                img = pygame.image.load(f'img/{self.char_type}/{i}.png').convert_alpha()    # import player 
                img = pygame.transform.scale(img, (int(img.get_width() * scale) , int(img.get_height() * scale)))    # size (scale) of player
                temp_list.append(img)
            self.animation_list.append(temp_list)

            
        
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect() # rectangle is the hitbox of the player
        self.rect.center = (x,y)
    
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

        #check collision with floor
        if self.rect.bottom + dy > 500:
            dy = 500 - self.rect.bottom
            self.in_air = False


        # update rectangle (hitbox's) position
        self.rect.x += dx
        self.rect.y += dy 

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

    def car_ai(self):
        '''
        computer controlled characters
        '''
        if self.alive and player.alive:
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
        


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE) - self.image.get_height())
    
    def update(self):
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
        self.rect.x += (self.direction * self.speed)
        #check if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
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


# create sprite groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
item_group = pygame.sprite.Group()
car_group = pygame.sprite.Group()

# temp create item boxes
item_box = ItemBox('Bread', 150, 470)
item_group.add(item_box)
item_box2 = ItemBox('Bread2', 300, 470)
item_group.add(item_box2)


player = Player('player1', 20, 400, 2, 4) # generating character at (x-coord, y-coord) [y - axis reverse]
enemy = Player('enemy2', 300, 450, 2, 2) # generating character at (x-coord, y-coord) [y - axis reverse]
enemy2 = Player('enemy2', 640, 450, 2, 2) # generating character at (x-coord, y-coord) [y - axis reverse]
car1 = Player('car2', 700, 450, 2, 8) # generating character at (x-coord, y-coord) [y - axis reverse]
enemy_group.add(enemy)
enemy_group.add(enemy2)
car_group.add(car1)




# main game loop
run = True
while run:
    clock.tick(FPS)
    draw_bg()
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
    bullet_group.draw(screen)
    item_group.draw(screen)
    car_group.draw(screen)

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
    
    player.move(moving_left, moving_right)
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