import pygame
from pygame.locals import SRCALPHA
import pygame.math
import random
import time
import os
import copy
import math
from pathlib import Path

"""
Palette des couleurs
"""
class Color:

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    ORANGE = (255, 165, 0)
    PINK = (255, 192, 203)
    PURPLE = (128, 0, 128)
    BROWN = (165, 42, 42)
    GRAY = (128, 128, 128)
    OLIVE = (107, 142, 35)
    LIME = (0, 255, 0)
    TEAL = (0, 128, 128)
    NAVY = (0, 0, 128)
    TURQUOISE = (64, 224, 208)
    MAROON = (128, 0, 0)
    INDIGO = (75, 0, 130)
    GOLD = (255, 215, 0)
    SILVER = (192, 192, 192)
    LIGHTGRAY = (240, 240, 240, 0)
    SHADOW = (50, 50, 50, 20)
    DEFAULT = (255, 255, 255)
    ALPHA = 100
    BUBBLE = (200, 200, 200, 120)
    TEXT = (0, 0, 100)

    def random():
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

class DEBUG:
    active = False
    alpha = 100
    color = Color.RED

class CText:
    @staticmethod
    def draw(screen, x=50, y=50, color=(255, 255, 255)):
        """
        Dessine un texte sur l'écran.

        :param screen: Surface sur laquelle dessiner.
        :param x: Position x du texte (par défaut 50).
        :param y: Position y du texte (par défaut 50).
        :param color: Couleur du texte (par défaut (255, 255, 255)).
        """
        font = pygame.font.Font(None, 14)
        text = f"{x:02d},{y:02d}"
        message = font.render(text, True, color)
        screen.blit(message, (x, y))

class Camera:
    x = 0
    y = 0
    def __init__(self):
        pass


