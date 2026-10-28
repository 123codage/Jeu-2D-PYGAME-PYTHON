"""
movement.py : entrées clavier/accéléromètre, physique du joueur, gravité,
collisions et destruction d'entités.

Principes :
- tout est basé sur le temps (dt en secondes) : le jeu se comporte pareil à 10, 20 ou 60 FPS
- unités : pixels et pixels/seconde (gravité en px/s²)
- déplacements résolus axe par axe (X puis Y) => plus de traversée de murs ni de saut "téléporté"
- positions sous-pixel conservées dans des restes (_rx, _ry) car pygame.Rect est entier
"""
import copy
import math
from itertools import chain

import pygame

from .common import Entite2D, Image, DEBUG

# L'accéléromètre n'existe que sur la carte Unihiker : import facultatif
try:
    from pinpong.extension.unihiker import accelerometer
except Exception:
    accelerometer = None


def _iter_sprites(container):
    """Parcourt un Sprite, un Group ou une liste (imbriquée) de sprites."""
    if container is None:
        return
    if isinstance(container, pygame.sprite.Sprite):
        yield container
    else:
        for item in container:
            yield from _iter_sprites(item)


def _approach(value, target, step):
    """Rapproche value de target de 'step' au maximum, sans dépasser."""
    if value < target:
        return min(value + step, target)
    return max(value - step, target)


# ---------------------------------------------------------------------------
# Entrées
# ---------------------------------------------------------------------------
class Event:
    quit = False
    key = 0
    keydown = False
    lauch = False                # tir (appui)

    move_x = 0.0                 # -1.0 (gauche) .. 1.0 (droite)
    jump_pressed = False         # front montant (une seule frame)
    jump_held = False            # touche maintenue (saut variable)
    down_held = False
    guidance = [0.0, 0.0]        # compatibilité avec l'ancien code

    JUMP = 150                   # hauteur du saut en pixels
    GO_RIGHT = [pygame.K_RIGHT]
    GO_LEFT = [pygame.K_LEFT]
    UP_JUMP = [pygame.K_UP, pygame.K_SPACE]
    TO_LAUNCH = [pygame.K_SPACE]
    GO_DOWN = [pygame.K_DOWN]

    screenRotation = False

    USE_TILT = False
    TILT_DEADZONE = 0.1
    _tilt_zero = None

    @staticmethod
    def _readTilt():
        """Retourne (déplacement -1..1, saut) depuis l'accéléromètre. Axes à calibrer selon la carte."""
        if not Event.USE_TILT or accelerometer is None:
            return 0.0, False
        try:
            ax, ay = accelerometer.get_x(), accelerometer.get_y()
        except Exception:
            return 0.0, False

        # La position de repos devient le "zéro" : plus de dérive permanente
        if Event._tilt_zero is None:
            Event._tilt_zero = (ax, ay)
        ax -= Event._tilt_zero[0]
        ay -= Event._tilt_zero[1]

        if Event.screenRotation:
            horizontal, vertical = -ax, ay
        else:
            horizontal, vertical = -ay, ax

        dz = Event.TILT_DEADZONE
        move = 0.0 if abs(horizontal) < dz else max(-1.0, min(1.0, horizontal * 2))
        return move, vertical < -dz

    @staticmethod
    def set(events):
        Event.quit = False
        Event.keydown = False
        Event.lauch = False
        Event.jump_pressed = False

        for ev in events:
            if ev.type == pygame.QUIT:
                Event.quit = True
            elif ev.type == pygame.KEYDOWN:
                Event.keydown = True
                Event.key = ev.key
                if DEBUG.active:
                    print("Key :", ev.key)
                if ev.key == pygame.K_ESCAPE:
                    Event.quit = True
                elif ev.key in Event.UP_JUMP:
                    Event.jump_pressed = True
                elif ev.key in Event.TO_LAUNCH:
                    Event.lauch = True

        # État continu des touches : pas de touche "collée" ni de perte d'appui
        keys = pygame.key.get_pressed()
        right = any(keys[k] for k in Event.GO_RIGHT)
        left = any(keys[k] for k in Event.GO_LEFT)
        Event.down_held = any(keys[k] for k in Event.GO_DOWN)
        move = float(right) - float(left)

        tilt_move, tilt_jump = Event._readTilt()
        if move == 0.0:
            move = tilt_move

        held = any(keys[k] for k in Event.UP_JUMP) or tilt_jump
        if tilt_jump and not Event.jump_held:
            Event.jump_pressed = True
        Event.jump_held = held

        Event.move_x = move
        Event.guidance[0] = move
        Event.guidance[1] = -1.0 if held else 0.0


