import random

import pygame
from groups import SpriteGroup
from methods import load_image
from damage_numbers import MoneyText
from interface import ShopMenu

trap_group = SpriteGroup()
shop_group = SpriteGroup()

FIRE = [load_image(f"traps/fire/{x}.png") for x in range(1, 20)]
ELECTRIC_FIELD = [load_image(f"traps/electric/{x}.png") for x in range(1, 10)]
POISON_CLOUD = [load_image(f"traps/poison/{x}.png") for x in range(1, 20)]

TREE = [load_image("decorations/tree/1.png")]
TOMBSTONE = [load_image(f"decorations/tombstones/{x}.png") for x in range(1, 4)]

SHOP = [load_image(f"decorations/shop/{x}.png") for x in range(1, 7)]
CHEST = [load_image(f"decorations/chest/{x}.png") for x in range(1, 8)]
PORTAL = [load_image(f"decorations/portal/{x}.png") for x in range(1, 7)]



class Object(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, type, hero_group, enemy_group):
        super().__init__()
        self.scale_factor = 1.5
        self.rect = pygame.Rect(pos_x, 0, 48 * self.scale_factor, 70 * self.scale_factor)
        self.rect.bottom = pos_y + 64

        self.damage = 0

        self.player = hero_group
        self.enemies = enemy_group

        self.type = type
        self.animation_index = 0
        self.animation_speed = 2
        self.animation_timer = 0
        self.images = {
            'fire': FIRE,
            'electric_field': ELECTRIC_FIELD,
            'poison_cloud': POISON_CLOUD,
            'shop': SHOP,
            'tree': TREE,
            'chest': CHEST,
            'tombstone': TOMBSTONE,
            'portal': PORTAL,
        }

        self.image = self.get_cropped_image(self.images[self.type][self.animation_index])

    def update(self):
        self.update_animation()

    def update_animation(self):
        self.animation_timer += self.animation_speed
        if self.animation_timer >= 10:
            self.animation_timer = 0
            self.animation_index += 1
            if self.animation_index >= len(self.images[self.type]):
                self.animation_index = 0
        else:
            self.image = self.get_cropped_image(self.images[self.type][self.animation_index])

    def get_cropped_image(self, original_image):
        scaled_width = int(original_image.get_rect().width * self.scale_factor)
        scaled_height = int(original_image.get_rect().height * self.scale_factor)
        scaled_image = pygame.transform.scale(original_image, (scaled_width, scaled_height))

        centered_image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)

        x_pos = (self.rect.width - scaled_image.get_width()) // 2
        y_pos = (self.rect.height - scaled_image.get_height())

        centered_image.blit(scaled_image, (x_pos, y_pos))

        return centered_image

    def damage_entity(self):
        entities = self.player.get_sprites() + self.enemies.get_sprites()
        if entities:
            for entity in entities:
                if self.rect.colliderect(entity.real_rect):
                    entity.take_hit(self.damage)

    def draw(self, screen):
        border_color = (255, 0, 0)  
        border_thickness = 2  
        pygame.draw.rect(screen, border_color, self.rect, border_thickness)


class Fire(Object):
    def __init__(self, pos_x, pos_y, type, hero_group, enemy_group):
        super().__init__(pos_x, pos_y, type, hero_group, enemy_group)
        self.add(trap_group)
        self.scale_factor = 1.5
        self.rect = pygame.Rect(pos_x, 0, 43 * self.scale_factor, 64 * self.scale_factor)
        self.rect.bottom = pos_y + 64
        self.damage = 0.5

    def update(self):
        self.update_animation()
        self.damage_entity()


class ElectricField(Object):
    def __init__(self, pos_x, pos_y, type, hero_group, enemy_group):
        super().__init__(pos_x, pos_y, type, hero_group, enemy_group)
        self.add(trap_group)
        self.scale_factor = 2
        self.rect = pygame.Rect(pos_x, 0, 64 * self.scale_factor, 96 * self.scale_factor)
        self.rect.bottom = pos_y + 64
        self.damage = 1

    def update(self):
        self.update_animation()
        self.damage_entity()


class PoisonCloud(Object):
    def __init__(self, pos_x, pos_y, type, hero_group, enemy_group):
        super().__init__(pos_x, pos_y, type, hero_group, enemy_group)
        self.add(trap_group)
        self.scale_factor = 2
        self.rect = pygame.Rect(pos_x, 0, 64 * self.scale_factor, 96 * self.scale_factor)
        self.rect.bottom = pos_y + 64
        self.damage = 0.2

    def update(self):
        self.update_animation()
        self.damage_entity()


