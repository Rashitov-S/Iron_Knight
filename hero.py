import pygame
from methods import load_image
import random
from groups import SpriteGroup

pygame.init()
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

PLAYER_IDLE = [load_image(f"data/hero_idle/{x}.png") for x in range(1, 11)]
PLAYER_RUN = [load_image(f"data/hero_run/{x}.png") for x in range(1, 11)]
PLAYER_FALL = [load_image(f"data/hero_fall/{x}.png") for x in range(1, 4)]
PLAYER_JUMP = [load_image(f"data/hero_jump/{x}.png") for x in range(1, 4)]
PLAYER_TAKE_HIT = [load_image(f"data/hero_take_hit/{x}.png") for x in range(1, 4)]
PLAYER_DEATH = [load_image(f"data/hero_death/{x}.png") for x in range(1, 11)]
PLAYER_ATTACK1 = [load_image(f"data/hero_attack1/{x}.png") for x in range(1, 5)]
PLAYER_ATTACK2 = [load_image(f"data/hero_attack2/{x}.png") for x in range(1, 7)]

PLAYER_ATTACK1_NO = [load_image(f"data/hero_attack1_NoMovement/{x}.png") for x in range(1, 5)]
PLAYER_ATTACK2_NO = [load_image(f"data/hero_attack2_NoMovement/{x}.png") for x in range(1, 7)]

