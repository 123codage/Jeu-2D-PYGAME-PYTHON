from classes.Game2D import *
from classes.common import *

class MyGame(Game2D):
    def __init__(
        self,
        caption,				    # Titre du jeu
        game2D_width=32*200,	    # Espace du jeu en largeur en pixel
        game2D_height=32*20,	    # Espace du jeu en hauteur en pixel
        screen_width=1200,		    # Largeur de l’écran en pixel
        screen_height=640,		    # Hauteur de l’écran en pixel
        fill_color=Color.LIGHTGRAY,	    # Couleur du fond de l’écran
        fps=24,				    # Nombre d’images par seconde
        screenRotation=False                # Orientation de la fenêtre portrait ou paysage
    ):
        super().__init__(
            caption,
            game2D_width,
            game2D_height,
            screen_width,
            screen_height,
            fill_color,
            fps,
            screenRotation
        )

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Conditions en fonction des niveaux du jeu
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def myUpdateLevel(self, level, step):
        pass

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Conditions et déplacements des objets de votre jeu
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def myUpdate(self):
        pass

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Dessiner les objets de votre jeu en fond
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def myDisplayBehind(self, screen, camera):
        sun.draw(screen)

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Dessiner les objets de votre jeu devant
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def myDisplayInFront(self, screen, camera):

        wall01.draw(screen, camera)
        sol.draw(screen, camera)
        platform01.draw(screen, camera)
        platform02.draw(screen, camera)
        platform03.draw(screen, camera)

        polygon01.draw(screen, camera)

        player.draw(screen, camera)


    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Initialisation du jeu
    Initialiser tous les objets dont vous aurez besoin pour votre jeu
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def myInitialization(self):
        global sol
        global player
        global platform01
        global platform02
        global platform03
        global wall01
        global sun
        global polygon01


        sol = Shape(0, Game2D.SIZE[1]-30,
                    Game2D.SIZE[0], 50,
                    Color.GREEN)

        player = Player(10, Game2D.SIZE[1]-60, 10, 20, Color.RED)
        self.setPlayer(player)

        self.gravity.addFloor(sol)
        self.gravity.addObject(player)

        Event.JUMP = 150
        Event.VELOCITY = 2

        Event.VELOCITY_MAX = 4

        Event.UP_JUMP.append(32)
        Event.GO_RIGHT.append(100)
        Event.GO_LEFT.append(113)

        platform01 = Shape(400, 480, 300, 10, Color.BLUE)
        platform02 = Shape(730, 380, 500, 10, Color.BLUE)
        platform03 = Shape(1260, 280, 50, 10, Color.BLUE)

        polygon01 = Polygon([(150, Game2D.SIZE[1]-90), (200, Game2D.SIZE[1]-30), (100, Game2D.SIZE[1]-30)], Color.RED)

        self.gravity.addFloor(platform01)
        self.gravity.addFloor(platform02)
        self.gravity.addFloor(platform03)

        wall01 = Shape(730, 390, 500, 700, (255,200,10))

        self.collisionsManager.addCollider(wall01)
        self.collisionsManager.addCollider(polygon01)

        self.collisionsManager.addMovingObject(player)

        sun = Circle(700, 200, 150, (255,255,0))
"""
Lancement du jeu
"""

myGame = MyGame("Mon premier jeu", fps=60)

myGame.run()

