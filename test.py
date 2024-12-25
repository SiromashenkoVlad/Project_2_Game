import os
import sys

import pygame
from screeninfo import get_monitors

pygame.init()
size = width, height = 800, 400
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)  # Открытие на весь экран
clock = pygame.time.Clock()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class MainCharacter(pygame.sprite.Sprite):
    image = load_image("picachu.png", -1)
    image = pygame.transform.scale(image, (75, 75))

    def __init__(self, *group):
        # НЕОБХОДИМО вызвать конструктор родительского класса Sprite.
        # Это очень важно!!!
        super().__init__(*group)
        self.image = MainCharacter.image
        self.rect = self.image.get_rect()
        self.rect.x = 1
        self.rect.y = 1

    def set_place(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def update(self):
        if LEFT:
            self.rect = self.rect.move(-3, 0)
        if RIGHT:
            self.rect = self.rect.move(3, 0)
        if UP:
            self.rect = self.rect.move(0, -3)
        if DOWN:
            self.rect = self.rect.move(0, 3)


class Floor(pygame.sprite.Sprite):
    image = load_image("picachu.png", -1)
    image = pygame.transform.scale(image, (75, 75))

    def __init__(self, *group):
        # НЕОБХОДИМО вызвать конструктор родительского класса Sprite.
        # Это очень важно!!!
        super().__init__(*group)
        floor = load_image("floor.png", -1)
        floor_on_sz = pygame.transform.scale(floor, (m[0].width - 1, m[0].height - 1))
        screen.blit(floor_on_sz, (0, 0))


if __name__ == '__main__':
    m = get_monitors()

    floor = load_image("floor.png", -1)
    floor_on_sz = pygame.transform.scale(floor, (m[0].width - 1, m[0].height - 1))
    screen.blit(floor_on_sz, (0, 0))

    characters = pygame.sprite.Group()
    we = MainCharacter(characters)
    we.set_place((m[0].width - we.rect.width) // 2, (m[0].height - we.rect.height // 2) // 2)

    # Константы
    LEFT = False
    RIGHT = False
    UP = False
    DOWN = False
    running = True
    fullscreen = True
    #

    while running:
        clock.tick(125)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        win = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                        floor_on_sz = pygame.transform.scale(floor, (m[0].width - 1, m[0].height - 1))
                        screen.blit(floor_on_sz, (0, 0))
                    else:
                        win = pygame.display.set_mode((800, 600))
                        floor_on_sz = pygame.transform.scale(floor, (800, 600))
                        screen.blit(floor_on_sz, (0, 0))
                if event.key == pygame.K_LEFT:
                    LEFT = True
                if event.key == pygame.K_RIGHT:
                    RIGHT = True
                if event.key == pygame.K_UP:
                    UP = True
                if event.key == pygame.K_DOWN:
                    DOWN = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    LEFT = False
                if event.key == pygame.K_RIGHT:
                    RIGHT = False
                if event.key == pygame.K_UP:
                    UP = False
                if event.key == pygame.K_DOWN:
                    DOWN = False

        screen.blit(floor_on_sz, (0, 0))
        characters.draw(screen)
        characters.update()
        pygame.display.flip()

    pygame.quit()
