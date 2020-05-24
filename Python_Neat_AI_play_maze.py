import pygame as py
import pygame.gfxdraw
import os
import random
import neat
#Note: dedention just press shift + Tab
Green = (0,255,0)
Red = (255,0,0)
Blue = (0,0,255)
White = (255,255,255)
Black = (0,0,0)

Border_x = 500
Border_y = 500

this_dir_path = os.path.dirname(__file__)

py.init()
Win = py.display.set_mode((Border_x,Border_y))
py.display.set_caption("NEAT playing 'Finding way Home'!")
clock = py.time.Clock()

#....................................................
class Player(py.sprite.Sprite):
    def __init__(self):
        super().__init__()
        ssurface = py.Surface((50,50), pygame.SRCALPHA) # including per-pixel alpha
        ssurface = ssurface.convert_alpha() # turn it into transparent in order to draw something from it
        py.gfxdraw.filled_circle(ssurface,25,25,25,White)
        self.image =ssurface
        self.rect = self.image.get_rect()
        self.rect.x = 3
        self.rect.y = 3

    def update(self):
        if py.key.get_pressed()[py.K_w] and self.rect.top > 0:
            self.rect.y -= 1
        if py.key.get_pressed()[py.K_s] and self.rect.bottom < Border_y:
            self.rect.y += 1
        if py.key.get_pressed()[py.K_d] and self.rect.right < Border_x:
            self.rect.x += 1
        if py.key.get_pressed()[py.K_a] and self.rect.left > 0:
            self.rect.x -= 1
    #.......for NEAT AI......
    def move_up(self):
        self.rect.y -= 1
        if self.rect.y < 0:
            self.rect.y = 0

    def move_down(self):
        self.rect.y += 1
        if self.rect.bottom > Border_y:
            self.rect.y = Border_y - self.rect.height

    def move_right(self):
        self.rect.x += 1
        if self.rect.right > Border_x:
            self.rect.x = Border_x - self.rect.width

    def move_left(self):
        self.rect.x -= 1
        if self.rect.x < 0:
            self.rect.x = 0

class Wall(py.sprite.Sprite):
    def __init__(self):
        x1,y1 = random.randint(1,200),random.randint(1,200)
        x2,y2 = x1-3,y1-3
        x3,y3 = random.randint(1,200),random.randint(1,200)
        x4,y4 = x3-3,y3-3
        super().__init__()
        ssurface = py.Surface((200,200), pygame.SRCALPHA)
        ssurface = ssurface.convert_alpha()
        py.gfxdraw.filled_polygon(ssurface,[(x1,y1),(x2,y2),(x3,y3),(x4,y4)],Green)
        self.image = ssurface
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(1,400)
        self.rect.y = random.randint(1,400)

class Destination(py.sprite.Sprite):
    def __init__(self):
        super().__init__()
        ssurface = py.Surface((10,10), pygame.SRCALPHA)
        ssurface = ssurface.convert_alpha()
        py.gfxdraw.filled_circle(ssurface,5,5,5,Red)
        self.image = ssurface
        self.rect = self.image.get_rect()
        self.rect.x = Border_x - 20
        self.rect.y = Border_y - 20
