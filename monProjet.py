from classes.Game2D import Game2D, Player, Event, Animation, LifeBar, EntitiesManager, SpeechBubble, TeleportationPoint
from classes.common import Color, Shape, Circle, Text, DEBUG, Chronometer, PlannerShapes, ShapeImage


class MyGame(Game2D):
    def __init__(
        self,
        caption,				# Titre du jeu
        game2D_width=6000,		# Espace du jeu en largeur en pixel
        game2D_height=800,		# Espace du jeu en hauteur en pixel
        screen_width=1200,		# Largeur de l’écran en pixel
        screen_height=600,		# Hauteur de l’écran en pixel
        fill_color=Color.LIGHTGRAY,	# Couleur du fond de l’écran
        fps=20,				# Nombre d’images par seconde
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

    Génération du player et de ses animations graphiques et sonores

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
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

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

    Génération des jetons avec les animations graphiques et sonores

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def generateToken(self):
        # Animations graphiques du jeton
        ANIMATIONS_TOKEN = {
            "WAIT": ["token01.png", "token02.png", "token03.png", "token04.png"],
            "DEAD": ["token_dead.png"],
        }
        # son lorsque le jeton est touché par le joueur
        SOUNDS_TOKEN = { "DEAD" : ["hit_12.wav"]}

        # création de l'animation du jeton
        animationToken = Animation(ANIMATIONS_TOKEN, "images/token", (128, 128), scale=0.25, delay=6, soundAnimation = SOUNDS_TOKEN, soundPath = "sounds")
        # création d'un token et affectation de son animation
        token = Circle(50, 50, 16, (255, 255, 0))
        token.loadAnimations(animationToken, "WAIT")
        return token


    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

    Génération des monstres avec les animations graphiques et sonores

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def generateMonster(self):

        ANIMATIONS_MONSTER = {
            "DEAD": ["Pink_Monster_Dead_4.png:4:H"],
            "WALK": ["Pink_Monster_Walk_6.png:6:H"],
        }

        SOUNDS_MONSTER = { "DEAD" : ["sf_defenestration_01.mp3"]}

        animationMonster = Animation(ANIMATIONS_MONSTER, "images/Monsters", (32, 32), scale=1, delay=1, soundAnimation = SOUNDS_MONSTER, soundPath = "Sounds")

        monster = Shape(300, 750, 32, 32, Color.RED)
        monster.loadAnimations(animationMonster, "WALK", 0, 0)

        return monster

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

    Génération des points de passages

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def generateFlag(self):

        ANIMATIONS_FLAG = {
            "FLOATING": ["red flag.png:5:H"],
            "FIXED": ["red flag.png:1:H"],
        }

        animationFlag = Animation(ANIMATIONS_FLAG, "images/flag", (64, 64), scale=0.5, delay=10)

        flag = Shape(200, 513, 32, 32, Color.RED)
        flag.loadAnimations(animationFlag, "FIXED", 0, 0)

        return flag

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

    Génération des portes

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

    class Gate():
        # Initialisation de l'objet
        def __init__(self):
            ANIMATIONS_GATE = {"OPEN": ["door 02 64x64.png:2:H"]}

            animationGate = Animation(ANIMATIONS_GATE, "images/gates", (64, 64), scale=1, delay=10)

            self.gate = Shape(1410, 355, 128, 64, Color.RED)
            self.gate.loadAnimations(animationGate, "OPEN", -32, 0)
            self.state = False

            self.teleportationPoint = TeleportationPoint((2000,355), 1470, 355)

        def move(self):
            self.state = not self.state
            self.gate.move()

        def draw(self, screen, camera):
            self.gate.draw(screen, camera)

        def isOpen(self):
            return self.state

        def isCollide(self, collider):
            return self.gate.isCollide(collider)

        def isTeleport(self, collider):
            return self.teleportationPoint.isCollide(collider)

        def goTeleport(self, collider):
            self.teleportationPoint.go(collider)

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

    Génération des jetons avec les animations graphiques et sonores

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def generateBigBird(self):
        # Animations graphiques du jeton
        ANIMATIONS = {
            "FLY": ["parrot-a.png", "parrot-b.png"],
            "DEAD": ["parrot-b.png"]        }
        # son lorsque le jeton est touché par le joueur
        SOUNDS = { "DEAD" : ["hit_12.wav"]}

        # création de l'animation du jeton
        animationBird = Animation(ANIMATIONS, "images/bird", (169, 142), scale=0.25, delay=10, soundAnimation = SOUNDS, soundPath = "sounds")
        bird = Shape(100, 100, 42, 35, Color.RED)
        bird.loadAnimations(animationBird, "FLY")
        bird.moveToTarget([2000,300],5)
        return bird

    def generateLittleBird(self):
        # Animations graphiques du jeton
        ANIMATIONS = {
            "FLY": ["parrot-a.png", "parrot-b.png"],
            "DEAD": ["parrot-b.png"]        }
        # son lorsque le jeton est touché par le joueur
        SOUNDS = { "DEAD" : ["hit_12.wav"]}

        # création de l'animation du jeton
        animationBird = Animation(ANIMATIONS, "images/bird", (169, 142), scale=0.15, delay=8, soundAnimation = SOUNDS, soundPath = "sounds")        # création d'un token et affectation de son animation
        bird = Shape(50, 50, 25, 21, Color.RED)
        bird.loadAnimations(animationBird, "FLY")
        bird.moveToTarget([2000,100],3)
        birds = EntitiesManager(bird, 1, 100, 100, 600, Game2D.SIZE[1]-300)
        bird.moveToTarget([1500,500],5)
        birds.addEntity(bird)
        bird.moveToTarget([2000,100],3)
        birds.addEntity(bird)

        return birds

    def myUpdateLevel(self, level, step):
        global flags
        global monsters
        global tokens

        """
        Chargement des niveaux
        """
        # Chargement du niveau 1
        if level == 0 :
            self.setDarken()
            # Chargement des maps TILED
            self.loadTiled("Farwest Level 01.tmx", "tiled", level=1, x=200, y=400, sound="sounds/ambiance/tearstream-alley-262939.mp3")

            # Gestion de l'action de la gravité sur le joueur avec le sol
            # Déclaration des sols
            #self.gravity.addFloor(sol)
            self.gravity.addFloor(platform01)
            self.gravity.addFloor(platform02)
            self.gravity.addFloor(platform03)
            self.gravity.addFloor(platform04)


            # Génération des jetons
            token = self.generateToken()
            # générateur de topkens
            tokens = None
            tokens = EntitiesManager(token, 10, 20, 250, Game2D.SIZE[0]-100, Game2D.SIZE[1]-180)
            #tokens = EntitiesManager(token, ((120,300),(400,200),(800,100),(1100,210)))
            tokens.moveToTarget([0,100],10)

            platform01.moveToTarget([0,100],5)
            platform04.moveToTarget([0,150],2)


            # Générations des flags
            flag = self.generateFlag()
            flags = EntitiesManager(flag, ((3500,402), (7900,102), (Game2D.SIZE[0]-300, 545)))


        # Chargement du niveau 2
        if level == 1 and step == 3 and player.rect.x > Game2D.SIZE[0] - 40 :
            self.setDarken(Color.BLUE)
            self.loadTiled("Farwest Level 02 bis.tmx", "tiled", level=2, x=400, y=400)

            platform01.setStartPoint((350,280))
            platform02.setStartPoint((1000,400))
            platform03.setStartPoint((1500,400))
            platform01.goToTarget(platform01.getStartPoint())

            platform01.setColor(Color.BLUE, 100)

            self.gravity.addFloor(platform01)
            self.gravity.addFloor(platform02)
            self.gravity.addFloor(platform03)

            platform01.moveToTarget([0,100],5)
            platform02.moveToTarget([0,200],5)
            platform03.moveToTarget([100,0],5)

            flag = self.generateFlag()
            flags = EntitiesManager(flag, ((800,182),(Game2D.SIZE[0]-300, 545)))

        """
        Gestion du niveau 1
        """
        if level == 1 :
            """
            Génération de monstres au niveau 1 après 3 secondes de jeu
            """
            if monsters == None and self.getChronoLevel() > 3 :
                monster = self.generateMonster()
                monsters = None
                monsters = EntitiesManager(monster, 10, 100, 150, Game2D.SIZE[0], Game2D.SIZE[1]-300)
                monsters.moveToTarget(player,5)
                self.gravity.addObject(monsters)
                self.collisionsManager.addMovingObject(monsters)
            """
            controle du temps du joueur sur le niveau 1
            """
            if step == 0 and self.getChronoStep() >= 40 and not(chrono.isStarted()) :
                chrono.start(10)

            if step == 1 and self.getChronoStep() >= 190 and not(chrono.isStarted()) :
                chrono.start(10)


            if chrono.isFinished():
                chrono.stop()
                self.goToStartOfLevel() # le joueur repart au début de la scène
                self.player.lessLifes() # il perd une vie
                hearts.refresh(self.player.getNbrLifes())
                speechBubblePlayer.goToTarget(player, "Zut  fin de mon temps ...")
                speechBubblePlayer.setShow(True,3)




    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

    Conditions et déplacements des objets de votre jeu

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def myUpdate(self):
        global flags
        global closedGate

        """
        Mouvements pour tous les niveaux
        """
        # Faire bouger les plateformes
        platform01.move()
        platform02.move()
        platform03.move()
        platform04.move()

        if gate :
            if gate.isCollide(player) :
                if not gate.isOpen() :
                    gate.move()
                if gate.isTeleport(player):
                    self.setDarken(Color.GREEN, darken = 80)
                    gate.goTeleport(player)
            else:
                if gate.isOpen() :
                    gate.move()

        if monsters :
            monsters.move()
            # Quand un monstre rencontre le palyer
            monster = monsters.isCollide(player)
            if monster :
                if monster.isJumpOnIt(player):
                    # Création d'un monstre qui va mourir
                    self.destructionManager.addEntity(monster,1, "DEAD")
                    # Destruction du monstre dans la liste des monstres
                    monsters.remove_entity(monster)
                    speechBubblePlayer.goToTarget(player, "Un de moins ...")
                    speechBubblePlayer.setShow(True,3)
                else :
                    # Le joueur recommence au début du niveau
                    self.goToStartOfLevel()
                    speechBubblePlayer.goToTarget(player, "Je suis touché ...")
                    speechBubblePlayer.setShow(True,3)
                    # Le joueur perd une vie
                    if self.player.getNbrLifes() > 0:
                        self.player.lessLifes()
                        hearts.refresh(self.player.getNbrLifes())

        if tokens :
            # Gestion des collisions avec les tokens
            tokens.move()
            # si collision entre le joueur et un des tokens
            token = tokens.isCollide(player)

            # si un token a été touché alors animer et programmer sa disparition
            # Si un jeton touché ajout d'une vie
            if token :
                self.destructionManager.addEntity(token,1, "DEAD")
                tokens.remove_entity(token)
                self.player.moreLifes()
                hearts.refresh(self.player.getNbrLifes())

        # Si le joueur sort de la scène vers le bas, et tombe hors du jeu
        if player.rect.y > Game2D.SIZE[1] :
            self.goToStartOfLevel() # le joueur repart au début de la scène
            self.player.lessLifes() # il perd une vie
            hearts.refresh(self.player.getNbrLifes())
            speechBubblePlayer.goToTarget(player, "Zut, je repars au début de l'étape ...")
            speechBubblePlayer.setShow(True,3)

        # Mouvement des indicateurs
        if flags :
            flags.move()
            flag = flags.isCollide(player)

            # Si l'indicateur est touché alors changement d'étape
            if flag and flag.getCurrentAnimation() == "FIXED":
                speechBubblePlayer.goToTarget(player, "Chouette je passe à l'étape suivante ...")
                speechBubblePlayer.setShow(True,3)

                # Animation du FLAG
                flag.setAnimation("FLOATING")
                # Plus 1 dans les étapes du jeu
                self.setValidationStep(flag)
                chrono.stop()

        if speechBubblePlayer :
            speechBubblePlayer.move()

        littleBirds.move()
        if bigBirds :
            bigBirds.move()


    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

    Dessiner les objets de votre jeu

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def myDisplayBehind(self, screen, camera):
        imageFond.draw(screen)
        sun.draw(screen)


    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

    Dessiner les objets de votre jeu

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    # devant
    def myDisplayInFront(self, screen, camera):

        # Dessin des plateformes
        platform01.draw(screen, camera)
        platform02.draw(screen, camera)
        platform03.draw(screen, camera)
        platform04.draw(screen, camera)

        if gate :
            gate.draw(screen, camera)

        if tokens :
            # Dessin des jetons
            tokens.draw(screen, camera)

        # Dessin des monstres
        if monsters :
            monsters.draw(screen, camera)

        # Dessin des monstres
        if flags :
            flags.draw(screen, camera)

        littleBirds.draw(screen, camera)
        if bigBirds :
            bigBirds.draw(screen, camera)

        # Dessin du joueur
        player.draw(screen, camera)

        # Affichage du niveau
        if levelDisplay :
            levelDisplay.setText(str(self.level) + " step : " + str(self.step))
            levelDisplay.draw(screen)

        # Affichage des nombre de vies
        hearts.draw(screen)

        chrono.draw(screen)

        if speechBubblePlayer :
            speechBubblePlayer.draw(screen, camera)



    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

    Initialisation du jeu
    Initialiser tous les objets dont vous aurez besoin pour votre jeu

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

    def myInitialization(self):
        global player
        global platform01
        global platform02
        global platform03
        global platform04
        global platform05
        global wall01
        global levelDisplay
        global hearts
        global monsters
        global chrono
        global flags
        global speechBubblePlayer
        global littleBirds
        global bigBirds
        global gate
        global imageFond
        global sun

        # Création d'un joueur
        player = self.generatePlayer()

        # Indication au moteur du jeu le joueur
        self.setPlayer(player)
        # Création des plateformes
        platform01 = Shape(5000, 480, 300, 30, (77, 52, 37), "01")
        platform02 = Shape(730, 380, 500, 30, (77, 52, 37))
        platform03 = Shape(1260, 280, 50, 30, (77, 52, 37))
        platform04 = Shape(10000, 400, 400, 30, (77, 52, 37), "04")

        gate = self.Gate()

        # Création de murs
        wall01 = Shape(730, 390, 500, 700, (255,200,10))

        monsters = None
        flags = None

        # Déclaration des objets soumis à la gravité
        self.gravity.addObject(player)

        # Déclaration des objets en mouvement qui peuvent rentrer en collision
        self.collisionsManager.addMovingObject(player)

        # Gestion de la force du saut du joueur
        Event.JUMP = 150

        # Gestion de la vitesse de déplacement du joueur
        Event.VELOCITY = 3
        Event.VELOCITY_UP = 1.1
        Event.VELOCITY_MAX = 20

        # Gestion des touches de déplacement du joueur
        Event.GO_RIGHT.append(100)
        Event.GO_LEFT.append(113)
        Event.UP_JUMP.append(122)

        # Création d'un chronmètre pour indiquer au joueur le temps restant sur une étape du jeu
        chrono = Chronometer(Text("Step finished at : ", (Game2D.SCREEN_SIZE[0]/2)-80, 10, size=24), None, "bip.wav", "Sounds")

        # génération de la barre des vies
        hearts = LifeBar(self.player.getNbrLifes(), "heart.png", "images/token", 10, 10, alpha=100)

        speechBubblePlayer = SpeechBubble(100,100,200,10,Color.BUBBLE,20,-10, "Boite de dialogue du joueur", size = 20)
        speechBubblePlayer.setShow(False)


        littleBirds = self.generateLittleBird()


        bigBird = self.generateBigBird()
        bigBirds = None
        bigBirds = EntitiesManager(bigBird, 5, 100, 100, 600, Game2D.SIZE[1]-300)

        levelDisplay = Text("Level : ", (Game2D.SCREEN_SIZE[0]/2)-50 , Game2D.SCREEN_SIZE[1]-10, Color.RED,size = 16)

        imageFond = ShapeImage("tiled/farwest/Background","Background_01.png")
        sun = Circle(50, 50, 50, (255,255,0))

"""
Lancement du jeu
- titre du jeu
- largeur de l'espace du jeu en pixel
- hauteur de l'espace du jeu en pixel
- largeur de la fenêtre de jeu en pixel
- hauteur de la fenêtre de jeu en pixel
- couleur de fond de la fenêtre de jeu
- FPS nombres d'images par seconde
"""

# Amuse-toi à modifier l’écran
myGame = MyGame("Mon premier jeu",
                			11520, 640,
                			1200, 640,
                            (220, 220, 240), 10, False)

myGame.run()

