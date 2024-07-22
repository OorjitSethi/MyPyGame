import pygame
import random
from .utility import LoadImages, Animations
from .entities import PhysicsEntity

class Enemy(PhysicsEntity):
    def __init__(self, game, pos):
        super().__init__(game, 'enemy', pos, (16, 16))
        self.velocity = [0, 0]
        self.flip = False
        self.action = 'run'
        self.frame = 0
        self.animation_database = {
            'idle': Animations(LoadImages('entities/enemy/idle'), img_dur=6),
            'run': Animations(LoadImages('entities/enemy/run'), img_dur=4),
            # 'jump': Animations(LoadImages('entities/enemy/jump'), img_dur=6)
        }
        self.animation = self.animation_database['run'].copy()
        self.patrol_direction = 1
        self.on_ground = False

        # Ensure the enemy spawns on the ground
        self.spawn_on_ground()

    def spawn_on_ground(self):
        for y_offset in range(0, 240, 16):  # Start from 0 and check every 16 pixels downwards
            self.rect.y = self.pos[1] + y_offset
            if self.check_ground(self.game.tilemap):
                self.pos[1] = self.rect.y - self.size[1]  # Position enemy on the ground
                self.on_ground = True
                break

    def check_ground(self, tilemap):
        rect = pygame.Rect(self.pos[0], self.pos[1] + self.size[1], self.size[0], 1)
        return any(rect.colliderect(pygame.Rect(tile['pos'][0] * tilemap.tileSize, tile['pos'][1] * tilemap.tileSize, tilemap.tileSize, tilemap.tileSize)) and tile['type'] == 'grass' for tile in tilemap.tiles_around(self.pos))

    def update(self, tilemap):
        self.patrol(tilemap)
        self.apply_gravity()
        super().update(tilemap)
        self.animation.update()

    def patrol(self, tilemap):
        self.set_action('run')
        if random.random() < 0.01:  # Randomly change direction
            self.patrol_direction *= -1
        self.flip = self.patrol_direction < 0
        self.velocity[0] = self.patrol_direction
        self.pos[0] += self.velocity[0]

        if not self.check_ground(tilemap):
            self.pos[0] -= self.velocity[0]  # Step back if no ground

    def apply_gravity(self):
        if not self.on_ground:
            self.velocity[1] += 0.2  # Gravity
            self.pos[1] += self.velocity[1]
            self.rect.y = self.pos[1]
            if self.check_ground(self.game.tilemap):
                self.on_ground = True
                self.velocity[1] = 0
                self.pos[1] = self.rect.y - self.size[1]
            else:
                self.on_ground = False
        else:
            self.velocity[1] = 0  # Ensure velocity is reset when on ground

    def set_action(self, action):
        if self.action != action:
            self.action = action
            self.frame = 0
            try:
                self.animation = self.game.assets[self.type + '/' + action].copy()
            except KeyError:
                self.animation = self.game.assets[self.type + '/idle'].copy()

    def render(self, surf, offset=(0, 0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False),
                  (self.pos[0] - offset[0], self.pos[1] - offset[1]))
