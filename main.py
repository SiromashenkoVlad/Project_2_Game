import pygame
import sys
import os
from screeninfo import get_monitors

import queue  # очередь, надо при нахождении кратчайших путей
from datetime import datetime
import time

from Sprites import all_sprites, grasses_group, walls_group, player_group, enemy_group, sword_group, bush_group
from Camera import Camera
from Enemy import Enemy


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
    'empty2': load_image('bush.png'),
    'enemy': pygame.transform.scale(load_image('enemy.png'), (50, 50))
}
player_image = pygame.transform.scale(load_image('mar.png'), (50, 50))
enemy_image = pygame.transform.scale(load_image('enemy.png', -1), (50, 50))
corpse_image = load_image('corpse.png')
endscreen_image = load_image('endscreen.png')
startscreen_image = load_image('startscreen.png')
animation_images = [load_image('an1.png'), load_image('an2.png'), load_image('an3.png'),
                    load_image('an4.png'), load_image('an5.png'), load_image('an6.png')]
monitors = get_monitors()
image = pygame.transform.scale(load_image("fon.png"), size)
screen.blit(image, (0, 0))

# загрузка музыки
sound_zastavka = os.path.join(f'data/ИГРА ЗАСТАВКА МУЗЫКА.mp3')
sound_battle = os.path.join(f'data/Музыка для игры 2.mp3')
sound_death = os.path.join(f'data/аудио_1_1.mp3')
sound_swing = os.path.join(f'data/se swing.mp3')
sound_walk_1 = os.path.join(f'data/шаг_1.mp3')
sound_walk_2 = os.path.join(f'data/шаг_2.mp3')
sound_z = pygame.mixer.Sound(sound_zastavka)
sound_z.play(loops=-1)
sound_z.set_volume(0.2)
sound_b = pygame.mixer.Sound(sound_battle)
sound_d = pygame.mixer.Sound(sound_death)
sound_s = pygame.mixer.Sound(sound_swing)
sound_w1 = pygame.mixer.Sound(sound_walk_1)
sound_w2 = pygame.mixer.Sound(sound_walk_2)
sound_s.set_volume(0.15)

tile_width = tile_height = 50

LEFT = False
RIGHT = False
UP = False
DOWN = False
DIRECTION = "EAST"
ATTACK = 0
FIRST_ROOM = 1
counter_walk = 0
SOUND_WALK = False