# ---------------------------------------------------------------------------
# Projectile
# ---------------------------------------------------------------------------
class Projectile(pygame.sprite.Sprite):
    SPEED = 900  # px/s
    _image = None

    def __init__(self, x, y, direction, bounds):
        super().__init__()
        if Projectile._image is None:
            img = Image.load("images/", "bullet.png", (10, 10))
            if img is None:
                img = pygame.Surface((10, 10))
                img.fill((255, 220, 0))
            Projectile._image = img.convert_alpha()
        self.image = Projectile._image
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction
        self.bounds = bounds
        self._fx = float(self.rect.x)

    def move(self, dt):
        """Retourne True quand le projectile sort du monde."""
        self._fx += self.direction * self.SPEED * dt
        self.rect.x = int(self._fx)
        return not self.bounds.colliderect(self.rect)

    def draw(self, screen, camera):
        screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))


# ---------------------------------------------------------------------------
# Joueur
# ---------------------------------------------------------------------------
class Player(Entite2D):

    def __init__(self, x=10, y=10, width=50, height=50, color=(255, 255, 255), nbrLifes=0):
        super().__init__(x, y, width, height, color)
        pygame.draw.rect(self.surface, self.color, self.surface.get_rect())

        self.nbrLifes = nbrLifes
        self.all_projectiles = pygame.sprite.Group()
        self.bounds = pygame.Rect(0, 0, 10 ** 6, 10 ** 6)   # défini par Game2D.setPlayer
        self.world_gravity = 2000.0                          # défini par Gravity.addObject

        # Réglages "game feel" (modifiables depuis le jeu)
        self.max_speed = 320.0         # px/s
        self.accel = 2400.0            # px/s²
        self.friction = 3000.0         # px/s² (au sol sans appui)
        self.air_control = 0.6         # part de l'accélération disponible en l'air
        self.coyote_time = 0.10        # s : saut encore possible après avoir quitté le sol
        self.jump_buffer_time = 0.12   # s : saut mémorisé avant l'atterrissage
        self.jump_cut = 0.5            # coupe le saut si on relâche la touche
        self.fire_cooldown = 0.25

        # État
        self.vx = 0.0
        self.speed = 0.0               # vitesse verticale (px/s), lue par Gravity
        self._rx = 0.0
        self._ry = 0.0
        self._coyote = 0.0
        self._buffer = 0.0
        self._jumping = False
        self._fire_cd = 0.0
        self._idle_time = 0.0
        self.facing = 1
        self.state = "IDLE"

    # -- téléportation / respawn : on remet la vitesse à zéro -----------------
    def goto(self, x=None, y=None):
        super().goto(x, y)
        self.vx = 0.0
        self.speed = 0.0
        self._rx = self._ry = 0.0

    def move(self, dt, world=None):
        """
        Met à jour le joueur.
        :param dt: temps écoulé en secondes
        :param world: CollisionsManager (résolution des murs sur l'axe X)
        """
        ground = self.isStick()

        # --- minuteries (coyote time / jump buffering) ---
        self._coyote = self.coyote_time if ground else max(0.0, self._coyote - dt)
        self._buffer = self.jump_buffer_time if Event.jump_pressed else max(0.0, self._buffer - dt)
        self._fire_cd = max(0.0, self._fire_cd - dt)

        # --- horizontal : accélération / frottement ---
        direction = Event.move_x
        target = direction * self.max_speed
        if direction != 0:
            self.facing = 1 if direction > 0 else -1
            rate = self.accel * (1.0 if ground else self.air_control)
            if self.vx * direction < 0:          # demi-tour plus nerveux
                rate *= 2
        else:
            rate = self.friction if ground else self.friction * 0.2
        self.vx = _approach(self.vx, target, rate * dt)

        # --- saut : hauteur en pixels => vitesse initiale v = sqrt(2 g h) ---
        if self._buffer > 0 and self._coyote > 0:
            self.speed = -math.sqrt(2 * self.world_gravity * Event.JUMP)
            self._buffer = self._coyote = 0.0
            self._jumping = True
            self._setStick(None)
        elif self._jumping:
            if self.speed >= 0:
                self._jumping = False
            elif not Event.jump_held:            # saut variable : relâcher = saut plus court
                self.speed *= self.jump_cut
                self._jumping = False

        # --- déplacement horizontal avec résolution des murs ---
        self._rx += self.vx * dt
        dx = int(self._rx)
        self._rx -= dx
        if dx:
            self.rect.x += dx
            if world and world.resolve_x(self, dx):
                self.vx = 0.0
                self._rx = 0.0
        if self.rect.left < self.bounds.left:
            self.rect.left = self.bounds.left
            self.vx = 0.0
        elif self.rect.right > self.bounds.right:
            self.rect.right = self.bounds.right
            self.vx = 0.0
        self.guidance = [dx, 0]

        # --- tir ---
        if Event.lauch and self._fire_cd == 0.0:
            self._fire_cd = self.fire_cooldown
            self.all_projectiles.add(
                Projectile(self.rect.centerx, self.rect.centery, self.facing, self.bounds))
        for p in list(self.all_projectiles):
            if p.move(dt):
                p.kill()

        # --- état d'animation ---
        moving = abs(self.vx) > 10
        if not ground:
            if self.speed < 0:
                self.state = "UP"
            else:
                self.state = ("RIGHT" if self.facing > 0 else "LEFT") if moving else "DOWN"
            self._idle_time = 0.0
        elif moving:
            self.state = "RIGHT" if self.vx > 0 else "LEFT"
            self._idle_time = 0.0
        else:
            self._idle_time += dt
            if self._idle_time > 0.5:
                self.state = "IDLE"
            else:
                self.state = "IDLERIGHT" if self.facing > 0 else "IDLELEFT"

        if self.animations:
            self.animations.move(self.state)

    def bounce(self, factor=0.6):
        """Rebond après avoir sauté sur un ennemi."""
        self.speed = -math.sqrt(2 * self.world_gravity * Event.JUMP * factor)
        self._setStick(None)

    def draw(self, screen, camera):
        if self.hide:
            return
        if self.animations:
            self.animations.draw(screen, camera, self.rect.x, self.rect.y)
            if DEBUG.active:
                self.surface.set_alpha(DEBUG.alpha)
                self.surface.fill(DEBUG.color)
                screen.blit(self.surface, (self.rect.x - camera.x, self.rect.y - camera.y))
        else:
            screen.blit(self.surface, (self.rect.x - camera.x, self.rect.y - camera.y))
        for p in self.all_projectiles:
            p.draw(screen, camera)

    # -- vies ---------------------------------------------------------------
    def getNbrLifes(self):
        return self.nbrLifes

    def setNbrLifes(self, nbrLifes):
        self.nbrLifes = nbrLifes

    def lessLifes(self, nbr=1):
        self.nbrLifes = max(0, self.nbrLifes - nbr)

    def moreLifes(self, nbr=1):
        self.nbrLifes += nbr


