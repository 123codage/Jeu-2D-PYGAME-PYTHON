import pygame
from pygame.locals import SRCALPHA
from .common import *
import time
from classes.levelsTiled import Levels_2D
import copy
import random
from pinpong.extension.unihiker import *
from pinpong.board import Board,Pin
from pathlib import Path

class GUI:

    def __init__(self):
        pass

    def on_a_click(self, function):
        pass

    def on_b_click(self, function):
        pass

    def draw_text(text = "",x = 10,y = 10,font_size = 15, color = "#000000", origin = "center"):
        pass

    def config(text = "",x = 10,y = 10,font_size = 15, color = "#000000", origin = "center"):
        pass

"""
Barre de vie

Exemple d'utilisation

# génération de la barre des vies
hearts = LifeBar(self.player.getNbrLifes(), "heart.png", "images/token", 10, Game2D.SCREEN_SIZE[1]-40)
hearts.refresh(self.player.getNbrLifes())

hearts.draw(screen)

"""
class LifeBar:
    def __init__(self, nbrLifes, image, path, x=10, y=10, size=(32, 32), alpha=255):
        """
        Initialise une barre de vie.

        :param nbrLifes: Nombre de vies.
        :param image: Image représentant une vie.
        :param path: Chemin vers l'image.
        :param x: Position x de la barre de vie (par défaut 10).
        :param y: Position y de la barre de vie (par défaut 10).
        :param size: Taille de chaque coeur (par défaut (32, 32)).
        """
        self.x = x
        self.y = y
        self.size = size
        self.image = image
        self.path = path
        self.alpha = alpha
        self.refresh(nbrLifes)

    def draw(self, screen, camera=Camera()):
        """
        Dessine la barre de vie sur l'écran.
        :param screen: Surface sur laquelle dessiner.
        :param camera: Caméra utilisée pour le rendu (par défaut None).
        """
        if self.hearts:
            for heart in self.hearts:
                heart.draw(screen, camera)

    def refresh(self, nbrLifes):
        """
        Met à jour le nombre de coeurs dans la barre de vie.
        :param nbrLifes: Nouveau nombre de vies.
        """
        self.hearts = [
            ShapeImage(self.path, self.image, (index * self.size[0]) + self.x, self.y, self.size, alpha=self.alpha)
            for index in range(nbrLifes)
        ]

class TeleportationPoint(Entite2D):
    def __init__(self, target, x=10, y=10, width=50, height=50):

        super().__init__(x, y, width, height)
        self.target = target

    def go(self, objet):
        if self.target :
            objet.goToTarget(self.target)

"""
Bulle d'échange du joueur

Exemple d'utilisation :

speechBubblePlayer = SpeechBubble(100,100,200,10,Color.BUBBLE,20,-10, "Boite de dialogue du joueur", size = 20)
speechBubblePlayer.setShow(False)

speechBubblePlayer.goToTarget(player, "Chouette je passe à l'étape suivante ...")
speechBubblePlayer.setShow(True,3)

speechBubblePlayer.draw(screen, camera)
"""