#..............................................
class Mouse(py.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.rect = py.Rect(0,0,1,1)

    def update(self):
        self.rect.x,self.rect.y = py.mouse.get_pos()

#...............................................
class You_play(py.sprite.Sprite):
    def __init__(self):
        super().__init__()
        ssurface = py.font.SysFont("Times New Roman, Arial",50)
        text = ssurface.render("Start Game",True,Black) 
        self.image = text
        self.rect = self.image.get_rect()
        self.rect.y = Border_y//2+50
        self.rect.x = Border_x//2-self.rect.width//2

class Ai_play(py.sprite.Sprite):
    def __init__(self):
        super().__init__()
        ssurface = py.font.SysFont("Times New Roman, Arial",50)
        text = ssurface.render("AI play game",True,Black) 
        self.image = text
        self.rect = self.image.get_rect()
        self.rect.y = Border_y//2+100
        self.rect.x = Border_x//2-self.rect.width//2
#.............................................................
Winning =False
Starting = True
mouse = Mouse()
you_play = You_play()
ai_play = Ai_play()
Before_start_game = py.sprite.Group()
Before_start_game.add(ai_play)
Before_start_game.add(you_play)

def main_game():
    Running = True
    All_sprite = py.sprite.Group()
    Wall_sprite = py.sprite.Group()
    for i in range(4):
        wall = Wall()
        Wall_sprite.add(wall)
        All_sprite.add(wall)
    player = Player()
    All_sprite.add(player)
    destination = Destination()
    All_sprite.add(destination)

    while Running:
        Win.fill(Black)
        py.draw.line(Win,Green,(0,0),(Border_x,0),3)
        py.draw.line(Win,Green,(0,0),(0,Border_y),3)
        py.draw.line(Win,Green,(Border_x,Border_y),(Border_x,1),3)
        py.draw.line(Win,Green,(Border_x,Border_y),(1,Border_y),3)
        for event in py.event.get():
            if event.type == py.QUIT or py.key.get_pressed()[py.K_ESCAPE]:
                Running = False
        player.update()
        for spr in Wall_sprite:
            if py.sprite.collide_mask(player,spr):
                if py.key.get_pressed()[py.K_w]:
                    player.rect.y += 1
                if py.key.get_pressed()[py.K_s]:
                    player.rect.y -= 1
                if py.key.get_pressed()[py.K_d]:
                    player.rect.x -= 1
                if py.key.get_pressed()[py.K_a]:
                    player.rect.x += 1

        if py.sprite.collide_mask(player,destination):
            Running = False
            global Winning
            Winning = True
            break
        All_sprite.draw(Win)
        py.display.update()
#......................................
#......................................
def AI_play(genomes,config):#fitness function, 'genomes' stands for neural networks that control each obj in one generation
    nets = []#.....keep track of the information of each obj.....neural network
    ge = []#.......each fitness
    players = []#.......the position of each player
    #each index of the above list keep track of the same obj
    Walls = []
    The_start_time = py.time.get_ticks()/1000 #count in second
    Breaking = False
    Running = True
    All_sprite = py.sprite.Group()
    Wall_sprite = py.sprite.Group()

    for i,g in genomes: #genomes have both index and obj e.g. [(1, g)....]
        net = neat.nn.FeedForwardNetwork.create(g,config)
        nets.append(net)
        player = Player()
        All_sprite.add(player)
        players.append(player)
        g.fitness = 0
        ge.append(g)


    for i in range(4):
        wall = Wall()
        Walls.append(wall)
        Wall_sprite.add(wall)
        All_sprite.add(wall)

    destination = Destination()
    All_sprite.add(destination)

    while Running:
        Win.fill(Black)
        py.draw.line(Win,Green,(0,0),(Border_x,0),3)
        py.draw.line(Win,Green,(0,0),(0,Border_y),3)
        py.draw.line(Win,Green,(Border_x,Border_y),(Border_x,1),3)
        py.draw.line(Win,Green,(Border_x,Border_y),(1,Border_y),3)
        for event in py.event.get():
            if event.type == py.QUIT or py.key.get_pressed()[py.K_ESCAPE]:
                Running = False
                Breaking = True
                break
        if py.time.get_ticks()/1000 - The_start_time > 90: #if those AI has run for so long that they are stuck, then quit this generation
            Running = False

        for index,player in enumerate(players):
            output = nets[index].activate((abs(player.rect.x-destination.rect.x),
                                           abs(player.rect.y-destination.rect.y),
                                           Walls[0].rect.x,Walls[0].rect.y,
                                           Walls[1].rect.x,Walls[1].rect.y,
                                           Walls[2].rect.x,Walls[2].rect.y,
                                           Walls[3].rect.x,Walls[3].rect.y)) #input -> outputs(movements)

            if output[0] > 0.5:
                player.move_up()
                for spr in Wall_sprite:
                    if py.sprite.collide_mask(player,spr):
                        ge[index].fitness -= 100 # if it hit the wall, fitness - 100
                        player.rect.y += 1
            if output[1] > 0.5:
                player.move_down()
                for spr in Wall_sprite:
                    if py.sprite.collide_mask(player,spr):
                        ge[index].fitness -= 100 # if it hit the wall, fitness - 100
                        player.rect.y -= 1
            if output[2] > 0.5:
                player.move_right()
                for spr in Wall_sprite:
                    if py.sprite.collide_mask(player,spr):
                        ge[index].fitness -= 100 # if it hit the wall, fitness - 100
                        player.rect.x -= 1
            if output[3] > 0.5:
                player.move_left()
                for spr in Wall_sprite:
                    if py.sprite.collide_mask(player,spr):
                        ge[index].fitness -= 100 # if it hit the wall, fitness - 100
                        player.rect.x += 1
 
            if py.sprite.collide_mask(player,destination):
                ge[index].fitness += 500 # if it hit the destination, fitness + 500
                Running = False

        for index, player in enumerate(players):# want it to get closer to destination, so give it bonus fitness if it get closer to
            ge[index].fitness += (Border_x + Border_y) - abs(player.rect.x-destination.rect.x) - abs(player.rect.y-destination.rect.y)
        if Breaking:
            py.quit()
        else:
            All_sprite.draw(Win)
            py.display.update()
#..........................................
#..........................................
while Starting:
    for event in py.event.get():
            if event.type == py.QUIT or py.key.get_pressed()[py.K_ESCAPE]:
                Starting = False
                break
    Win.fill(White)
    Text_surface = py.font.SysFont("Times New Roman, Arial",50,True)
    Game_title = Text_surface.render("Finding way home!",True,Black)
    Game_title_rect = Game_title.get_rect()
    Win.blit(Game_title,(Border_x//2-Game_title_rect.width//2,50))
    Before_start_game.draw(Win)
    py.display.update()
    if py.mouse.get_pressed()[0]:
        mouse.update()
        if py.sprite.collide_rect(mouse,you_play):
            Starting = False
            main_game()
        if py.sprite.collide_rect(mouse,ai_play):
            Starting = False
            config_path = os.path.join(this_dir_path,"neat.txt")#........1
            config = neat.config.Config(neat.DefaultGenome,neat.DefaultReproduction,neat.DefaultSpeciesSet,
                                        neat.DefaultStagnation,config_path)#......2 load configuration
            population = neat.Population(config)#.....3 create population based on our configuration
            population.add_reporter(neat.StdOutReporter(True))#.........4 create some statistic on the population
            population.add_reporter(neat.StatisticsReporter())#.........4
            winner = population.run(AI_play, 20)#.......5 set the fitness function to find the best, and set the generation for the fitness (e.g. 20)

    
    
#................................................


while Winning:
    for event in py.event.get():
            if event.type == py.QUIT or py.key.get_pressed()[py.K_ESCAPE] or py.mouse.get_pressed()[0]:
                Winning = False

    Win.fill(White)
    Text_surface = py.font.SysFont("Times New Roman, Arial",100,True,False)
    text = Text_surface.render("Win Win!!",True,Black)
    text_rect = text.get_rect()
    Win.blit(text,(Border_x//2-text_rect.width//2,Border_y//2-text_rect.height//2))
    py.display.update()


py.quit()
