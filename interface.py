import os

import pygame
from methods import load_image

SPACING = 10
FONT_PATH = "fonts/monogram.ttf"

ITEM_BOX = load_image("interface/item_box_border.png")
ITEM_BOX_PATTERN = load_image("interface/item_box_pattern.png")
VALUE_BAR = load_image("interface/value_bar.png")

ARMOR_ICON = load_image("interface/armor_icon.png")
DAMAGE_ICON = load_image("interface/damage_icon.png")
STAMINA_ICON = load_image("interface/stamina_icon.png")


class Bar:
    def __init__(self, screen, x, y, max_value, name, width=200, height=20,
                 foreground_color=(255, 0, 0),
                 background_color=(60, 60, 60),
                 border_color=(30, 30, 30)):
        self.screen = screen
        self.x = x
        self.y = y
        self.name = name
        self.max_value = max_value
        self.width = width
        self.height = height
        self.foreground_color = foreground_color
        self.background_color = background_color
        self.border_color = border_color

        self.current_value = max_value
        self.display_value = max_value
        self.animation_speed = 0.5
        self.font = pygame.font.Font(FONT_PATH, 24)
        self.name_font = pygame.font.Font(FONT_PATH, 36)

    def update(self, current_value):
        self.current_value = max(0, min(current_value, self.max_value))
        self.display_value += (self.current_value - self.display_value) * self.animation_speed

    def draw(self):
        progress = self.display_value / self.max_value
        self._draw_bar(progress)

    def _draw_bar(self, progress):
        
        bg_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(self.screen, self.background_color, bg_rect)

        
        filled_width = self.width * progress
        fill_rect = pygame.Rect(self.x, self.y, filled_width, self.height)
        pygame.draw.rect(self.screen, self.foreground_color, fill_rect)

        
        border_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(self.screen, self.border_color, border_rect, 2)

        
        text = self._get_text(progress)
        text_surface = self.font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.x + self.width / 2, self.y + self.height / 2))
        self.screen.blit(text_surface, text_rect)

        text_name = self.name
        text_surface = self.name_font.render(text_name, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.x + self.width / 2, self.y - self.height))
        self.screen.blit(text_surface, text_rect)

    def _get_text(self, progress):
        return f"{int(progress * 100)}%"


class HealthBar(Bar):
    def __init__(self, screen, x, y, max_health, name, width=200, height=20):
        super().__init__(screen, x, y, max_health, name, width, height,
                         foreground_color=(255, 0, 0),
                         background_color=(60, 60, 60),
                         border_color=(30, 30, 30))


class StaminaBar(Bar):
    def __init__(self, screen, x, y, max_stamina, name, width=200, height=20):
        super().__init__(screen, x, y, max_stamina, name, width, height,
                         foreground_color=(0, 0, 204),
                         background_color=(60, 60, 60),
                         border_color=(30, 30, 30))


class CoinCounter:
    def __init__(self, x, y, font_size=60):
        self.coin_count = 0
        self.font = pygame.font.Font("fonts/monogram.ttf", font_size)
        self.position = (x, y)
        self.coin_image = pygame.image.load("interface/coin.png")
        self.coin_image = pygame.transform.scale(self.coin_image, (70, 70))

    def draw(self, screen, count):
        self.coin_count = count
        screen.blit(self.coin_image, self.position)
        count_text = self.font.render(str(self.coin_count), True, (255, 255, 255))
        screen.blit(count_text, (self.position[0] + 80, self.position[1] + 10))


