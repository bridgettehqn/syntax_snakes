from pyamaze import maze
import pygame, sys, time, random
import numpy as np
from heapq import *


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


'''Path Finding Adjusted From https://code.activestate.com/recipes/578919-python-a-pathfinding-with-binary-heap/'''
def heuristic(a, b):
    return (b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2

def astar(array, start, goal):

    # Adjusted to only move left, right, up, and down
    neighbors = [(0,1),(0,-1),(1,0),(-1,0)]

    close_set = set()
    came_from = {}
    gscore = {start:0}
    fscore = {start:heuristic(start, goal)}
    oheap = []

    heappush(oheap, (fscore[start], start))
    
    while oheap:

        current = heappop(oheap)[1]

        if current == goal:
            data = []
            while current in came_from:
                data.append(current)
                current = came_from[current]
            return data

        close_set.add(current)
        for i, j in neighbors:
            neighbor = current[0] + i, current[1] + j            
            tentative_g_score = gscore[current] + heuristic(current, neighbor)
            if 0 <= neighbor[0] < array.shape[0]:
                if 0 <= neighbor[1] < array.shape[1]:                
                    if array[neighbor[0]][neighbor[1]] == 1:
                        continue
                else:
                    # array bound y walls
                    continue
            else:
                # array bound x walls
                continue
                
            if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0):
                continue
                
            if  tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [i[1]for i in oheap]:
                came_from[neighbor] = current
                gscore[neighbor] = tentative_g_score
                fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heappush(oheap, (fscore[neighbor], neighbor))
                
    return False

start = (1, 1)  
end = (rowAC - 2, colAC - 2) 
path = astar(mazearray, start, end)
AStarMoves = len(path)

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
        self.locations = []

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
            self.locations.append(self.rect.topleft)


player = Player(border + wallSize, border + wallSize, wallSize)
goal = [border + wallSize*(rowAC - 2), border + wallSize*(colAC - 2)]
orggoal = [border + wallSize*(rowAC - 2), border + wallSize*(colAC - 2)]
all_sprites = pygame.sprite.Group(player)
clock = pygame.time.Clock()

# Count of Moves Made
def MoveCount(color, font, size):
    score_font = pygame.font.SysFont(font, size)
    score_surface = score_font.render('Move Count : ' + str(player.moves), True, color)
    score_rect = score_surface.get_rect()
    score_rect.midtop = (frameSizeX/2, 5)
    game_window.blit(score_surface, score_rect)


# Game Over Screen 
def gameoverScreen():
    my_font = pygame.font.SysFont('consolas', 90)
    game_over_surface = my_font.render('Maze Complete', True, white)
    game_over_rect = game_over_surface.get_rect()
    game_over_rect.midtop = (frameSizeX/2, frameSizeY/4 - 100)
    game_window.fill(black)
    game_window.blit(game_over_surface, game_over_rect)
    

    if player.moves > AStarMoves:
        color = red
        acolor = green
        endtext = my_font.render('You Lost', True, color)
    elif player.moves <= AStarMoves:
        color = green
        acolor = red
        endtext = my_font.render('You Win', True, color)

    endtextrect = endtext.get_rect()
    endtextrect.midtop = (frameSizeX/2, frameSizeY/4 + 50)
    game_window.blit(endtext, endtextrect)
    smallfont = pygame.font.SysFont('consolas', 20)
    movec = smallfont.render('Move Count : ' + str(player.moves), True, color)
    movecrect = movec.get_rect()
    movecrect.midtop = (frameSizeX/2, frameSizeY/4 + 200)
    game_window.blit(movec, movecrect)
    ASC = smallfont.render('A* Move Count : ' + str(AStarMoves), True, acolor)
    ASCrect = ASC.get_rect()
    ASCrect.midtop = (frameSizeX/2, frameSizeY/4 + 230)
    game_window.blit(ASC, ASCrect)
    viewpath = smallfont.render('PRESS SPACE TO VIEW PATHS', True, white)
    viewpathrect = viewpath.get_rect()
    viewpathrect.midtop = (frameSizeX/2, frameSizeY/4 + 260)
    game_window.blit(viewpath, viewpathrect)

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
            elif event.key == pygame.K_SPACE:
                goal[0] += 1
                goal[1] += 1
    
    game_window.fill(black)
    WALLS.draw(game_window)
    all_sprites.draw(game_window)
    for l in player.locations:
        x = l[0]
        y = l[1]   
        if 0 <= row < rowAC and 0 <= col < colAC:         
            pygame.draw.rect(game_window, red, (x, y, wallSize/2, wallSize/2))

    # End Point
    pygame.draw.rect(game_window, green, (orggoal[0], orggoal[1], wallSize, wallSize))

    '''fix this'''
    if player.rect.x != goal[0] and player.rect.y != goal[1]:
        MoveCount(white, 'consolas', 20)
    '''fix this'''

    # Game Over
    if player.rect.x == goal[0] and player.rect.y == goal[1]:
        gameoverScreen()

    # Space Bar Press to View Paths
    if goal[0] > orggoal[0] and goal[1] > orggoal[1]:
        for p in path:
            col = p[0]
            row = p[1]   
            if 0 <= row < rowAC and 0 <= col < colAC:         
                pygame.draw.rect(game_window, green, ((row * wallSize + border) + wallSize/2, (col * wallSize + border) + wallSize/2, wallSize/2, wallSize/2))
        
    pygame.display.flip()
    clock.tick(60)





    
