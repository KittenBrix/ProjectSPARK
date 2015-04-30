from Constants import *
from DObject import *
import math
class Spark(pygame.sprite.Sprite):
    def __init__(self, parent):
        pygame.sprite.Sprite.__init__(self)
        self.parent = parent
        self.state = 1 #can be 0, 1 or 2 chr, off, def
        self.action = 0
        self.LS = [0,0]
        self.RS = [0,0]
        self.imglst = []
        self.statelist = [0,1,2]
        self.energy = FPS*10.0 #takes 10 seconds to load up fully in charge state
        self.MaxNRG = FPS*10.0
        self.NRGlvl = 2
        self.MaxNRGlvl = 5
        self.imglst.append(MIL2('objects/Cam/lasersparkfire*.png',2)[0])
        self.imglst.append(MIL2('objects/Cam/lasersparkfire*.png',2)[1])
        self.imglst.append(MIL2('objects/Cam/lasersparkfire*',2)[0])
        self.imglst.append(MIL2('objects/Cam/lasersparkfire*',2)[1])
        self.imglst.append(MIL2('objects/spark/defsource*',2)[1])
        self.imglst.append(MIL2('objects/spark/defsource*',2)[1])
        self.image = pygame.image.load('objects/Cam/lasercamsource.png')
        #self.image = pygame.image.load('randomcyborg.png')
        self.original = self.image
        #for i in range(len(self.imglst)):
        #    g = self.imglst[i]
        #    self.imglst[i] = pygame.transform.scale(g,(int(self.image.get_width()*1.3),int(self.image.get_height()*1.3)))
        self.original = self.image
        self.frame = 0
        self.x = self.parent.x
        self.y = self.parent.y
        self.rect = self.image.get_rect()
        print "made spark"
        #~~~~~~~~~~variables can be set by parent later on ~~~ use a save file maybe, or have the level set it
        self.CanPerformADInfinitely = True        
        
        
    def changeState(self, newstate):
        newstate = newstate%3
        self.state = newstate
        self.image = self.imglst[self.state*2+self.parent.direction][self.frame%len(self.imglst[self.state*2+self.parent.direction])]
        
    def Draw(self,surface,relrect):
        if relrect == None:
            #we weren't given a location to defer to
            surface.blit(self.image,self.rect)
        else:
            surface.blit(self.image,relrect)
        #draw gui for debuging TODO
        #draw energy bar
        r = 10+self.NRGlvl*20
        d = 400.0*self.energy/self.MaxNRG
        if d < 0:
            d = 0
        w = self.NRGlvl*2+2
        pygame.draw.line(surface, (255-d/400*255,0,d/400*250),(100,50),(100+d,50),w)
        pygame.draw.line(surface, (250-d/400*250,r,d/400*250+5),(100,50),(100+d,50),2*w/3)
        pygame.draw.line(surface, (255-d/400*100,r*2,d/400*100+155),(100,50),(100+d,50),w/3)
        #surface.blit(overlay, (TLWDTH/4,SCRNHGHT - TLHGHT/4 - overlay.get_height()))
        #draw left and right stick inputs
        pygame.draw.line(surface, (255,155,0),(50,50),(40*self.RS[0]+50,40*self.RS[1]+50),3)
        pygame.draw.line(surface, (0,150,255),(50,50),(40*self.LS[0]+50,40*self.LS[1]+50),3)
    
    def FixNRG(self, amount = 0.0):
        self.energy += amount
        if self.state == 0:
            self.energy += 1.0
        elif self.state == 2:
            self.energy -= .03
        if self.energy > self.MaxNRG:
            self.NRGlvl += 1
            dif = self.energy-self.MaxNRG
            if self.NRGlvl > self.MaxNRGlvl:
                self.NRGlvl = self.MaxNRGlvl
                self.energy = self.MaxNRG
            else:
                self.energy = dif
        if self.energy < 0:
            self.NRGlvl -= 1
            dif = self.energy
            if self.NRGlvl < 0:
                self.NRGlvl = 0
                self.energy = 0
            else:
                self.energy = self.MaxNRG+dif
        #print "NRGlvl: "+str(self.NRGlvl) + " energy: "+str(self.energy)
        
        
    def update(self, interactables = None):
        self.frame +=1
        self.FixNRG()
        #if offensive state, must float behind. 
        #if defensive state, rotate image based on right stick, or
        #on left stick if the action command is held
        #if charge state, play the image matching the parent.
        if self.state == 0:
            #charge state
            self.x = self.parent.rect.centerx
            self.y = self.parent.rect.centery
            self.image = self.imglst[self.state*2+self.parent.direction][self.frame%len(self.imglst[self.state*2+self.parent.direction])]
            self.rect.center = (self.x,self.y)
            if self.action == 1:
                #indicates button press while in charge form. Do something to the player
                angle = 0
                #if not self.parent.grounded and not self.parent.doublejump and (self.MaxNRG*(self.NRGlvl)+self.energy > FPS*3):
                if not self.parent.grounded and (self.MaxNRG*(self.NRGlvl)+self.energy > FPS*3):
                    #parent in air, push them in the direction indicated by the right stick or left stick
                    #energy must be above 3 seconds' charge time
                    self.AirDash(FPS*3)
        elif self.state == 1:
            #offensive
            dx = -self.parent.image.get_width()/3-self.image.get_width()/3
            dy = -self.image.get_height()/2 -10
            vx = 10.0*math.cos(self.frame/21.4)
            vy = 10.0*math.sin(self.frame/33.3)
            if vx == 0.0:
                vx += .1
            if vy == 0.0:
                vy += .1
            self.image = self.imglst[self.state*2+self.parent.direction][self.frame%len(self.imglst[self.state*2+self.parent.direction])]
            self.x = self.parent.x + vx + dx 
            self.y = self.parent.y + vy + dy
            self.rect.center = (self.x,self.y)
            
        
        elif self.state == 2:
            #defensive
            #if not (action or right stick)
            #
            self.image = self.imglst[self.state*2+self.parent.direction][self.frame%len(self.imglst[self.state*2+self.parent.direction])]
            self.x = self.parent.x
            self.y = self.parent.y
            self.rect.center = (self.x,self.y)
        #TODO remove the following when update actually deals with inputs
        if self.frame % 70 == 0:
            self.changeState(0)
            print self.state
        #self.image = pygame.transform.rotate(self.original,15*math.sin(self.frame/10.0))
        
    def AirDash(self, NRG_used):
        '''should be executed when possible. whoever calls this must set energy and NRGlvls.'''
        if self.parent.doublejump and not self.CanPerformADInfinitely:
            #if we've used this before in the air and can't do it repeatedly.
            return
        else:
            self.energy -= NRG_used
            self.parent.doublejump = True
        if abs(self.RS[0]) <= 0 and abs(self.RS[1]) <= 0:
            #right stick null, use left stick. first option is to air dodge.
            #right stick within deadzone
            x = self.LS[0]; y = self.LS[1];
            hyp = math.sqrt(x*x+y*y) 
            ratio = 1/(hyp+.0000001) #would turn the hypotenuse into a unit vector
            if (x == y) and (y == 0):
                y = -.5
                ratio = 1
            if (x/(self.parent.ddx+.00001) < 0)or (self.parent.ddx == 0) : #different signs or 0 speed
                self.parent.ddx += x * ratio * P_WALKSPEED
            else: #same signs, add on but don't exceed 1.5x P_WALKSPEED
                self.parent.ddx += x * ratio *P_WALKSPEED
            if y/(self.parent.ddy+.00001) < 0: #different signs
                self.parent.ddy += y * ratio * P_MAXFALLSPEED
            else: #same signs, add on but don't exceed 1.5x P_FALLSPEED
                self.parent.ddy += y * ratio * P_MAXFALLSPEED
        else:
            self.parent.ddx = 0
            self.parent.ddy = 0
            x = self.RS[0]; y = self.RS[1]; hyp = math.sqrt(x*x+y*y)
            ratio = 1/(hyp+.0000001) #would turn the hypotenuse into a unit vector
            if (x/(self.parent.ddx+.00001) < 0)or (self.parent.ddx == 0) : #different signs or 0 speed
                self.parent.ddx += x * ratio * 4*P_WALKSPEED
            else: #same signs, add on but don't exceed 1.5x P_WALKSPEED
                self.parent.ddx += x * ratio * 4.5*P_WALKSPEED
            if y/(self.parent.ddy+.00001) < 0: #different signs
                self.parent.ddy += y * ratio * 2 * P_MAXFALLSPEED
            else: #same signs, add on but don't exceed 1.5x P_FALLSPEED
                self.parent.ddy += y * ratio * 2.5* P_MAXFALLSPEED
        
        
    def StoreValues(self, action, LS=[0.0,0.0],RS=[0.0,0.0]):
        '''action is -1,0,1. -1 = release, 0 = no change from previous state.
        1 is press. for LS and RS, they are dicts of two elements each. 
        LS[0] and RS[0] are x values between -1 and 1, likewise for y values
        in LS[1] and RS[1]
        Assume that deadzone is compensated for in the reading device'''
        
        self.action = action
        self.LS[0] = LS[0]
        self.LS[1] = LS[1]
        self.RS[0] = RS[0]
        self.RS[1] = RS[1]
        
        
        
        
        
        
        
