import sys
import pygame
import random
import math
from scripts.entities import PhysicsEntity, Player, Enemy
from scripts.utility import LoadImage, LoadImages, Animations
from scripts.tilemap import TileMap
from scripts.clouds import Clouds
from scripts.particles import ParticleSystem, Particle
from scripts.spark import Spark

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Infinite Noise Game")
        self.screen = pygame.display.set_mode((800, 600))
        self.display = pygame.Surface((320, 240))
        self.clock = pygame.time.Clock()
        self.movement = [False, False]
        self.assets = {
            'decor': LoadImages('tiles/decor'),
            'grass': LoadImages('tiles/grass'),
            'large_decor': LoadImages('tiles/large_decor'),
            'stone': LoadImages('tiles/stone'),
            'player': LoadImage('entities/player.png'),
            'background': LoadImage('background.png'),
            'clouds': LoadImages('clouds'),
            'enemy/idle': Animations(LoadImages('entities/enemy/idle'), img_dur=6),
            'enemy/run': Animations(LoadImages('entities/enemy/run'), img_dur=4),
            'player/idle': Animations(LoadImages('entities/player/idle'), img_dur=6),
            'player/run': Animations(LoadImages('entities/player/run'), img_dur=4),
            'player/jump': Animations(LoadImages('entities/player/jump')),
            'player/slide': Animations(LoadImages('entities/player/slide')),
            'player/wall_slide': Animations(LoadImages('entities/player/wall_slide')),
            'particle/particle': Animations(LoadImages('particles/particle'), img_dur=6, loop=False),
            'gun': LoadImage('gun.png'),
            'projectile': LoadImage('projectile.png')
        }

        self.clouds = Clouds(self.assets['clouds'], count=16)
        self.player = Player(self, (50, 50), (8, 15))
        seed = random.randint(0, 1000000)
        print(f"Seed: {seed}")  # Print the seed for reference
        self.tilemap = TileMap(self, tile_size=16, seed=seed)
        self.scroll = [0, 0]
        self.enemies = []
        self.particles = ParticleSystem(self, 'particle')
        self.projectiles = []  # Initialize the projectiles list
        self.sparks = []
        
        self.score = 0
        self.font = pygame.font.Font(None, 36)
        self.next_enemy_spawn_score = 20  # Score threshold for next enemy spawn
        self.last_player_x = self.player.pos[0]
        self.distance_score = 0
        self.enemy_score = 0

        self.generate_initial_enemies()
        self.confirm_quit = False
        self.game_over = False

    def generate_initial_enemies(self):
        # Generate initial enemies at random positions
        for i in range(5):  # Adjust number of enemies as needed
            x = random.randint(50, 500)
            y = random.randint(50, 300)
            self.enemies.append(Enemy(self, (x, y), (8, 15)))

    def generate_enemies(self):
        # Generate a random number of enemies (2-6) to the right of the player
        num_enemies = random.randint(2, 6)
        for _ in range(num_enemies):
            x = self.player.pos[0] + random.randint(200, 400)
            y = random.randint(50, 300)
            self.enemies.append(Enemy(self, (x, y), (8, 15)))

    def update_score(self):
        # Increment score based on distance traveled
        distance_traveled = self.player.pos[0] - self.last_player_x
        if distance_traveled > 0:
            self.distance_score += distance_traveled / 20
            self.score = self.distance_score + self.enemy_score
        self.last_player_x = self.player.pos[0]

    def render_score(self):
        # Render the score on the screen, divided by 20 to make it smaller
        score_text = self.font.render(f"Score: {int(self.score)}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(self.screen.get_width() // 2, 20))
        self.screen.blit(score_text, score_rect.topleft)

    def render_health(self):
        # Render the health on the screen
        health_text = self.font.render(f"Health: {self.player.health}", True, (255, 255, 255))
        self.screen.blit(health_text, (10, 10))

    def game_over_screen(self):
        self.screen.fill((0, 0, 0))
        game_over_text = self.font.render("Sorry, you lost. Press R to restart or Command + Q to exit", True, (255, 0, 0))
        self.screen.blit(game_over_text, (self.screen.get_width() // 2 - game_over_text.get_width() // 2, self.screen.get_height() // 2))
        pygame.display.flip()
        
        while True:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.__init__()  # Restart the game
                    self.run()
                elif event.key == pygame.K_q and pygame.key.get_mods() & pygame.KMOD_META:
                    pygame.quit()
                    sys.exit()

    def run(self):
        running = True

        while running:
            self.display.blit(self.assets['background'], (0, 0))
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 15
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 15
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            self.clouds.update()
            self.clouds.render(self.display, offset=render_scroll)
            movement = [0, 0]

            if self.movement[0]:
                movement[0] = -2
            if self.movement[1]:
                movement[0] = 2

            self.tilemap.render(self.display, offset=render_scroll)
            self.player.update(self.tilemap, movement)
            self.player.render(self.display, offset=render_scroll)

            for enemy in self.enemies:
                enemy.update(self.tilemap)
                enemy.render(self.display, offset=render_scroll)

            for projectile in self.projectiles.copy():
                projectile[0][0] += projectile[1]
                projectile[2] += 1
                img = self.assets['projectile']
                self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0], projectile[0][1] - img.get_height() / 2 - render_scroll[1]))
                if self.tilemap.solid_check(projectile[0]):
                    self.projectiles.remove(projectile)
                    for i in range(4):
                        self.sparks.append(Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 + random.random()))
                elif projectile[2] > 360:
                    self.projectiles.remove(projectile)
                elif abs(self.player.dashing) < 50:
                    if self.player.rect().collidepoint(projectile[0]):
                        self.projectiles.remove(projectile)
                        self.player.health -= 1  # Adjust player health handling as needed
                        if self.player.health <= 0:
                            self.player.alive = False  # Handle player death
                            self.game_over = True
                            running = False
                        self.particles.add_particle(self.player.rect().center)

            self.particles.update()
            self.particles.render(self.display, offset=render_scroll)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_SPACE:
                        self.player.jump()
                    if event.key == pygame.K_c:
                        self.player.dash()
                    if event.key == pygame.K_ESCAPE:
                        if not self.confirm_quit:
                            self.confirm_quit = True
                        else:
                            running = False
                    if event.key == pygame.K_q and pygame.key.get_mods() & pygame.KMOD_META:
                        pygame.quit()
                        sys.exit()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False

            self.update_score()  # Update the score based on distance traveled
            if self.score >= self.next_enemy_spawn_score:
                self.generate_enemies()
                self.next_enemy_spawn_score += 20  # Set the next threshold

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            self.render_score()  # Render the score on the screen
            self.render_health()  # Render the health on the screen

            # Display exit instruction
            exit_text = self.font.render("Press ESC to exit", True, (255, 255, 255))
            self.screen.blit(exit_text, (10, self.screen.get_height() - 30))

            # Handle quit confirmation
            if self.confirm_quit:
                confirm_text = self.font.render("Are you sure you want to quit? Press Cmd+Q for yes, any other key for no.", True, (255, 0, 0))
                self.screen.blit(confirm_text, (self.screen.get_width() // 2 - confirm_text.get_width() // 2, self.screen.get_height() // 2))
                pygame.display.flip()
                event = pygame.event.wait()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    else:
                        self.confirm_quit = False

            pygame.display.update()
            self.clock.tick(60)

        if self.game_over:
            self.game_over_screen()

Game().run()
