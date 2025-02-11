import pygame


class SpriteGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()

    def get_event(self, event):
        for sprite in self:
            sprite.get_event(event)

    def get_sprites(self):
        sprites = []
        for sprite in self:
            sprites.append(sprite)
        return sprites