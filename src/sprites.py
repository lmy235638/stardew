from random import randint, choice
import pygame
from settings import *
from timer import Timer


class Generic(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, z=LAYERS['main']):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = z
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2, -self.rect.height * 0.75)

        # 添加类型标识属性
        self.sprite_type = self.__class__.__name__.lower()

    def get_sprite_type(self):
        """返回精灵的具体类型"""
        return self.sprite_type

    def print_sprite_info(self):
        """打印精灵类型信息"""
        print(f"This is a {self.sprite_type}")
        # if self.sprite_type == 'apple':
        #     print(f"This is a {self.sprite_type}")


class Water(Generic):
    def __init__(self, pos, frames, groups):
        # animation setup
        self.frames = frames
        self.frame_index = 0

        # sprite setup
        super().__init__(
            pos=pos,
            surf=self.frames[self.frame_index],
            groups=groups,
            z=LAYERS['water']
        )
        self.sprite_type = 'water'

    def animate(self, dt):
        self.frame_index += 5 * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def update(self, dt):
        self.animate(dt)


class WildFlower(Generic):
    def __init__(self, pos, surf, groups):
        super().__init__(pos, surf, groups)
        self.hitbox = self.rect.copy().inflate(-20, -self.rect.height * 0.9)
        self.sprite_type = 'grass'


class Tree(Generic):
    def __init__(self, pos, surf, groups, name):
        super().__init__(pos, surf, groups)

        # tree属性
        self.health = 5
        self.alive = True
        stump_path = f'assets/graphics/stumps/{"small" if name == "Small" else "large"}.png'
        self.stump_surf = pygame.image.load(stump_path).convert_alpha()  # 树桩
        self.invul_timer = Timer(200)  # invulnerability timer 无敌时间

        # apples
        self.apple_surf = pygame.image.load('assets/graphics/fruit/apple.png').convert_alpha()
        self.apple_pos = APPLE_POS[name]
        self.apple_sprites = pygame.sprite.Group()
        self.create_apple()

        self.sprite_type = f'tree_{name}'
        print(f"Tree created with {len(self.apple_sprites)} apples")  # 调试信息

    def damage(self):
        # 树被攻击
        self.health -= 1

        # 掉落苹果
        if len(self.apple_sprites.sprites()) > 0:
            random_apple = choice(self.apple_sprites.sprites())
            print(f'remove apple at {random_apple.rect.center}')
            random_apple.kill()

    def create_apple(self):
        from level import CameraGroup
        all_sprites = None
        for group in self.groups():
            # 检查组是否是CameraGroup的实例（对应level.py中的all_sprites）
            if isinstance(group, CameraGroup):
                all_sprites = group
                break  # 找到后退出循环

        for pos in self.apple_pos:
            if randint(0, 9) < 2:  # 每个苹果有五分之一的概率出现
                x = pos[0] + self.rect.left

                y = pos[1] + self.rect.top
                # 创建苹果, 添加进apple_sprites组中
                apple = Generic(pos=(x, y),
                                surf=self.apple_surf,
                                groups=[self.apple_sprites, all_sprites],
                                z=LAYERS['fruit']
                                )
                apple.sprite_type = 'apple'
                # print(f'create apple at {x, y}')
