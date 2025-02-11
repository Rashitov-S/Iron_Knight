import random

import pygame
from methods import load_image
from groups import SpriteGroup
from particles import Particle
from damage_numbers import DamageText

pygame.init()
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

SKELETON_IDLE = [load_image(f"data/skeleton_idle/{x}.png") for x in range(1, 5)]
SKELETON_RUN = [load_image(f"data/skeleton_run/{x}.png") for x in range(1, 5)]
SKELETON_ATTACK = [load_image(f"data/skeleton_attack/{x}.png") for x in range(1, 9)]
SKELETON_DEATH = [load_image(f"data/skeleton_death/{x}.png") for x in range(1, 5)]
SKELETON_TAKE_HIT = [load_image(f"data/skeleton_take_hit/{x}.png") for x in range(1, 5)]

MUSHROOM_IDLE = [load_image(f"data/mushroom_idle/{x}.png") for x in range(1, 5)]
MUSHROOM_RUN = [load_image(f"data/mushroom_run/{x}.png") for x in range(1, 9)]
MUSHROOM_ATTACK = [load_image(f"data/mushroom_attack/{x}.png") for x in range(1, 9)]
MUSHROOM_DEATH = [load_image(f"data/mushroom_death/{x}.png") for x in range(1, 5)]
MUSHROOM_TAKE_HIT = [load_image(f"data/mushroom_take_hit/{x}.png") for x in range(1, 5)]

ARCHER_IDLE = [load_image(f"data/archer_idle/{x}.png") for x in range(1, 6)]
ARCHER_RUN = [load_image(f"data/archer_run/{x}.png") for x in range(1, 9)]
ARCHER_ATTACK = [load_image(f"data/archer_attack/{x}.png") for x in range(1, 12)]
ARCHER_DEATH = [load_image(f"data/archer_death/{x}.png") for x in range(1, 7)]
ARCHER_TAKE_HIT = [load_image(f"data/archer_take_hit/{x}.png") for x in range(1, 6)]
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
enemy_group = SpriteGroup()
weapon_object_group = SpriteGroup()

skeleton_images = {
    'idle': SKELETON_IDLE,
    'fall': SKELETON_IDLE,
    'run': SKELETON_RUN,
    'attack': SKELETON_ATTACK,
    'death': SKELETON_DEATH,
    'take_hit': SKELETON_TAKE_HIT
}

mushroom_images = {
    'idle': MUSHROOM_IDLE,
    'fall': MUSHROOM_IDLE,
    'run': MUSHROOM_RUN,
    'attack': MUSHROOM_ATTACK,
    'death': MUSHROOM_DEATH,
    'take_hit': MUSHROOM_TAKE_HIT
}

archer_images = {
    'idle': ARCHER_IDLE,
    'fall': ARCHER_IDLE,
    'run': ARCHER_RUN,
    'attack': ARCHER_ATTACK,
    'death': ARCHER_DEATH,
    'take_hit': ARCHER_TAKE_HIT
}