running = True
fullscreen = True


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        if tile_type == 'empty':
            super().__init__(grasses_group, all_sprites)
        if tile_type == 'wall':
            super().__init__(walls_group, all_sprites)
        if tile_type == 'enemy':
            super().__init__(enemy_group, all_sprites)
        if tile_type == 'empty2':
            super().__init__(bush_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.mask = pygame.mask.from_surface(self.image)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = pygame.transform.scale(load_image(f'mar.png'), (50, 50))
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.mask = pygame.mask.from_surface(self.image)
        print(pos_x, pos_y)
        self.x = pos_x
        self.y = pos_y
        self.COUNTSPEEDCHARACTER = 0
        self.ind = 0

    def shortest_paths(self, lvl):  # получаем сохранённую карту, которую получали из load_level. Вернйм карту с
        # родителем, из которого мы пришли, используется bfs
        n, m = len(lvl), len(lvl[0])
        shortest_paths = [[1e20] * n for i in range(m)]
        daddies = [[-1] * n for i in range(m)]
        daddies[self.x][self.y] = (self.x, self.y)
        shortest_paths[self.x][self.y] = 0
        q = queue.Queue()
        q.put((self.x, self.y))
        while not q.empty():
            x, y = q.get()
            q.task_done()
            if lvl[y][x] != '#':
                if x > 0 and shortest_paths[x - 1][y] == 1e20:
                    shortest_paths[x - 1][y] = shortest_paths[x][y] + 1
                    q.put((x - 1, y))
                    daddies[x - 1][y] = (x, y)

                if x < n and shortest_paths[x + 1][y] == 1e20:
                    shortest_paths[x + 1][y] = shortest_paths[x][y] + 1
                    q.put((x + 1, y))
                    daddies[x + 1][y] = (x, y)

                if y > 0 and shortest_paths[x][y - 1] == 1e20:
                    shortest_paths[x][y - 1] = shortest_paths[x][y] + 1
                    q.put((x, y - 1))
                    daddies[x][y - 1] = (x, y)

                if y < m and shortest_paths[x][y + 1] == 1e20:
                    shortest_paths[x][y + 1] = shortest_paths[x][y] + 1
                    q.put((x, y + 1))
                    daddies[x][y + 1] = (x, y)
        return daddies

    def update(self):  # передвижение основного персонажа
        if self.COUNTSPEEDCHARACTER > 5:  # передвигаемся каждые пять тиков
            if LEFT or RIGHT or UP or DOWN:
                self.image = pygame.transform.scale(animation_images[self.ind % 6], (50, 50))
                self.ind += 1
            else:
                self.image = pygame.transform.scale(animation_images[0], (50, 50))

            if LEFT:
                self.rect.x -= 50
                self.x -= 1
                if any(pygame.sprite.collide_mask(self, x) for x in walls_group):
                    self.rect.x += 50
                    self.x += 1
            if RIGHT:
                self.rect.x += 50
                self.x += 1
                if any(pygame.sprite.collide_mask(self, x) for x in walls_group):
                    self.rect.x -= 50
                    self.x -= 1
            if UP:
                self.rect.y -= 50
                self.y -= 1
                if any(pygame.sprite.collide_mask(self, x) for x in walls_group):
                    self.rect.y += 50
                    self.y += 1
            if DOWN:
                self.rect.y += 50
                self.y += 1
                if any(pygame.sprite.collide_mask(self, x) for x in walls_group):
                    self.rect.y -= 50
                    self.y -= 1
            self.COUNTSPEEDCHARACTER = 0

        if any(pygame.sprite.collide_mask(self, x) and x.CANWALK for x in enemy_group):
            end_screen("You are dead")
        sword.change_position(self.x, self.y)
        self.COUNTSPEEDCHARACTER += 1


class Sword(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(sword_group, all_sprites)

        self.image = pygame.transform.scale(load_image('sword.png'), (25, 80))
        self.image = pygame.transform.rotate(self.image, -45)
        self.x = pos_x
        self.y = pos_y
        self.pos_x = tile_width * pos_x + 15
        self.pos_y = tile_height * pos_y - 30
        self.rect = self.image.get_rect().move(
            self.pos_x, self.pos_y)
        self.mask = pygame.mask.from_surface(self.image)
        self.angle = -100

    def change_position(self, pos_x, pos_y):
        self.x = player.x
        self.y = player.y
        self.pos_x = player.rect.x + 15
        self.pos_y = player.rect.y + 15
        self.rect = self.image.get_rect().move(
            self.pos_x, self.pos_y)
        self.mask = pygame.mask.from_surface(self.image)

    def blitRotate(self, surf, pos):
        image = pygame.transform.scale(load_image('sword.png'), (25, 80))
        image = pygame.transform.rotate(image, -100)
        w, h = image.get_size()
        box = [pygame.math.Vector2(p) for p in [(0, 0), (w, 0), (w, -h), (0, -h)]]
        box_rotate = [p.rotate(self.angle) for p in box]
        min_box = (min(box_rotate, key=lambda p: p[0])[0], min(box_rotate, key=lambda p: p[1])[1])
        max_box = (max(box_rotate, key=lambda p: p[0])[0], max(box_rotate, key=lambda p: p[1])[1])
        origin = (self.pos_x + min_box[0], self.pos_y - max_box[1])

        self.rect = self.image.get_rect().move(origin)
        self.mask = pygame.mask.from_surface(self.image)

        self.image = rotated_image = pygame.transform.rotate(image, self.angle)
        surf.blit(rotated_image, origin)
        self.angle -= 15

        for x in enemy_group:
            if pygame.sprite.collide_mask(self, x):
                x.CANWALK = False
                x.image = corpse_image


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
            elif level[y][x] == '!':
                Tile('empty', x, y)
                Enemy(x, y, enemy_image)
            elif level[y][x] == '$':
                Tile('empty2', x, y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


def start_screen():
    intro_text = ["Добро пожаловать!", "",
                  "Нажмите кнопку мыши,",
                  "Чтобы начать игру"]

    screen.fill((0, 0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    ind = 0
    time = 0

    while True:
        screen.blit(pygame.transform.scale(startscreen_image, size), (0, 0))
        font = pygame.font.Font(None, 30)
        text_coord = 50
        for line in intro_text:
            string_rendered = font.render(line, 2, pygame.Color('black'))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 30
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)
        time += 1
        if time > 10:
            time = 0
            ind += 1
        im_an = pygame.transform.scale(animation_images[ind % 6], (100, 100))
        screen.blit(im_an, (250, 250))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                sound_z.stop()
                sound_b.play(loops=-1)
                sound_b.set_volume(0.2)
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


def end_screen(text="The end"):
    sound_b.stop()
    sound_d.play(loops=-1)
    sound_d.set_volume(0.3)
    intro_text = [text]
    rec = open('records.txt', 'r+').readlines()
    best_time = float(rec[0])
    if best_time > (datetime.now() - start_time).total_seconds():
        intro_text.append(f'Your time: {(datetime.now() - start_time).total_seconds()}')
        if text == "The end":
            f = open('records.txt', 'w')
            f.truncate(0)
            f.write(str((datetime.now() - start_time).total_seconds()))
    else:
        intro_text.append(f'Your time: {(datetime.now() - start_time).total_seconds()}')
    intro_text.append(f'Best time: {best_time}')
    # fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    # screen.blit(fon, (0, 0))

    while True:
        screen.blit(pygame.transform.scale(endscreen_image, size), (0, 0))
        font = pygame.font.Font(None, 50)
        text_coord = 50
        for line in intro_text:
            string_rendered = font.render(line, 1, pygame.Color('black'))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 30
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    player = None

    start_time = datetime.now()
    start_screen()

    # загрузка уровня
    level = load_level('map.txt')
    player, level_x, level_y = generate_level(level)
    camera = Camera()

    sword = Sword(player.x, player.y)
    running = True

    while running:

        if all(en.CANWALK == False for en in enemy_group) and FIRST_ROOM:
            all_sprites.empty()
            grasses_group.empty()
            walls_group.empty()
            player_group.empty()
            enemy_group.empty()
            sword_group.empty()
            bush_group.empty()
            screen.blit(image, (0, 0))
            level = load_level('map2.txt')
            player, level_x, level_y = generate_level(level)
            daddies = player.shortest_paths(level)
            sword = Sword(player.x, player.y)
            FIRST_ROOM = not FIRST_ROOM
        elif all(en.CANWALK == False for en in enemy_group):
            end_screen()

        screen.fill((0, 0, 0))
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    LEFT = True
                    DIRECTION = "WEST"
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    RIGHT = True
                    DIRECTION = "EAST"
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    UP = True
                    DIRECTION = "NORTH"
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    DOWN = True
                    DIRECTION = "SOUTH"

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    LEFT = False
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    RIGHT = False
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    UP = False
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    DOWN = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                ATTACK = 1
                sound_s.play()
                # Звук Удара

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

        if 0 < ATTACK < 25:
            sword.blitRotate(screen, (tile_width * player.x, tile_height * player.y))
            ATTACK += 1
        elif ATTACK > 25:
            ATTACK = 0

        bush_group.draw(screen)
        grasses_group.draw(screen)
        walls_group.draw(screen)
        enemy_group.draw(screen)
        player_group.draw(screen)
        sword_group.draw(screen)
        pygame.display.flip()

    pygame.quit()