class Shop(Object):
    def __init__(self, pos_x, pos_y, type, hero_group, enemy_group):
        super().__init__(pos_x, pos_y, type, hero_group, enemy_group)
        self.add(shop_group)
        self.scale_factor = 2
        self.rect = pygame.Rect(pos_x, 0, 120 * self.scale_factor, 120 * self.scale_factor)
        self.rect.bottom = pos_y + 64

        self.font = pygame.font.Font(None, 48)
        self.color = (255, 255, 255)
        self.open_key = "E"

    def check_for_player(self):
        player = self.player.get_sprites()
        if player:
            for pl in player:
                if self.rect.colliderect(pl.real_rect):
                    return True

    def update(self):
        self.update_animation()
        if self.check_for_player():
            print("да")
            text_surface = self.font.render(self.open_key, True, self.color)
            self.image.blit(text_surface, ((self.rect.width - 24) // 2, (self.rect.height - 72) // 2))


class Tree(Object):
    def __init__(self, pos_x, pos_y, type, hero_group, enemy_group):
        super().__init__(pos_x, pos_y, type, hero_group, enemy_group)
        self.add(trap_group)
        self.scale_factor = 2
        self.rect = pygame.Rect(pos_x, 0, 192 * self.scale_factor, 192 * self.scale_factor)
        self.rect.bottom = pos_y + 64

    def get_cropped_image(self, original_image):
        non_transparent_rect = original_image.get_bounding_rect()
        
        crop_width = non_transparent_rect.width
        crop_height = non_transparent_rect.height

        
        crop_rect = pygame.Rect(
            non_transparent_rect.x + (non_transparent_rect.width // 2) - (crop_width // 2),
            non_transparent_rect.y + (non_transparent_rect.height // 2) - (crop_height // 2),
            crop_width,
            crop_height
        )

        
        cropped_image = pygame.Surface((crop_width, crop_height), pygame.SRCALPHA)

        
        cropped_image.blit(original_image, (0, 0), crop_rect)

        
        scaled_image = pygame.transform.scale(cropped_image,
                                              (int(crop_width * self.scale_factor),
                                               int(crop_height * self.scale_factor)))

        centered_image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)

        x_pos = (self.rect.width - scaled_image.get_width()) // 2
        y_pos = (self.rect.height - scaled_image.get_height())

        centered_image.blit(scaled_image, (x_pos, y_pos))

        return centered_image


class Chest(Object):
    def __init__(self, pos_x, pos_y, type, hero_group, enemy_group, money_inside):
        super().__init__(pos_x, pos_y, type, hero_group, enemy_group)
        self.add(trap_group)
        self.scale_factor = 1.5
        self.rect = pygame.Rect(pos_x, 0, 64 * self.scale_factor, 64 * self.scale_factor)
        self.rect.bottom = pos_y + 64
        self.image = self.get_cropped_image(self.images[self.type][self.animation_index])
        self.opened = False
        self.opening = False
        self.send_money = False
        self.font = pygame.font.Font(None, 48)
        self.open_key = "E"
        self.color = (255, 255, 255)
        self.money_inside = money_inside
        self.original_image = self.image.copy()

    def get_cropped_image(self, original_image):
        non_transparent_rect = original_image.get_bounding_rect()
        
        crop_width = non_transparent_rect.width
        crop_height = non_transparent_rect.height

        
        crop_rect = pygame.Rect(
            non_transparent_rect.x + (non_transparent_rect.width // 2) - (crop_width // 2),
            non_transparent_rect.y + (non_transparent_rect.height // 2) - (crop_height // 2),
            crop_width,
            crop_height
        )

        
        cropped_image = pygame.Surface((crop_width, crop_height), pygame.SRCALPHA)

        
        cropped_image.blit(original_image, (0, 0), crop_rect)

        
        scaled_image = pygame.transform.scale(cropped_image,
                                              (int(crop_width * self.scale_factor),
                                               int(crop_height * self.scale_factor)))

        centered_image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)

        x_pos = (self.rect.width - scaled_image.get_width()) // 2
        y_pos = (self.rect.height - scaled_image.get_height())

        centered_image.blit(scaled_image, (x_pos, y_pos))

        return centered_image

    def update(self):
        if self.check_for_player() and not self.opened and not self.opening:
            print("да")
            text_surface = self.font.render(self.open_key, True, self.color)
            self.image.blit(text_surface, ((self.rect.width - 24) // 2, (self.rect.height - 72) // 2))
            self.open()
            self.send_money = True
        elif not self.opened and not self.opening:
            self.image = self.original_image.copy()
        if self.opening:
            print("вызвал")
            self.update_animation()
            if self.animation_index == len(self.images[self.type]) - 1:
                self.opened = True
                self.opening = False

    def open(self):
        if not self.opened and not self.opening:
            if self.check_for_player():
                self.opening = True
                MoneyText(self.rect.x + self.rect.width // 2, self.rect.y, self.money_inside)

    def get_money(self):
        if self.opened and self.send_money:
            self.send_money = False
            return self.money_inside
        return False

    def check_for_player(self):
        player = self.player.get_sprites()
        if player:
            for pl in player:
                if self.rect.colliderect(pl.real_rect):
                    return True

class Tombstone(Object):
    def __init__(self, pos_x, pos_y, type, hero_group, enemy_group):
        super().__init__(pos_x, pos_y, type, hero_group, enemy_group)
        self.add(trap_group)
        self.scale_factor = 2
        self.rect = pygame.Rect(pos_x, 0, 32 * self.scale_factor, 48 * self.scale_factor)
        self.rect.bottom = pos_y + 64
        self.image = self.get_cropped_image(self.images[self.type][random.randint(0, 2)])

    def update(self):
        pass

class Portal(Object):
    def __init__(self, pos_x, pos_y, type, hero_group, enemy_group):
        super().__init__(pos_x, pos_y, type, hero_group, enemy_group)
        self.add(trap_group)
        self.scale_factor = 4
        self.rect = pygame.Rect(pos_x, 0, 24 * self.scale_factor, 32 * self.scale_factor)
        self.rect.bottom = pos_y + 64
        self.damage = 0.2

    def teleport(self):
        entities = self.player.get_sprites()
        if entities:
            entity = entities[0]
            if self.rect.colliderect(entity.real_rect):
                return True
            return False
        return False



    def update(self):
        self.update_animation()
