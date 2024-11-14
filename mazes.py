from pyamaze import maze
import pygame, sys, time, random
import numpy as np

# Difficulty/Changing the Size of the Maze
# mazesize = 10
mazesize = 20
# mazesize = 30
# mazesize = 50


'''Maze Creation'''
# Create random Maze with multiple paths
m = maze(mazesize, mazesize)
m.CreateMaze(loopPercent=30)
mazecoord = m.maze_map
mazearray = np.full(((mazesize*2) + 1, (mazesize*2) + 1), 0)
# m.run()

# Maze Matrix Creation
mazerow = 1
mazecol = 1
for xy, nsew in mazecoord.items():
    if mazerow == mazesize + 1:
        mazerow = 1
        mazecol += 1

    if xy[0] == mazerow and xy[1] == mazecol:
        for dir, bin in nsew.items():

            if dir == 'E' and bin == 0:
                mazearray[xy[0] + mazerow - 2, xy[1] + mazecol] = 1
                mazearray[xy[0] + mazerow - 1, xy[1] + mazecol] = 1
                mazearray[xy[0] + mazerow, xy[1] + mazecol] = 1
            

            if dir == 'W' and bin == 0:
                mazearray[xy[0] + mazerow - 2, xy[1] + mazecol - 2] = 1
                mazearray[xy[0] + mazerow - 1, xy[1] + mazecol - 2] = 1
                mazearray[xy[0] + mazerow, xy[1] + mazecol - 2] = 1

            if dir == 'N' and bin == 0:
                mazearray[xy[0] + mazerow - 2, xy[1] + mazecol - 2] = 1
                mazearray[xy[0] + mazerow - 2, xy[1] + mazecol - 1] = 1
                mazearray[xy[0] + mazerow - 2, xy[1] + mazecol] = 1

            if dir == 'S' and bin == 0:
                mazearray[xy[0] + mazerow, xy[1] + mazecol - 2] = 1
                mazearray[xy[0] + mazerow, xy[1] + mazecol - 1] = 1
                mazearray[xy[0] + mazerow, xy[1] + mazecol] = 1

        mazerow += 1

rowAC = mazearray.shape[0]
colAC = mazearray.shape[1]
# np.savetxt('BinaryMaze.csv', mazearray, delimiter=',', fmt='%d')


'''Path Finding'''



'''Game Creation'''
# Adjust size of image and border around maze
border = 30
frameSizeX = 800
frameSizeY = 800

# Checks for errors encountered
check_errors = pygame.init()
if check_errors[1] > 0:
    print(f'[!] Had {check_errors[1]} errors when initialising game, exiting...')
    sys.exit(-1)
else:
    print('[+] Game successfully initialised')

pygame.display.set_caption('Maze Game')
game_window = pygame.display.set_mode((frameSizeX, frameSizeY))


# Colors
black = pygame.Color(0,0,0)
white = pygame.Color(255, 255, 255)
red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)

# Maze Drawing and Wall Creation 
wallSize = min((frameSizeX - border*2) // colAC, (frameSizeY - border*2) // rowAC)
class mazewall(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill((white))
        self.rect = self.image.get_rect(topleft=(x, y))

WALLS = pygame.sprite.Group()
for row in range(rowAC):
    for col in range(colAC):
        if mazearray[row][col] == 1:
            WALLS.add(mazewall((col*wallSize) + border, (row*wallSize) + border, wallSize))

# Player and Wall Collision
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill(red)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.moveAmount = size
        self.moves = 0

    def move(self, direction):
        # Track original position
        original_position = self.rect.topleft

        # Move the player
        if direction == 'left':
            self.rect.x -= self.moveAmount
        elif direction == 'right':
            self.rect.x += self.moveAmount
        elif direction == 'up':
            self.rect.y -= self.moveAmount
        elif direction == 'down':
            self.rect.y += self.moveAmount

        # Check for collisions with walls
        wall_collisions = pygame.sprite.spritecollide(self, WALLS, False)
        if wall_collisions:
            # If collision, reset to original position
            self.rect.topleft = original_position
        else:
            self.moves += 1

player = Player(border + wallSize, border + wallSize, wallSize)
goal = [border + wallSize*(rowAC - 2), border + wallSize*(colAC - 2)]
all_sprites = pygame.sprite.Group(player)
clock = pygame.time.Clock()

# Count of Moves Made
def MoveCount(choice, color, font, size):
    score_font = pygame.font.SysFont(font, size)
    score_surface = score_font.render('Move Count : ' + str(player.moves), True, color)
    score_rect = score_surface.get_rect()
    if choice == 1:
        score_rect.midtop = (frameSizeX/2, 5)
    else:
        score_rect.midtop = (frameSizeX/2, 100)
    game_window.blit(score_surface, score_rect)

''' UPDATE ONCE A* ALORITHEM IS DONE'''
# Game Over Screen 
def gameoverScreen():
    my_font = pygame.font.SysFont('consolas', 90)
    game_over_surface = my_font.render('Maze Complete', True, white)
    game_over_rect = game_over_surface.get_rect()
    game_over_rect.midtop = (frameSizeX/2, frameSizeY/4)
    game_window.fill(black)
    game_window.blit(game_over_surface, game_over_rect)

    # if MoveCount > AStarMove:
    #     color = green
    # elif MoveCount <= AStarMove:
    #     color = red

    MoveCount(0, red, 'times', 20)

    pygame.display.flip()



'''Game Loop'''
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif event.key == pygame.K_LEFT:
                player.move('left')
            elif event.key == pygame.K_RIGHT:
                player.move('right')
            elif event.key == pygame.K_UP:
                player.move('up')
            elif event.key == pygame.K_DOWN:
                player.move('down')

    
    game_window.fill((black))
    WALLS.draw(game_window)
    all_sprites.draw(game_window)

    # End Point
    pygame.draw.rect(game_window, green, (goal[0], goal[1], wallSize, wallSize))

    # Game Over
    if player.rect.x == goal[0] and player.rect.y == goal[1]:
        gameoverScreen()

    # for p in path:
    #     a, b = p   
    #     if 0 <= a < rowAC and 0 <= b < colAC:         
    #         pygame.draw.rect(game_window, green, (a * wallSize + border, b * wallSize + border, wallSize/2, wallSize/2))

    MoveCount(1, white, 'consolas', 20)
    pygame.display.flip()
    clock.tick(60)