class Arrow(pygame.sprite.Sprite):
    def __init__(self, x, y, sprite_group, hero_group, direction, damage=20):
        super().__init__(weapon_object_group)
        print("создался")
        self.scale_factor = 1.5
        self.speed = 15 * direction
        self.sprite_group = sprite_group
        self.hero_group = hero_group
        self.distance = 0
        self.stopped = False
        self.rect = pygame.Rect(x - 10, y - 5, 30 * self.scale_factor, 5 * self.scale_factor)
        self.damage = damage
        self.original_image = load_image(f"data/weapon_objects/arrow.png")
        self.image = self.get_cropped_image(self.original_image)
        if direction == -1:
            self.image = pygame.transform.flip(self.image, True, False)

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
        y_pos = (self.rect.height - scaled_image.get_height()) // 2
        

        centered_image.blit(scaled_image, (x_pos, y_pos))

        return centered_image

    def update(self):
        if not self.stopped:
            self.check_for_collision_player()
            self.check_for_collision()
            self.rect.y += abs(self.distance / 500)
            self.rect.x += self.speed
            self.distance += self.speed
            self.speed -= 0.02

    def check_for_collision_player(self):
        if self.hero_group.get_sprites():
            player = self.hero_group.get_sprites()[0]
            if self.rect.colliderect(player.real_rect):
                player.take_hit(self.damage)
                Particle(player.real_rect.centerx, player.real_rect.centery, "spark1")
                self.destroy()

    def check_for_collision(self):
        for sprite in self.sprite_group:
            if self.rect.colliderect(sprite.rect):
                self.stop()

    def stop(self):
        self.stopped = True

    def destroy(self):
        self.kill()

    def draw(self, screen):
        border_color = (255, 0, 0)  
        border_thickness = 2  
        pygame.draw.rect(screen, border_color, self.rect, border_thickness)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, sprite_group, hero_group, images, max_health=100, enemy_type="melee", cur_lvl=1, name="skeleton"):
        super().__init__(enemy_group)
        self.enemy_type = enemy_type
        self.player = hero_group
        self.images = images
        self.name = name
        self.current_animation = 'idle'
        self.animation_index = 0
        self.scale_factor = 2
        self.damage = enemy_damage[cur_lvl][self.name]

        self.sprite_group = sprite_group

        self.is_attacking = False
        self.attack_timer = 0
        if self.enemy_type == "melee":
            self.search_rect = pygame.Rect(0, 0, 360, 55)
            self.original_rect = pygame.Rect(0, 0, 90, 55)
        elif self.enemy_type == "ranged":
            self.search_rect = pygame.Rect(0, 0, 540, 55)
            self.original_rect = pygame.Rect(0, 0, 450, 55)
        self.fact_rect = pygame.Rect(0, 0, 30, 55)

        
        self.search_rect.width *= self.scale_factor
        self.search_rect.height *= self.scale_factor

        x = x - self.fact_rect.width - 30
        y = y - self.fact_rect.height + 8

        self.rect = pygame.Rect(x, y,
                                self.original_rect.width * self.scale_factor,
                                self.original_rect.height * self.scale_factor)

        self.real_rect = pygame.Rect(self.rect.x + self.rect.width // 3,
                                     y,
                                     self.fact_rect.width * self.scale_factor,
                                     self.fact_rect.height * self.scale_factor)
        self.search_rect.center = self.rect.center
        self.image = self.get_cropped_image(self.images[self.current_animation][self.animation_index])

        self.is_alive = True
        self.is_expired = False
        self.expired_timer = 0
        self.health = max_health
        self.taking_hit = False

        self.gravity = 0.5
        self.on_ground = True

        self.velocity_x = 0
        self.velocity_y = 0
        self.animation_speed = 1
        self.animation_timer = 0

        self.current_alpha = 255

        self.direction = random.choice([-1, 1])

        self.need_obj = False

        self.walking_auto_delay = random.randint(300, 800)
        self.walking_auto_timer = 0

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

        if self.current_animation == 'death':
            
            y_pos = self.rect.height - scaled_image.get_height()
        else:
            
            y_pos = (self.rect.height - scaled_image.get_height()) // 2
        y_pos = self.rect.height - scaled_image.get_height()

        
        centered_image.blit(scaled_image, (x_pos, y_pos))

        return centered_image

    def update(self):
        self.check_health()
        if self.is_alive:
            self.walk_auto()
            self.search_player()
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
                if self.current_animation == 'take_hit' and self.animation_index == len(SKELETON_TAKE_HIT) - 1:
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
        self.search_rect.center = self.real_rect.center

        self.update_animation()
        self._check_ground()
        self.spawn_object()

    def walk_auto(self):
        self.walking_auto_timer += 1
        if 0 < self.walking_auto_timer - self.walking_auto_delay < 60:
            if self.walking_auto_timer - self.walking_auto_delay == 59:
                self.walking_auto_timer = 0
                self.direction *= -1
                print(self.direction)
            self.move_x(5 * self.direction)
        else:
            self.move_x(0)

    def search_player(self):
        if self.player.get_sprites():
            player = self.player.get_sprites()[0]
            if player.is_alive and self.search_rect.colliderect(player.real_rect):
                if not self.rect.colliderect(player.real_rect):
                    direction = 1 if player.real_rect.centerx > self.search_rect.centerx else -1
                    self.move_x(4 * direction)
                else:
                    if self.attack() == "continued":
                        Particle(player.real_rect.centerx, player.real_rect.centery, "spark1")
                        player.take_hit(self.damage)

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

    def check_health(self):
        if self.health <= 0 and self.is_alive:
            self.health = 0
            self.is_alive = False
            if self.current_animation != 'death':
                self.current_animation = 'death'
                self.animation_index = 0
                self.animation_timer = 0
        elif not self.is_alive and not self.is_expired:
            if self.expired_timer < 600:
                self.expired_timer += 1
            else:
                self.current_alpha -= 5
                if self.current_alpha <= 0:
                    self.expired_timer = 0
                    self.is_expired = True
        elif self.is_expired:
            self.kill()

    def spawn_object(self):
        if self.enemy_type == 'ranged':
            if self.need_obj and self.current_animation == 'attack' and self.animation_index == len(
                    self.images[self.current_animation]) - 2 and self.is_alive:
                Arrow(self.real_rect.midright[0], self.real_rect.midright[1], self.sprite_group, self.player,
                      self.direction, self.damage)
                self.need_obj = False

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

        self.image = self.get_cropped_image(self.images[self.current_animation][self.animation_index])
        self.image.set_alpha(self.current_alpha)

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

    def take_hit(self, damage):
        if self.is_alive:
            self.current_animation = 'take_hit'
            if not self.taking_hit:
                self.animation_index = 0
                self.animation_timer = 0
                self.taking_hit = True
            DamageText(self.real_rect.centerx, self.real_rect.centery, damage)
            self.health -= damage

    def attack(self):
        if self.on_ground and not self.is_attacking and not self.taking_hit and self.is_alive:
            self.is_attacking = True
            self.animation_index = 0
            self.current_animation = 'attack'
            self.need_obj = True
            print("начал")
            return "started"
        elif self.is_attacking and not self.taking_hit and self.is_alive and self.current_animation == 'attack' and self.animation_index == len(
                self.images[self.current_animation]) - 3 and self.enemy_type == 'melee' and self.animation_timer == 2:
            print(self.animation_timer)
            print(self.animation_speed)
            print("продолжил")
            return "continued"
        return False

    def draw(self, screen):
        
        border_color = (255, 0, 0)  
        border_thickness = 2  
        pygame.draw.rect(screen, border_color, self.real_rect, border_thickness)  
        pygame.draw.rect(screen, border_color, self.rect, border_thickness)
        pygame.draw.rect(screen, border_color, self.search_rect, border_thickness)


def main():
    player = Enemy(300, 700, sprite_group=SpriteGroup(), images=skeleton_images)

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

        screen.fill((0, 0, 0))
        player.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == '__main__':
    main()
