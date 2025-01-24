import pygame
import sys
import os
from screeninfo import get_monitors

import queue  # очередь, надо при нахождении кратчайших путей


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


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def terminate():
    pygame.quit()
    sys.exit()



# Константы

FPS = 50
pygame.init()
size = WIDTH, HEIGHT = width, height = 600, 600
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png'),
    'enemy': pygame.transform.scale(load_image('enemy.png'), (50, 50))
}
player_image = pygame.transform.scale(load_image('mar.png'), (50, 50))
enemy_image = pygame.transform.scale(load_image('enemy.png'), (50, 50))


monitors = get_monitors()
image = load_image("fon.jpg", -1)
image = pygame.transform.scale(image, (monitors[0].width - 1, monitors[0].height - 1))
screen.blit(image, (0, 0))


tile_width = tile_height = 50

LEFT = False
RIGHT = False
UP = False
DOWN = False
running = True
fullscreen = True
#



class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        if tile_type == 'empty':
            super().__init__(grasses_group, all_sprites)
        if tile_type == 'wall':
            super().__init__(walls_group, all_sprites)
        if tile_type == 'enemy':
            super().__init__(enemy_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.mask = pygame.mask.from_surface(self.image)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.mask = pygame.mask.from_surface(self.image)
        self.x = pos_x
        self.y = pos_y
        self.COUNTSPEEDCHARACTER = 0

    def shortest_paths(self, lvl):  # получаем сохранённую карту, которую получали из load_level. Вернйм карту с
        # родителем, из которого мы пришли, используется bfs
        n, m = len(lvl), len(lvl[0])
        shortest_paths = [[1e20] * m for i in range(n)]
        daddies = [[-1] * m for i in range(n)]
        daddies[self.x][self.y] = (self.x, self.y)
        shortest_paths[self.x][self.y] = 0
        q = queue.Queue()
        q.put((self.x, self.y))
        while not q.empty():
            x, y = q.get()
            q.task_done()
            if lvl[x][y] != '#':
                if x > 0 and shortest_paths[x - 1][y] == 1e20:
                    shortest_paths[x - 1][y] = shortest_paths[x][y] + 1
                    daddies[x - 1][y] = (x, y)
                    q.put((x - 1, y))
                if x < n and shortest_paths[x + 1][y] == 1e20:
                    shortest_paths[x + 1][y] = shortest_paths[x][y] + 1
                    daddies[x + 1][y] = (x, y)
                    q.put((x + 1, y))
                if y > 0 and shortest_paths[x][y - 1] == 1e20:
                    shortest_paths[x][y - 1] = shortest_paths[x][y] + 1
                    daddies[x][y - 1] = (x, y)
                    q.put((x, y - 1))
                if y < m and shortest_paths[x][y + 1] == 1e20:
                    shortest_paths[x][y + 1] = shortest_paths[x][y] + 1
                    daddies[x][y + 1] = (x, y)
                    q.put((x, y + 1))
        return daddies


    def update(self):  # передвижение основного персонажа
        if self.COUNTSPEEDCHARACTER > 5:  # передвигаемся каждые пять тиков
            if LEFT:
                player.rect.x -= 50
                self.x -= 1
                if any(pygame.sprite.collide_mask(self, x) for x in walls_group):
                    player.rect.x += 50
                    self.x += 1
            if RIGHT:
                player.rect.x += 50
                self.x += 1
                if any(pygame.sprite.collide_mask(self, x) for x in walls_group):
                    player.rect.x -= 50
                    self.x -= 1
            if UP:
                player.rect.y -= 50
                self.y -= 1
                if any(pygame.sprite.collide_mask(self, x) for x in walls_group):
                    player.rect.y += 50
                    self.y += 1
            if DOWN:
                player.rect.y += 50
                self.y += 1
                if any(pygame.sprite.collide_mask(self, x) for x in walls_group):
                    player.rect.y -= 50
                    self.y -= 1
            self.COUNTSPEEDCHARACTER = 0
        self.COUNTSPEEDCHARACTER += 1


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(enemy_group, all_sprites)
        self.image = enemy_image
        self.x = pos_x
        self.y = pos_y
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.mask = pygame.mask.from_surface(self.image)
        self.COUNTSPEEDCHARACTER = 0

    def update(self, daddy):  # ДОПИСАТЬ
        if self.COUNTSPEEDCHARACTER > 8:
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


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.' :
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
            elif level[y][x] == '!':
                Tile('empty', x, y)
                Enemy(x, y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)





if __name__ == '__main__':
    player = None

    # группы спрайтов
    all_sprites = pygame.sprite.Group()
    grasses_group = pygame.sprite.Group()
    walls_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()
    level = load_level('map.txt')
    player, level_x, level_y = generate_level(level)
    camera = Camera()
    running = True

    while running:
        screen.fill((0, 0, 0))
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
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

        screen.blit(image, (0, 0))
        player.update()
        daddies = player.shortest_paths(level)
        # обновление расположения врагов
        for el in enemy_group:
            el.update(daddies)
        camera.update(player)
        # обновляем положение всех спрайтов
        for sprite in all_sprites:
            camera.apply(sprite)

        grasses_group.draw(screen)
        walls_group.draw(screen)
        player_group.draw(screen)
        enemy_group.draw(screen)
        pygame.display.flip()

    pygame.quit()
# лалул
