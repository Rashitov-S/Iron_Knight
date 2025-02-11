import json
import random
import pygame

from methods import load_image
from hero import Player, hero_group
from enemies import Enemy, skeleton_images, mushroom_images, archer_images, enemy_group, weapon_object_group
from particles import particles_group
from traps import trap_group, Fire, ElectricField, PoisonCloud, Shop, Tree, shop_group, Chest, Tombstone, Portal
from groups import SpriteGroup
from interface import HealthBar, StaminaBar, ShopMenu, MainMenu, CoinCounter
from damage_numbers import damage_text_group


pygame.init()


screen_width, screen_height = 1920, 1024
clock = pygame.time.Clock()
screen = pygame.display.set_mode((screen_width, screen_height))


TILE_WIDTH = 64
TILE_HEIGHT = 64
GRASS_TILE = pygame.transform.scale(load_image("ground/2.png"), (64, 64))
EARTH_TILE = pygame.transform.scale(load_image("ground/76.png"), (64, 64))
TILES = {"-": GRASS_TILE, "#": EARTH_TILE}

logo = pygame.image.load('logo/iron_knight_transparent.png')
logo_rect = logo.get_rect(center=(screen_width // 2, 100))


sprite_group = SpriteGroup()

enemy_damage = {
    1: {
        "mushroom": 15,
        "skeleton": 20,
        "archer": 25
    },
    2: {
        "mushroom": 40,
        "skeleton": 55,
        "archer": 60
    },
    3: {
        "mushroom": 70,
        "skeleton": 95,
        "archer": 120
    }
}

levels = {1: "map/1.txt", 2: "map/2.txt", 3: "map/3.txt"}


class Sprite(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.rect = None

    def get_event(self, event):
        pass


class Tile(Sprite):
    def __init__(self, tile_symb, pos_x, pos_y):
        super().__init__(sprite_group)
        self.image = TILES[tile_symb]
        self.rect = self.image.get_rect().move(TILE_WIDTH * pos_x, TILE_HEIGHT * pos_y)


class Camera:
    def __init__(self, map_width, map_height):
        self.camera = pygame.Rect(0, 0, map_width, map_height)
        self.map_width = map_width
        self.map_height = map_height
        self.smooth_speed = 0.1
        self.current_x = 0
        self.current_y = 0

    def apply(self, rect):
        return rect.move(self.camera.topleft)

    def update(self, target):
        target_x = -target.rect.centerx + int(screen_width / 2)
        target_y = -target.rect.centery + int(screen_height / 1.5)

        new_x = min(-(self.map_width - screen_width), target_x)
        new_y = max(-(self.map_height - screen_height), target_y)

        self.current_x += (new_x - self.current_x) * self.smooth_speed
        self.current_y += (new_y - self.current_y) * self.smooth_speed

        self.camera = pygame.Rect(self.current_x, self.current_y,
                                  self.map_width, self.map_height)
        return target_x != new_x


class ParallaxBackground:
    def __init__(self, image_path, speed_factor=0.5):
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.original_image,
                                            (screen_width, screen_height))
        self.speed_factor = speed_factor
        self.image_width = self.image.get_width()
        self.rect = self.image.get_rect()

    def update(self, camera):
        self.rect.x = round(-camera.camera.x * self.speed_factor)
        if self.rect.x >= self.image_width:
            self.rect.x %= self.image_width
        elif self.rect.x < 0:
            self.rect.x += self.image_width

    def draw(self, screen):
        screen.blit(self.image, (-self.rect.x, 0))
        screen.blit(self.image, (-self.rect.x + self.image_width, 0))



background_layers = [
    ParallaxBackground("background/background_layer_1.png", 0.2),
    ParallaxBackground("background/background_layer_2.png", 0.5),
    ParallaxBackground("background/background_layer_3.png", 0.8)
]


class Game:
    def __init__(self):
        pygame.display.set_caption("Iron Knight")
        self.main_menu_opened = True
        self.final_menu = False
        self.main_menu = MainMenu(screen)
        self.font = pygame.font.Font("fonts/monogram.ttf", 120)

        
        self.health_bar = HealthBar(screen, screen_width / 2 - screen_width // 30 - 200,
                                    screen_height * 0.9, 100, "health")
        self.stamina_bar = StaminaBar(screen, screen_width / 2 + screen_width // 30,
                                      screen_height * 0.9, 500, "stamina")
        self.shop_menu = ShopMenu(screen, 1, 2, 3)
        self.coin_counter = CoinCounter(30, 30)

        
        self.camera = Camera(screen_width, screen_height)

        
        self.damage = 0
        self.death_timer = 0
        self.money = 0
        self.score = 0
        self.current_level = 1
        self.level_transition_duration = 1000  
        self.transition_start_time = None
        self.transitioning = False

        self.running = True
        self.e_pressed = False
        self.left_click = False
        self.menu_opened = False

        self.attack_cooldown = 1
        self.last_attack_time = 0

    def transition_to_next_level(self):
        self.transitioning = True
        self.transition_start_time = pygame.time.get_ticks()

    def update(self):
        if self.transitioning:
            current_time = pygame.time.get_ticks()
            if current_time - self.transition_start_time < self.level_transition_duration:
                
                alpha = (current_time - self.transition_start_time) / self.level_transition_duration
                overlay = pygame.Surface((screen_width, screen_height))
                overlay.fill((0, 0, 0))
                overlay.set_alpha(int(alpha * 255))
                self.transitioning = False
        else:
            if not self.hero.is_alive:
                self.death_timer += 1
                if self.death_timer >= 240:
                    self.score = 0
                    self.money = 0
                    self.prepare_level()
                    return
            print(self.hero.attack_timer)
            self.handle_user_input()
            self.camera.update(self.hero)
            self.update_attributes()

            
            for layer in background_layers:
                layer.update(self.camera)

            
            self.health_bar.update(self.hero.health)
            self.stamina_bar.update(self.hero.endurance)

            
            screen.fill((0, 0, 0))

            
            for layer in background_layers:
                layer.draw(screen)

            
            for tile in sprite_group:
                screen.blit(tile.image, self.camera.apply(tile.rect))

            for trap in trap_group:
                screen.blit(trap.image, self.camera.apply(trap.rect))
                if isinstance(trap, Chest):
                    money = trap.get_money()
                    if money:
                        self.money += money
                        self.score += money
                if isinstance(trap, Portal):
                    if trap.teleport():
                        self.hero.kill()
                        self.current_level += 1
                        self.save_game(self.current_level, self.money, self.score, self.shop_menu.current_value_damage, self.shop_menu.current_value_armor, self.shop_menu.current_value_stamina)
                        self.transition_to_next_level()
                        self.prepare_level()
                        return

            for shop in shop_group:
                screen.blit(shop.image, self.camera.apply(shop.rect))
                if shop.check_for_player() and self.e_pressed:
                    self.menu_opened = True

            for enemy in enemy_group:
                screen.blit(enemy.image, self.camera.apply(enemy.rect))

            for entity in hero_group:
                screen.blit(entity.image, self.camera.apply(entity.rect))

            for text in damage_text_group:
                screen.blit(text.image, self.camera.apply(text.rect))

            for arrow in weapon_object_group:
                screen.blit(arrow.image, self.camera.apply(arrow.rect))

            
            self.health_bar.draw()
            self.stamina_bar.draw()
            self.coin_counter.draw(screen, self.money)
            if self.menu_opened:
                self.shop_menu.draw_menu()

            
            weapon_object_group.update()
            trap_group.update()
            self.hero.update()
            shop_group.update()
            particles_group.update()
            enemy_group.update()
            damage_text_group.update()

            pygame.display.flip()
            clock.tick(60)

    def set_current_level(self):
        self.level_map = self.load_level(f"map/{self.current_level}.txt")
        self.hero = self.generate_level(self.level_map)

    def generate_level(self, level):
        new_player = None
        for y in range(len(level)):
            for x in range(len(level[y])):
                symb = level[y][x]
                if symb == '-':
                    Tile('-', x, y)
                elif symb == '#':
                    Tile('#', x, y)
                elif symb == '@':
                    new_player = Player(x * TILE_WIDTH, y * TILE_HEIGHT, sprite_group)
                    level[y][x] = "."
                elif symb == '!':
                    Enemy(x * TILE_WIDTH, y * TILE_HEIGHT, sprite_group, hero_group, skeleton_images, name="skeleton")
                elif symb == '?':
                    Enemy(x * TILE_WIDTH, y * TILE_HEIGHT, sprite_group, hero_group, mushroom_images, name="mushroom")
                elif symb == '*':
                    Enemy(x * TILE_WIDTH, y * TILE_HEIGHT, sprite_group, hero_group, archer_images, enemy_type='ranged', name="archer")
                elif symb == 'F':
                    Fire(x * TILE_WIDTH, y * TILE_HEIGHT, "fire", hero_group, enemy_group)
                elif symb == 'E':
                    ElectricField(x * TILE_WIDTH, y * TILE_HEIGHT, "electric_field", hero_group, enemy_group)
                elif symb == 'P':
                    PoisonCloud(x * TILE_WIDTH, y * TILE_HEIGHT, "poison_cloud", hero_group, enemy_group)
                elif symb == 'S':
                    Shop(x * TILE_WIDTH, y * TILE_HEIGHT, "shop", hero_group, enemy_group)
                elif symb == 'T':
                    Tree(x * TILE_WIDTH, y * TILE_HEIGHT, "tree", hero_group, enemy_group)
                elif symb == 'C':
                    money = random.randint(100, 500)
                    Chest(x * TILE_WIDTH, y * TILE_HEIGHT, "chest", hero_group, enemy_group, money)
                elif symb == 'R':
                    Tombstone(x * TILE_WIDTH, y * TILE_HEIGHT, "tombstone", hero_group, enemy_group)
                elif symb == 'G':
                    Portal(x * TILE_WIDTH, y * TILE_HEIGHT, "portal", hero_group, enemy_group)
        return new_player

    def load_level(self, filename):
        with open(filename, 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]
        max_width = max(map(len, level_map))
        return list(map(lambda x: list(x.ljust(max_width, '.')), level_map))

    def handle_user_input(self):
        if self.e_pressed:
            self.e_pressed = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYUP and event.key == pygame.K_z:
                self.player_attack(self.hero, enemy_group)
            if event.type == pygame.KEYUP and event.key == pygame.K_e:
                self.e_pressed = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  
                    if self.menu_opened:
                        flag = self.shop_menu.handle_click(pygame.mouse.get_pos(), self.money)
                        if flag == "closed":
                            self.menu_opened = False
                        if flag:
                            if "damage" in flag:
                                self.money -= flag[1]
                            elif "armor" in flag:
                                self.money -= flag[1]
                            elif "stamina" in flag:
                                self.money -= flag[1]
                    else:
                        self.hero.attack()

        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.hero.move_x(5)
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.hero.move_x(-5)
        else:
            self.hero.move_x(0)

        if keys[pygame.K_SPACE]:
            self.hero.jump()

    def attack_engine(self, hero, enemies):
        if enemies:
            for enemy in enemies:
                if (hero.rect.colliderect(enemy.real_rect)
                        and hero.is_alive and hero.is_attacking
                        and hero.on_ground):
                    enemy.take_hit(self.damage)
                    hero.attacking_flag = False
                    self.check_enemies(enemy)

    def player_attack(self, hero, enemies):
        current_time = pygame.time.get_ticks() / 1000  
        if current_time - self.last_attack_time >= self.attack_cooldown:
            hero.attack()
            if hero.attack_timer == 1:
                hero.attacking_flag = True
            else:
                hero.attacking_flag = False
            self.attack_engine(hero, enemies)
            self.last_attack_time = current_time

    def check_enemies(self, enemy):
        if enemy.is_expired:
            enemy_group.remove(enemy)

    def update_attributes(self):
        attributes = self.shop_menu.get_attributes()
        if self.damage != attributes[0]:
            self.damage = attributes[0]
        if self.hero.max_health != attributes[1]:
            diff = attributes[1] / self.hero.max_health
            self.hero.max_health = attributes[1]
            self.hero.health *= diff
            self.health_bar.max_value = self.hero.max_health
        if self.hero.endurance_regen != attributes[2]:
            self.hero.endurance_regen = attributes[2]

    def save_game(self, level, money, score, damage, health, stamina):
        game_state = {
            'level': level,
            'money': money,
            'score': score,
            'damage': damage,
            'health': health,
            'stamina': stamina
        }
        with open('save/save_game.json', 'w') as f:
            json.dump(game_state, f)

    def load_game(self):
        with open('save/save_game.json', 'r') as f:
            game_state = json.load(f)
        return game_state['level'], game_state['money'], game_state['score'], game_state['damage'], game_state[
            'health'], game_state['stamina']

    def prepare_level(self):
        weapon_object_group.empty()
        trap_group.empty()
        shop_group.empty()
        particles_group.empty()
        enemy_group.empty()
        damage_text_group.empty()
        hero_group.empty()
        try:
            level, money, score, damage, health, stamina = self.load_game()
            self.current_level = level
            if self.current_level > 3:
                self.final_menu = True
                return
            self.money += money
            self.score += score
            self.death_timer = 0
            self.level_map = self.load_level(f"map/{self.current_level}.txt")
            self.hero = self.generate_level(self.level_map)
            self.shop_menu.current_value_damage = damage
            self.shop_menu.current_value_armor = health
            self.shop_menu.current_value_stamina = stamina
            self.menu_opened = False
            self.main_menu_opened = False
        except Exception as e:
            print(e.args)
            self.new_game()

    def new_game(self):
        weapon_object_group.empty()
        trap_group.empty()
        shop_group.empty()
        particles_group.empty()
        enemy_group.empty()
        damage_text_group.empty()
        hero_group.empty()
        self.current_level = 1
        self.money = 0
        self.score = 0
        self.death_timer = 0
        self.level_map = self.load_level(f"map/{self.current_level}.txt")
        self.hero = self.generate_level(self.level_map)
        self.shop_menu.current_value_damage = 0
        self.shop_menu.current_value_health = 0
        self.shop_menu.current_value_stamina = 0
        self.menu_opened = False
        self.main_menu_opened = False

    def start_cycle(self):
        while self.running:
            if self.final_menu:
                screen.fill((0, 0, 0))
                self.draw_won_menu()
                pygame.display.flip()
                clock.tick(60)
            else:
                if self.main_menu_opened:
                    screen.fill((0, 0, 0))
                    for layer in self.main_menu.background_layers:
                        layer.update()
                        layer.draw(screen)

                    screen.blit(logo, logo_rect)

                    for i, (text, (x, y)) in enumerate(zip(self.main_menu.menu_items, self.main_menu.button_positions)):
                        mouse_pos = pygame.mouse.get_pos()
                        is_hovered = (x - (self.main_menu.font.size(text)[0] + 20) // 2 <= mouse_pos[0] <= x + (
                                self.main_menu.font.size(text)[0] + 20) // 2 and
                                      y - (self.main_menu.font.get_height() + 10) // 2 <= mouse_pos[1] <= y + (
                                              self.main_menu.font.get_height() + 10) // 2)
                        self.main_menu.draw_button(text, x, y, is_hovered)

                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            self.running = False
                            return

                        if event.type == pygame.MOUSEBUTTONDOWN:
                            if event.button == 1:  
                                button_clicked = self.main_menu.check_button_click(event.pos)
                                if button_clicked == 1:
                                    print("Продолжить игру...")
                                    self.main_menu_opened = False
                                    self.prepare_level()
                                elif button_clicked == 2:
                                    print("Начать новую игру...")
                                    self.main_menu_opened = False
                                    self.new_game()
                                elif button_clicked == 3:
                                    pygame.quit()
                                    return
                    pygame.display.flip()
                    clock.tick(60)
                else:
                    self.update()  

    def draw_won_menu(self):
        text = self.font.render("You Won!", True, (255, 0, 0))
        text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2 - 50))
        screen.blit(text, text_rect)

        score_text = self.font.render(f"Score: {self.score}", True, (255, 215, 0))  # Золотой цвет
        score_rect = score_text.get_rect(center=(screen_width // 2, screen_height // 2 + 20))
        screen.blit(score_text, score_rect)



if __name__ == '__main__':
    game = Game()
    game.start_cycle()
