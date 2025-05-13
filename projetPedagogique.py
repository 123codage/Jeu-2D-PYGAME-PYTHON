from classes.Game2D import *
from classes.common import *

class MyGame(Game2D):
    def __init__(
        self,
        caption,				    # Titre du jeu
        game2D_width=6000,		    # Espace du jeu en largeur en pixel
        game2D_height=800,		    # Espace du jeu en hauteur en pixel
        screen_width=1200,		    # Largeur de l’écran en pixel
        screen_height=600,		    # Hauteur de l’écran en pixel
        fill_color=Color.LIGHTGRAY,	# Couleur du fond de l’écran
        fps=20,				        # Nombre d’images par seconde
        screenRotation=False
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
        plateforme01.move()

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Dessiner les objets de votre jeu en fond
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def myDisplayBehind(self, screen, camera):
        pass


    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Dessiner les objets de votre jeu devant
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    # devant
    def myDisplayInFront(self, screen, camera):
        sol.draw(screen, camera)
        plateforme01.draw(screen, camera)
        plateforme02.draw(screen, camera)
        player.draw(screen, camera)

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Initialisation du jeu
    Initialiser tous les objets dont vous aurez besoin pour votre jeu
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def myInitialization(self):
        global sol
        global player
        global plateforme01
        global plateforme02

        sol = Shape(0, Game2D.SIZE[1]-30,
                    Game2D.SIZE[0], 50,
                    Color.GREEN)

        plateforme01 = Shape(100, 550,
                    200, 5,
                    Color.GREEN)

        plateforme02 = Shape(300, 500,
                    200, 70,
                    Color.GREEN)

        plateforme01.moveToTarget([0,20],2)

                # Création du joueur
        player = Player(20, 10, 10, 20, Color.RED)
        # Indiquer au moteur le joueur
        self.setPlayer(player)

        self.gravity.addFloor(sol)
        self.gravity.addFloor(plateforme01)
        self.gravity.addObject(player)

        self.collisionsManager.addCollider(plateforme02)
        self.collisionsManager.addMovingObject(player)

        Event.JUMP = 80
        Event.VELOCITY = 3
        Event.VELOCITY_UP = 2
        Event.VELOCITY_MAX = 20


"""
Lancement du jeu
- titre du jeu
- largeur de l'espace du jeu en pixel
- hauteur de l'espace du jeu en pixel
- largeur de la fenêtre de jeu en pixel
- hauteur de la fenêtre de jeu en pixel
- couleur de fond de la fenêtre de jeu
- FPS nombres d'images par seconde
- Orientation de la fenêtre portrait ou paysage
"""

# Amuse-toi à modifier l’écran
myGame = MyGame("Mon premier jeu",
                			11520, 640,
                			1200, 640,
                            (220, 220, 240), 10, False)

myGame.run(True)



