import pygame, sys, copy, random
from pygame.locals import *

# Initialise Display
pygame.init()
display_surf = pygame.display.set_mode((890, 650), pygame.DOUBLEBUF)
game_screen = pygame.Surface((750, 650), pygame.SRCALPHA, 32)
score_screen = pygame.Surface((140, 650))
pygame.display.set_caption("Platformer")

# Load Music
pygame.mixer.music.load("backgroundmusic.mp3")

# Initialise Variables
myfont = pygame.font.SysFont('Arial', 14)
ScoreBoard = pygame.image.load("scoreboard.png")
ScoreMusic = pygame.image.load("scoremusic.png")
ScoreFX = pygame.image.load("scorefx.png")
ScoreQuit = pygame.image.load("scorequit.png")
FX = True

Grid = [[0 for x in range(20)] for x in range(20)]
PrevGrid = Grid[:]
MouseGridPosX = 0
MouseGridPosY = 0

class player(object):
    def __init__(self):
        self.Sprite = [None for x in range(10)]
        # Initialise Variables
        for x in range(1, 9):
            self.Sprite[x] = pygame.image.load("mario" + str(x) + ".png")
            self.Sprite[x] = pygame.transform.scale(self.Sprite[x], (50, 50))
        self.CurrentSprite = 1
        self.SpriteNumber = []
        self.SpriteInc = 1
        self.PosX = 50
        self.PosY = 50
        self.PrevPosX = 50
        self.PrevPosY = 50
        self.SizeX = 50
        self.SizeY = 50
        self.MovSpeed = 6
        self.Direct = 0 # 1 - Up, 2 - Right, 3 - Down, 4 - Left
        self.PrevDirect = 0
        self.AllignN = False
        self.AllignE = False
        self.AllignS = False
        self.AllignW = False
        self.AllignAmount = 0
        self.CurrentPlayer = 1
        self.KeyUp = None
        self.KeyDown = None
        self.KeyLeft = None
        self.KeyRight = None
        self.KeyBomb = None
        self.Lives = 3
        self.Alpha = 255
        self.Immune = False
        self.ImmuneCount = 0
        self.Dead = False
        self.DeathCount = 0
        self.DeathCountX = 1
        self.DeathCountY = 1
        self.Diff = 0
        self.BombLength = 2
        self.PassThrough = False
        self.PassThroughCount = 0
        self.BombCount = 1
        self.Music = True
        self.FX = True
        self.HitAudio = pygame.mixer.Sound("ow.wav")
        self.PowerAudio = pygame.mixer.Sound("beep.wav")

    def Set(self, player):
        self.CurrentPlayer = player
        if self.CurrentPlayer == 1:
            self.PosX = 50
            self.PosY = 50
            self.KeyUp = K_w
            self.KeyDown = K_s
            self.KeyLeft = K_a
            self.KeyRight = K_d
            self.KeyBomb = K_TAB
            self.SpriteNumber = [0, 1, 2, 3, 4]
        elif self.CurrentPlayer == 2:
            self.PosX = 650
            self.PosY = 550
            self.KeyUp = K_UP
            self.KeyDown = K_DOWN
            self.KeyLeft = K_LEFT
            self.KeyRight = K_RIGHT
            self.KeyBomb = K_RCTRL
            self.SpriteNumber = [0, 5, 6, 7, 8]
        
    def Handle(self):        
        # Keyboard Inputs
        self.Direct = 0
        key = pygame.key.get_pressed()
        if key[self.KeyUp]:
            self.Direct = 1
            self.CurrentSprite = 1
        elif key[self.KeyLeft]:
            self.Direct = 4
            self.CurrentSprite = 4
        elif key[self.KeyDown]:
            self.Direct = 3
            self.CurrentSprite = 3
        elif key[self.KeyRight]:
            self.Direct = 2
            self.CurrentSprite = 2

        if key[self.KeyBomb]:
            for x in range(1, 20):
                if Bomb[x].Free() == False and self.BombCount > 0:                    
                    if Grid[int((self.PosX + (self.SizeX / 2)) // 50)][int((self.PosY + (self.SizeX / 2)) // 50)] != 12:
                        self.BombCount -= 1
                        Bomb[x].Set((self.PosX + (self.SizeX / 2)) // 50, (self.PosY + (self.SizeX / 2)) // 50, self.CurrentPlayer, self.BombLength)
                        Grid[int((self.PosX + (self.SizeX / 2)) // 50)][int((self.PosY + (self.SizeX / 2)) // 50)] = 12
                        break
                    
        mouseposx, mouseposy = pygame.mouse.get_pos()
        # Events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                # Handle Music Muting
                if mouseposx > 10 and mouseposx < 65:
                    if mouseposy > 569 and mouseposy < 599:
                        if self.Music == True:
                            pygame.mixer.music.pause()
                            self.Music = False
                        elif self.Music == False:
                            pygame.mixer.music.unpause()
                            self.Music = True
                # Handle FX Muting
                if mouseposx > 75 and mouseposx < 130:
                    if mouseposy > 569 and mouseposy < 599:
                        if self.FX == True:
                            self.FX = False
                        elif self.FX == False:
                            self.FX = True
                        for x in range(1, 20):
                            Bomb[x].Audio()
                        
                

    def Update(self):
        # Movement -----------------------------------------------------------
        self.PrevPosX = self.PosX
        self.PrevPosY = self.PosY
        if self.Direct == 1:
            self.PosY -= self.MovSpeed
        elif self.Direct == 2:
            self.PosX += self.MovSpeed
        elif self.Direct == 3:
            self.PosY += self.MovSpeed
        elif self.Direct == 4:
            self.PosX -= self.MovSpeed

        self.PrevDirect = self.Direct

        # COLLISION
        self.AllignE = False
        self.AllignW = False
        self.AllignS = False
        self.AllignN = False
        for x in range(15):
            for y in range(13):
                BPX, BPY, BSX, BSY = Block[x][y].Rect()
                if Grid[x][y] == 10:
                    # Check if the player intersects with the block
                    if self.PosX < BPX + BSX and self.PosX + self.SizeX > BPX:
                        if self.PosY < BPY + BSY and self.PosY + self.SizeY > BPY:
                            # SIDES
                            if self.PrevPosX + self.SizeX <= BPX:
                                # Collision from left to right
                                if self.PosX + self.SizeX >= BPX and self.PosX <= BPX:
                                    
                                    if self.PosY > BPY + (BSY / 2):
                                        self.AllignE = True
                                        self.AllignAim = (y * 50) + 50
                                        
                                    if self.PosY + self.SizeY < BPY + (BSY / 2):
                                        self.AllignE = True
                                        self.AllignAim = (y * 50) - 50
                                        
                                    self.PosX = BPX - self.SizeX
                            if self.PrevPosX >= BPX + BSX:
                                # Collision from right to left
                                if self.PosX <= BPX + BSX and self.PosX + self.SizeX >= BPX + BSX:

                                    if self.PosY > BPY + (BSY / 2):
                                        self.AllignW = True
                                        self.AllignAim = (y * 50) + 50
                                        
                                    if self.PosY + self.SizeY < BPY + (BSY / 2):
                                        self.AllignW = True
                                        self.AllignAim = (y * 50) - 50
                                        
                                    self.PosX = BPX + BSX
                            # TOPOM        
                            if self.PrevPosY + self.SizeY <= BPY:
                                # Collision from above
                                if self.PosY + self.SizeY >= BPY and self.PosY <= BPY:

                                    if self.PosX > BPX + (BSX / 2):
                                        self.AllignS = True
                                        self.AllignAim = (x * 50) + 50
                                        
                                    if self.PosX + self.SizeX < BPX + (BSX / 2):
                                        self.AllignS = True
                                        self.AllignAim = (x * 50) - 50
                                        
                                    self.PosY = BPY - self.SizeY
                            if self.PrevPosY >= BPY + BSY:
                                # Collision from below
                                if self.PosY <= BPY + BSY and self.PosY + self.SizeY >= BPY + BSY:

                                    if self.PosX > BPX + (BSX / 2):
                                        self.AllignN = True
                                        self.AllignAim = (x * 50) + 50
                                        
                                    if self.PosX + self.SizeX < BPX + (BSX / 2):
                                        self.AllignN = True
                                        self.AllignAim = (x * 50) - 50
                                        
                                    self.PosY = BPY + BSY
                                    
        # Allignment
        if self.AllignE == True:
            self.Diff = self.PosY - self.AllignAim
            if self.Diff > 0:
                if self.Diff > self.MovSpeed:
                    self.PosY -= self.MovSpeed
                else:
                    self.PosY -= self.Diff
            elif self.Diff < 0:
                if self.Diff < -self.MovSpeed:
                    self.PosY += self.MovSpeed
                else:
                    self.PosY -= self.Diff
                    
        elif self.AllignW == True:
            self.Diff = self.PosY - self.AllignAim
            if self.Diff > 0:
                if self.Diff > self.MovSpeed:
                    self.PosY -= self.MovSpeed
                else:
                    self.PosY -= self.Diff
            elif self.Diff < 0:
                if self.Diff < -self.MovSpeed:
                    self.PosY += self.MovSpeed
                else:
                    self.PosY -= self.Diff
                    
        elif self.AllignS == True:
            self.Diff = self.PosX - self.AllignAim
            if self.Diff > 0:
                if self.Diff > self.MovSpeed:
                    self.PosX -= self.MovSpeed
                else:
                    self.PosX -= self.Diff
            elif self.Diff < 0:
                if self.Diff < -self.MovSpeed:
                    self.PosX += self.MovSpeed
                else:
                    self.PosX -= self.Diff
                
        elif self.AllignN == True:
            self.Diff = self.PosX - self.AllignAim
            if self.Diff > 0:
                if self.Diff > self.MovSpeed:
                    self.PosX -= self.MovSpeed
                else:
                    self.PosX -= self.Diff
            elif self.Diff < 0:
                if self.Diff < -self.MovSpeed:
                    self.PosX += self.MovSpeed
                else:
                    self.PosX -= self.Diff
                                    
#------------------------------------------------------------------------------------------------------------------------

        for x in range(15):
            for y in range(13):
                BPX, BPY, BSX, BSY = Crate[x][y].Rect()
                if Grid[x][y] == 11 and Crate[x][y].Active == True:
                    # Check if the player intersects with the block
                    if self.PosX < BPX + BSX and self.PosX + self.SizeX > BPX:
                        if self.PosY < BPY + BSY and self.PosY + self.SizeY > BPY:
                            # SIDES
                            if self.PrevPosX + self.SizeX <= BPX:
                                # Collision from left to right
                                if self.PosX + self.SizeX >= BPX and self.PosX <= BPX:
                                    self.PosX = BPX - self.SizeX
                            if self.PrevPosX >= BPX + BSX:
                                # Collision from right to left
                                if self.PosX <= BPX + BSX and self.PosX + self.SizeX >= BPX + BSX:
                                    self.PosX = BPX + BSX
                            # TOPOM        
                            if self.PrevPosY + self.SizeY <= BPY:
                                # Collision from above
                                if self.PosY + self.SizeY >= BPY and self.PosY <= BPY:
                                    self.PosY = BPY - self.SizeY
                            if self.PrevPosY >= BPY + BSY:
                                # Collision from below
                                if self.PosY <= BPY + BSY and self.PosY + self.SizeY >= BPY + BSY:
                                    self.PosY = BPY + BSY

                BPX = x * 50
                BPY = y * 50
                BSX = 50
                BSY = 50          
                if Grid[x][y] == 12 and self.PassThrough == False:
                    # Check if the player intersects with the bomb
                    if self.PosX < BPX + BSX and self.PosX + self.SizeX > BPX:
                        if self.PosY < BPY + BSY and self.PosY + self.SizeY > BPY:
                            # SIDES
                            if self.PrevPosX + self.SizeX <= BPX:
                                # Collision from left to right
                                if self.PosX + self.SizeX >= BPX and self.PosX <= BPX:
                                    self.PosX = BPX - self.SizeX
                            if self.PrevPosX >= BPX + BSX:
                                # Collision from right to left
                                if self.PosX <= BPX + BSX and self.PosX + self.SizeX >= BPX + BSX:
                                    self.PosX = BPX + BSX
                            # TOPOM        
                            if self.PrevPosY + self.SizeY <= BPY:
                                # Collision from above
                                if self.PosY + self.SizeY >= BPY and self.PosY <= BPY:
                                    self.PosY = BPY - self.SizeY
                            if self.PrevPosY >= BPY + BSY:
                                # Collision from below
                                if self.PosY <= BPY + BSY and self.PosY + self.SizeY >= BPY + BSY:
                                    self.PosY = BPY + BSY

#-----------------------------------------------------------------------------------------------------------
        for x in range(1, 20):
            if Bomb[x].Free() == True:
                BPX, BPY, BSX, BSY = Bomb[x].Rect()
                if Grid[int((BPX + (BSX / 2)) // 50)][int((BPY + (BSY / 2)) // 50)] == 13:
                    Bomb[x].Activate()               

#-----------------------------------------------------------------------------------------------------------

        for x in range(1, 20):
            if PowerUp[x].Free() == True:
                BPX, BPY, BSX, BSY, PN = PowerUp[x].Rect()
                # Check if the player intersects with the PowerUp
                if Grid[int((BPX + (BSX / 2)) // 50)][int((BPY + (BSY / 2)) // 50)] == 13:
                    PowerUp[x].Set()
                if self.PosX < BPX + BSX and self.PosX + self.SizeX > BPX:
                    if self.PosY < BPY + BSY and self.PosY + self.SizeY > BPY:
                        PowerUp[x].Set()
                        if self.FX == True:
                            self.PowerAudio.play()
                        if PN == 1:
                            self.MovSpeed += 1
                        elif PN == 2:
                            self.BombLength += 1
                        elif PN == 3:
                            self.BombCount += 1
                        elif PN == 4:
                            self.PassThrough = True
                            self.Alpha = 50

        if self.PassThrough == True:
            self.PassThroughCount += 1
            if self.PassThroughCount >= 100:
                 self.PassThroughCount = 0
                 self.PassThrough = False
                 self.Alpha = 255

#------------------------------------------------------------------------------------------------------------------------

        if self.Immune == False:
            for x in range(15):
                for y in range(13):
                    if Grid[int((self.PosX + (self.SizeX / 2)) // 50)][int((self.PosY + (self.SizeX / 2)) // 50)] == 13 and self.Immune == False:
                        self.Immune = True
                        if self.FX == True:
                            self.HitAudio.play()
                        self.Lives -= 1
                        
        if self.Lives == 0:
            self.Dead = True

        if self.Dead == True:
            self.DeathCount += 1
            if self.DeathCount == 1:
                Block[self.DeathCountX][self.DeathCountY].Set(self.DeathCountX * 50, self.DeathCountY * 50, True)
                self.DeathCount = 0
                self.DeathCountX += 1
                if self.DeathCountX == 14:
                    self.DeathCountX = 1
                    self.DeathCountY += 1
                    if self.DeathCountY == 13:
                        if self.CurrentPlayer == 1:
                            print("Red player wins!")
                        elif self.CurrentPlayer == 2:
                            print("Blue player wins!")
                        pygame.quit()
                        sys.exit()
                        

        if self.Immune == True:
            if self.PassThrough == True:
                self.Alpha = 255
            self.ImmuneCount += 1
            if self.ImmuneCount < 20 or (self.ImmuneCount > 40 and self.ImmuneCount < 60):
                self.Alpha -= 10
            elif (self.ImmuneCount > 20 and self.ImmuneCount < 40) or self.ImmuneCount > 60:
                self.Alpha += 10

            if self.Alpha < 0:
                self.Alpha = 0
            elif self.Alpha > 255:
                self.Alpha = 255
                
            if self.ImmuneCount == 80:
                self.Immune = False
                self.Alpha = 255
                self.ImmuneCount = 0

    def BombIncrease(self):
        self.BombCount += 1

    def AmountLives(self):
        return self.Lives

    def Alive(self):
        if self.Dead == True:
            alive = False
        elif self.Dead == False:
            alive = True
        return alive
            
    def Draw(self):
        ImgCopy = self.Sprite[self.SpriteNumber[self.CurrentSprite]].copy()
        ImgCopy.fill((255, 255, 255, self.Alpha), None, pygame.BLEND_RGBA_MULT)
        game_screen.blit(ImgCopy, (self.PosX, self.PosY - 10))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     
class block(object):
    def __init__(self):
        self.Sprite = pygame.image.load("block.png")
        self.PosX = 0
        self.PosY = 0
        self.SizeX = 50
        self.SizeY = 50
        self.Active = False

    def Set(self, posX, posY, active):
        self.PosX = posX
        self.PosY = posY
        self.Active = active

    def Rect(self):
        return (self.PosX, self.PosY, self.SizeX, self.SizeY)
    
    def Draw(self):
        if self.Active == True:
            game_screen.blit(self.Sprite, (self.PosX, self.PosY))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class crate(block):
    def __init__(self):
        self.Sprite = pygame.image.load("crate.png")
        self.PosX = 0
        self.PosY = 0
        self.SizeX = 50
        self.SizeY = 50
        self.Active = False

    def Destroy(self):
        self.Active = False
        for x in range(1, 20):
            if PowerUp[x].Free() == False:
                PowerUp[x].Roll(self.PosX, self.PosY)
                break
        
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class powerup(object):
    def __init__(self):        
        self.Sprite = [None for y in range(5)]
        for x in range(1, 4):            
            self.Sprite[x] = pygame.image.load("power" + str(x) + ".png")
        self.CurrentSprite = 0
        self.PosX = 0
        self.PosY = 0
        self.SizeX = 50
        self.SizeY = 50
        self.Active = False

    def Roll(self, posx, posy):        
        self.PosX = posx
        self.PosY = posy
        rand = random.randint(1, 100)
        if rand >= 70:
            self.Active = True
            self.CurrentSprite = random.randint(1, 3)

    def Free(self):
        return self.Active

    def Set(self):
        self.Active = False

    def Rect(self):
        return (self.PosX, self.PosY, self.SizeX, self.SizeY, self.CurrentSprite)
    
    def Draw(self):
        if self.Active == True:
            game_screen.blit(self.Sprite[self.CurrentSprite], (self.PosX, self.PosY))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class explosion(object):
    def __init__(self):        
        self.Sprite = [[0 for x in range(7)] for y in range(20)]
        for x in range(1, 7):
            for y in range(1, 20):                
                self.Sprite[y][x] = pygame.image.load("beam" + str(x) + ".png")

        self.CurrentBeam = 1
        self.CurrentSprite = 1
        self.PosX = [0 for y in range(20)]
        self.PosY = [0 for y in range(20)]
        for x in range(1, 20):
            self.PosX[x] = 0
            self.PosY[x] = 0
        self.SizeX = 50
        self.SizeY = 50
        self.Length = 1
        self.Exploding = False
        self.Count = 0
        self.Time = 25
        self.Length = 0
        self.grid = [[0 for x in range(20)] for x in range(20)]
        self.GridX = 0
        self.GridY = 0
        self.Number = 0
        self.Alpha = 255

    def Free(self):
        return self.Exploding

    def Explode(self, GridX, GridY, length, team):
        if self.Exploding == False:
            self.Exploding = True
            self.Count = 0
            self.Length = length
            self.grid = copy.deepcopy(Grid[:])
            if team == 1:
                self.CurrentSprite = 1
            elif team == 2:
                self.CurrentSprite = 4
            
            for x in range(GridX, GridX + length, 1):
                if self.grid[x][GridY] == 10:
                    break
                elif self.grid[x][GridY] == 11 and Crate[x][GridY].Active == True:
                    Crate[x][GridY].Destroy()
                    self.grid[x][GridY] = self.CurrentSprite                    
                    break
                self.grid[x][GridY] = self.CurrentSprite
                Grid[x][GridY] = 13
            for x in range(GridX, GridX - length, -1):
                if self.grid[x][GridY] == 10:
                    break
                elif self.grid[x][GridY] == 11 and Crate[x][GridY].Active == True:
                    Crate[x][GridY].Destroy()
                    self.grid[x][GridY] = self.CurrentSprite
                    break
                self.grid[x][GridY] = self.CurrentSprite
                Grid[x][GridY] = 13

            for y in range(GridY, GridY + length, 1):
                if self.grid[GridX][y] == 10:
                    break
                elif self.grid[GridX][y] == 11 and Crate[GridX][y].Active == True:
                    Crate[GridX][y].Destroy()
                    self.grid[GridX][y] = self.CurrentSprite + 1                    
                    break
                self.grid[GridX][y] = self.CurrentSprite + 1
                Grid[GridX][y] = 13
            for y in range(GridY, GridY - length, -1):
                if self.grid[GridX][y] == 10:
                    break
                elif self.grid[GridX][y] == 11 and Crate[GridX][y].Active == True:
                    Crate[GridX][y].Destroy()
                    self.grid[GridX][y] = self.CurrentSprite + 1                    
                    break
                self.grid[GridX][y] = self.CurrentSprite + 1
                Grid[GridX][y] = 13

            self.grid[GridX][GridY] = self.CurrentSprite + 2

    def Update(self):
        if self.Exploding == True:
            self.Count += 1
            if self.Count > (self.Time - ((self.Time // 10) * 3)):
                self.Alpha -= 40
            if self.Count == self.Time:
                for x in range(15):                
                    for y in range(13):
                        if Grid[x][y] == 13:
                            Grid[x][y] = 0
                self.Count = 0
                self.Alpha = 255
                self.Exploding = False                

    def Rect(self):
        return (self.PosX, self.PosY, self.SizeX, self.SizeY)
    
    def Draw(self):
        if self.Exploding == True:            
            for x in range(15):                
                for y in range(13):
                    if self.grid[x][y] == 1 or self.grid[x][y] == 2 or self.grid[x][y] == 3:
                        ImgCopy = self.Sprite[self.CurrentBeam][self.grid[x][y]].copy()
                        ImgCopy.fill((255, 255, 255, self.Alpha), None, pygame.BLEND_RGBA_MULT)
                        game_screen.blit(ImgCopy, (x * 50, y * 50))
                        self.CurrentBeam += 1
                    elif self.grid[x][y] == 4 or self.grid[x][y] == 5 or self.grid[x][y] == 6:
                        ImgCopy = self.Sprite[self.CurrentBeam][self.grid[x][y]].copy()
                        ImgCopy.fill((255, 255, 255, self.Alpha), None, pygame.BLEND_RGBA_MULT)
                        game_screen.blit(ImgCopy, (x * 50, y * 50))
                        self.CurrentBeam += 1
                        
                    if self.CurrentBeam == 19:
                        self.CurrentBeam = 1
                    
        
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class bomb(object):
    def __init__(self):
        self.Sprite = [0 for x in range(3)]
        for x in range(1, 3):                
                self.Sprite[x] = pygame.image.load("bomb" + str(x) + ".png")
        self.CurrentSprite = 1
        self.PosX = 50
        self.PosY = 50
        self.SizeX = 50
        self.SizeY = 50
        self.set = False
        self.Timer = 0
        self.Limit = 60
        self.Length = 0
        self.ExplosionAudio = pygame.mixer.Sound("bombexplosion.wav")
        self.Sound = True

    def Audio(self):
        if self.Sound == True:
            self.Sound = False
        elif self.Sound == False:
            self.Sound = True

    def Update(self):
        if self.set == True:
            self.Timer += 1
            if self.Timer == self.Limit - (self.Limit // 10) and self.Sound == True:
                self.ExplosionAudio.play()
            if self.Timer >= self.Limit:                
                Grid[int(self.PosX / 50)][int(self.PosY / 50)] = 0
                self.Timer = 0
                self.set = False
                Player[self.CurrentSprite].BombIncrease()
                if self.CurrentSprite == 1:
                    for x in range(1, 40):
                        if Explosion[x].Free() == False:
                            Explosion[x].Explode(int(self.PosX / 50), int(self.PosY / 50), self.Length, self.CurrentSprite)
                            break
                elif self.CurrentSprite == 2:
                    for x in range(1, 40):
                        if Explosion[x].Free() == False:
                            Explosion[x].Explode(int(self.PosX / 50), int(self.PosY / 50), self.Length, self.CurrentSprite)
                            break
                            
    def Set(self, gridx, gridy, sprite, length):
        if self.set == False:
            self.set = True
            self.PosX = gridx * 50
            self.PosY = gridy * 50
            self.CurrentSprite = sprite
            self.Length = length

    def Activate(self):
        self.Timer = self.Limit

    def Rect(self):
        return (self.PosX, self.PosY, self.SizeX, self.SizeY)

    def Free(self):
        return self.set
    
    def Draw(self):
        if self.set == True:
            game_screen.blit(self.Sprite[self.CurrentSprite], (self.PosX, self.PosY))
        
# Initialise Classes
BackgroundImage = pygame.image.load("grass.png")
#----------------------------------------------------------------------
Player = [0 for x in range(3)]
for x in range(1, 3):
    Player[x] = player()
    Player[x].Set(x)
#----------------------------------------------------------------------
PowerUp = [0 for x in range(20)]
for x in range(1, 20):
    PowerUp[x] = powerup()
#----------------------------------------------------------------------
Bomb = [0 for x in range(20)]
for x in range(1, 20):
    Bomb[x] = bomb()
#----------------------------------------------------------------------
Explosion = [0 for x in range(40)]
for x in range(1, 40):
    Explosion[x] = explosion()
#----------------------------------------------------------------------
Block = [[0 for x in range(17)] for x in range(15)] 
for x in range(15):
    for y in range(13):
        Block[x][y] = block()

# Create Border    
for x in range(0, 15):
    for y in range(0, 13):
        if x == 0 or x == 14 or y == 0 or y == 12:
            Grid[x][y] = 10
# Create Middle Pillars
for x in range(0, 15, 2):
    for y in range(0, 13, 2):
        Grid[x][y] = 10

# Add blocks to grid
for x in range(15):
    for y in range(13):
        if Grid[x][y] == 10:
            Block[x][y].Set(x * 50, y * 50, True)
#----------------------------------------------------------------------
Crate = [[0 for x in range(17)] for x in range(15)]
for x in range(15):
    for y in range(13):
        Crate[x][y] = crate()
          
for x in range(3, 12):
    for y in range(1, 3):
        if Grid[x][y] != 10:
            Grid[x][y] = 11

for x in range(3, 12):
    for y in range(10, 12):
        if Grid[x][y] != 10:
            Grid[x][y] = 11

for x in range(1, 14):
    for y in range(3, 10):
        if Grid[x][y] != 10:
            Grid[x][y] = 11

# Add blocks to grid
for x in range(15):
    for y in range(13):
        if Grid[x][y] == 11:
            SpawnChance = random.randint(1, 10)
            if SpawnChance < 8:
                Crate[x][y].Set(x * 50, y * 50, True)                
#----------------------------------------------------------------------
pygame.mixer.music.play()
# Main Loop
while True:
    pygame.time.Clock().tick(60)
    # Handle-------------------------------------------------------------------------
    for x in range(1, 3):
        Player[x].Handle()
    # Update-------------------------------------------------------------------------
    for x in range(1, 3):
        Player[x].Update()
    for x in range(1, 40):
        Explosion[x].Update()
    for x in range(1, 20):
        Bomb[x].Update()
    # Draw -------------------------------------------------------------------------
    score_screen.fill((255, 255, 255))
    score_screen.blit(ScoreBoard, (0, 0))
    game_screen.fill((255, 255, 255))
    game_screen.blit(BackgroundImage, (50, 50))
    for x in range(15):
        for y in range(13):
            Crate[x][y].Draw()
    for x in range(1, 20):
        Bomb[x].Draw()
    for x in range(1, 40):
        Explosion[x].Draw()
    for x in range(1, 20):
        PowerUp[x].Draw()
    if Player[1].Alive() == True and Player[2].Alive() == True:
        for x in range(15):
            for y in range(13):
                Block[x][y].Draw()
    for x in range(1, 3):
        Player[x].Draw()
    if Player[1].Alive() == False or Player[2].Alive() == False:
        for x in range(15):
            for y in range(13):
                Block[x][y].Draw()

    score_screen.blit(myfont.render(str(Player[1].AmountLives()), True, (255,255,255)), (101, 137))
    score_screen.blit(myfont.render(str(Player[2].AmountLives()), True, (255,255,255)), (101, 248))
    score_screen.blit(ScoreMusic, (10, 569))
    score_screen.blit(ScoreFX, (75, 569))
    score_screen.blit(ScoreQuit, (10, 610))
    display_surf.blit(score_screen, (0, 0))
    display_surf.blit(game_screen, (140, 0))
    pygame.display.update()

