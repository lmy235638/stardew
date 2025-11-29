import pygame
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic, Water, Tree
from pytmx import load_pygame
from sprites import WildFlower
from support import import_folder


class Level:
    def __init__(self):
        # get the display surface
        self.display_surface = pygame.display.get_surface()

        # sprite groups
        self.all_sprites = CameraGroup()
        self.collision_sprites = pygame.sprite.Group()  # 所有需要碰撞的物体
        self.tree_sprites = pygame.sprite.Group()

        self.setup()
        self.overlay = Overlay(self.player)

    def setup(self):
        tmx_data = load_pygame('assets/data/map.tmx')

        # house
        for layer in ['HouseFloor', 'HouseFurnitureBottom']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE),
                        surf,
                        self.all_sprites,
                        z=LAYERS['house bottom']
                        ).sprite_type = 'house'
        for layer in ['HouseWalls', 'HouseFurnitureTop']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE),
                        surf,
                        self.all_sprites,
                        z=LAYERS['main']
                        ).sprite_type = 'house'

        # fence
        for x, y, surf in tmx_data.get_layer_by_name('Fence').tiles():
            Generic((x * TILE_SIZE, y * TILE_SIZE),
                    surf,
                    [self.all_sprites, self.collision_sprites],
                    z=LAYERS['main']
                    ).sprite_type = 'fence'

        # water
        water_frames = import_folder('assets/graphics/water')
        for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
            Water((x * TILE_SIZE, y * TILE_SIZE), water_frames, self.all_sprites)

        # trees
        for obj in tmx_data.get_layer_by_name('Trees'):
            Tree(pos=(obj.x, obj.y),
                 surf=obj.image,
                 groups=[self.all_sprites, self.collision_sprites, self.tree_sprites],
                 name=obj.name)

        # wildflowers
        for obj in tmx_data.get_layer_by_name('Decoration'):
            WildFlower(pos=(obj.x, obj.y), surf=obj.image, groups=[self.all_sprites, self.collision_sprites])

        # collision tiles
        for x, y, surf in tmx_data.get_layer_by_name('Collision').tiles():
            Generic((x * TILE_SIZE, y * TILE_SIZE),
                    pygame.Surface((TILE_SIZE, TILE_SIZE)),
                    self.collision_sprites
                    ).sprite_type = 'collision'

        # player
        for obj in tmx_data.get_layer_by_name('Player'):
            if obj.name == 'Start':
                self.player = Player(pos=(obj.x, obj.y),
                                     groups=self.all_sprites,
                                     collision_sprites=self.collision_sprites,
                                     tree_sprites=self.tree_sprites)

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

        # 打印所有sprite的类别信息
        for sprite in self.sprites():
            sprite.print_sprite_info()

        # 按图层绘制, 高图层会覆盖低图层
        for layer in LAYERS.values():
            for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
                if sprite.z == layer:
                    offset_rect = sprite.rect.copy()  # offset仅用于视觉效果, 不改变世界坐标系中实际位置
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect)

                    # # 详细调试苹果
                    # if hasattr(sprite, 'apple_sprites'):
                    #     print(f"Drawing tree with {len(sprite.apple_sprites.sprites())} apples")  # 输出苹果总数
                    #     for apple in sprite.apple_sprites.sprites():
                    #         apple_rect = apple.rect.copy()
                    #         apple_offset_rect = apple_rect.copy()
                    #         apple_offset_rect.center -= self.offset
                    #
                    #         # 检查苹果是否在屏幕内并输出结果
                    #         screen_rect = self.display_surface.get_rect()
                    #         is_on_screen = screen_rect.colliderect(apple_offset_rect)
                    #         print(f"Apple at {apple.rect.center} - On screen: {is_on_screen}")  # 输出每个苹果的位置和是否在屏幕内

                    # # 红色:玩家rect边界, 绿色: hitbox碰撞边界, 蓝色: 工具作用点
                    # if sprite == player and layer == LAYERS['main']:
                    #     print(f'enter {sprite.__str__()}')
                    #     pygame.draw.rect(self.display_surface, 'red', offset_rect, 5)
                    #     hitbox_rect = player.hitbox.copy()
                    #     hitbox_rect.center = offset_rect.center
                    #     pygame.draw.rect(self.display_surface, 'green', hitbox_rect, 5)
                    #     target_pos = offset_rect.center + PLAYER_TOOL_OFFSET[player.status.split('_')[0]]
                    #     pygame.draw.circle(self.display_surface, 'blue', target_pos, 5)

        # 玩家边界
        offset_rect = player.rect.copy()
        offset_rect.center -= self.offset
        pygame.draw.rect(self.display_surface, 'red', offset_rect, 5)
        # 碰撞箱
        hitbox_rect = player.hitbox.copy()
        hitbox_rect.center = offset_rect.center
        pygame.draw.rect(self.display_surface, 'green', hitbox_rect, 5)
        # 工具目标点
        target_pos = offset_rect.center + PLAYER_TOOL_OFFSET[player.status.split('_')[0]]
        pygame.draw.circle(self.display_surface, 'blue', target_pos, 5)
