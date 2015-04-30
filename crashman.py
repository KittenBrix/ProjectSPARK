#! /usr/bin/env python

import pygame, sys, DObject, Constants, Player, Wall, glob, Spark, math
from pygame.locals import *
from Constants import *
from DObject import MIL2
pygame.init()
JS = pygame.joystick.Joystick(0)
JS.init()
G = 5
SCREEN_SIZE = (SCRNWDTH, SCRNHGHT) #resolution of the game
global HORIZ_MOV_INCR
HORIZ_MOV_INCR = P_WALKSPEED #speed of movement
global FPS
global clock
global time_spent

def RelRect(actor, camera):
    return pygame.Rect(actor.rect.x-camera.rect.x, actor.rect.y-camera.rect.y, actor.image.get_width(), actor.image.get_height())

class Camera(object):
    '''Class for center screen on the player'''
    def __init__(self, screen, player, level_width, level_height):
        self.player = player
        self.rect = screen.get_rect()
        self.rect.center = self.player.center
        self.world_rect = Rect(-TLWDTH/2, -TLHGHT/2, level_width, level_height)
        #we use -TLWDTH/2 and - TLHGHT/2 because we draw the objects 
        #at their centers, not their topleft corner.
    def update(self):
      if self.player.centerx > self.rect.centerx + CMTLRNC:
          self.rect.centerx = self.player.centerx - CMTLRNC
      elif self.player.centerx < self.rect.centerx - CMTLRNC:
          self.rect.centerx = self.player.centerx + CMTLRNC
      if self.player.centery > self.rect.centery + CMTLRNC:
          self.rect.centery = self.player.centery - CMTLRNC
      elif self.player.centery < self.rect.centery - CMTLRNC:
          self.rect.centery = self.player.centery + CMTLRNC
      self.rect.clamp_ip(self.world_rect)

    def draw_sprites(self, surf, sprites):
        for s in sprites:
            if s.rect.colliderect(self.rect):
                #new draw method
                s.Draw(surf, RelRect(s,self))
                #surf.blit(s.image, RelRect(s, self))

              
