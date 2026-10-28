import pygame
from .common import DEBUG


class Level_2D:
    """
    Niveau Tiled.
    Optimisation principale : toutes les tuiles sont dessinées UNE SEULE FOIS dans une grande
    surface au chargement ; à chaque frame on ne copie que la zone visible (1 blit au lieu
    de plusieurs milliers).
    """

    def __init__(self, name,
                 nbrTilesWidth, nbrTilesHeight,
                 tileWidth, tileHeight,
                 tilesGroup,
                 collidersFloor,
                 collidersGroup):
        self.name = name
        self.new = True
        self.nbrTilesWidth = nbrTilesWidth
        self.nbrTilesHeight = nbrTilesHeight
        self.tileWidth = tileWidth
        self.tileHeight = tileHeight
        self.tilesGroup = tilesGroup
        self.collidersFloor = collidersFloor
        self.collidersGroup = collidersGroup
        self.surface = self._prerender()

    def _prerender(self):
        width, height = self.getSize()
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        surface.blits([(s.image, s.rect) for s in self.tilesGroup], doreturn=False)
        # Pour de très grands niveaux (> ~50 millions de pixels), découper en blocs.
        return surface.convert_alpha()

    def draw(self, screen, camera):
        view = pygame.Rect(max(0, int(camera.x)), max(0, int(camera.y)), *screen.get_size())
        screen.blit(self.surface, (0, 0), view)

        if DEBUG.active:
            for group in (self.collidersGroup, self.collidersFloor):
                for sprite in group:
                    if sprite.rect.colliderect(view):
                        screen.blit(sprite.image,
                                    (sprite.rect.x - view.x, sprite.rect.y - view.y))

    def getSize(self):
        return (self.nbrTilesWidth * self.tileWidth, self.nbrTilesHeight * self.tileHeight)

    def collide(self, player, direction):
        if hasattr(player, "moveCollider"):
            player.moveCollider(direction)
        if not self.collidersGroup:
            return None
        collides = pygame.sprite.spritecollide(player, self.collidersGroup, False)
        return collides or None

    def isChanged(self):
        new = self.new
        self.new = False
        return new
