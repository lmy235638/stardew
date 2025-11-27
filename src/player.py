import pygame
from settings import *
from timer import Timer
from support import import_folder


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites):
        super().__init__(groups)

        self.import_assets()
        self.status = 'down_idle'
        self.frame_index = 0

        # 通用属性
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center=pos)
        self.z = LAYERS['main']

        # 移动属性
        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 200

        # 碰撞
        self.collision_sprites = collision_sprites
        self.hitbox = self.rect.copy().inflate((-126, -70))

        # 定时器
        self.timers = {
            'tool_use': Timer(duration=350, func=self.use_tool),
            'tool_switch': Timer(duration=200),
            'seed_use': Timer(duration=350, func=self.use_seed),
            'seed_switch': Timer(duration=200),
        }

        # 工具
        self.tools = ['axe', 'hoe', 'water']
        self.tool_index = 0
        self.selected_tool = self.tools[self.tool_index]

        # 种子
        self.seeds = ['corn', 'tomato']
        self.seed_index = 0
        self.selected_seed = self.seeds[self.seed_index]

    def import_assets(self):
        self.animations = {'up': [], 'down': [], 'left': [], 'right': [],
                           'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': [],
                           'right_hoe': [], 'left_hoe': [], 'up_hoe': [], 'down_hoe': [],
                           'right_axe': [], 'left_axe': [], 'up_axe': [], 'down_axe': [],
                           'right_water': [], 'left_water': [], 'up_water': [], 'down_water': []}

        for animation in self.animations.keys():
            full_path = 'assets/graphics/character/' + animation
            self.animations[animation] = import_folder(full_path)

    def animate(self, dt):
        self.frame_index += 4 * dt
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0

        self.image = self.animations[self.status][int(self.frame_index)]

    def input(self):
        keys = pygame.key.get_pressed()

        if not self.timers['tool_use'].active:
            # 方向
            if keys[pygame.K_UP]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pygame.K_DOWN]:
                self.direction.y = 1
                self.status = 'down'
            else:
                self.direction.y = 0

            if keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.status = 'left'
            elif keys[pygame.K_RIGHT]:
                self.direction.x = 1
                self.status = 'right'
            else:
                self.direction.x = 0

            # 工具
            if keys[pygame.K_SPACE]:
                self.timers['tool_use'].activate()
                # 工具使用时, 会锁定上一状态的方向, 因此需要清空之前状态
                self.direction = pygame.math.Vector2()
                self.frame_index = 0

            if keys[pygame.K_q] and not self.timers['tool_switch'].active:
                self.timers['tool_switch'].activate()
                self.tool_index += 1
                self.tool_index = self.tool_index % len(self.tools)
                self.selected_tool = self.tools[self.tool_index]

            # 使用种子
            if keys[pygame.K_LCTRL]:
                self.timers['seed_use'].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0

            # 切换种子
            if keys[pygame.K_e] and not self.timers['seed_switch'].active:
                self.timers['seed_switch'].activate()
                self.seed_index += 1
                self.seed_index = self.seed_index % len(self.seeds)
                self.selected_seed = self.seeds[self.seed_index]

    def use_tool(self):
        # print(self.selected_tool)
        pass

    def use_seed(self):
        # print(self.selected_seed)
        pass

    def get_status(self):
        # 检测是否为空闲状态
        if self.direction.y == 0 and self.direction.x == 0:
            self.status = self.status.split('_')[0] + '_idle'

        # 检测是否使用工具
        if self.timers['tool_use'].active:
            # 当前状态 + 现在所选用的工具
            self.status = self.status.split('_')[0] + '_' + self.selected_tool

    def update_timers(self):
        for name, timer in self.timers.items():
            timer.update()

    def collision(self, direction):
        for sprite in self.collision_sprites.sprites():  # 遍历所有碰撞对象
            if hasattr(sprite, 'hitbox'):  # 确保对方有碰撞箱
                if sprite.hitbox.colliderect(self.hitbox):  # 碰撞箱重叠检测
                    if direction == 'horizontal':
                        if self.direction.x > 0:  # 向右移动时碰撞
                            self.hitbox.right = sprite.hitbox.left  # 玩家右边界 = 障碍物左边界（阻止穿透）
                        if self.direction.x < 0:  # 向左移动时碰撞
                            self.hitbox.left = sprite.hitbox.right  # 玩家左边界 = 障碍物右边界
                        # 同步实际位置（修正后）
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx

                    if direction == 'vertical':
                        if self.direction.y > 0:  # moving down
                            self.hitbox.bottom = sprite.hitbox.top
                        if self.direction.y < 0:  # moving up
                            self.hitbox.top = sprite.hitbox.bottom
                        self.rect.centery = self.hitbox.centery
                        self.pos.y = self.hitbox.centery

    def move(self, dt):
        # 向量归一化
        if self.direction.magnitude() > 0:  # 模大于1
            self.direction = self.direction.normalize()

        # 水平移动更新
        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')

        # 垂直移动更新
        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')

    def update(self, dt):
        self.input()
        self.get_status()
        self.update_timers()

        self.move(dt)
        self.animate(dt)
