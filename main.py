import pygame
import sys
import os
from screeninfo import get_monitors


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
    'empty': load_image('grass.png')
}
player_image = load_image('mar.png')


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
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.mask = pygame.mask.from_surface(self.image)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)
        self.mask = pygame.mask.from_surface(self.image)
        self.COUNTSPEEDCHARACTER = 0

    def update(self):
        if self.COUNTSPEEDCHARACTER > 5:
            if LEFT:
                player.rect.x -= 50
                if any(pygame.sprite.collide_mask(self, x) for x in walls_group):
                    player.rect.x += 50
            if RIGHT:
                player.rect.x += 50
                if any(pygame.sprite.collide_mask(self, x) for x in walls_group):
                    player.rect.x -= 50
            if UP:
                player.rect.y -= 50
                if any(pygame.sprite.collide_mask(self, x) for x in walls_group):
                    player.rect.y += 50
            if DOWN:
                player.rect.y += 50
                if any(pygame.sprite.collide_mask(self, x) for x in walls_group):
                    player.rect.y -= 50
            self.COUNTSPEEDCHARACTER = 0
        self.COUNTSPEEDCHARACTER += 1


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
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
    player, level_x, level_y = generate_level(load_level('map.txt'))
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
        camera.update(player)
        # обновляем положение всех спрайтов
        for sprite in all_sprites:
            camera.apply(sprite)

        grasses_group.draw(screen)
        walls_group.draw(screen)
        player_group.draw(screen)

        pygame.display.flip()

    pygame.quit()
# лалул