hero_group = SpriteGroup()


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, sprite_group, max_health=100):
        super().__init__(hero_group)
        self.images = {
            'idle': PLAYER_IDLE,
            'run': PLAYER_RUN,
            'fall': PLAYER_FALL,
            'jump': PLAYER_JUMP,
            'take_hit': PLAYER_TAKE_HIT,
            'death': PLAYER_DEATH,
            'attack1': PLAYER_ATTACK1_NO,
            'attack2': PLAYER_ATTACK2_NO
        }
        self.current_animation = 'idle'
        self.animation_index = 0
        self.scale_factor = 3  

        self.sprite_group = sprite_group

        self.is_attacking = False
        self.attack_timer = 0
        self.attacking_flag = False

        self.original_rect = pygame.Rect(0, 0, 60, 38)  
        self.fact_rect = pygame.Rect(0, 0, 20, 38)

        x = x - self.fact_rect.width - 50
        y = y - self.fact_rect.height - 12

        self.rect = pygame.Rect(x, y,
                                self.original_rect.width * self.scale_factor,
                                self.original_rect.height * self.scale_factor)

        self.real_rect = pygame.Rect(self.rect.x + self.rect.width // 3,
                                     y,
                                     self.fact_rect.width * self.scale_factor,
                                     self.fact_rect.height * self.scale_factor)
        self.image = self.get_cropped_image(self.images[self.current_animation][self.animation_index])

        self.is_alive = True
        self.taking_hit = False

        self.health = max_health
        self.max_health = max_health
        self.endurance = 500
        self.max_endurance = 500
        self.endurance_regen = 0.5
        self.gravity = 0.5
        self.on_ground = True

        self.velocity_x = 0
        self.velocity_y = 0
        self.animation_speed = 1
        self.animation_timer = 0

        self.direction = 1

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
        y_pos = self.rect.height - scaled_image.get_height()

        
        centered_image.blit(scaled_image, (x_pos, y_pos))

        return centered_image

    def check_health(self):
        if self.health <= 0 and self.is_alive:
            self.health = 0
            self.is_alive = False
            if self.current_animation != 'death':
                self.current_animation = 'death'
                self.animation_index = 0
                self.animation_timer = 0
                print(self.animation_timer)

    def update(self):
        self.check_health()
        if self.is_alive:
            if not self.taking_hit:
                if self.is_attacking:
                    self.attack_timer += self.animation_speed
                else:
                    
                    if not self.on_ground:
                        self.velocity_y += self.gravity
                        if self.velocity_y > 0:
                            if self.current_animation != 'fall':
                                self.current_animation = 'fall'
                                self.animation_index = 0
                        else:
                            if self.current_animation != 'jump':
                                self.current_animation = 'jump'
                                self.animation_index = 0
                    elif self.velocity_x != 0:
                        if self.current_animation != 'run':
                            self.current_animation = 'run'
                            self.animation_index = 0
                    else:
                        if self.current_animation != 'idle':
                            self.current_animation = 'idle'
                            self.animation_index = 0
            else:
                if self.current_animation == 'take_hit' and self.animation_index == len(PLAYER_TAKE_HIT) - 1:
                    self.taking_hit = False
        else:
            self.velocity_x = 0
        if not self.is_alive or self.taking_hit:
            if not self.on_ground:
                self.velocity_y += self.gravity

        self.real_rect.x += self.velocity_x
        self._check_collisions('horizontal')

        self.real_rect.y += self.velocity_y
        self._check_collisions('vertical')
        self.rect.center = self.real_rect.center

        
        self.update_animation()

        
        self._check_ground()

        
        if self.is_alive:
            if self.endurance < self.max_endurance:
                self.endurance += self.endurance_regen

    def _check_collisions(self, direction):
        for sprite in self.sprite_group:
            if self.real_rect.colliderect(sprite.rect):
                if direction == 'horizontal':
                    if self.velocity_x > 0:  
                        self.real_rect.right = sprite.rect.left
                    elif self.velocity_x < 0:  
                        self.real_rect.left = sprite.rect.right
                    self.velocity_x = 0

                elif direction == 'vertical':
                    if self.velocity_y > 0:  
                        self.real_rect.bottom = sprite.rect.top
                        self.on_ground = True
                    elif self.velocity_y < 0:  
                        self.real_rect.top = sprite.rect.bottom
                    self.velocity_y = 0

    def _check_ground(self):
        
        temp_rect = self.real_rect.copy()
        temp_rect.y += 2
        self.on_ground = False
        for sprite in self.sprite_group:
            if temp_rect.colliderect(sprite.rect):
                self.on_ground = True
                break

    def update_animation(self):
        self.animation_timer += self.animation_speed
        if self.animation_timer >= 10:
            self.animation_timer = 0
            if self.is_alive:
                self.animation_index += 1
            else:
                if not self.animation_index == len(self.images['death']) - 1:
                    self.animation_index += 1
            self.attack_timer = 0
            if self.animation_index >= len(self.images[self.current_animation]):
                if self.is_attacking:
                    self.is_attacking = False
                    self.current_animation = 'idle'
                self.animation_index = 0
        if self.current_animation not in ('attack1', 'attack2'):
            self.is_attacking = False

        
        self.image = self.get_cropped_image(self.images[self.current_animation][self.animation_index])
        self.change_direction()

    def change_direction(self):
        if self.velocity_x < 0:
            self.direction = -1
        elif self.velocity_x > 0:
            self.direction = 1
        if self.direction == -1:  
            self.image = pygame.transform.flip(self.image, True, False)  
        elif self.direction == 1:  
            self.image = pygame.transform.flip(self.image, False, False)  

    def move_x(self, dx):
        if self.is_alive:
            self.velocity_x = dx

    def jump(self):
        if self.on_ground and not self.is_attacking and self.endurance >= 100 and self.is_alive:  
            self.velocity_y = -10  
            self.on_ground = False
            self.endurance -= 100

    def attack(self):
        if self.on_ground and not self.is_attacking and not self.taking_hit and self.endurance >= 80 and self.is_alive:
            rand = random.randint(1, 2)
            self.is_attacking = True
            self.endurance -= 80
            self.animation_index = 0
            self.current_animation = f'attack{rand}'
            self.attacking_flag = True

    def take_hit(self, damage):
        if self.is_alive:
            self.current_animation = 'take_hit'
            if not self.taking_hit:
                self.animation_index = 0
                self.animation_timer = 0
                self.taking_hit = True
            self.health -= damage

    def draw(self, screen):
        
        border_color = (255, 0, 0)  
        border_thickness = 2  
        pygame.draw.rect(screen, border_color, self.real_rect, border_thickness)  
        pygame.draw.rect(screen, border_color, self.rect, border_thickness)


def main():
    player = Player(300, 700, max_health=100)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYUP and event.key == pygame.K_z:
                player.attack()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.move_x(-5)
        elif keys[pygame.K_RIGHT]:
            player.move_x(5)
        else:
            player.move_x(0)
        if keys[pygame.K_SPACE]:
            player.jump()

        player.update()

        screen.fill((255, 255, 255))
        player.draw(screen)
        hero_group.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


