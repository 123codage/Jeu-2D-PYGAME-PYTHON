from classes.Game2D import *
from classes.common import *

class MyGame(Game2D):
    def __init__(
        self
    ):
        super().__init__(
        )
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

    Conditions et déplacements des objets de votre jeu

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def myUpdate(self):
        monsters.move()
        monster = monsters.isCollide(player)
        if monster :
            if monster.isJumpOnIt(player):
                # Destruction du monstre dans la liste des monstres
                monsters.remove_entity(monster)
            else :
                # Le joueur recommence au début du niveau
                self.goToStartOfLevel()

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Dessiner les objets de votre jeu devant
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def myDisplayInFront(self, screen, camera):
        sol.draw(screen, camera)
        player.draw(screen, camera)
        monsters.draw(screen, camera)
        plateformes.draw(screen, camera)

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Initialisation du jeu
    Initialiser tous les objets dont vous aurez besoin pour votre jeu
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def myInitialization(self):
        global sol
        global player
        global monsters
        global plateformes

        sol = Shape(0, Game2D.SIZE[1]-30,
                    Game2D.SIZE[0], 50,
                    Color.GREEN)

        player = Player(10, 10, 32, 32, Color.BLUE)
        self.setPlayer(player)

        self.gravity.addFloor(sol)
        self.gravity.addObject(player)

        Event.JUMP = 150
        Event.VELOCITY = 2
        Event.VELOCITY_MAX = 6

        plateforme = Shape(10, 10, 256, 16, Color.GREEN)
        plateformes = EntitiesManager(plateforme, 20, 100, 300, Game2D.SIZE[0], Game2D.SIZE[1]-96)
        for platform in plateformes.getList():
            self.gravity.addFloor(platform)

        monster = Shape(10, 10, 32, 32, Color.RED)
        monsters = EntitiesManager(monster, 20, 100, Game2D.SIZE[1]-62, Game2D.SIZE[0], Game2D.SIZE[1]-62)

        monsters.moveToTarget(player,1)

"""
Lancement du jeu
"""
myGame = MyGame()
myGame.run(True)
