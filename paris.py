# platformer game
__author__ = 'Simon Lee: Game Developer, simonlee711@gmail.com'


import pygame
from pygame import mixer
import os

mixer.init()
pygame.init()


# Screen size - adjustable
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)


# Building the screen and caption
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Where's my bread?")

# set frame rate
clock = pygame.time.Clock()
FPS = 60

#define game variables
GRAVITY = 0.5


# define player action variables. Essentially initialize player movement
moving_left = False
moving_right = False

# load music and sounds
#pygame.mixer.music.load('audio/awake.mp3')
#pygame.mixer.music.set_volume(0.2)
#pygame.mixer.music.play(-1,0.5,10000)


# defining colors
BG = (0,0,0) # background color RGB (currently set at black)
BLUE = (0,0,255)
RED = (255,0,0)


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
        
        # idle animation
        temp_list = []
        for i in range(2): # loads a sequence of images making an animation
            img = pygame.image.load(f'img/{self.char_type}/idle/{i}.png')    # import player 
            img = pygame.transform.scale(img, (int(img.get_width() * scale) , int(img.get_height() * scale)))    # size (scale) of player
            temp_list.append(img)
        self.animation_list.append(temp_list)
        '''
        # moving animation
        temp_list = []
        for i in range(11): # loads a sequence of images making an animation
            img = pygame.image.load(f'img/{self.char_type}/movement/{i}.png')    # import player 
            img = pygame.transform.scale(img, (int(img.get_width() * scale) , int(img.get_height() * scale)))    # size (scale) of player
            temp_list.append(img)
        self.animation_list.append(temp_list)

        # falling animation
        temp_list = []
        for i in range(5): # loads a sequence of images making an animation
            img = pygame.image.load(f'img/{self.char_type}/fall/{i}.png')    # import player 
            img = pygame.transform.scale(img, (int(img.get_width() * scale) , int(img.get_height() * scale)))    # size (scale) of player
            temp_list.append(img)
        self.animation_list.append(temp_list)

        # squatting animation
        temp_list = []
        for i in range(5): # loads a sequence of images making an animation
            img = pygame.image.load(f'img/{self.char_type}/squat/{i}.png')    # import player 
            img = pygame.transform.scale(img, (int(img.get_width() * scale) , int(img.get_height() * scale)))    # size (scale) of player
            temp_list.append(img)
        self.animation_list.append(temp_list)
        '''
        
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect() # rectangle is the hitbox of the player
        self.rect.center = (x,y)

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


    def draw(self):
        '''
        Method that draws character from the __init__()
        '''
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)



player = Player('player', 20, 400, 2, 5) # generating character at (x-coord, y-coord) [y - axis reverse]




# main game loop
run = True
while run:
    clock.tick(FPS)
    draw_bg()
    player.update_animation()
    player.draw()

    #update player actions
    if player.alive:
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
            

    pygame.display.update()

pygame.quit()