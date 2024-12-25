import os
import sys

import pygame
from screeninfo import get_monitors


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


class MainCharacter(pygame.sprite.Sprite):
    image = load_image("picachu.png")

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


class Board:
    # создание поля
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        # значения клеток по умолчанию(не по умолчанию пока не хочется)
        self.left = 10
        self.top = 10
        self.cell_size = 50

        # установка главного героя на доске
        self.character = MainCharacter()
        self.character.set_place((width // 2) * self.cell_size + self.left, (height // 2) * self.cell_size + self.top)
        self.board[width // 2][height // 2] = 1

    # настройка внешнего вида
    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, screen):
        for x in range(self.width):
            for y in range(self.height):
                if self.board[x][y] != 1:
                    pygame.draw.rect(screen, pygame.Color('black'),
                                     (x * self.cell_size + self.left, y * self.cell_size + self.top, self.cell_size,
                                      self.cell_size))
                pygame.draw.rect(screen, pygame.Color('white'),
                                 (x * self.cell_size + self.left, y * self.cell_size + self.top, self.cell_size,
                                  self.cell_size), 1)

    def get_click(self, mouse_pos):  # переписать
        cell = self.get_cell(mouse_pos)
        if cell:
            self.on_click(cell)
            self.render(screen)
        else:
            print(None)

    def get_cell(self, mouse_pos):
        cell_x = (mouse_pos[0] - self.left) // self.cell_size
        cell_y = (mouse_pos[1] - self.top) // self.cell_size
        if cell_x < 0 or cell_x >= self.width or cell_y < 0 or cell_y >= self.height:
            return None
        return cell_x, cell_y

    def on_click(self, cell):
        print(cell)
        self.board[cell[1]][cell[0]] = (self.board[cell[1]][cell[0]] + 1) % 3


if __name__ == '__main__':
    m = get_monitors()
    pygame.init()
    size = width, height = 800, 400
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)  # Открытие на весь экран

    characters = pygame.sprite.Group()
    MainCharacter(characters)

    board = Board(m[0].width // 50, m[0].height // 50)
    running = True
    fullscreen = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                board.get_click(event.pos)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        win = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        win = pygame.display.set_mode((800, 600))
        screen.fill((0, 0, 0))
        characters.draw(screen)
        characters.update()
        board.render(screen)
        pygame.display.flip()
    pygame.quit()
