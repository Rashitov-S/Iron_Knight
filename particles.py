import pygame
from methods import load_image
from groups import SpriteGroup

SPARK1 = [load_image(f"particles/spark1/{x}.png") for x in range(1, 21)]
particles_group = SpriteGroup()


class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, particle_type):
        super().__init__(particles_group)
        self.scale_factor = 1.5
        self.rect = pygame.Rect(0, 0, 100 * self.scale_factor, 100 * self.scale_factor)
        self.rect.center = x, y
        self.particle_type = particle_type
        self.images = {
            'spark1': SPARK1
        }
        self.animation_index = 0
        self.animation_speed = 71
        self.animation_timer = 0
        self.image = self.get_cropped_image(self.images[self.particle_type][self.animation_index])



    def update(self):
        self.update_animation()

    def update_animation(self):
        self.animation_timer += self.animation_speed
        if self.animation_timer >= 10:
            self.animation_timer = 0
            self.animation_index += 1
        if self.animation_index >= len(self.images[self.particle_type]):
            self.destroy()
            print("уничтожил")
        else:
            self.image = self.get_cropped_image(self.images[self.particle_type][self.animation_index])

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

    def destroy(self):
        self.kill()

    def draw(self, screen):
        border_color = (255, 0, 0)  
        border_thickness = 2  
        pygame.draw.rect(screen, border_color, self.rect, border_thickness)