class ShopMenu:
    def __init__(self, screen, first, second, third, foreground_color=(255, 0, 0), background_color=(180, 180, 150),
                 border_color=(30, 30, 30)):
        self.screen = screen

        self.foreground_color = foreground_color
        self.background_color = background_color
        self.border_color = border_color

        self.armor_values = {0: 100, 1: 125, 2: 150, 3: 200, 4: 300}
        self.damage_values = {0: 10, 1: 20, 2: 40, 3: 70, 4: 120}
        self.stamina_values = {0: 0.5, 1: 1, 2: 1.5, 3: 2, 4: 2.5}

        self.border_width = 3
        self.item_size = self.screen.get_height() // 6
        self.item_image = pygame.transform.scale(ITEM_BOX, (self.item_size, self.item_size))
        self.item_pattern = pygame.transform.scale(ITEM_BOX_PATTERN, (
            ITEM_BOX_PATTERN.get_width() * self.item_size // ITEM_BOX_PATTERN.get_width(),
            ITEM_BOX_PATTERN.get_height() * self.item_size // ITEM_BOX_PATTERN.get_width()))

        self.value_bar_image = pygame.transform.scale(VALUE_BAR, (
            VALUE_BAR.get_width() * self.item_size // VALUE_BAR.get_width(),
            VALUE_BAR.get_height() * self.item_size // VALUE_BAR.get_width()))

        self.damage_icon = pygame.transform.scale(DAMAGE_ICON, (
            VALUE_BAR.get_width() * self.item_size // VALUE_BAR.get_width(),
            VALUE_BAR.get_width() * self.item_size // VALUE_BAR.get_width()))

        self.armor_icon = pygame.transform.scale(ARMOR_ICON, (
            VALUE_BAR.get_width() * self.item_size // VALUE_BAR.get_width(),
            VALUE_BAR.get_width() * self.item_size // VALUE_BAR.get_width()))

        self.stamina_icon = pygame.transform.scale(STAMINA_ICON, (
            VALUE_BAR.get_width() * self.item_size // VALUE_BAR.get_width(),
            VALUE_BAR.get_width() * self.item_size // VALUE_BAR.get_width()))

        self.name_font = pygame.font.Font(FONT_PATH, 72)
        self.plus_font = pygame.font.Font(FONT_PATH, 60)
        self.price_font = pygame.font.Font(FONT_PATH, 36)

        self.current_value_damage = 1
        self.current_value_armor = 0
        self.current_value_stamina = 0
        self.max_value = 4
        self.is_open = False

        self.draw_menu()

    def draw_slot(self, title, current_value, position, mouse_pos):
        
        image_rect = self.item_image.get_rect(center=position)
        pattern_rect = self.item_pattern.get_rect(midbottom=image_rect.midtop)
        bar_rect = self.value_bar_image.get_rect(midtop=(image_rect.centerx, image_rect.centery + image_rect.height))
        print(image_rect.centerx, image_rect.centery)

        
        self.screen.blit(self.item_image, image_rect)
        self.screen.blit(self.item_pattern, pattern_rect)
        if title == "damage":
            icon = self.damage_icon
        elif title == "armor":
            icon = self.armor_icon
        elif title == "stamina":
            icon = self.stamina_icon
        else:
            icon = None

            
        if icon:
            icon_rect = icon.get_rect(center=image_rect.center)  
            self.screen.blit(icon, icon_rect)

        text_surface = self.name_font.render(title, True, (255, 255, 255))
        text_rect = text_surface.get_rect(midtop=(image_rect.centerx, image_rect.centery + image_rect.height // 2))
        self.screen.blit(text_surface, text_rect)

        text_surface2 = self.price_font.render("price: 250$", True, (255, 255, 255))
        text_rect2 = text_surface.get_rect(midtop=(image_rect.centerx, image_rect.centery + image_rect.height + 20))
        self.screen.blit(text_surface2, text_rect2)

        
        fill_width = (current_value / self.max_value) * bar_rect.width - 2
        fill_rect = pygame.Rect(bar_rect.left + 2, bar_rect.top, fill_width, bar_rect.height)
        pygame.draw.rect(self.screen, (0, 255, 0), fill_rect)
        
        self.screen.blit(self.value_bar_image, bar_rect)

        
        for i in range(1, 4):
            line_x = bar_rect.left + (bar_rect.width / 4) * i
            pygame.draw.line(self.screen, (255, 255, 255), (line_x, bar_rect.top), (line_x, bar_rect.bottom), 3)

        
        plus_text = self.plus_font.render("+", True, (255, 255, 255))
        plus_rect = plus_text.get_rect(midright=(bar_rect.left, bar_rect.centery))

        
        if plus_rect.collidepoint(mouse_pos):
            plus_text = self.plus_font.render("+", True, (255, 255, 0))  

        self.screen.blit(plus_text, plus_rect)
        return plus_rect

    def draw_menu(self):
        self.bg_rect = pygame.Rect(0, 0, self.screen.get_width() / 2, self.screen.get_height() / 2)
        self.bg_rect.center = self.screen.get_rect().center
        pygame.draw.rect(self.screen, self.background_color, self.bg_rect)

        border_rect = pygame.Rect(0, 0, self.screen.get_width() / 2, self.screen.get_height() / 2)
        border_rect.center = self.screen.get_rect().center
        pygame.draw.rect(self.screen, self.border_color, border_rect, self.border_width)

        self.draw_close_button()

        
        slot_positions = [
            (self.bg_rect.centerx - self.bg_rect.width // 3, self.bg_rect.centery - self.bg_rect.height // 9),
            (self.bg_rect.centerx, self.bg_rect.centery - self.bg_rect.height // 9),
            (self.bg_rect.centerx + self.bg_rect.width // 3, self.bg_rect.centery - self.bg_rect.height // 9)
        ]
        self.plus_rects = []
        for i, title in enumerate(["damage", "armor", "stamina"]):
            plus_rect = self.draw_slot(title, [self.current_value_damage, self.current_value_armor,
                                               self.current_value_stamina][i], slot_positions[i],
                                       pygame.mouse.get_pos())
            self.plus_rects.append(plus_rect)

    def draw_close_button(self):
        
        close_x = self.bg_rect.right - 40
        close_y = self.bg_rect.top + 10
        
        pygame.draw.line(self.screen, (255, 0, 0), (close_x, close_y), (close_x + 20, close_y + 20), 3)  
        pygame.draw.line(self.screen, (255, 0, 0), (close_x, close_y + 20), (close_x + 20, close_y), 3)  

    def get_attributes(self):
        return (self.damage_values[self.current_value_damage], self.armor_values[self.current_value_armor],
                self.stamina_values[self.current_value_stamina])

    def check_close_button_click(self, mouse_pos):
        close_x = self.bg_rect.right - 40
        close_y = self.bg_rect.top + 10
        if close_x <= mouse_pos[0] <= close_x + 20 and close_y <= mouse_pos[1] <= close_y + 20:
            return True

    def handle_click(self, mouse_pos, money):
        if self.check_close_button_click(mouse_pos):
            return "closed"
        for i, plus_rect in enumerate(self.plus_rects):
            if plus_rect.collidepoint(mouse_pos):
                if i == 0 and self.current_value_damage < self.max_value and money >= 250:
                    self.current_value_damage += 1
                    return "damage", 250
                elif i == 1 and self.current_value_armor < self.max_value and money >= 250:
                    self.current_value_armor += 1
                    return "armor", 250
                elif i == 2 and self.current_value_stamina < self.max_value and money >= 250:
                    self.current_value_stamina += 1
                    return "stamina", 250


class ParallaxBackgroundMenu:
    def __init__(self, screen, image_path, speed_factor=0.5):
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.original_image, (screen.get_width(), screen.get_height()))
        self.speed_factor = speed_factor
        self.image_width = self.image.get_width()
        self.rect = self.image.get_rect()
        self.rect.x = 0  

    def update(self):
        
        self.rect.x -= self.speed_factor
        if self.rect.x <= -self.image_width:
            self.rect.x = 0  

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, 0))
        screen.blit(self.image, (self.rect.x + self.image_width, 0))


class MainMenu:
    def __init__(self, screen):
        pygame.display.set_caption("Iron Knight")
        self.font_size = 60
        self.font = pygame.font.Font("fonts/monogram.ttf", self.font_size)
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.screen = screen

        
        self.menu_items = [
            "Continue",
            "New game",
            "Exit"
        ]

        
        self.button_bg_color = (100, 100, 100, 128)  
        self.button_bg_color_inactive = (255, 255, 255, 0)  

        
        self.button_positions = [
            (self.width // 2, self.height // 2 - 50),  
            (self.width // 2, self.height // 2 + 10),  
            (self.width // 2, self.height // 2 + 70)  
        ]

        
        self.background_layers = [
            ParallaxBackgroundMenu(self.screen, "background/background_layer_1.png", 0.5),
            
            ParallaxBackgroundMenu(self.screen, "background/background_layer_2.png", 1.0),
            
            ParallaxBackgroundMenu(self.screen, "background/background_layer_3.png", 1.5)
            
        ]

    def draw_text(self, text, x, y):
        textobj = self.font.render(text, True, (0, 0, 0))
        textrect = textobj.get_rect(center=(x, y))  
        return textobj, textrect

    def draw_button(self, text, x, y, active):
        
        bg_color = self.button_bg_color if active else self.button_bg_color_inactive
        bg_rect = pygame.Rect(x - (self.font.size(text)[0] + 20) // 2, y - (self.font.get_height() + 10) // 2,
                              self.font.size(text)[0] + 20, self.font.get_height() + 10)
        pygame.draw.rect(self.screen, bg_color, bg_rect)

        
        textobj, textrect = self.draw_text(text, bg_rect.centerx,
                                           bg_rect.centery)  
        self.screen.blit(textobj, textrect)

    def check_button_click(self, pos):
        for i, (x, y) in enumerate(self.button_positions):
            if x - (self.font.size(self.menu_items[i])[0] + 20) // 2 <= pos[0] <= x + (
                    self.font.size(self.menu_items[i])[0] + 20) // 2 and \
                    y - (self.font.get_height() + 10) // 2 <= pos[1] <= y + (self.font.get_height() + 10) // 2:
                return i + 1  
        return None
