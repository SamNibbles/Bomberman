import pygame, sys, copy, random
from pygame.locals import *

# Initialise Display
pygame.init()
display_surf = pygame.display.set_mode((890, 650), pygame.DOUBLEBUF)
game_screen = pygame.Surface((750, 650), pygame.SRCALPHA, 32)
score_screen = pygame.Surface((140, 650))
title_screen = pygame.Surface((890, 650))
pygame.display.set_caption("Platformer")

# Initialise Joystick
Joy = [None for x in range(2)]
pygame.joystick.init()

# Load Music
pygame.mixer.music.load("backgroundmusic.wav")

# Initialise Variables
myfont = pygame.font.SysFont('Arial', 14)
mytitlefont = pygame.font.SysFont('Eras Bold ITC', 100)
mycontrollerfont = pygame.font.SysFont('Eras Bold ITC', 50)
TitleMain = [0 for x in range(7)]
for x in range(1, 7):
    TitleMain[x] = pygame.image.load("title" + str(x) + ".png")
CurrentScreen = 1
ScoreBoard = pygame.image.load("scoreboard.png")
ScoreMusic = pygame.image.load("scoremusic.png")
ScoreFX = pygame.image.load("scorefx.png")
ScoreQuit = pygame.image.load("scorequit.png")
PausedMenu = pygame.image.load("paused.png")
Title = True
Paused = False
KeyPressed = False
FX = True
PlayerAmount = 0
PlayersAlive = 0
GameFinish = False
EndCount = 0
EndCountX = 0
EndCountY = 0
WinningPlayer = 0
ControllerText = ""
ControllerTextCount = 0

LevelFile = None
Grid = [[0 for x in range(20)] for x in range(20)]
PrevGrid = Grid[:]
MouseGridPosX = 0
MouseGridPosY = 0