# ---------------------------------------------------------------------------
# Gravité (axe Y) : sols à sens unique, murs pleins, plateformes mobiles
# ---------------------------------------------------------------------------
class Gravity:
    TERMINAL_SPEED = 1400.0   # px/s
    STEP_TOLERANCE = 6        # px : marge pour considérer qu'on se pose sur un sol

    def __init__(self, gravity=2000):
        """:param gravity: accélération en px/s² (2000 environ = saut de 150 px avec v0=775)."""
        self.gravity = float(gravity)
        self.objects = []
        self.floors = []    # traversables par le bas (plateformes)
        self.solids = []    # pleins (murs, sols Tiled "collidersGroup")

    # -- déclaration ---------------------------------------------------------
    def initFloor(self, floor):
        self.floors = []
        self.addFloor(floor)

    def addFloor(self, floor):
        self.floors.append(floor)

    def addSolid(self, solid):
        self.solids.append(solid)

    def clearSolids(self):
        self.solids = []

    def addObject(self, obj):
        if isinstance(obj, (list, tuple)):
            for o in obj:
                self.addObject(o)
            return
        if hasattr(obj, "getList"):        # EntitiesManager
            for o in obj.getList():
                self.addObject(o)
            return
        if obj not in self.objects:
            obj.world_gravity = self.gravity
            self.objects.append(obj)

    def removeObject(self, obj):
        if obj in self.objects:
            self.objects.remove(obj)

    # -- simulation ----------------------------------------------------------
    def move(self, dt):
        for obj in self.objects:
            self._apply(obj, dt)

    def _apply(self, obj, dt):
        rect = obj.rect

        # 1) suivre la plateforme sur laquelle on est posé (mobile ou non)
        floor = obj._getStick()
        last = getattr(obj, "_stick_pos", None)
        if floor is not None and last is not None:
            rect.x += floor.rect.x - last[0]
            rect.y += floor.rect.y - last[1]

        # 2) gravité + déplacement vertical (avec reste sous-pixel)
        obj.speed = min(obj.speed + self.gravity * dt, self.TERMINAL_SPEED)
        total = obj.speed * dt + getattr(obj, "_ry", 0.0)
        dy = int(total)
        obj._ry = total - dy
        obj._setStick(None)

        prev_bottom = rect.bottom
        rect.y += dy

        if dy < 0:
            # plafond : on cogne la tête sous un solide
            for s in _iter_sprites(self.solids):
                if s is not obj and rect.colliderect(s.rect):
                    rect.top = s.rect.bottom
                    obj.speed = 0.0
                    obj._ry = 0.0
        else:
            # atterrissage : le sol le plus haut atteint depuis le dessus
            tol = self.STEP_TOLERANCE
            probe = pygame.Rect(rect.left, prev_bottom - tol, rect.width, tol + 1 + dy)
            best = None
            for s in chain(_iter_sprites(self.floors), _iter_sprites(self.solids)):
                if s is obj:
                    continue
                r = s.rect
                if probe.colliderect(r) and r.top >= prev_bottom - tol:
                    if best is None or r.top < best.rect.top:
                        best = s
            if best is not None:
                rect.bottom = best.rect.top
                obj.speed = 0.0
                obj._ry = 0.0
                obj._setStick(best)
                obj._stick_pos = best.rect.topleft