class Crashman(pygame.sprite.Sprite):
    '''class for player and collision'''
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        #~~~~~~movement attr
        self.dy = 0.0
        self.dx = 0.0
        self.x = x
        self.y = y
        self.prevpos = (0,0)
        #~~~~~~ contact flags
        self.contact = False
        self.jump = True
        self.wasonground = False
        self.doublejump = True
        self.grounded = False
        #~~~~~~~~~~ image/draw stuff
        self.image = pygame.image.load('player/Idle1.png').convert()
        self.rect = self.image.get_rect()
        self.collisionrect = Rect(x,y,36,52)
        self.run_left = MIL2("player/Run*",4)
        self.run_right = self.run_left[0]
        self.run_left = self.run_left[1]
        self.run_left.sort()
        self.run_right.sort()
        self.jump_anim = [[self.run_right[0]],[self.run_left[0]]] #replace with jumping animation
        self.crouch = MIL2('player/CrouchHold1.png',1)
        t = self.crouch[0][0]
        self.crouch[0][0] = self.crouch[1][0]
        self.crouch[1][0] = t
        self.idle = MIL2('player/Idle*',4)
        self.idle = MIL2('Ma*',4)
        self.direction = 0
        self.spark = Spark.Spark(self)
        self.collisionrect.topleft = [x, y]
        self.frame = 0
        
    def touchground(self,touchedobj):
        self.grounded = True
        self.jump = self.doublejump = False
        
    def Draw(self, surface, relrect = None):
        if relrect == None:
            #we weren't given a location to defer to
            surface.blit(self.image,self.rect)
        else:
            surface.blit(self.image,relrect)
            
    def update(self, up, down, left, right, action = 0):
        #This is where state handling is kept
        #check for inputs button presses and joystick states.
        
        #check for intended direction to move this frame. add forces together. add force to speed. 
        #limit speed. add speed to position

        #check for collisions with regards to x
        #~~Call collider's act method. if true, we can stay there, otherwise we have been moved back.
        #check for collisions with respect to y
        #~~call collider's act method for dy. 
        self.frame += 1
        self.contact = False
        #self.dy += 1.2
        self.prevpos = self.collisionrect.center
        if self.grounded:
            self.wasonground = True
        if up:
            if self.grounded:
                if not self.jump:
                    self.dy = -12
                self.jump = True
                self.grounded = False
                self.frame = 0
            if not self.grounded and self.dy!=0 and not self.doublejump:
                self.dy -= .8 #extend jump range by holding it down
        elif down:
            if self.grounded:
                self.image = self.crouch[self.direction][0].convert_alpha()
                self.frame = 0
                self.dx = self.dx*.9
        self.image = self.idle[self.direction][self.frame%len(self.idle[0])]

        if left:
            self.direction = 1            
            if self.grounded:
                self.dx += (-HORIZ_MOV_INCR-self.dx)*abs(JS.get_axis(PS3["LSX"]))
                self.frame = self.frame % len(self.run_left)
                self.image = self.run_left[self.frame%len(self.run_left)].convert_alpha()
            else:
                if self.dx > -HORIZ_MOV_INCR:
                    self.dx += (-HORIZ_MOV_INCR-self.dx)*.15
                #self.image = self.run_left[2].convert_alpha()
                else:
                    self.dx = self.dx*.99
        elif right:
            self.direction = 0            
            if self.grounded:
                self.dx += (HORIZ_MOV_INCR-self.dx)*abs(JS.get_axis(PS3["LSX"]))
                self.frame = self.frame % len(self.run_right)
                self.image = self.run_right[self.frame%len(self.run_right)].convert_alpha()
            else:
                #self.image = self.run_right[2].convert_alpha()
                if self.dx < HORIZ_MOV_INCR:
                    self.dx += (HORIZ_MOV_INCR-self.dx)*.15
                else:
                    self.dx = self.dx*.99
        if not (left or right):
            if self.grounded:
                self.dx = self.dx*.5
            if self.wasonground:
                self.dx = self.dx*.7
                
        self.collisionrect.right += math.floor(self.dx+.5)
        #print self.dx
        #print "contact test before x collision: "+ str(self.contact)
        self.collide(self.dx, 0, world)
        print world
        #print "contact test after x collision: "+ str(self.contact)
        #print "~~~~~~~"

        if not self.contact:
            b = "contact was false..."
            if self.dy > P_MAXFALLSPEED: #maxfallspeed
                self.dy = (P_MAXFALLSPEED + (self.dy-P_MAXFALLSPEED)*.8)
                b += "falling past fallspeed set to maxspeed..."
            if self.grounded and self.dy >= 0:
                #if we were grounded last frame, drop by 4 to see if we could be on slopes
                #but only do so if we aren't rising from jumping or something.
                self.dy = 1 #since dy > 0, make it 0.1 since we are on the ground
                self.collisionrect.bottom += 10
                b+= "was grounded and dy > 0, adjusting +6 y pixels"
            elif self.dy < 0:
                #else go by the speed.
                b+= "and am rising/jumping"
                self.collisionrect.bottom += math.floor(self.dy+.5)
            elif not self.grounded:
                self.frame = len(self.jump_anim)-2
                b+= "and am falling"
                self.collisionrect.bottom += math.floor(self.dy+.5)
            #print b
        if not self.grounded:
            i = self.frame
            if i >= len(self.jump_anim[self.direction]):
                i = -1
            self.image = self.jump_anim[self.direction][i]
            
            self.dy += 1.5
            self.collisionrect.top += math.floor(self.dy+.5)
            if self.contact == True:
                self.jump = False
                self.doublejump = False
        #self.collisionrect.top += self.dy
        #print self.dy
        #print self.contact
        self.collide(0, self.dy, world)
        #print self.contact
        #print "````````````"

        
        #set image rect data
        self.rect = self.image.get_rect()
        self.rect.bottom = self.collisionrect.bottom
        self.rect.midbottom = self.collisionrect.midbottom
        self.x = self.collisionrect.centerx
        self.y = self.collisionrect.centery
        #end fix 
        if self.contact == False:
            self.grounded = False
            self.wasonground = False #used for shortening horizontal speed when holding jump
            #if we haven't contacted anything, we should be falling
        #print str(self.x)+": " + str(self.y)
        #print str(self.x)+": " + str(self.y)
        #update components attached to self
        l = [0,0]
        if left:
            l[0]=-1.0
        if right:
            l[0]=1.0
        if up:
            l[1]=-1.0
        if down:
            l[1]=1.0
        #TODO self.spark.StoreValues(action,l)
        self.spark.update()
        
    def collide(self, dx, dy, world):
        for o in world:
            #ignore intangible blocks, TODO world sould become a spritegroup instead.
            if not o.CanCollide:
                continue
            if self.collisionrect.colliderect(o):
                if (str(type(o)) == "<class 'Wall.Wall'>"):
                    o.act(self,dx,dy)
                