class SpeechBubble(Entite2D):
    """
    Initialise une bulle de texte.

    :param x: Position x initiale (par défaut 10).
    :param y: Position y initiale (par défaut 10).
    :param width: Largeur de la bulle (par défaut 50).
    :param height: Hauteur de la bulle (par défaut 50).
    :param color: Couleur de la bulle (par défaut Color.BUBBLE).
    :param separate: Séparation entre la pointe et la bulle (par défaut 30).
    :param direction: Direction de la pointe de la bulle (par défaut 0).
    :param text: Texte à afficher dans la bulle (par défaut "").
    :param colorText: Couleur du texte (par défaut Color.TEXT).
    :param font: Police de caractères (par défaut None).
    :param size: Taille de la police (par défaut 50).
    """

    def __init__(self, x=10, y=10, width=50, height=50, color=Color.BUBBLE, separate=30, direction=0, text = "", colorText=Color.TEXT, font=None, size=50):

        super().__init__(x, y, width, height, color)

        self.separate = separate
        self.direction = direction
        self.text = text
        self.colorText = colorText

        self.font = pygame.font.Font(font, size)

        self.animations = None

        self.lignes = self._textGenerated()

    def draw(self, screen, camera = Camera()):

        if self.timer > 0 :
            if (time.time() - self.start_timer) >= self.timer:
                self.hide = not self.hide
                self.timer = 0

        if not self.hide :
            x = self.rect.x - (self.width // 2) if (self.rect.x - (self.width // 2)) > 0 else 10
            y = self.rect.y - (self.height + self.separate) if (self.rect.y - (self.height + self.separate)) > 0 else 10
            screen.blit(self.surface, (x - camera.x, y - camera.y))

            x_text = x + 10
            y_text = y + 10
            for ligne in self.lignes:
                texte_surface = self.font.render(u'{}'.format(ligne), True, self.colorText)
                screen.blit(texte_surface, (x_text - camera.x, y_text - camera.y))
                y_text += texte_surface.get_height()

    def moveToTarget(self, target, velocity = 10, text=""):
        """
        Déplace la bulle de texte vers une cible.

        :param target: Cible vers laquelle déplacer la bulle.
        :param velocity: Vitesse de déplacement (par défaut 10).
        :param text: Nouveau texte à afficher (par défaut "").
        """
        self.text = text
        self.lignes = self._textGenerated()
        super().moveToTarget(target, velocity)

    def goToTarget(self, target, text=""):
        self.text = text
        self.lignes = self._textGenerated()
        super().goToTarget(target)

    def _textGenerated(self):
            lignes = []
            height_text = 0

            if len(self.text) >  0 :
                largeur_max = self.width - 20
                height_text = 30
                mots = self.text.split(' ')
                ligne_actuelle = []

                for mot in mots:
                    largeur_ligne, hauteur_ligne = self.font.size(' '.join(ligne_actuelle + [mot]))


                    if largeur_ligne <= largeur_max:
                        ligne_actuelle.append(mot)
                    else:
                        lignes.append(' '.join(ligne_actuelle))
                        ligne_actuelle = [mot]
                        height_text += hauteur_ligne

                if ligne_actuelle:
                    lignes.append(' '.join(ligne_actuelle))

            if height_text > self.height :
                self.height = height_text

            self.surface = pygame.Surface((self.width, self.height+self.separate), pygame.SRCALPHA)
            pygame.draw.rect(self.surface, self.color, (0, 0, self.width, self.height))

            if self.separate > 0:
                # Dessiner le triangle de la bulle
                points = [((self.width // 2) + self.direction, self.height + self.separate),
                          (+ self.width // 2 - 20, self.height ),
                          (+ self.width // 2 + 20, self.height)]
                pygame.draw.polygon(self.surface, self.color, points)

            return lignes

class Projectile(pygame.sprite.Sprite):
    SPEED_MOVING = 30

    def __init__(self, x, y, guidance):
        super().__init__()

        self.velocity = 5
        self.image = Image.load("images/","bullet.png",(10,10))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.guidance = copy.copy(guidance)

    def move(self):
        if self.guidance[0] != 0:
            self.rect.x = self.rect.x + (self.SPEED_MOVING * self.guidance[0])
            if self.rect.x > Game2D.SCREEN_SIZE[0] or self.rect.x < 0 :
                return True
        elif self.guidance[1] != 0:
            self.rect.y = self.rect.y + (self.SPEED_MOVING * (1 if self.guidance[1] > 0 else -1))
            if self.rect.y > Game2D.SCREEN_SIZE[1] or self.rect.y < 0 :
                return True
        return False

    def draw(self, screen, camera = Camera()):
        screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))

"""
Animation visuelle et sonore d'un objet 2D

Exemple d'utilisation :

player = Player(300, 200, 10, 20, Color.GREEN)

# Définition des animations du joueur
ANIMATIONS_PLAYER = {"DOWN" : ["devant01.png",
                                    "devant02.png",
                                    "devant03.png"],
                     "UP" : ["dos01.png",
                                  "dos02.png",
                                  "dos03.png"],
                     "LEFT" : ["cotegauche01.png",
                                       "cotegauche02.png",
                                       "cotegauche03.png"],
                     "RIGHT" : ["cotedroit01.png",
                                         "cotedroit02.png",
                                         "cotedroit03.png"],
                     "IDLE" : ["attendredevant.png"],
                     "IDLEDOWN" : ["attendredevant.png"],
                     "IDLEUP" : ["attendredos.png"],
                     "IDLELEFT" : ["attendregauche.png"],
                     "IDLERIGHT" : ["attendredroit.png"]}

SOUNDS_PLAYER = { "UP" : ["jump_01.wav"],
                  "LEFT" : ["SF-course_beton-2.mp3"],
                  "RIGHT" : ["SF-course_beton-2.mp3"]}

animation = Animation(ANIMATIONS_PLAYER, "images/player", (100, 200),  scale=0.25, delay=5, soundAnimation = SOUNDS_PLAYER, soundPath = "sounds")

# Affectation de l'animation au joueur
player.loadAnimations(animation, "IDLE", 8, 30)

"""

class Animation(pygame.sprite.Sprite):
    """
    Initialise une animation.

    :param animationGroup: Dictionnaire contenant les différentes images de l'animations.
    :param path: Chemin du répertoire contenant les images (par défaut None).
    :param size: Taille des images (par défaut (40, 60)).
    :param scale: Facteur d'échelle pour les images (par défaut 1).
    :param delay: Délai entre les images de l'animation (par défaut 10).
    :param soundAnimation: Dictionnaire contenant les groupes de sons (par défaut None).
    :param soundPath: Chemin du répertoire contenant les sons (par défaut None).
    """

    shift_x = 0
    shift_y = 0
    currentAnimation = None
    soundAnimation = None

    def __init__(self, animationGroup, path=None, size=(40, 60), scale=1, delay=10, soundAnimation = None, soundPath = None, alpha = 255):
        super().__init__()
        self.alpha = alpha
        try:

            self.animationGroup = animationGroup
            # Chargement des images
            for name, animations in self.animationGroup.items():
                new_animations = []
                for index, imageName in enumerate(animations):

                    imageVignettes = imageName.split(":")
                    imageVignettes = [vignette.strip() for vignette in imageVignettes]

                    nbr_decoupage = 1
                    sens_decoupage = "H"

                    for index_vignette, vignette in enumerate(imageVignettes):
                        if index_vignette == 0 :
                            imageName = vignette
                        if index_vignette == 1 :
                            nbr_decoupage = int(vignette)
                        if index_vignette == 2 :
                            sens_decoupage = vignette
                    if sens_decoupage == "H":
                        #image = Image.load(path, imageName, (size[0] * nbr_decoupage , size[1]))
                        image = Image.load(path, imageName)
                        w, h = image.get_size()

                        for col in range(0, nbr_decoupage):
                            # Définir la position de la sous-image
                            if size[0] > w or size[1] > h :
                                rect = pygame.Rect(col * size[0], 0, w, h)
                            else:
                                rect = pygame.Rect(col * size[0], 0, size[0], size[1])
                            # Découper la sous-image
                            sub_image = image.subsurface(rect)
                            # Ajouter la sous-image à la liste
                            if scale != 1:
                                sub_image = pygame.transform.scale(sub_image, (size[0]*scale, size[1]*scale))
                            # sub_image = pygame.transform.flip(sub_image, True, False)
                            new_animations.append(sub_image)

                    elif sens_decoupage == "V":
                        image = Image.load(path, imageName, (size[0], size[1] * nbr_decoupage))

                        for row in range(0, nbr_decoupage):
                            # Définir la position de la sous-image
                            rect = pygame.Rect(0, row * size[1], size[0], size[1])
                            # Découper la sous-image
                            sub_image = image.subsurface(rect)
                            # Ajouter la sous-image à la liste
                            if scale != 1:
                                sub_image = pygame.transform.scale(sub_image, (size[0]*scale, size[1]*scale))
                            # sub_image = pygame.transform.flip(sub_image, True, False)
                            new_animations.append(sub_image)

                self.animationGroup[name] = new_animations

        except ValueError as e:
            print("erreur : ",e)
            self.animationGroup = None
        except Exception as e:
            print("erreur : ",e)
            self.animationGroup = None

        # Chagement des sons
        self.soundAnimationGroup = soundAnimation

        if self.soundAnimationGroup != None:
            for name, sounds in self.soundAnimationGroup.items():
                for index, sound in enumerate(sounds):
                    try:
                        sounds[index] = pygame.mixer.Sound(Path(soundPath) / sound if soundPath else sound)
                        self.soundAnimationGroup[name] = sounds
                    except Exception as e:
                            print(
                                "Une erreur est survenue lors de l'ouverture du fichier : "
                                + soundPath
                                + "/"
                                + sound,
                                str(e))


        self.delay = delay
        self.index = 0
        self.currentAnimation = None
        self.imageAnimation = None
        self.last_tick = pygame.time.get_ticks()

    def move(self, animation):
        """
        Met à jour l'animation en cours.

        :param animation: Nom de l'animation à jouer.
        """
        if self.animationGroup != None:
            if animation and animation == self.currentAnimation :
                if pygame.time.get_ticks() - self.last_tick >= (self.delay*Game2D.FPS):
                    self.last_tick = pygame.time.get_ticks()
                    self.index += 1
                    if self.index >= len(self.animationGroup[animation]):
                        self.index = 0
            else:
                self.currentAnimation = animation
                self.index = 0
                self.last_tick = pygame.time.get_ticks()

                if self.soundAnimation!= None:
                    self.soundAnimation.stop()
                    self.soundAnimation = None

                if self.soundAnimationGroup != None and animation in self.soundAnimationGroup:
                        self.soundAnimation = self.soundAnimationGroup[animation][0]

            self.imageAnimation = self.animationGroup[animation][self.index]

    # Dessin du joueur et des animations
    def draw(self, screen, camera = Camera(), x=0, y=0, guidance = [0, 0]):
        """
        Dessine l'animation sur l'écran.

        :param screen: Surface sur laquelle dessiner.
        :param camera: Caméra utilisée pour le rendu (par défaut None).
        :param x: Position x de l'animation (par défaut 0).
        :param y: Position y de l'animation (par défaut 0).
        :param guidance: Guidance pour l'inversion de l'image (par défaut (0, 0)).
        """
        if self.imageAnimation :
            self.imageAnimation.set_alpha(self.alpha)
            if guidance[0] < 0 :
                self.imageInversion = pygame.transform.flip(self.imageAnimation, True, False)
                screen.blit(self.imageInversion, (x-self.shift_x - camera.x, y-self.shift_y - camera.y))
            else:
                screen.blit(self.imageAnimation, (x-self.shift_x - camera.x, y-self.shift_y - camera.y))

            if self.soundAnimation !=None and self.index == 0 :
                if not pygame.mixer.get_busy():
                    try:
                        self.soundAnimation.play()
                    except Exception as e:
                            print(
                                "Une erreur est survenue : ", str(e))

    def setCurrentAnimation(self, animation, shift_x=0, shift_y=0):
        """
        Définit l'animation en cours.

        :param animation: Nom de l'animation à jouer.
        :param shift_x: Décalage en x (par défaut 0).
        :param shift_y: Décalage en y (par défaut 0).
        """
        if self.currentAnimation != animation:
            self.currentAnimation = animation
            self.index = 0
            self.last_tick = pygame.time.get_ticks()
            if shift_x != 0 :
                self.shift_x = shift_x
            if shift_y != 0 :
                self.shift_y = shift_y

            # Animation du joueur en fonction de sa direction
            if self.animationGroup != None:
                self.imageAnimation = self.animationGroup[self.currentAnimation][self.index]

            if self.soundAnimation!= None:
                self.soundAnimation.stop()
                self.soundAnimation = None
            if self.soundAnimationGroup != None and animation in self.soundAnimationGroup:
                    self.soundAnimation = self.soundAnimationGroup[animation][0]

    def getCurrentAnimation(self):
        """
        Obtient l'animation en cours.

        :return: Nom de l'animation en cours.
        """
        return self.currentAnimation

    def getShift_x(self):
        """
        Obtient le décalage en x.

        :return: Décalage en x.
        """
        return self.shift_x

    def getShift_y(self):
        """
        Obtient le décalage en y.

        :return: Décalage en y.
        """
        return self.shift_y

"""
Animation visuelle et sonore d'un objet avant de mourir

Exemple d'utilisation :
self.destructionManager.addEntity(monster,1, "DEAD")

"""
class DestructionManager:
    """
    Initialise le gestionnaire de destruction.
    """

    def __init__(self):
        self.entitiesDestroyGroup = []

    def addEntity(self, entity, delay = 0, animation = None):
        """
        Ajoute une entité à la liste de destruction.

        :param entity: Entité à ajouter.
        :param delay: Délai avant la destruction de l'entité (par défaut 0).
        :param animation: Animation à jouer avant la destruction (par défaut None).
        """

        newEntity = copy.copy(entity)
        self.entitiesDestroyGroup.append((newEntity, delay, pygame.time.get_ticks()))

        if newEntity.animations and animation :
            newEntity.animations.move(animation)

    def move(self):
        """
        Met à jour les entités et vérifie si elles doivent être détruites.
        """

        for item_deleted in self.entitiesDestroyGroup:
            entity_deleted = item_deleted[0]
            delay = item_deleted[1]
            last_ticks = item_deleted[2]

            if pygame.time.get_ticks() - last_ticks >= (delay*1000):
                self.entitiesDestroyGroup = [item for item in self.entitiesDestroyGroup if item != item_deleted]

        for item in self.entitiesDestroyGroup:
            item[0].move()

    def draw(self, screen, camera = Camera()):
        """
        Dessine les entités sur l'écran.

        :param screen: Surface sur laquelle dessiner.
        :param camera: Caméra utilisée pour le rendu (par défaut None).
        """
        for item in self.entitiesDestroyGroup:
            item[0].draw(screen, camera)

"""
Génération et gestion de plusieurs entités

Exemple d'utilisation :
monsters = EntitiesManager(monster, 10, 100, 150, Game2D.SIZE[0], Game2D.SIZE[1]-300)
monsters.moveToTarget(player,5)

monster = monsters.isCollide(player)
if monster :
    if monster.isJumpOnIt(player):
        # Création d'un monstre qui va mourir
        self.destructionManager.addEntity(monster,1, "DEAD")
        # Destruction du monstre dans la liste des monstres
        monsters.remove_entity(monster)

if monsters :
    monsters.move()

if monsters :
    monsters.draw(screen, camera)

"""
class EntitiesManager:


    def __init__(self, entity, pointsList = None, start_x=0, start_y=0, end_x=0, end_y=0):
        """
        Initialise le gestionnaire d'entités.

        :param entity: Entité prototype à copier.
        :param pointsList: Liste des entités à créer ou leur nombre.
        :param start_x: Position x de départ (par défaut 0).
        :param start_y: Position y de départ (par défaut 0).
        :param end_x: Position x de fin (par défaut 0).
        :param end_y: Position y de fin (par défaut 0).
        """
        self.entitiesGroup = []

        if end_x == 0 and end_y==0:
            end_x = Game2D.SIZE[0]

        if entity is not None and pointsList is not None:
            if isinstance(pointsList, int):
                for index in range(0, pointsList):
                    x = random.randint(start_x, end_x) if end_x > 0 else start_x
                    y = random.randint(start_y, end_y) if end_y > 0 else start_y
                    new = entity._copy(x, y)
                    self.entitiesGroup.append(new)

            if isinstance(pointsList, tuple) or isinstance(pointsList, list):
                if len(pointsList) > 1 :
                    for point in pointsList:
                        new = entity._copy(point[0], point[1])
                        self.entitiesGroup.append(new)
                else:
                    new = entity._copy(pointsList[0], pointsList[1])
                    self.entitiesGroup.append(new)


    def addEntity(self, entity):
        """
        Ajoute une entité au groupe.

        :param entity: Entité à ajouter.
        """
        new = entity._copy()
        self.entitiesGroup.append(new)

    def move(self):
        """
        Met à jour les positions des entités.
        """
        for entity in self.entitiesGroup:
            entity.move()

    def draw(self, screen, camera = Camera()):
        """
        Dessine les entités sur l'écran.

        :param screen: Surface sur laquelle dessiner.
        :param camera: Caméra utilisée pour suivre le joueur.
        """
        for entity in self.entitiesGroup:
            entity.draw(screen, camera)

    def getList(self):
        """
        Obtient la liste des entités.

        :return: Liste des entités.
        """
        return self.entitiesGroup

    def isCollide(self, collider):
        """
        Vérifie si une entité est en collision avec un autre objet.

        :param collider: Objet à vérifier pour la collision.
        :return: Entité en collision ou None.
        """
        for entity in self.entitiesGroup:
            if entity.rect.colliderect(collider):
                return entity

        return None

    def isJumpOnIt(self, collider):
        """
        Vérifie si une entité est sautée par un autre objet.

        :param collider: Objet à vérifier pour le saut.
        :return: Entité sautée ou None.
        """
        for entity in self.entitiesGroup:
            if entity.isJumpOnIt(collider):
                return entity

        return None

    def remove_entity(self, entity_deleted):
        """
        Supprime une entité du groupe.

        :param entity_deleted: Entité à supprimer.
        """
        self.entitiesGroup = [entity for entity in self.entitiesGroup if entity != entity_deleted]


    def moveToTarget(self, target, velocity = 10):
        """
        Déplace les entités vers une cible.

        :param target: Cible vers laquelle déplacer les entités.
        :param velocity: Vitesse de déplacement (par défaut 10).
        """

        for entity in self.entitiesGroup:
            entity.moveToTarget(target, velocity)
"""
Exemple d'utilisation :

    # Génération du player et de ses animations graphiques et sonores
    def generatePlayer(self):
        # Création d'un joueur
        player = Player(300, 200, 10, 20, Color.GREEN)

        # Définition des animations du joueur
        ANIMATIONS_PLAYER = {"DOWN" : ["devant01.png",
                                            "devant02.png",
                                            "devant03.png"],
                             "UP" : ["dos01.png",
                                          "dos02.png",
                                          "dos03.png"],
                             "LEFT" : ["cotegauche01.png",
                                               "cotegauche02.png",
                                               "cotegauche03.png"],
                             "RIGHT" : ["cotedroit01.png",
                                                 "cotedroit02.png",
                                                 "cotedroit03.png"],
                             "IDLE" : ["attendredevant.png"],
                             "IDLEDOWN" : ["attendredevant.png"],
                             "IDLEUP" : ["attendredos.png"],
                             "IDLELEFT" : ["attendregauche.png"],
                             "IDLERIGHT" : ["attendredroit.png"]}

        SOUNDS_PLAYER = { "UP" : ["jump_01.wav"],
                          "LEFT" : ["SF-course_beton-2.mp3"],
                          "RIGHT" : ["SF-course_beton-2.mp3"]}

        animation = Animation(ANIMATIONS_PLAYER, "images/player", (100, 200),  scale=0.25, delay=5, soundAnimation = SOUNDS_PLAYER, soundPath = "sounds")

        # Affectation de l'animation au joueur
        player.loadAnimations(animation, "IDLE", 8, 30)

        player.setNbrLifes(5)

        return player


    # Création d'un joueur
    player = self.generatePlayer()

    # Indication au moteur du jeu le joueur
    self.setPlayer(player)

    # Dessin du joueur
    player.draw(screen, camera)


"""
class Player(Entite2D):

    def __init__(
        self,
        x=10,
        y=10,
        width=50,
        height=50,
        color=Color.DEFAULT,
        nbrLifes = 0
    ):
        """
        Initialise le joueur.

        :param x: Position x initiale (par défaut 10).
        :param y: Position y initiale (par défaut 10).
        :param width: Largeur du joueur (par défaut 50).
        :param height: Hauteur du joueur (par défaut 50).
        :param color: Couleur du joueur (par défaut Color.DEFAULT).
        :param nbrLifes: Nombre de vies du joueur (par défaut 0).
        """
        super().__init__(x, y, width, height, color)

        pygame.draw.rect(self.surface, self.color, self.surface.get_rect())

        self.state = "IDLE"
        self.guidance = [0, 0]
        self.start_moving = time.time()
        self.speed_moving = Event.VELOCITY
        self.threshold_moving = 0.8
        self.start_idle = time.time()
        self.threshold_idle = 0.5
        self.all_projectiles = pygame.sprite.Group()
        self.nbrLifes = nbrLifes

    def move(self, guidance):
        """
        Déplace le joueur en fonction de la guidance.

        :param guidance: Liste contenant les directions de déplacement [x, y].
        :return: Nouvelle position du joueur (x, y).
        """

        originx = self.rect.x
        originy = self.rect.y

        if guidance[0] == 0 and guidance[1] == 0:
            self.start_moving = time.time()
            if self.state and self.state[0:4] != "IDLE":
                self.state = "IDLE" + self.state
                self.start_idle = time.time()
            else:
                if ((time.time() - self.start_idle) > self.threshold_idle):
                    self.state = "IDLE"
        else:
            if ((time.time() - self.start_moving) > self.threshold_moving) :
                #self.speed_moving *= Event.VELOCITY_UP
                self.speed_moving = self.speed_moving ** 2
                if self.speed_moving > Event.VELOCITY_MAX:
                    self.speed_moving = Event.VELOCITY_MAX
            else:
                self.speed_moving = Event.VELOCITY

            if guidance[1] > 0:
                if not(self.isStick()):
                    self.state = "DOWN"
                else:
                    self.state = "IDLE"
                    guidance[1] = 0
                self.rect.y += self.guidance[1]

            if guidance[0] > 0:
                self.state = "RIGHT"
                self.rect.x = self.rect.x + (self.speed_moving * guidance[0])
                if self.rect.x + (self.width//2) > Game2D.SIZE[0] :
                    self.rect.x = Game2D.SIZE[0] - (self.width//2) - 1

                x = (self.rect.x - (Game2D.SCREEN_SIZE[0]//2) if self.rect.x > (Game2D.SCREEN_SIZE[0]//2) else 0)
                if (Game2D.SIZE[0] - self.rect.x) < (Game2D.SCREEN_SIZE[0]//2):
                    x = Game2D.SIZE[0] - (Game2D.SCREEN_SIZE[0])

            if guidance[0] < 0:
                self.state = "LEFT"
                self.rect.x = self.rect.x + (self.speed_moving * guidance[0])
                if self.rect.x + (self.width//2) < 0 :
                    self.rect.x = 1 - (self.width//2)

            if guidance[1] < 0 and self.isStick():
                self.state = "UP"
                self.rect.y += guidance[1]
                self._setStick(None)

        if Event.lauch:
            self.start_idle = time.time()
            self.addProjectiles(self.guidance)

        if self.animations :
            self.animations.move(self.state)

        x = max(0, self.rect.x - (Game2D.SCREEN_SIZE[0] // 2))
        y = max(0, self.rect.y - (Game2D.SCREEN_SIZE[1] // 2))

        if (Game2D.SIZE[0] - self.rect.x) < ((Game2D.SCREEN_SIZE[0]//2)):
            x = Game2D.SIZE[0] - (Game2D.SCREEN_SIZE[0])

        if (Game2D.SIZE[1] - self.rect.y) < (Game2D.SCREEN_SIZE[1]//2):
            y = Game2D.SIZE[1] - ((Game2D.SCREEN_SIZE[1]))

        self.guidance = [originx - self.rect.x, originy - self.rect.y]

        if len(self.all_projectiles) > 0 :
            for projectile in self.all_projectiles:
                if projectile.move():
                    pygame.sprite.Group.remove(self.all_projectiles, projectile)

        return x, y

    def draw(self, screen, camera = Camera()):
        """
        Dessine le joueur sur l'écran.

        :param screen: Surface sur laquelle dessiner.
        :param camera: Caméra utilisée pour suivre le joueur.
        """
        if not self.hide :

            if self.animations :
                self.animations.draw(screen, camera, self.rect.x, self.rect.y)
                if DEBUG.active:
                    self.surface.convert_alpha()
                    self.surface.set_alpha(DEBUG.alpha)
                    self.surface.fill(DEBUG.color)
                    screen.blit(self.surface,
                            (self.rect.x - camera.x,
                             self.rect.y - camera.y))

            else:
                screen.blit(self.surface, (self.rect.x - camera.x, self.rect.y - camera.y))

            if len(self.all_projectiles) > 0 :
                for projectile in self.all_projectiles:
                    projectile.draw(screen)

    def addProjectiles(self, guidance):
        """
        Ajoute un projectile en fonction de la guidance.

        :param guidance: Liste contenant les directions de déplacement [x, y].
        """
        if guidance[0] != 0 or guidance[1] != 0:
            self.all_projectiles.add(Projectile(self.rect.x, self.rect.y, guidance))

    def getNbrLifes(self):
        """
        Obtient le nombre de vies du joueur.

        :return: Nombre de vies.
        """
        return self.nbrLifes

    def setNbrLifes(self, nbrLifes):
        """
        Définit le nombre de vies du joueur.

        :param nbrLifes: Nombre de vies à définir.
        """
        self.nbrLifes = nbrLifes

    def lessLifes(self, nbr = 1):
        """
        Réduit le nombre de vies du joueur.

        :param nbr: Nombre de vies à réduire (par défaut 1).
        """
        self.nbrLifes -= nbr

    def moreLifes(self, nbr = 1):
        """
        Augmente le nombre de vies du joueur.

        :param nbr: Nombre de vies à ajouter (par défaut 1).
        """
        self.nbrLifes += nbr

class Event:
    quit = False
    key = 0
    keydown = False
    guidance = [0, 0]
    mouse = False
    mousexy = [0, 0]
    button1 = False
    button2 = False
    lauch = False

    JUMP = 10
    VELOCITY = 2
    VELOCITY_MAX = 20
    VELOCITY_UP = 1.1

    key = 0

    GO_RIGHT = [pygame.K_RIGHT]
    GO_LEFT = [pygame.K_LEFT]
    UP_JUMP = [pygame.K_UP]
    TO_LAUNCH = [pygame.K_SPACE]
    GO_DOWN = [pygame.K_DOWN]

    screenRotation = False

    def set(events):
        """
        Met à jour les événements en fonction des interactions utilisateur.

        :param events: Liste des événements Pygame.
        """

        Event.quit = False
        Event.keydown = False
        Event.mouse = False
        Event.lauch = False

        if accelerometer.get_x() == 9:
            pass
        elif accelerometer.get_x() < -0.1:
            if Event.screenRotation :
                Event.guidance[0] = (accelerometer.get_x() * 10) * -1
            else:
                Event.guidance[1] = Event.JUMP * (-1)

        elif accelerometer.get_x() > 0.1:
            if Event.screenRotation :
                Event.guidance[0] = (accelerometer.get_x() * 10) * -1
            else:
                Event.guidance[1] = 0
        else:
            if Event.screenRotation :
                Event.guidance[0] = 0
            else:
                Event.guidance[1] = 0


        if accelerometer.get_y() == 9:
            pass
        elif accelerometer.get_y() < -0.1:
            if Event.screenRotation :
                Event.guidance[1] = Event.JUMP * (-1)
            else:
                Event.guidance[0] = (accelerometer.get_x() * 10)

        elif accelerometer.get_y() > 0.1:
            if Event.screenRotation :
                Event.guidance[1] = 0
            else:
                Event.guidance[0] = (accelerometer.get_x() * 10) * -1
        else:
            if Event.screenRotation :
                Event.guidance[1] = 0
            else:
                Event.guidance[0] = 0


        for event in events:
            if event.type == pygame.QUIT:
                Event.quit = True

            elif event.type == pygame.KEYDOWN:
                Event.keydown = True
                Event.key = event.key

                if event.key == pygame.K_ESCAPE:
                    Event.quit = True
                # Gestion du clavier et des mouvements
                if event.key in Event.GO_LEFT:
                    Event.guidance[0] = (-1*Event.VELOCITY)
                elif event.key in Event.GO_RIGHT:
                    Event.guidance[0] = Event.VELOCITY
                elif event.key in Event.UP_JUMP:
                    Event.guidance[1] = Event.JUMP * (-1)
                elif event.key in Event.TO_LAUNCH:
                    Event.lauch = True
                elif event.key in Event.GO_DOWN:
                    Event.guidance[1] = Event.VELOCITY

            elif event.type == pygame.KEYUP:
                if event.key in Event.GO_LEFT or event.key in Event.GO_RIGHT:
                    Event.guidance[0] = 0
                if event.key in Event.UP_JUMP :
                    Event.guidance[1] = 0
                Event.lauch = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    Event.mouse = True
                    Event.button1 = True
                elif event.button == 3:
                    Event.mouse = True
                    Event.button2 = True
            elif event.type == pygame.MOUSEBUTTONUP:
                Event.mouse = False
                Event.guidance = [0, 0]
                if event.button == 1:
                    Event.button1 = False
                elif event.button == 3:
                    Event.button2 = False
            elif event.type == pygame.MOUSEMOTION:
                x, y = event.rel
                #print("Mouvement de la souris à la position:", event.pos, "Relatif:", event.rel)
                if Event.mousexy != [x, y]:
                    Event.mouse = True
                    Event.mousexy[0], Event.mousexy[1] = event.pos

                if Event.button1 and Event.mouse:
                    if Event.screenRotation :
                        if y > 0:
                            Event.guidance[0] = -1 * Event.VELOCITY
                        elif y < 0:
                            Event.guidance[0] = Event.VELOCITY
                        elif x > 0:
                            Event.guidance[1] = Event.VELOCITY
                        elif x < 0:
                            Event.guidance[1] = Event.JUMP * (-1)
                        else :
                            Event.guidance = [0, 0]
                            Event.lauch = False
                    else :
                        if x < 0:
                            Event.guidance[0] = -1 * Event.VELOCITY
                        elif x > 0:
                            Event.guidance[0] = Event.VELOCITY
                        elif y > 0:
                            Event.guidance[1] = Event.VELOCITY
                        elif y < 0:
                            Event.guidance[1] = Event.JUMP * (-1)
                        else :
                            Event.guidance = [0, 0]
                            Event.lauch = False



class CollisionsManager:
    def __init__(self, gravity = None):
        """
        Initialise le gestionnaire de collisions.
        """
        self.collidersGroup = []
        self.movingObjectsGroup = []
        self.gravity = gravity

    def addCollider(self, collider):
        """
        Ajoute un collider au groupe de colliders.

        :param collider: Collider à ajouter.
        """
        self.collidersGroup.append(collider)
        if self.gravity:
            self.gravity.addFloor(collider)

    def getCollider(self):
        """
        Récupération du groupe de colliders.

        :return le groupe de collider
        """
        return self.collidersGroup


    def addMovingObject(self, movingObject):
        """
        Ajoute un objet en mouvement au groupe d'objets en mouvement.

        :param movingObject: Objet en mouvement à ajouter.
        """

        if isinstance(movingObject, list):
            for mobject in movingObject:
                self.movingObjectsGroup.append(mobject)
        elif isinstance(movingObject, EntitiesManager):
            for mobject in movingObject.getList():
                self.movingObjectsGroup.append(mobject)
        else:
            self.movingObjectsGroup.append(movingObject)

    def move(self):
        """
        Met à jour les positions des objets en mouvement en fonction des collisions.
        """
        for collider in self.collidersGroup:

            if isinstance(collider, pygame.sprite.Sprite):
                for movingObject in self.movingObjectsGroup:
                    self._handleCollision(movingObject, collider)

            if isinstance(collider, pygame.sprite.Group):
                for movingObject in self.movingObjectsGroup:
                    collides = pygame.sprite.spritecollide(movingObject, collider, False)
                    if collides and len(collides) > 0:
                        self._handleCollision(movingObject, collides[0])

    def _handleCollision(self, movingObject, collider):
        """
        Gère la collision entre un objet en mouvement et un collider.

        :param movingObject: Objet en mouvement.
        :param collider: Collider.
        """
        if movingObject.getGuidance()[0] != 0 or movingObject.getGuidance()[1] != 0 :
            while movingObject.rect.colliderect(collider):
                if movingObject.getGuidance()[0] != 0 :
                    movingObject.rect.x += 1 if movingObject.getGuidance()[0] > 0 else -1
                if movingObject.getGuidance()[1] != 0 :
                    movingObject.rect.y += 1 if movingObject.getGuidance()[1] > 0 else -1



class Gravity:
    def __init__(self, gravity=40):
        """
        Initialise le gestionnaire de gravité.

        :param gravity: Valeur de la gravité (par défaut 40).
        """
        self.gravity = gravity // 10
        self.collidersGroup = []
        self.collidersFloor = []

    def initFloor(self, floor):
        """
        Initialise le sol avec un objet ou une liste d'objets.

        :param floor: Objet ou liste d'objets représentant le sol.
        """
        self.collidersFloor = []
        self.collidersFloor.append(floor)

    def addFloor(self, floor):
        """
        Ajoute un sol au groupe de sols.

        :param floor: Objet ou liste d'objets représentant le sol.
        """
        self.collidersFloor.append(floor)
        if isinstance(floor, list):
            for f in floor:
                self.collidersFloor.append(f)
        else:
            self.collidersFloor.append(floor)

    def addObject(self, obj):
        """
        Ajoute un objet au groupe de colliders.

        :param obj: Objet ou liste d'objets à ajouter.
        """
        if isinstance(obj, list):
            for mobj in obj:
                self.collidersGroup.append(mobj)
        elif isinstance(obj, EntitiesManager):
            for mobj in obj.getList():
                self.collidersGroup.append(mobj)
        else:
            self.collidersGroup.append(obj)

    def move(self, guidance):
        """
        Met à jour les positions des objets en fonction de la gravité.

        :param guidance: Liste contenant les directions de déplacement [x, y].
        """
        if self.collidersGroup and self.collidersFloor :

            for collider in self.collidersGroup:

                if not (collider in self.collidersFloor):

                    if (collider.isStick() and
                        collider._getStick().getGuidance()[1] != 0 and
                        collider.getGuidance()[1] == 0):
                        collider.rect.y = collider._getStick().rect.y - collider.height

                    floorTouched = None
                    if collider.speed > 0:
                        collider._setStick(floorTouched)

                    origin = collider.rect.y
                    originy = origin
                    increment = 1 if collider.speed > 0 else -1

                    while (collider.rect.y != (origin + collider.speed) and
                          floorTouched is None) :

                        for floor in self.collidersFloor:
                            # Recherche d'un objet ou un groupe d'objets en collision avec un sol
                            if floor is not collider :
                                if isinstance(floor, pygame.sprite.Sprite):
                                    if floor.rect.colliderect(collider):
                                        floorTouched = floor
                                        break
                                if isinstance(floor, pygame.sprite.Group):
                                    collides = pygame.sprite.spritecollide(collider,
                                                                           floor,
                                                                           False)
                                    if collides and len(collides) > 0:
                                        floorTouched = collides[0]
                                        break

                        if floorTouched is None :
                            originy = collider.rect.y

                        if (floorTouched and
                            (collider.rect.y + collider.height - 5) >= floorTouched.rect.y):
                            floorTouched = None

                        collider.rect.y += increment

                    # un sol est touché
                    #if floorTouched and (originy + collider.height - 5) <= floorTouched.rect.y :
                    if floorTouched :
                        collider.rect.y = originy
                        collider.speed = 0
                        collider._setStick(floorTouched)
                    else:
                        collider.speed += self.gravity

"""
Exemple d'utilisation :

from classes.Game2D import Game2D, Player, Event, Animation, LifeBar, EntitiesManager, SpeechBubble
from classes.common import  Color, Shape, Circle, Text, DEBUG, Chronometer, PlannerShapes

class MyGame(Game2D):
    def __init__(
        self,
        caption,				# Titre du jeu
        game2D_width=6000,		# Espace du jeu en largeur en pixel
        game2D_height=800,		# Espace du jeu en hauteur en pixel
        screen_width=1200,		# Largeur de l’écran en pixel
        screen_height=600,		# Hauteur de l’écran en pixel
        fill_color=Color.LIGHTGRAY,  # Couleur du fond de l’écran
        fps=20				# Nombre d’images par seconde
    ):
        super().__init__(
            caption,
            game2D_width,
            game2D_height,
            screen_width,
            screen_height,
            fill_color,
            fps,
        )

    def myUpdateLevel(self, level, step):
        pass

    # Organiser tous les déplacements des objets de votre jeu
    def myUpdate(self):
        pass

    # Dessiner tous les objets de votre jeu
    # en arrière
    def myDisplayBehind(self, screen, camera):
        pass
    # devant
    def myDisplayInFront(self, screen, camera):
        pass

    # Initialiser tous les objets dont vous aurez besoin pour votre jeu
    def myInitialization(self):

        pass

# Lancement du jeu
# Amuse-toi à modifier l’écran
myGame = MyGame("Mon premier jeu",
                6016, 640,
                1200, 640,
                (220, 220, 240), 60)

myGame.run()
"""

class Game2D:

    SIZE = [3000, 600]
    SCREEN_SIZE = [800, 600]
    CAPTION = ""
    FILL_COLOR = Color.LIGHTGRAY
    FPS = 20

    def __init__(self,
                 caption,
                 game2D_width=3000,
                 game2D_height=3000,
                 screen_width=800,
                 screen_height=600,
                 fill_color=Color.LIGHTGRAY,
                 fps=20, screenRotation = False):
        """
        Initialise le jeu 2D.

        :param caption: Titre de la fenêtre du jeu.
        :param game2D_width: Largeur du monde du jeu (par défaut 3000).
        :param game2D_height: Hauteur du monde du jeu (par défaut 600).
        :param screen_width: Largeur de la fenêtre (par défaut 800).
        :param screen_height: Hauteur de la fenêtre (par défaut 600).
        :param fill_color: Couleur de remplissage de la fenêtre (par défaut Color.LIGHTGRAY).
        :param fps: Nombre d'images par seconde (par défaut 20).
        :param screenRotation: Indique si la fenêtre en paysage ou portrait (par défaut paysage).
        """

        self.FPS = fps

        self.screenRotation = screenRotation

        self.SIZE[0] = game2D_width
        self.SIZE[1] = game2D_height
        self.SCREEN_SIZE[0] = screen_width
        self.SCREEN_SIZE[1] = screen_height

        self.CAPTION = caption
        self.FILL_COLOR = fill_color
        self.color_darken = Color.BLACK
        self.darken = 200
        self.stepDarken = -5
        self.startChronoGame = time.time()
        self.startChronoLevel = 0
        self.startChronoStep = 0

        self.scheduler = PlannerShapes()

        self.player = None

        self.levels = None
        self.level = 0
        self.step = 0
        self.init_x = -1
        self.init_y = -1

        self.daylight = 0
        self.nightlight = 200

        self.day = 600
        self.step_day = 0

    def getHourDay(self):
        return self.day //60 if self.day > 0 else 0

    def getTimeDay(self):
        return self.day

    def setHourDay(self, hour):
        self.day = hour * 60

    def setTimeDay(self, time):
        self.day = time

    def getStepDay(self):
        return self.step_day

    def setStepDay(self, step=1):
        self.step_day = step

    # Fonction pour assombrir l'écran
    def darken_screen(self, color, screen, alpha):
        """
        Assombrit l'écran pour l'éclairer.

        :param color: Couleur de l'overlay.
        :param screen: Surface sur laquelle dessiner.
        :param alpha: Transparence de l'overlay.
        :return: Surface avec l'overlay appliqué.
        """
        overlay = pygame.Surface((self.SCREEN_SIZE[0], self.SCREEN_SIZE[1]), SRCALPHA)
        overlay.fill(color)
        overlay.set_alpha(alpha)
        screen.blit(overlay, (0, 0))
        return screen

    def setDarken(self, color = Color.BLACK, darken = 255, stepDarken = -20):
        """
        Définit les paramètres d'assombrissement de l'écran.

        :param color: Couleur de l'overlay (par défaut Color.BLACK).
        :param darken: Niveau d'assombrissement (par défaut 200).
        :param stepDarken: Incrément de changement de l'assombrissement (par défaut -20).
        """
        self.color_darken = color
        self.darken = darken
        self.stepDarken = stepDarken

    def getChronoLevel(self):
        """
        Obtient le temps écoulé depuis le début du niveau.

        :return: Temps écoulé en secondes.
        """
        return 0 if self.startChronoLevel ==0 else int(time.time() - self.startChronoLevel)

    def getChronoStep(self):
        """
        Obtient le temps écoulé depuis le début de l'étape.

        :return: Temps écoulé en secondes.
        """
        return 0 if self.startChronoStep == 0 else int(time.time() - self.startChronoStep)

    def setValidationStep(self, validationPoint):
        """
        Définit le point de validation pour l'étape.

        :param validationPoint: Point de validation (liste, tuple, Shape ou int).
        """
        if isinstance(validationPoint, list):
            self.init_x = validationPoint[0]
            self.init_y = validationPoint[1]
        elif isinstance(validationPoint,Entite2D):
            self.init_x = validationPoint.getX()
            self.init_y = validationPoint.getY() - validationPoint.getHeight()
        elif isinstance(validationPoint, tuple):
            self.init_x = validationPoint[0]
            self.init_y = validationPoint[1]
        elif isinstance(validationPoint, int):
            self.init_x = validationPoint
            self.init_y = self.init_y

        self.step += 1
        self.startChronoStep = time.time()

    def myUpdateLevel(self, level, step):
        """
        Met à jour le niveau et l'étape.
        Pose les règles du jeu en fonction du niveau et l'étape en cours

        :param level: Niveau actuel.
        :param step: Étape actuelle.
        """
        pass

    def myUpdate(self):
        """
        Met à jour les éléments personnalisés du jeu.
        """
        pass

    # Modification des objets du jeu
    def _update(self):
        """
        Met à jour les objets du jeu.
        """
        # Changement de niveau
        if self.levels:
            if self.levels.getCurrentLevel():
                if self.levels.getCurrentLevel().isChanged():
                    pygame.display.set_caption(self.CAPTION +
                                               " (" +
                                               self.levels.getCurrentLevel().name +
                                               ")")

        self.myUpdateLevel(self.level, self.step)

        self.myUpdate()

        if self.player :
            self.camera.x, self.camera.y = self.player.move(Event.guidance)

        if self.gravity:
            self.gravity.move(Event.guidance)

        if self.collisionsManager:
            self.collisionsManager.move()

        if self.destructionManager:
            self.destructionManager.move()

        if self.scheduler:
            self.scheduler.move()


    def myDisplayBehind(self, screen, camera = Camera()):
        """
        Affiche les éléments graphiques en arrière plan.

        :param screen: Surface sur laquelle dessiner.
        :param camera: Caméra utilisée pour suivre le joueur.
        """
        pass

    def myDisplayInFront(self, screen, camera = Camera()):
        """
        Affiche les éléments graphiques devant.

        :param screen: Surface sur laquelle dessiner.
        :param camera: Caméra utilisée pour suivre le joueur.
        """
        pass

    # Affichage du jeu
    def _display(self):
        """
        Affiche le jeu.
        """
        self.screen.fill(self.FILL_COLOR)

        screen = pygame.Surface((self.SCREEN_SIZE[0], self.SCREEN_SIZE[1]), SRCALPHA)


        self.myDisplayBehind(screen, self.camera)

        if self.levels and self.levels.getCurrentLevel():
            self.levels.getCurrentLevel().draw(screen, self.camera)


        if self.destructionManager:
            self.destructionManager.draw(screen, self.camera)

        self.myDisplayInFront(screen, self.camera)

        if self.scheduler:
            self.scheduler.draw(screen, self.camera)

        if self.darken > self.daylight:
            if self.stepDarken > 0 :
                self.stepDarken *=-1
            self.darken += self.stepDarken
            if self.darken < 0 :
                self.darken = 0
        elif self.darken < self.daylight:
            if self.stepDarken < 0 :
                self.stepDarken *=-1
            self.darken += self.stepDarken
            if self.darken > self.daylight :
                self.darken = self.daylight

        if self.darken > 0:
            screen = self.darken_screen(self.color_darken, screen, self.darken)

        if self.screenRotation :
            screen = pygame.transform.rotate(screen, 90)
        self.screen.blit(screen, (0, 0))

        pygame.display.update()

    def myInitialization(self):
        """
        Initialisation personnalisée des objets du jeu.
        """
        pass

    def setPlayer(self, player):
        """
        Définit le joueur.

        :param player: Joueur à définir.
        """
        self.player = player

    def loadTiled(self, fileName, path=None, level= -1, x = -1 , y = -1, sound=None, volume=0.05):
        """
        Charge un niveau à partir d'un fichier Tiled.

        :param fileName: Nom du fichier Tiled.
        :param path: Chemin du fichier Tiled (par défaut None).
        :param level: Niveau à charger (par défaut -1).
        :param x: Position x initiale du joueur (par défaut -1).
        :param y: Position y initiale du joueur (par défaut -1).
        :param sound: Chemin du fichier son (par défaut None).
        :param volume: Volume de la musique (par défaut 0.05).
        """
        self.levels = Levels_2D(fileName, path)
        if self.levels and self.levels.getCurrentLevel():
            self.level = self.level + 1 if level < 0 else level
            self.step = 0
            self.startChronoLevel = time.time()
            self.startChronoStep = time.time()
            self.gravity.initFloor(self.levels.getCurrentLevel().collidersFloor)
            self.collisionsManager.addCollider(self.levels.getCurrentLevel().collidersGroup)
            self.gravity.addFloor(self.levels.getCurrentLevel().collidersGroup)

        if self.player and x > 0 and y > 0:
            self.init_x = x
            self.init_y = y
            self.player.goToTarget([self.init_x, self.init_y])
            self.startChronoStep = time.time()

        if sound:
            # Charger la musique d'ambiance
            # 'sounds/ambiance/tearstream-alley-262939.mp3'
            pygame.mixer.music.load(sound)
            # Régler le volume de la musique d'ambiance (0.0 à 1.0)
            pygame.mixer.music.set_volume(volume)  # 50% du volume
            # Jouer la musique en boucle
            pygame.mixer.music.play(loops=-1)


    def goToStartOfLevel(self):
        """
        Déplace le joueur au début du niveau.
        """
        if self.player and self.init_x > 0 and self.init_y > 0:
            self.player.goToTarget([self.init_x, self.init_y])
            self.startChronoStep = time.time()

    def run(self, debug = False):
        """
        Lance le jeu.
        """
        DEBUG.active = debug

        # Initialisation du jeu et création de la fenêtre du jeu
        pygame.init()

        Board().begin()
        gui = GUI()

        Event.screenRotation = self.screenRotation

        if self.screenRotation :
            self.screen = pygame.display.set_mode((Game2D.SCREEN_SIZE[1],
                                                   Game2D.SCREEN_SIZE[0]))
        else:
            self.screen = pygame.display.set_mode((Game2D.SCREEN_SIZE[0],
                                                   Game2D.SCREEN_SIZE[1]))

        self.camera = Camera()

        pygame.display.set_caption(self.CAPTION)

        self.gravity = Gravity()
        self.collisionsManager = CollisionsManager(self.gravity)
        self.destructionManager = DestructionManager()

        running = True

        self.myInitialization()

        while running:

            # Vitesse d'affichage
            pygame.time.Clock().tick(self.FPS)

            # Gestion des intéractions clavier avec le joueur
            Event.set(pygame.event.get())
            if Event.quit:
                running = False
            if Event.key == pygame.KEYDOWN:
                running = False
            # Modification en cours du jeu
            self._update()
            # Affichage du jeu
            self._display()

            if self.step_day > 0 :

                self.day += self.step_day
                if self.day > 1440 :
                        self.day = 0
                if self.nightlight > 0 :
                    if self.day < 500 or self.day > 1320 :
                        self.daylight = self.nightlight
                    else:
                        self.daylight = 0

        # Arrêt du jeu
        pygame.quit()

