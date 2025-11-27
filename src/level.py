import pygame
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic, Water, Tree
from pytmx import load_pygame

from src.sprites import WildFlower
from support import import_folder


class Level:
    def __init__(self):
        # get the display surface
        self.display_surface = pygame.display.get_surface()

        # sprite groups
        self.all_sprites = CameraGroup()
        self.collision_sprites = pygame.sprite.Group()  # 所有需要碰撞的物体

        self.setup()
        self.overlay = Overlay(self.player)

    def setup(self):
        tmx_data = load_pygame('assets/data/map.tmx')

        # house
        for layer in ['HouseFloor', 'HouseFurnitureBottom']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, z=LAYERS['house bottom'])
        for layer in ['HouseWalls', 'HouseFurnitureTop']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, z=LAYERS['main'])

        # fence
        for x, y, surf in tmx_data.get_layer_by_name('Fence').tiles():
            Generic((x * TILE_SIZE, y * TILE_SIZE), surf, [self.all_sprites, self.collision_sprites], z=LAYERS['main'])

        # water
        water_frames = import_folder('assets/graphics/water')
        for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
            Water((x * TILE_SIZE, y * TILE_SIZE), water_frames, self.all_sprites)

        # trees
        for obj in tmx_data.get_layer_by_name('Trees'):
            Tree((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites], obj.name)

        # wildflowers
        for obj in tmx_data.get_layer_by_name('Decoration'):
            WildFlower(pos=(obj.x, obj.y), surf=obj.image, groups=[self.all_sprites, self.collision_sprites])

        # collision tiles
        for x, y, surf in tmx_data.get_layer_by_name('Collision').tiles():
            Generic((x * TILE_SIZE, y * TILE_SIZE), pygame.Surface((TILE_SIZE, TILE_SIZE)), self.collision_sprites)

        # player
        for obj in tmx_data.get_layer_by_name('Player'):
            if obj.name == 'Start':
                self.player = Player(pos=(obj.x, obj.y), groups=self.all_sprites, collision_sprites=self.collision_sprites)

        # ground
        Generic(
            pos=(0, 0),
            surf=pygame.image.load('assets/graphics/world/ground.png').convert_alpha(),
            groups=self.all_sprites,
            z=LAYERS['ground']
        )

    def run(self, dt):
        self.display_surface.fill('black')
        self.all_sprites.customize_draw(self.player)
        self.all_sprites.update(dt)

        self.overlay.display()


class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()

    def customize_draw(self, player):
        # 计算camera与player的偏移
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2

        # 按图层绘制, 高图层会覆盖低图层
        for layer in LAYERS.values():
            for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
                if sprite.z == layer:
                    offset_rect = sprite.rect.copy()    # offset仅用于视觉效果, 不改变世界坐标系中实际位置
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect)