class Level(object):
    '''Read a map and create a level'''
    def __init__(self, open_level):
        self.level1 = [] 
        self.world = []
        self.all_sprite = pygame.sprite.Group()
        self.level = open(open_level, "r") #level is text format
        self.crashman = None
    def create_level(self, dx, dy):
        x = dx
        y = dy
        for char in self.level:
            self.level1.append(char)
        for row in self.level1:
            for col in row:
                if col == "C":
                    #obstacle = Obstacle(x, y)
                    obstacle = Wall.Wall(x,y,[0,0],pygame.image.load('TileSets/Grass/slice27_27.png'))
                    #obstacle = DObject.DObject(x,y,[0,0],[0,0])
                    self.world.append(obstacle)
                    self.all_sprite.add(obstacle)
                elif col == "X":
                    #obstacle = Obstacle(x, y)
                    obstacle = Wall.Wall(x,y,[0,0],pygame.image.load('TileSets/Grass/slice03_03.png'))
                    #obstacle = DObject.DObject(x,y,[0,0],[0,0])
                    self.world.append(obstacle)
                    self.all_sprite.add(obstacle)
                elif col == "P":
                    self.crashman = Player.Player(x,y)
                    
                    #self.crashman = Crashman(x,y-3)
                    self.all_sprite.add(self.crashman)
                    #self.all_sprite.add(self.crashman.spark)
                elif col == "L":
                    #obstacle = Obstacle(x,y,(-0.5))
                    obstacle = Wall.Wall(x,y,[1,0], pygame.image.load('TileSets/Grass/slice07_07.png'))
                    self.world.append(obstacle)
                    self.all_sprite.add(obstacle)
                elif col == "l":
                    #obstacle = Obstacle(x,y,(-0.5))
                    obstacle = Wall.Wall(x,y,[0,1], pygame.transform.flip(pygame.image.load('TileSets/Grass/slice07_07.png'),True,False))
                    self.world.append(obstacle)
                    self.all_sprite.add(obstacle)
                elif col == "T":
                    #obstacle = Obstacle(x,y,(-0.5))
                    obstacle = Wall.Wall(x,y,[1,.5], pygame.image.load('TileSets/Grass/tip.png'))
                    self.world.append(obstacle)
                    self.all_sprite.add(obstacle)
                elif col == "t":
                    #obstacle = Obstacle(x,y,(-0.5))
                    obstacle = Wall.Wall(x,y,[.5,1], pygame.transform.flip(pygame.image.load('TileSets/Grass/tip.png'),True,False))
                    self.world.append(obstacle)
                    self.all_sprite.add(obstacle)
                elif col == "B":
                    #obstacle = Obstacle(x,y,(-0.5))
                    obstacle = Wall.Wall(x,y,[.5,0], pygame.image.load('TileSets/Grass/base.png'))
                    self.world.append(obstacle)
                    self.all_sprite.add(obstacle)
                elif col == "b":
                    #obstacle = Obstacle(x,y,(-0.5))
                    obstacle = Wall.Wall(x,y,[0,.5], pygame.transform.flip(pygame.image.load('TileSets/Grass/base.png'),True,False))
                    self.world.append(obstacle)
                    self.all_sprite.add(obstacle)
                elif col == "F":
                    #obstacle= Obstacle(x,y,(-0.5))
                    obstacle = Wall.Wall(x,y,[1,0], pygame.transform.flip(pygame.image.load('TileSets/Grass/base.png'),True,False))
                    obstacle.rect.top-=TLHGHT
                    obstacle.rect.height = TLHGHT*2
                    self.world.append(obstacle)
                    self.all_sprite.add(obstacle)
                    
                x += TLWDTH #TILEWIDTH
            y += TLHGHT #TILEHEIGHT
            x = dx 
        if self.crashman != None:
            self.crashman.setCollideables(self.world)
            pass
    def get_size(self):
        lines = self.level1
        #line = lines[0]
        line = max(lines, key=len)
        self.width = (len(line))*TLWDTH #TILEWIDTH
        self.height = (len(lines))*TLHGHT #TILEHEIGHT
        return (self.width, self.height)