class Entite2D(pygame.sprite.Sprite):
    def __init__(self, x=10, y=10, width=50, height=50, color=Color.DEFAULT, name = None):
        """
        Initialise une forme.

        :param x: Position x initiale (par défaut 10).
        :param y: Position y initiale (par défaut 10).
        :param width: Largeur de la forme (par défaut 50).
        :param height: Hauteur de la forme (par défaut 50).
        :param color: Couleur de la forme (par défaut (255, 0, 0)).
        """
        super().__init__()
        self.width = width
        self.height = height
        self.color = color
        self.animations = None
        self.edge = 0
        self.resistance = 50
        self.speed = 0
        self.strength = 0
        self.angle = 0
        self.hide = False
        self.timer = 0
        self.start_timer = 0
        self.stick = None
        self.target = None
        self.velocity = 10
        self.guidance = [0, 0]
        self.target = None

        self.surface = pygame.Surface((self.width, self.height), SRCALPHA)
        self.surface.fill((0, 0, 0, 0))
        self.rect = self.surface.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.init_x = x
        self.init_y = y

        self.enable = True

        self.name = name

    def _copy(self, x=None, y=None):
        """
        Crée une copie de la forme.

        :param x: Position x de la copie (par défaut la position actuelle).
        :param y: Position y de la copie (par défaut la position actuelle).
        :return: Une nouvelle instance de Shape.
        """

        x = self.rect.x if x is None else x
        y = self.rect.y if y is None else y
        new_copy = Shape(x, y, self.width, self.height, self.color)
        new_copy.target = self.target
        new_copy.velocity = self.velocity
        if self.animations:
            new_copy.loadAnimations(self.animations,
                                   self.animations.getCurrentAnimation(),
                                   self.animations.getShift_x(),
                                   self.animations.getShift_y())
        return new_copy

    def draw(self, screen, camera = Camera()):
        """
        Dessine la forme sur l'écran.

        :param screen: Surface sur laquelle dessiner.
        :param camera: Caméra utilisée pour suivre le joueur.
        """
        if self.timer > 0 :
            if (time.time() - self.start_timer) >= self.timer:
                self.hide = not self.hide
                self.timer = 0


        if not self.hide:
            if self.animations:
                self.animations.draw(screen, camera, self.rect.x, self.rect.y, self.guidance)
            else:
                screen.blit(self.surface, (self.rect.x + (self.edge // 2) - camera.x,
                                           self.rect.y + (self.edge // 2) - camera.y))
            if DEBUG.active:
                CText.draw(screen, self.rect.x - camera.x, self.rect.y - camera.y)

    def goto(self, x=None, y=None):
        """
        Déplace la forme à une position donnée.

        :param x: Nouvelle position x (par défaut la position actuelle).
        :param y: Nouvelle position y (par défaut la position actuelle).
        """

        self.rect.x = x if x is not None else self.rect.x
        self.rect.y = y if y is not None else self.rect.y

    def changeSizeBy(self, size):
        """
        Change la taille de la forme par une valeur donnée.

        :param size: Valeur de changement de taille.
        """
        if self.width + size > 0 and self.height + size > 0:
            self.width += size
            self.height += size
            self.surface = pygame.transform.scale(self.surface, (self.width, self.height))

    def setSizeToo(self, percentage=None):
        """
        Définit la taille de la forme à un pourcentage donné.

        :param percentage: Pourcentage de la taille actuelle.
        """
        if percentage and percentage > 0:
            self.width = (self.width / 100) * percentage
            self.height = (self.height / 100) * percentage
            self.surface = pygame.transform.scale(self.surface, (self.width, self.height))
            self.rect = self.surface.get_rect(topleft=(self.rect.x, self.rect.y))

    def rotate(self, angle=None):
        """
        Fait tourner la forme d'un angle donné.

        :param angle: Angle de rotation.
        """
        if angle:
            self.surface = pygame.transform.rotate(self.surface, angle)
            self.rect = self.surface.get_rect(center=self.rect.center)

    def setShow(self, show=True, timer=0):
        """
        Définit la visibilité de la forme.

        :param show: Visibilité de la forme.
        :param timer: Durée de la visibilité ou non visibilité.
        """
        if timer > 0 :
            self.timer = timer
            self.start_timer = time.time()
            self.hide = not show
        else:
            self.hide = not show

    def isHide(self):
        """
        Vérifie si la forme est cachée.

        :return: True si cachée, False sinon.
        """
        return self.hide


    def isCollide(self, collider):
        """
        Vérifie si la forme est en collision avec un autre objet.

        :param collider: Objet à vérifier.
        :return: True si en collision, False sinon.
        """
        return self.rect.colliderect(collider)

    def isJumpOnIt(self, collider):
        """
        Vérifie si la forme saute sur un autre objet.

        :param collider: Objet à vérifier.
        :return: True si sauté, False sinon.
        """
        return self.rect.colliderect(collider) and not collider.isStick()

    def _getStick(self):
        """
        Renvoie la forme collante.
        """
        return self.stick

    def _setStick(self, stick):
        """
        Définit si la forme est collante.

        :param stick: Valeur de collage.
        """
        self.stick = stick

    def isStick(self):
        """
        Vérifie si la forme est collante.

        :return: True si collante, False sinon.
        """
        return True if self.stick else False

    def loadAnimations(self, animations, first_animation, shift_x=0, shift_y=0):
        """
        Charge les animations de la forme.

        :param animations: Animations à charger.
        :param first_animation: Première animation à définir.
        :param shift_x: Décalage en x.
        :param shift_y: Décalage en y.
        """
        if animations:
            self.animations = copy.copy(animations)
            self.animations.setCurrentAnimation(first_animation, shift_x, shift_y)


    def move(self, guidance = None):
        """
        Déplace la forme en fonction de la guidance.

        :param guidance: Guidance de déplacement.
        """

        if self.animations :
            self.animations.move(self.animations.getCurrentAnimation())

        if self.target is not None:
            # Créer les vecteurs pour les positions des objets
            target_vec = self._get_target_vector()

            if target_vec:

                originx = self.rect.x
                originy = self.rect.y

                self_vec = pygame.math.Vector2([self.rect.x, self.rect.y])

                # Calculer le vecteur de déplacement
                deplacement_vec = target_vec - self_vec

                inversion = True
                if isinstance(self.target, int):
                    if deplacement_vec[0] < -1*(self.velocity) or deplacement_vec[0] > self.velocity:
                        inversion=False
                elif isinstance(self.target, list) or isinstance(self.target, tuple):
                    if self.target[0] != 0:
                        if deplacement_vec[0] < -1*(self.velocity) or deplacement_vec[0] > self.velocity:
                            inversion=False
                    elif self.target[1] != 0:
                        if deplacement_vec[1] < -1*(self.velocity) or deplacement_vec[1] > self.velocity:
                            inversion=False
                    else:
                        inversion=False
                else:
                    inversion=False

                if inversion:
                    self._invert_target()
                else:
                    self._move_towards_target(deplacement_vec)

                if (self.rect.x - originx) != 0 or (self.rect.y - originy) != 0:
                    self.setGuidance([self.rect.x - originx, self.rect.y - originy])

    def _get_target_vector(self):
        """
        Obtient le vecteur cible en fonction du type de cible.

        :return: Vecteur cible ou None.
        """
        if isinstance(self.target, pygame.sprite.Sprite):
            if abs(self.target.rect.x - self.rect.x) < 500:
                return pygame.math.Vector2(self.target.rect.x, self.target.rect.y)
        elif isinstance(self.target, (tuple, list)):
            return pygame.math.Vector2(self.init_x + self.target[0], self.init_y + self.target[1])
        elif isinstance(self.target, int):
            return pygame.math.Vector2(self.init_x + self.target, self.rect.y)
        return None

    def _should_invert_target(self, displacement_vec):
        """
        Vérifie si la cible doit être inversée.

        :param displacement_vec: Vecteur de déplacement.
        :return: True si la cible doit être inversée, False sinon.
        """
        if isinstance(self.target, int):
            return abs(displacement_vec.x) > self.velocity
        elif isinstance(self.target, (list, tuple)):
            return (self.target[0] != 0 and abs(displacement_vec.x) > self.velocity) or \
                   (self.target[1] != 0 and abs(displacement_vec.y) > self.velocity)
        return False

    def _invert_target(self):
        """
        Inverse la cible.
        """
        if isinstance(self.target, int):
            self.target *= -1
        elif isinstance(self.target, list):
            self.target[0] *= -1
            self.target[1] *= -1
        else:
            self.target = None

    def _move_towards_target(self, displacement_vec):
        """
        Déplace la forme vers la cible.

        :param displacement_vec: Vecteur de déplacement.
        """
        try:
            displacement_vec.normalize_ip()
            displacement_vec *= self.velocity + 1
            self_vec = pygame.math.Vector2(self.rect.x, self.rect.y)
            self_vec += displacement_vec
            self.rect.x = int(self_vec.x)
            if isinstance(self.target, (tuple, list)):
                self.rect.y = int(self_vec.y)
            if self.animations:
                self.animations.move(self.animations.getCurrentAnimation())
        except ValueError:
            self.target = None

    def getCurrentAnimation(self):
        """
        Obtient l'animation actuelle.

        :return: Animation actuelle ou None.
        """
        return self.animations.getCurrentAnimation() if self.animations else None

    def setAnimation(self, animation=None, velocity=None):
        """
        Définit l'animation actuelle.

        :param animation: Animation à définir.
        :param velocity: Vitesse de l'animation.
        """
        if velocity:
            self.velocity = velocity
        if animation and self.animations:
            self.animations.setCurrentAnimation(animation)

    def distance(self, objet):
        """
        Calcule la distance entre la forme et un autre objet.

        :param objet: Objet à vérifier.
        :return: Distance entre les objets.
        """
        return math.sqrt((self.rect.x - objet.rect.x) ** 2 + (self.rect.y - objet.rect.y) ** 2)

    def moveToTarget(self, target, velocity=10):
        """
        Déplace la forme vers une cible donnée.

        :param target: Cible à atteindre.
        :param velocity: Vitesse de déplacement.
        """
        self.setGuidance([0,0])
        self.target = target
        self.velocity = velocity

    def setGuidance(self, guidance):
        """
        Définit la guidance de la forme.

        :param guidance: Guidance à définir.
        """
        self.guidance = guidance

    def getGuidance(self):
        """
        Obtient la guidance actuelle de la forme.

        :return: Guidance actuelle.
        """
        return self.guidance

    def getX(self):
        """
        Obtient la position x de la forme.

        :return: Position x.
        """
        return self.rect.x

    def getY(self):
        """
        Obtient la position y de la forme.

        :return: Position y.
        """
        return self.rect.y

    def position(self):
        """
        Obtient la position actuelle de la forme.

        :return: Tuple (x, y) de la position.
        """
        return self.rect.x, self.rect.y

    def setStartPoint(self, validation_point):
        """
        Définit le point de départ de la forme.

        :param validation_point: Point de départ à définir.
        """
        if isinstance(validation_point, list):
            self.init_x, self.init_y = validation_point
        elif isinstance(validation_point, Shape):
            self.init_x, self.init_y = validation_point.position()
        elif isinstance(validation_point, tuple):
            self.init_x, self.init_y = validation_point
        elif isinstance(validation_point, int):
            self.init_x = validation_point
            self.init_y = self.rect.y

    def getStartPoint(self):
        """
        Obtient le point de départ de la forme.

        :return: Tuple (x, y) du point de départ.
        """
        self.setGuidance([0,0])
        return self.init_x, self.init_y

    def goToTarget(self, target):
        """
        Déplace la forme vers une cible donnée.

        :param target: Cible à atteindre.
        """
        self.setGuidance([0,-1])
        if isinstance(target, list):
            self.goto(target[0], target[1])
        elif isinstance(target, Entite2D):
            self.goto(target.getX(), target.getY()-target.getHeight())
        elif isinstance(target, tuple):
            self.goto(target[0], target[1])
        elif isinstance(target, int):
            self.goto(target, None)

    def setColor(self, color=(255, 255, 255), alpha=255):
        """
        Définit la couleur de la forme.

        :param color: Couleur à définir.
        :param alpha: Transparence de la couleur.
        """
        self.surface.convert_alpha()
        self.surface.set_alpha(alpha)
        self.surface.fill(color)

    def getWidth(self):
        """
        Obtient la largeur de la forme.

        :return: Largeur de la forme.
        """
        return self.width

    def getHeight(self):
        """
        Obtient la hauteur de la forme.

        :return: Hauteur de la forme.
        """
        return self.height

    def disable(self):
        self.enable = False

    def enable(self):
        self.enable = True

    def isEnable(self):
        return self.enable

    def getName(self):
        return self.name
"""
Dessin d'un rectangle ou un carré,
    point en haut droit
    point en bas gauche
    couleur de remplissage de la forme

    Exemple d'utilisation
    square = Shape(200, 20, 200, 200, Color.BLUE)
    square.draw(screen, camera)

"""

class Shape(Entite2D):
    def __init__(self, x=10, y=10, width=50, height=50, color=Color.DEFAULT, name=None):
        super().__init__(x, y, width, height, color, name)
        pygame.draw.rect(self.surface, self.color, self.surface.get_rect())

"""
Dessin d'un polygone à plusieurs cotés
    liste des points
    couleur de remplissage de la forme

    Exemple d'utilisation
    polygon = Polygon([(150, 10), (200, 100), (100, 100)], Color.RED)
    polygon.draw(screen, camera)

"""
class Polygon(Entite2D):
    def __init__(self, coordinates=None, color=Color.DEFAULT):
        """
        Initialise un polygone.

        :param coordinates: Liste de coordonnées des sommets du polygone.
        :param color: Couleur du polygone (par défaut Color.DEFAULT).
        """
        if coordinates is None:
            coordinates = []

        # Calcul des dimensions du polygone
        x_coords, y_coords = zip(*coordinates) if coordinates else ([], [])
        self.x = min(x_coords, default=0)
        self.y = min(y_coords, default=0)
        self.width = max(x_coords, default=0) - self.x
        self.height = max(y_coords, default=0) - self.y

        # Initialisation des attributs de la classe parente
        super().__init__(self.width, self.height, self.x, self.y, color)

        # Ajustement des coordonnées pour qu'elles soient relatives à (self.x, self.y)
        self.coordinates = [(x - self.x, y - self.y) for x, y in coordinates]

        # Création de la surface pour dessiner le polygone
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.surface.fill((0, 0, 0, 0))
        self.rect = self.surface.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        # Dessin du polygone sur la surface
        pygame.draw.polygon(self.surface, self.color, self.coordinates)

"""
Dessin du cercle
    Coordonnées du centre
    Rayon
    Couleur de remplissage ou None si pas de remplissage
    largeur du bordure
    couleur du bord

    Exemple d'utilisation
    circle = Circle(400, 400, 100, Color.BLUE)
    circle.draw(screen, camera)

"""
class Circle(Entite2D):
    def __init__(self, x=10, y=10, radius=10, color=Color.DEFAULT):
        """
        Initialise un cercle.

        :param x: Position x initiale (par défaut 10).
        :param y: Position y initiale (par défaut 10).
        :param radius: Rayon du cercle (par défaut 10).
        :param color: Couleur du cercle (par défaut Color.DEFAULT).
        """
        super().__init__(x, y, radius * 2, radius * 2, color)
        self.radius = radius

        # Création de la surface pour dessiner le cercle
        self.surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        self.surface.fill((0, 0, 0, 0))

        # Dessin du cercle sur la surface
        pygame.draw.circle(self.surface, self.color, (self.radius, self.radius), self.radius)

    def _copy(self, x=0, y=0):
        """
        Crée une copie du cercle.

        :param x: Position x de la copie (par défaut 0).
        :param y: Position y de la copie (par défaut 0).
        :return: Une nouvelle instance de Circle.
        """
        x = self.rect.x if x == 0 else x
        y = self.rect.y if y == 0 else y

        newCopy = Circle(x, y, self.radius, self.color)
        if self.animations:
            newCopy.loadAnimations(self.animations,
                                  self.animations.getCurrentAnimation(),
                                  self.animations.getShift_x(),
                                  self.animations.getShift_y())
        return newCopy


"""
Dessin d'une ellipse
    Coordonnées des points de l'élipse
    Couleur de l'élipse

    Exemple d'utilisation
    ellipse = Ellipse(500, 100, 50, 200, Color.RED)
    ellispe.draw(screen, camera)


"""
class Ellipse(Entite2D):
    def __init__(self, x=10, y=10, width=50, height=50, color=Color.DEFAULT):
        """
        Initialise une ellipse.

        :param x: Position x de l'ellipse (par défaut 10).
        :param y: Position y de l'ellipse (par défaut 10).
        :param width: Largeur de l'ellipse (par défaut 50).
        :param height: Hauteur de l'ellipse (par défaut 50).
        :param color: Couleur de l'ellipse (par défaut Color.DEFAULT).
        """
        super().__init__(x, y, width, height, color)

        # Initialisation des coordonnées de l'ellipse
        self.coordinates = [0, 0, width, height]

        # Dessin de l'ellipse sur la surface
        pygame.draw.ellipse(self.surface, self.color, self.coordinates)


"""
Dessin d'un trait
    Coordonnées de départ
    Coordonnées de fin
    Couleur du trait
    Largeur du trait

Exemple d'utilisation
    line = Line(startPoint=(50, 50), endPoint=(200, 200), color=(255, 0, 0), thickness=3)
    line.draw(screen, camera)

"""
class Line(Entite2D):
    def __init__(self, startPoint=(0, 0), endPoint=(10, 10), color=Color.DEFAULT, thickness=1):
        """
        Initialise une ligne.

        :param startPoint: Coordonnées du point de départ (par défaut (0, 0)).
        :param endPoint: Coordonnées du point de fin (par défaut (10, 10)).
        :param color: Couleur de la ligne (par défaut Color.DEFAULT).
        :param thickness: Épaisseur de la ligne (par défaut 1).
        """
        super().__init__(startPoint[0], startPoint[1], endPoint[0] - startPoint[0], endPoint[1] - startPoint[1], color)

        self.thickness = thickness
        self.startPoint = (0, 0)
        self.endPoint = (self.width, self.height)

        # Dessin de la ligne sur la surface
        pygame.draw.line(self.surface, self.color, self.startPoint, self.endPoint, self.thickness)

"""
Affichage d'un texte
    Texte à afficher
    x
    y
    Couleur
    Font à utiliser
    Taille de la police

    Exemple d'utilisation
    text = Text("Name : ",10, 10,Color.BLACK, size = 50)
    text.setText("Dupont")
    text.draw(screen, camera)

"""
class Text(Entite2D):
    def __init__(self, caption=None, x=0, y=0, color=Color.DEFAULT, font_name=None, size=50):

        """
        Initialise un objet texte.

        :param caption: Texte à afficher (par défaut None).
        :param x: Position x initiale (par défaut 0).
        :param y: Position y initiale (par défaut 0).
        :param color: Couleur du texte (par défaut Color.DEFAULT).
        :param font_name: Nom de la police de caractères (par défaut None).
        :param size: Taille de la police (par défaut 50).
        """
        super().__init__(x, y, 0, 0, color)
        self.font = pygame.font.Font(font_name, size)
        self.caption = str(caption) if caption is not None else ""
        self.text = None
        self.timer = 0
        self.start_timer = 0
        self.hide = False

        self.surface = self.font.render(u'{}'.format(self.caption), True, self.color)
        self.rect = self.surface.get_rect()
        self.rect.x = x
        self.rect.y = y

    def setText(self, text):
        """
        Définit le texte à afficher.

        :param text: Nouveau texte à afficher.
        """
        self.text = str(text) if text is not None else ""

    def getText(self):
        """
        Obtient le texte actuel.

        :return: Texte actuel.
        """
        return self.text

    def draw(self, screen, camera = Camera()):
        """
        Dessine le texte sur l'écran.

        :param screen: Surface sur laquelle dessiner.
        :param camera: Caméra utilisée pour suivre le joueur.
        """
        if self.timer > 0:
            if time.time() - self.start_timer >= self.timer:
                self.hide = not self.hide
                self.timer = 0

        if not self.hide :
            self.message = self.font.render(u'{}'.format(
                                            (self.caption if self.caption else "") +
                                            (self.text if self.text else "")),
                                            True, self.color)
            screen.blit(self.message, (self.rect.x - camera.x, self.rect.y - camera.y))

"""
Plannificateur pour le lancement d'objets graphiques
    plannerShappes = PlannerShappes()
    plannerShappes.add(square)
    plannerShappes.add(text)
    plannerShappes.add(image)

    planner.start(3)

"""
class PlannerShapes:
    shapes = []
    delay = 0

    def __init__(self):
        pass

    def init(self):
        self.shapes = []

    def start(self, shape, delay=3):

        for plannedShape in self.shapes:
            if plannedShape[0] == shape :
                plannedShape[1] = delay
                plannedShape[2] = time.time()
                return True
        self.shapes.append([shape,delay,time.time()])
        return True

    def move(self):
        for plannedShape in self.shapes:
            plannedShape[0].move()

    def draw(self, screen, camera = Camera()):
        # print(self.current, self.current - self.start, self.delay * 1000)
        for index, plannedShape in enumerate(self.shapes):

            if (time.time() - plannedShape[2] <= plannedShape[1]):  # Conversion en millisecondes
                plannedShape[0].draw(screen)
            else:
                plannedShape[1] = 0

        self.shapes = [plannedShape for plannedShape in self.shapes if plannedShape[1] > 0]

"""
Lancement et affichage d'un chronomètre

    textChrono = Text("00:00", 15, 15, Color.RED)
    shapeChrono = Shape(10, 10, 100, 40, Color.BLUE, 2, Color.GREEN)
    chronometer = Chronometer(textChrono, shapeChrono)

Exemple d'utilisation
    chrono = Chronometer(text=Text("Step finished at : ", x=400, y=10, size=40), sound="bip.wav", sound_path="sounds")
    chrono.start(delay=5)
    chrono.draw(screen, camera)

    chrono.draw(screen)  ou pour un affichage fixe


"""
class Chronometer:
    chrono = None
    delay = 0
    state = 0


    def __init__(self, text=None, shape=None, sound=None, soundPath=None):
        """
        Initialise un chronomètre.

        :param text: Objet Text pour afficher le temps (par défaut None).
        :param shape: Objet Shape pour dessiner une forme (par défaut None).
        :param sound: Nom du fichier son (par défaut None).
        :param sound_path: Chemin du répertoire contenant le fichier son (par défaut None).
        """
        self.text = text if text else Text(x=10, y=10)
        self.shape = shape
        self.sound = None
        self.delay = 0
        self.state = 0
        self.startChrono = 0
        self.currentChrono = 0

        if sound:
            try:
                self.sound = pygame.mixer.Sound(Path(soundPath) / sound if soundPath else sound)
            except Exception as e:
                print(
                    "Une erreur est survenue lors de l'ouverture du fichier : "
                    + soundPath
                    + "/"
                    + sound,
                    str(e))

    def stop(self):
        """
        Arrête le chronomètre.
        """
        self.delay = 0
        self.currentChrono = 0
        self.state = 0

    def start(self, delay=3):
        """
        Démarre le chronomètre.

        :param delay: Durée du chronomètre en secondes (par défaut 3).
        """
        if self.delay == 0:
            self.startChrono = time.time()
            self.delay = delay
            self.currentChrono = time.time()
            self.state = 1
            if self.sound:
                self.sound.play()

    def getChrono(self):
        """
        Obtient le temps restant du chronomètre.

        :return: Temps restant formaté en "MM:SS".
        """

        if self.delay > 0:
            # Vérifier si le temps d'affichage est écoulé
            if self.sound:
                if time.time() - self.currentChrono >= 1:
                    self.currentChrono = time.time()
                    self.sound.play()

            if (
                time.time() - self.startChrono >= self.delay
            ):  # Conversion en millisecondes
                self.stop()
                self.state = 2

        if self.delay > 0:
            minutes = int((self.delay - (time.time() - self.startChrono)) // 60)
            seconds = int((self.delay - (time.time() - self.startChrono)) % 60)
            return f"{minutes:02d}:{seconds:02d}"
        else:
            return f"{00:02d}:{00:02d}"

    def draw(self, screen, camera = Camera()):
        """
        Dessine le chronomètre sur l'écran.

        :param screen: Surface sur laquelle dessiner.
        :param camera: Caméra utilisée pour le rendu (par défaut None).
        """

        if self.delay > 0 and self.text:
            if self.shape:
                self.shape.draw(screen, camera)
            self.text.setText(self.getChrono())
            self.text.draw(screen, camera)

    def getState(self):
        """
        Obtient l'état actuel du chronomètre.

        :return: État du chronomètre (0: arrêté, 1: en cours, 2: terminé).
        """
        return self.state

    def isStarted(self):
        """
        Vérifie si le chronomètre est démarré.

        :return: True si le chronomètre est démarré, False sinon.
        """
        return True if self.state > 0 else False

    def isFinished(self):
        """
        Vérifie si le chronomètre est terminé.

        :return: True si le chronomètre est terminé, False sinon.
        """
        return True if self.state == 2 else False


"""
Chargement d'images

Exemple d'utilisation
shape_image = ShapeImage("path/to/images", "example.png", x=50, y=50, size=(100, 100))
shape_image.draw(screen, camera)

"""
class Image:
    """
    Charge une image depuis un fichier et la redimensionne si nécessaire.

    :param path: Chemin du répertoire contenant le fichier image.
    :param nameFile: Nom du fichier image.
    :param size: Taille à laquelle redimensionner l'image (par défaut None).
    :return: Surface de l'image chargée ou None en cas d'erreur.
    """

    def load(path, nameFile, size=None):
        if nameFile:
            try:
                if size:
                    return pygame.transform.scale(
                        pygame.image.load(os.path.join(path, nameFile)), size
                    )
                else:
                    return pygame.image.load(os.path.join(path, nameFile))
            except Exception as e:
                print(
                    "Une erreur est survenue lors de l'ouverture du fichier : "
                    + path
                    + "/"
                    + nameFile,
                    str(e),
                )
                return None
        else:
            return None

"""
    Affichage d'une image
    image = ShapeImage("images/", "bullet.png", 200, 200, (100,100))
"""
class ShapeImage(Entite2D):

    # Initialisation de l'objet
    def __init__(self, path, nameFile, x=0, y=0, size=None, color=Color.DEFAULT, alpha = 255):
        """
        Initialise une forme avec une image.

        :param path: Chemin du répertoire contenant le fichier image.
        :param nameFile: Nom du fichier image.
        :param x: Position x initiale (par défaut 0).
        :param y: Position y initiale (par défaut 0).
        :param size: Taille à laquelle redimensionner l'image (par défaut None).
        :param color: Couleur de la forme (par défaut Color.DEFAULT).
        """

        super().__init__(x, y, 0, 0, color)

        # Création de la surface pour dessiner la forme
        self.surface = Image.load(path, nameFile, size)
        if not size:
            if self.surface:
                self.width, self.height = self.surface.get_size()
            else:
                self.width, self.height = (32, 32)

        if not self.surface:
            self.surface = pygame.Surface((self.width, self.height), SRCALPHA)
            square = pygame.Rect(0, 0, self.width, self.height)
            pygame.draw.rect(self.surface, self.color, square)

        self.rect = self.surface.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.alpha = alpha

    # Dessin de la forme sur l'écran
    def draw(self, screen, camera = Camera()):
        """
        Dessine la forme sur l'écran.

        :param screen: Surface sur laquelle dessiner.
        :param camera: Caméra utilisée pour le déplacement du joueur.
        """
        self.surface.set_alpha(self.alpha)
        screen.blit(self.surface, (self.rect.x - camera.x, self.rect.y - camera.y))

class Transform():
    def scale(originalImage=None, scale=None):
        if originalImage and scale:
            return pygame.transform.scale(originalImage, scale)



