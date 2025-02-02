import pygame


tile_width = tile_height = 50
enemy_group = pygame.sprite.Group()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, enemy_image):
        super().__init__(enemy_group)
        self.image = enemy_image
        self.x = pos_x
        self.y = pos_y
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.mask = pygame.mask.from_surface(self.image)
        self.COUNTSPEEDCHARACTER = 0
        self.CANWALK = True

    def update(self, daddy):  # ДОПИСАТЬ
        if self.COUNTSPEEDCHARACTER > 16 and self.CANWALK:
            if daddy[self.x][self.y][0] - self.x > 0:
                self.rect.x += 50
                self.x += 1
            elif daddy[self.x][self.y][0] - self.x < 0:
                self.rect.x -= 50
                self.x -= 1
            elif daddy[self.x][self.y][1] - self.y > 0:
                self.rect.y += 50
                self.y += 1
            elif daddy[self.x][self.y][1] - self.y < 0:
                self.rect.y -= 50
                self.y -= 1
            self.COUNTSPEEDCHARACTER = 0
        self.COUNTSPEEDCHARACTER += 1