def tps(orologio,fps):
    temp = orologio.tick(fps)
    tps = temp / 1000.
    #print tps #use this to see how many seconds are passing in each frame
    return tps


pygame.init()

screen = pygame.display.set_mode(SCREEN_SIZE, 32)
screen_rect = screen.get_rect()
#create 5 layers of screens, mimics z axis TODO

background = pygame.image.load("world/background2.jpg").convert()
background_rect = background.get_rect()
level = Level("level/level3")
level.create_level(0,0)
world = level.world #get the world from the level
crashman = level.crashman #get the player from the level

pygame.mouse.set_visible(0)
camera = Camera(screen, crashman.collisionrect, level.get_size()[0], level.get_size()[1])
all_sprite = level.all_sprite #get all sprites from the level
#DEBUG_SPRITE
clock = pygame.time.Clock()

up = down = left = right = action = False
x, y = 0, 0
frame = 0
while True:
    frame += 1
    if frame >= background_rect.width:
        frame = 0
    action = 0
    QC = 0
    for event in pygame.event.get():
        if event.type == JOYBUTTONDOWN:
            if event.button == PS3["O"]:
                up = 1
            elif event.button == PS3["R1"]:
                action = 1
            elif (event.button == PS3["DD"]) or (event.button == PS3["DR"]) or (event.button == PS3["DU"]) or (event.button == PS3["DL"]):
                QC += FPS/4
        elif event.type == JOYBUTTONUP:
            if event.button == PS3["O"]:
                up = 0
            elif event.button == PS3["R1"]:
                action = -1
        elif event.type == KEYDOWN:
            if event.key == K_UP:
                up = 1
            elif event.key == K_DOWN:
                down = True
            elif event.key == K_LEFT:
                left = True
            elif event.key == K_RIGHT:
                right = True
            elif event.key == K_SPACE:
                action = 1
            elif event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
        elif event.type == KEYUP:
            if event.key == K_UP:
                up = 0
            elif event.key == K_DOWN:
                down = False
            elif event.key == K_LEFT:
                left = False
            elif event.key == K_RIGHT:
                right = False
            elif event.key == K_SPACE:
                action = -1
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        
    asize = ((screen_rect.w // background_rect.w + 2) * background_rect.w, (screen_rect.h // background_rect.h + 1) * background_rect.h)
    bg = pygame.Surface(asize)
    if crashman.rect.top > camera.world_rect.height:
        crashman.collisionrect.top = -5
    if crashman.rect.left > camera.world_rect.width:
        crashman.collisionrect.left = 0
    for x in range(0, asize[0], background_rect.w):
        for y in range(0, asize[1], background_rect.h):
            screen.blit(background, (x-frame, y))

    time_spent = tps(clock, FPS)
    print time_spent
    camera.draw_sprites(screen, all_sprite)
    #camera should draw sprites based on order of spritegroups.
    #all_sprite should be DrawOrder[i] where objects in DrawOrder[0] are drawn first
    LSX = JS.get_axis(PS3["LSX"])
    LSY = JS.get_axis(PS3["LSY"])
    if abs(LSX) <.15:
        LSX = 0.0
    if LSX > 0:
        right = True
        left = False
    elif LSX < 0:
        left = True
        right = False
    else:
        left = right = False
    if abs(LSY) <.15:
        LSY = 0.0
    RSX = JS.get_axis(PS3["RSX"])
    RSY = JS.get_axis(PS3["RSY"])
    if abs(RSX) <.15:
        RSX = 0.0
    if abs(RSY) <.15:
        RSY = 0.0
    #crashman.spark.StoreValues(action, [LSX,LSY],[RSX,RSY])
    crashman.spark.FixNRG(QC)
    crashman.PumpInput({'LSX':LSX,'LSY':LSY,'RSX':RSX,'RSY':RSY,'O':up ,'R1':action})
    crashman.update()
    
    camera.update()
    
    
    pygame.display.flip()