# ---------------------------------------------------------------------------
# Collisions horizontales et sécurité anti-incrustation
# ---------------------------------------------------------------------------
class CollisionsManager:
    def __init__(self, gravity=None):
        self.collidersGroup = []
        self.movingObjectsGroup = []
        self.gravity = gravity

    def addCollider(self, collider):
        self.collidersGroup.append(collider)
        if self.gravity:
            self.gravity.addSolid(collider)

    def clearColliders(self):
        self.collidersGroup = []
        if self.gravity:
            self.gravity.clearSolids()

    def getCollider(self):
        return self.collidersGroup

    def addMovingObject(self, movingObject):
        if isinstance(movingObject, (list, tuple)):
            for m in movingObject:
                self.addMovingObject(m)
        elif hasattr(movingObject, "getList"):
            for m in movingObject.getList():
                self.addMovingObject(m)
        elif movingObject not in self.movingObjectsGroup:
            self.movingObjectsGroup.append(movingObject)

    def removeMovingObject(self, obj):
        if obj in self.movingObjectsGroup:
            self.movingObjectsGroup.remove(obj)

    def resolve_x(self, obj, dx):
        """Repousse obj hors des solides après un déplacement horizontal dx. True si choc."""
        hit = False
        for s in _iter_sprites(self.collidersGroup):
            if s is not obj and obj.rect.colliderect(s.rect):
                if dx > 0:
                    obj.rect.right = s.rect.left
                else:
                    obj.rect.left = s.rect.right
                hit = True
        return hit

    def move(self):
        """Sécurité : sort de force les objets (monstres...) incrustés dans un solide."""
        for obj in self.movingObjectsGroup:
            for s in _iter_sprites(self.collidersGroup):
                if s is obj or not obj.rect.colliderect(s.rect):
                    continue
                r, w = obj.rect, s.rect
                pushes = (
                    (w.right - r.left, 1, 0),    # vers la droite
                    (r.right - w.left, -1, 0),   # vers la gauche
                    (w.bottom - r.top, 0, 1),    # vers le bas
                    (r.bottom - w.top, 0, -1),   # vers le haut
                )
                depth, sx, sy = min(pushes, key=lambda p: p[0])
                r.x += sx * depth
                r.y += sy * depth


# ---------------------------------------------------------------------------
# Destruction animée
# ---------------------------------------------------------------------------
class DestructionManager:
    def __init__(self):
        self.entitiesDestroyGroup = []

    def addEntity(self, entity, delay=0, animation=None):
        new = copy.copy(entity)
        # copie propre de l'animation, sinon on modifie celle des entités encore vivantes
        if entity.animations:
            new.animations = copy.copy(entity.animations)
        self.entitiesDestroyGroup.append((new, delay, pygame.time.get_ticks()))
        if new.animations and animation:
            new.animations.move(animation)

    def move(self):
        now = pygame.time.get_ticks()
        # on reconstruit la liste (l'ancienne version la modifiait pendant le parcours)
        self.entitiesDestroyGroup = [i for i in self.entitiesDestroyGroup
                                     if now - i[2] < i[1] * 1000]
        for item in self.entitiesDestroyGroup:
            item[0].move()

    def draw(self, screen, camera):
        for item in self.entitiesDestroyGroup:
            item[0].draw(screen, camera)