class player(object):
    def __init__(self):
        self.Sprite = [None for x in range(17)]
        # Initialise Variables
        for x in range(1, 17):
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
        self.Joy = False
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
        self.BombCount = 1
        self.Music = True
        self.FX = True
        self.HitAudio = pygame.mixer.Sound("ow.wav")
        self.PowerAudio = pygame.mixer.Sound("beep.wav")
        self.FontX = 101
        self.FontY = 0

    def Set(self, player):
        self.CurrentPlayer = player
        if self.CurrentPlayer == 1:
            self.FontY = 137
            self.PosX = 50
            self.PosY = 50
            self.KeyUp = K_w
            self.KeyDown = K_s
            self.KeyLeft = K_a
            self.KeyRight = K_d
            self.KeyBomb = K_TAB
            self.SpriteNumber = [0, 1, 2, 3, 4]
        elif self.CurrentPlayer == 2:
            self.FontY = 248
            self.PosX = 650
            self.PosY = 550
            self.KeyUp = K_UP
            self.KeyDown = K_DOWN
            self.KeyLeft = K_LEFT
            self.KeyRight = K_RIGHT
            self.KeyBomb = K_RCTRL
            self.SpriteNumber = [0, 5, 6, 7, 8]
        elif self.CurrentPlayer == 3:
            self.FontY = 359
            self.Joy = True
            self.PosX = 50
            self.PosY = 550
            self.SpriteNumber = [0, 9, 10, 11, 12]
        elif self.CurrentPlayer == 4:
            self.FontY = 470
            self.Joy = True
            self.PosX = 650
            self.PosY = 50
            self.SpriteNumber = [0, 13, 14, 15, 16]
        
    def Handle(self):
        global Paused, KeyPressed
        if self.Dead == False:
            self.Direct = 0
            # Joy Stick
            if self.Joy == True:
                if abs(Joy[self.CurrentPlayer - 3].get_axis(0)) > abs(Joy[self.CurrentPlayer - 3].get_axis(1)):
                    
                    if Joy[self.CurrentPlayer - 3].get_axis(0) > 0.25:
                        self.Direct = 2
                        self.CurrentSprite = 2
                    elif Joy[self.CurrentPlayer - 3].get_axis(0) < -0.25:
                        self.Direct = 4
                        self.CurrentSprite = 4
                        
                if abs(Joy[self.CurrentPlayer - 3].get_axis(0)) < abs(Joy[self.CurrentPlayer - 3].get_axis(1)):
                    
                    if Joy[self.CurrentPlayer - 3].get_axis(1) > 0.25:
                        self.Direct = 3
                        self.CurrentSprite = 3
                    elif Joy[self.CurrentPlayer - 3].get_axis(1) < -0.25:
                        self.Direct = 1
                        self.CurrentSprite = 1

                if Joy[self.CurrentPlayer - 3].get_button(0) == True:
                    for x in range(1, 20):
                        if Bomb[x].Free() == True and self.BombCount > 0:
                            if Grid[int((self.PosX + (self.SizeX / 2)) // 50)][int((self.PosY + (self.SizeX / 2)) // 50)] != "D":
                                self.BombCount -= 1
                                Bomb[x].Set((self.PosX + (self.SizeX / 2)) // 50, (self.PosY + (self.SizeX / 2)) // 50, self.CurrentPlayer, self.BombLength)
                                Grid[int((self.PosX + (self.SizeX / 2)) // 50)][int((self.PosY + (self.SizeX / 2)) // 50)] = "D"
                                break
            # Keyboard Inputs
            if self.Joy == False:
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
                        if Bomb[x].Free() == True and self.BombCount > 0:                    
                            if Grid[int((self.PosX + (self.SizeX / 2)) // 50)][int((self.PosY + (self.SizeX / 2)) // 50)] != "D":
                                self.BombCount -= 1
                                Bomb[x].Set((self.PosX + (self.SizeX / 2)) // 50, (self.PosY + (self.SizeX / 2)) // 50, self.CurrentPlayer, self.BombLength)
                                Grid[int((self.PosX + (self.SizeX / 2)) // 50)][int((self.PosY + (self.SizeX / 2)) // 50)] = "D"
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
                                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p and KeyPressed == False:
                        Paused = True
                        KeyPressed = True
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_p:
                        KeyPressed = False
                

    def Update(self):
        if self.Dead == False:
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
                    if Grid[x][y] == "B":
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
                                        
                                        
            # Alligning the play to fit inbetween the blocks
            # Alligning from the east
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
            # Alligning from the west  
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
            # Alligning from the south           
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
            # Alligning from the north      
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
                    # Checking from playing collisions with crates
                    if Grid[x][y] == "C" and Crate[x][y].Active() == True:
                        self.PosX, self.PosY = HandleCollision(self.PosX, self.PrevPosX, self.PosY, self.PrevPosY, self.SizeX, self.SizeY, BPX, BPY, BSX, BSY)

                    BPX, BPY, BSX, BSY = x * 50, y * 50, 50 , 50
                    # Checking from playing collisions with bombs
                    if Grid[x][y] == "D":
                        self.PosX, self.PosY = HandleCollision(self.PosX, self.PrevPosX, self.PosY, self.PrevPosY, self.SizeX, self.SizeY, BPX, BPY, BSX, BSY)      

    #-----------------------------------------------------------------------------------------------------------

            # Checking for player collision with a powerup
            for x in range(1, 20):
                if PowerUp[x].Free() == True:
                    BPX, BPY, BSX, BSY, PN = PowerUp[x].Rect()
                    if Grid[int((BPX + (BSX / 2)) // 50)][int((BPY + (BSY / 2)) // 50)] == "E":
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

            # Check for bomb chain reaction
            for x in range(1, 20):
                if Bomb[x].Free() == False:
                    BPX, BPY, BSX, BSY = Bomb[x].Rect()
                    if Grid[int((BPX + (BSX / 2)) // 50)][int((BPY + (BSY / 2)) // 50)] == "E":
                        Bomb[x].Activate()

    #------------------------------------------------------------------------------------------------------------------------

            # Check for collisions between the player and explosions
            if self.Immune == False:
                for x in range(15):
                    for y in range(13):
                        if Grid[int((self.PosX + (self.SizeX / 2)) // 50)][int((self.PosY + (self.SizeX / 2)) // 50)] == "E" and self.Immune == False:
                            self.Immune = True
                            if self.FX == True:
                                self.HitAudio.play()
                            self.Lives -= 1
                            
            if self.Lives == 0:
                self.Dead = True
                            
            # Check for invinciblity frames and adjust player flashing accordingly
            if self.Immune == True:
                self.ImmuneCount += 1
                if self.ImmuneCount < 20 or (self.ImmuneCount > 40 and self.ImmuneCount < 60):
                    self.Alpha -= 10
                elif (self.ImmuneCount > 20 and self.ImmuneCount < 40) or self.ImmuneCount > 60:
                    self.Alpha += 10

                # Cap alpha value between 0 and 255 to account for errors
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
        return self.Lives, self.FontX, self.FontY

    def Alive(self):
        if self.Dead == True:
            alive = False
        elif self.Dead == False:
            alive = True
        return alive
            
    def Draw(self):
        if self.Dead == False:
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
        self.Alive = False

    def Set(self, posX, posY, active):
        self.PosX = posX
        self.PosY = posY
        self.Alive = active

    def Rect(self):
        return (self.PosX, self.PosY, self.SizeX, self.SizeY)

    def Active(self):
        return self.Alive
    
    def Draw(self):
        if self.Alive == True:
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
        self.Alive = False

    def Destroy(self):
        self.Alive = False
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
        self.Spritetest = [[None for y in range(19)] for x in range(5)]
        for x in range(1, 4):
            if x != 1:
                self.Sprite[x] = pygame.image.load("power" + str(x) + ".png")
            if x == 1:
                for y in range(1, 19):
                    self.Spritetest[x][y] = pygame.image.load("power" + str(x) + "_" + str(y) + ".png")
        self.CurrentSprite = 1
        self.CurrentAnimation = 1
        self.AnimationCount = 0
        self.PosX = 0
        self.PosY = 0
        self.SizeX = 50
        self.SizeY = 50
        self.Active = False

    def Update(self):
        self.AnimationCount += 1
        if self.AnimationCount == 2:
            self.CurrentAnimation += 1
            self.AnimationCount = 0
            if self.CurrentAnimation == 19:
                self.CurrentAnimation = 1
                

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
            if self.CurrentSprite == 1:
                game_screen.blit(self.Spritetest[self.CurrentSprite][self.CurrentAnimation], (self.PosX, self.PosY))
            else:
                game_screen.blit(self.Sprite[self.CurrentSprite], (self.PosX, self.PosY))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class explosion(object):
    def __init__(self):        
        self.Sprite = [[0 for x in range(37)] for y in range(20)]
        for x in range(1, 37):
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
        if self.Exploding == True:
            free = False
        elif self.Exploding == False:
            free = True
        return free

    def Reset(self):
        self.Count = 0
        self.Alpha = 255
        self.Exploding = False   
        

    def Explode(self, GridX, GridY, length, team):
        if self.Exploding == False:
            self.Exploding = True
            self.Count = 0
            self.Length = length
            self.grid = copy.deepcopy(Grid[:])
            self.CurrentSprite = team
            
            for x in range(GridX, GridX + length, 1):
                if self.grid[x][GridY] == "B":
                    self.grid[x - 1][GridY] = 8
                    break
                elif self.grid[x][GridY] == "C" and Crate[x][GridY].Active() == True:
                    Crate[x][GridY].Destroy()
                    self.grid[x][GridY] = 8
                    break
                if x == (GridX + length - 1):
                    self.grid[x][GridY] = 8
                else:
                    self.grid[x][GridY] = 3
                Grid[x][GridY] = "E"
            for x in range(GridX, GridX - length, -1):
                if self.grid[x][GridY] == "B":
                    self.grid[x + 1][GridY] = 6
                    break
                elif self.grid[x][GridY] == "C" and Crate[x][GridY].Active() == True:
                    Crate[x][GridY].Destroy()
                    self.grid[x][GridY] = 6
                    break
                if x == (GridX - length + 1):
                    self.grid[x][GridY] = 6
                else:
                    self.grid[x][GridY] = 1
                Grid[x][GridY] = "E"

            for y in range(GridY, GridY + length, 1):
                if self.grid[GridX][y] == "B":
                    self.grid[GridX][y - 1] = 9
                    break
                elif self.grid[GridX][y] == "C" and Crate[GridX][y].Active() == True:
                    Crate[GridX][y].Destroy()
                    self.grid[GridX][y] = 9
                    break
                if y == (GridY + length - 1):
                    self.grid[GridX][y] = 9
                else:
                    self.grid[GridX][y] = 4
                Grid[GridX][y] = "E"
            for y in range(GridY, GridY - length, -1):
                if self.grid[GridX][y] == "B":
                    self.grid[GridX][y + 1] = 7
                    break
                elif self.grid[GridX][y] == "C" and Crate[GridX][y].Active() == True:
                    Crate[GridX][y].Destroy()
                    self.grid[GridX][y] = 7
                    break
                if y == (GridY - length + 1):
                    self.grid[GridX][y] = 7
                else:
                    self.grid[GridX][y] = 2
                Grid[GridX][y] = "E"

            self.grid[GridX][GridY] = 5

    def Update(self):
        if self.Exploding == True:
            self.Count += 1
            if self.Count > (self.Time - ((self.Time // 10) * 3)):
                self.Alpha -= 40
            if self.Count == self.Time:
                for x in range(15):                
                    for y in range(13):
                        if Grid[x][y] == "E":
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
                    if self.CurrentSprite == 1:
                        if self.grid[x][y] == 1 or self.grid[x][y] == 2 or self.grid[x][y] == 3 or self.grid[x][y] == 4 or self.grid[x][y] == 5 or self.grid[x][y] == 6 or self.grid[x][y] == 7  or self.grid[x][y] == 8 or self.grid[x][y] == 9:
                            ImgCopy = self.Sprite[self.CurrentBeam][self.grid[x][y]].copy()
                            ImgCopy.fill((255, 255, 255, self.Alpha), None, pygame.BLEND_RGBA_MULT)
                            game_screen.blit(ImgCopy, (x * 50, y * 50))
                            self.CurrentBeam += 1
                    elif self.CurrentSprite == 2:
                        if self.grid[x][y] == 1 or self.grid[x][y] == 2 or self.grid[x][y] == 3 or self.grid[x][y] == 4 or self.grid[x][y] == 5 or self.grid[x][y] == 6 or self.grid[x][y] == 7  or self.grid[x][y] == 8 or self.grid[x][y] == 9:
                            ImgCopy = self.Sprite[self.CurrentBeam][self.grid[x][y] + 9].copy()
                            ImgCopy.fill((255, 255, 255, self.Alpha), None, pygame.BLEND_RGBA_MULT)
                            game_screen.blit(ImgCopy, (x * 50, y * 50))
                            self.CurrentBeam += 1
                    elif self.CurrentSprite == 3:
                        if self.grid[x][y] == 1 or self.grid[x][y] == 2 or self.grid[x][y] == 3 or self.grid[x][y] == 4 or self.grid[x][y] == 5 or self.grid[x][y] == 6 or self.grid[x][y] == 7  or self.grid[x][y] == 8 or self.grid[x][y] == 9:
                            ImgCopy = self.Sprite[self.CurrentBeam][self.grid[x][y] + 18].copy()
                            ImgCopy.fill((255, 255, 255, self.Alpha), None, pygame.BLEND_RGBA_MULT)
                            game_screen.blit(ImgCopy, (x * 50, y * 50))
                            self.CurrentBeam += 1
                    elif self.CurrentSprite == 4:
                        if self.grid[x][y] == 1 or self.grid[x][y] == 2 or self.grid[x][y] == 3 or self.grid[x][y] == 4 or self.grid[x][y] == 5 or self.grid[x][y] == 6 or self.grid[x][y] == 7  or self.grid[x][y] == 8 or self.grid[x][y] == 9:
                            ImgCopy = self.Sprite[self.CurrentBeam][self.grid[x][y] + 27].copy()
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
        self.Sprite = [0 for x in range(5)]
        for x in range(1, 5):                
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
                for x in range(1, 40):
                    if Explosion[x].Free() == True:
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
        if self.set == True:
            free = False
        elif self.set == False:
            free = True
        return free

    def Reset(self):
        self.Timer = 0
        self.set = False
    
    def Draw(self):
        if self.set == True:
            game_screen.blit(self.Sprite[self.CurrentSprite], (self.PosX, self.PosY))

#----------------------------------------------------------------------------------------------

def HandleCollision(PosX, PrevPosX, PosY, PrevPosY, SizeX, SizeY, BPX, BPY, BSX, BSY):
    # Check if the player intersects with the block
    if PosX < BPX + BSX and PosX + SizeX > BPX:
        if PosY < BPY + BSY and PosY + SizeY > BPY:
            # SIDES
            if PrevPosX + SizeX <= BPX:
                # Collision from left to right
                if PosX + SizeX >= BPX and PosX <= BPX:
                    PosX = BPX - SizeX
            if PrevPosX >= BPX + BSX:
                # Collision from right to left
                if PosX <= BPX + BSX and PosX + SizeX >= BPX + BSX:
                    PosX = BPX + BSX
            # TOPOM        
            if PrevPosY + SizeY <= BPY:
                # Collision from above
                if PosY + SizeY >= BPY and PosY <= BPY:
                    PosY = BPY - SizeY
            if PrevPosY >= BPY + BSY:
                # Collision from below
                if PosY <= BPY + BSY and PosY + SizeY >= BPY + BSY:
                    PosY = BPY + BSY

    return PosX, PosY

#----------------------------------------------------------------------------------------------

def PauseScreen():
    global Paused, KeyPressed, Title, CurrentScreen
    while Paused == True:
        game_screen.blit(PausedMenu, (200, 200))
        display_surf.blit(game_screen, (140, 0))
        pygame.display.update()

        mouseposx, mouseposy = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_p:
                    KeyPressed = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p and KeyPressed == False:
                    Paused = False
                    KeyPressed = True

            if event.type == MOUSEBUTTONDOWN:
                # Check for the choice - RESUME
                if mouseposx > 370 and mouseposx < 500:
                    if mouseposy > 294 and mouseposy < 344:
                        Paused = False
                        KeyPressed = False
                # Check for the choice - QUIT
                if mouseposx > 530 and mouseposx < 660:
                    if mouseposy > 294 and mouseposy < 344:
                        pygame.quit()
                        sys.exit()
                # Check for the choice - MAIN MENU
                if mouseposx > 370 and mouseposx < 660:
                    if mouseposy > 371 and mouseposy < 421:
                        Title = True
                        Paused = False
                        CurrentScreen = 1
                        ClassReset()
            elif event.type == QUIT:
                pygame.quit()
                sys.exit()

#----------------------------------------------------------------------------------------------

def TitleScreen():
    global Title, CurrentScreen, PlayerAmount, ControllerText, ControllerTextCount
    
    mouseposx, mouseposy = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0] == True:
                if CurrentScreen == 1:
                    # Check for the choice - PLAY
                    if mouseposx > 300 and mouseposx < 590:
                        if mouseposy > 280 and mouseposy < 330:
                            CurrentScreen = 5
                    # Check for the choice - HOW TO PLAY
                    if mouseposx > 300 and mouseposx < 590:
                        if mouseposy > 355 and mouseposy < 405:
                            CurrentScreen = 2
                    # Check for the choice - CONTROLS
                    if mouseposx > 300 and mouseposx < 590:
                        if mouseposy > 430 and mouseposy < 480:
                            CurrentScreen = 3
                    # Check for the choice - HIGHSCORES
                    if mouseposx > 300 and mouseposx < 590:
                        if mouseposy > 505 and mouseposy < 555:
                            CurrentScreen = 4
                elif CurrentScreen == 2 or CurrentScreen == 3 or CurrentScreen == 4:
                    if mouseposx > 31 and mouseposx < 103:
                        if mouseposy > 32 and mouseposy < 68:
                            CurrentScreen = 1
                elif CurrentScreen == 5:
                    # Check for the choice - 2 Player
                    if mouseposx > 300 and mouseposx < 590:
                        if mouseposy > 280 and mouseposy < 330:
                            CurrentScreen = 6
                            PlayerAmount = 2
                    # Check for the choice - 3 Player
                    if mouseposx > 300 and mouseposx < 590:
                        if mouseposy > 355 and mouseposy < 405:
                            if pygame.joystick.get_count() == 1 or pygame.joystick.get_count() == 2:
                                for x in range(pygame.joystick.get_count()):
                                    Joy[x] = pygame.joystick.Joystick(x)
                                    Joy[x].init()
                                CurrentScreen = 6
                                PlayerAmount = 3
                            elif pygame.joystick.get_count() == 0:
                                ControllerText = "Please plug in a controller!"
                                ControllerTextCount = 0
                            
                    # Check for the choice - 4 Player
                    if mouseposx > 300 and mouseposx < 590:
                        if mouseposy > 430 and mouseposy < 480:
                            if pygame.joystick.get_count() == 2:
                                for x in range(pygame.joystick.get_count()):
                                    Joy[x] = pygame.joystick.Joystick(x)
                                    Joy[x].init()
                                CurrentScreen = 6
                                PlayerAmount = 4
                            elif pygame.joystick.get_count() == 1:
                                ControllerText = "Please plug in a controller!"
                                ControllerTextCount = 0
                            elif pygame.joystick.get_count() == 0:
                                ControllerText = "Please plug in 2 controllers!"
                                ControllerTextCount = 0
                            
                elif CurrentScreen == 6:
                    # Check for the choice - Level 1
                    if mouseposx > 300 and mouseposx < 590:
                        if mouseposy > 280 and mouseposy < 330:
                            CreateLevel(1)
                            Title = False
                    # Check for the choice - Level 2
                    if mouseposx > 300 and mouseposx < 590:
                        if mouseposy > 355 and mouseposy < 405:
                            CreateLevel(2)
                            Title = False
                    # Check for the choice - Level 3
                    if mouseposx > 300 and mouseposx < 590:
                        if mouseposy > 430 and mouseposy < 480:
                            CreateLevel(3)
                            Title = False
                    # Check for the choice - Level 4
                    if mouseposx > 300 and mouseposx < 590:
                        if mouseposy > 505 and mouseposy < 555:
                            CreateLevel(4)
                            Title = False
                        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                CurrentScreen = 1
                ControllerText = ""
                ControllerTextCount = 0
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    if ControllerText != "":
        ControllerTextCount += 1
        if ControllerTextCount == 80:
            ControllerText = ""
            ControllerTextCount = 0

    title_screen.fill((255, 255, 255))
    title_screen.blit(TitleMain[CurrentScreen], (0, 0))
    title_screen.blit(mycontrollerfont.render(ControllerText, 1, (255,255,255)), (215, 540))
    display_surf.blit(title_screen, (0, 0))
    pygame.display.update()
                    
#----------------------------------------------------------------------------------------------

def CreateLevel(level):
    global PlayerAmount
    LevelFile = open("level" + str(level) + ".txt", "r")
    for y in range(14):
        for x in range(16):
            Grid[x][y] = LevelFile.read(1)
            
    LevelFile.close()

    for x in range(1, PlayerAmount + 1):
        Player[x] = player()
        Player[x].Set(x)

    # Add blocks to grid
    for x in range(15):
        for y in range(13):
            if Grid[x][y] == "B":
                Block[x][y].Set(x * 50, y * 50, True)

    for x in range(3, 12):
        for y in range(1, 3):
            if Grid[x][y] != "B":
                Grid[x][y] = "C"

    for x in range(3, 12):
        for y in range(10, 12):
            if Grid[x][y] != "B":
                Grid[x][y] = "C"

    for x in range(1, 14):
        for y in range(3, 10):
            if Grid[x][y] != "B":
                Grid[x][y] = "C"

    # Add blocks to grid
    for x in range(15):
        for y in range(13):
            if Grid[x][y] == "C":
                SpawnChance = random.randint(1, 10)
                if SpawnChance < 8:
                    Crate[x][y].Set(x * 50, y * 50, True)

#----------------------------------------------------------------------------------------------

def EndGame():
    global Title, CurrentScreen, GameFinish, EndCount, EndCountX, EndCountY
    if GameFinish == True:
        EndCount += 1
        if EndCount == 1:
            Block[EndCountX][EndCountY].Set(EndCountX * 50, EndCountY * 50, True)
            EndCount = 0
            EndCountX += 1
            if EndCountX == 14:
                EndCountX = 1
                EndCountY += 1
                if EndCountY == 13:
                    Title = True
                    EndCount = 0
                    EndCountX = 0
                    EndCountY = 0
                    GameFinish = False
                    CurrentScreen = 1
                    ClassReset()

#----------------------------------------------------------------------------------------------

def ClassReset():
    for x in range(15):
        for y in range(13):
            Block[x][y].Set(0, 0, False)

    for x in range(1, 20):
        if PowerUp[x].Free() == True:
            PowerUp[x].Set()

    for x in range(1, 40):
        if Explosion[x].Free() == False:
            Explosion[x].Reset()

    for x in range(1, 20):
        if Bomb[x].Free() == False:
            Bomb[x].Reset()

        
# Initialise Classes
BackgroundImage = pygame.image.load("grass.png")
#----------------------------------------------------------------------
Player = [0 for x in range(5)]
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
#----------------------------------------------------------------------
Crate = [[0 for x in range(17)] for x in range(15)]
for x in range(15):
    for y in range(13):
        Crate[x][y] = crate()            
#----------------------------------------------------------------------
pygame.mixer.music.play()
# Main Loop
while Title == True:
    TitleScreen()
    while Title == False:
        pygame.time.Clock().tick(60)
        if GameFinish == False:
            PauseScreen()
            
            # Handle-------------------------------------------------------------------------
            for x in range(1, PlayerAmount + 1):
                Player[x].Handle()
                
            # Update-------------------------------------------------------------------------
            for x in range(1, PlayerAmount + 1):
                Player[x].Update()
            for x in range(1, 40):
                Explosion[x].Update()
            for x in range(1, 20):
                if PowerUp[x].Free() == True:
                    PowerUp[x].Update()
            for x in range(1, 20):
                Bomb[x].Update()

            # Check how many players are alive
            PlayersAlive = 0
            WinningPlayer = 0
            for x in range(1, PlayerAmount + 1):
                if Player[x].Alive() == True:
                    PlayersAlive += 1
                    WinningPlayer = x

            if PlayersAlive == 1:
                GameFinish = True
        
        # Draw -------------------------------------------------------------------------
        # Clear the screen to the specified colour
        score_screen.fill((255, 255, 255))
        score_screen.blit(ScoreBoard, (0, 0))
        game_screen.fill((255, 255, 255))
        game_screen.blit(BackgroundImage, (50, 50))
        
        for x in range(15):
            for y in range(13):
                Crate[x][y].Draw()        
        for x in range(1, 20):
            Bomb[x].Draw()
        if GameFinish == False:
            for x in range(15):
                for y in range(13):
                    Block[x][y].Draw()
        for x in range(1, 40):
            Explosion[x].Draw()
        for x in range(1, 20):
            PowerUp[x].Draw()
        for x in range(1, PlayerAmount + 1):
            Player[x].Draw()
        if GameFinish == True:
            for x in range(15):
                for y in range(13):
                    Block[x][y].Draw()

            
        # Draw Players Lives
        for x in range(1, PlayerAmount + 1):
            text, fontx, fonty = Player[x].AmountLives()
            score_screen.blit(myfont.render(str(text), 1, (255,255,255)), (fontx, fonty))
        score_screen.blit(ScoreMusic, (10, 569))
        score_screen.blit(ScoreFX, (75, 569))
        score_screen.blit(ScoreQuit, (10, 610))
        if GameFinish == True:
            game_screen.blit(mytitlefont.render("Player " + str(WinningPlayer) + " wins!", 1, (255,255,255)), (140, 245))
        display_surf.blit(score_screen, (0, 0))
        display_surf.blit(game_screen, (140, 0))
        pygame.display.update()
        
        # End the game
        EndGame()




        

