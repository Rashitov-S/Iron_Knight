import random
import pygame

from groups import SpriteGroup
from methods import load_image

damage_text_group = SpriteGroup()


class DamageText(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, color=(255, 0, 0), outline_color=(0, 0, 0),
                 outline_thickness=1, duration=100, rise_speed=1, size=32):
        super().__init__(damage_text_group)
        self.x = x
        self.y = y
        self.damage = str(damage)
        self.color = color
        self.duration = duration
        self.rise_speed = rise_speed
        self.outline_color = outline_color
        self.outline_thickness = outline_thickness
        self.alpha = 255
        self.expire_timer = 0
        self.font = pygame.font.Font(None, size)
        self.x += random.randint(-20, 20)
        self.y += random.randint(-10, 10)
        self.image = None
        self.rect = None
        self._update_surfaces()

    def update(self):
        self.y -= self.rise_speed
        self.expire_timer += 1
        if self.expire_timer >= self.duration:
            self.alpha -= 10
            if self.expire_timer >= self.duration + 60:
                print("убил текст")
                self.kill()
        self._update_surfaces()

    def _update_surfaces(self):
        text_surface = self.font.render(self.damage, True, self.color)
        outline_surface = self.font.render(self.damage, True, self.outline_color)

        text_surface.set_alpha(int(self.alpha))
        outline_surface.set_alpha(int(self.alpha))

        width = text_surface.get_width() + 2 * self.outline_thickness
        height = text_surface.get_height() + 2 * self.outline_thickness
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)

        for dx in range(-self.outline_thickness, self.outline_thickness + 1):
            for dy in range(-self.outline_thickness, self.outline_thickness + 1):
                if dx == 0 and dy == 0:
                    continue
                self.image.blit(outline_surface,
                                (self.outline_thickness + dx,
                                 self.outline_thickness + dy))

        self.image.blit(text_surface,
                        (self.outline_thickness,
                         self.outline_thickness))

        self.rect = self.image.get_rect(center=(self.x, self.y))

class MoneyText(DamageText):
    def __init__(self, x, y, count, color=(255, 215, 0), outline_color=(0, 0, 0), outline_thickness=1, duration=150, rise_speed=0.7, size=42):
        super().__init__(x, y, f"{count}$", color, outline_color, outline_thickness, duration, rise_speed, size)
