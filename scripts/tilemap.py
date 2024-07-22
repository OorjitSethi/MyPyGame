import json
import pygame
import noise
import random

# Mapping of autotile configurations to their corresponding tile index
AUTOTILE_MAP = {
    tuple(sorted([(1, 0), (0, 1)])): 0,
    tuple(sorted([(1, 0), (0, 1), (-1, 0)])): 1,
    tuple(sorted([(-1, 0), (0, 1)])): 2, 
    tuple(sorted([(-1, 0), (0, -1), (0, 1)])): 3,
    tuple(sorted([(-1, 0), (0, -1)])): 4,
    tuple(sorted([(-1, 0), (0, -1), (1, 0)])): 5,
    tuple(sorted([(1, 0), (0, -1)])): 6,
    tuple(sorted([(1, 0), (0, -1), (0, 1)])): 7,
    tuple(sorted([(1, 0), (-1, 0), (0, 1), (0, -1)])): 8,
}

# Offsets to check neighboring tiles
NEIGHBOR_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]
# Types of tiles that have physical properties
PHYSICS_TILES = {'grass', 'stone'}
# Types of tiles that can be autotiled
AUTOTILE_TYPES = {'grass', 'stone'}

# Size of each chunk in tiles
CHUNK_SIZE = 8

class TileMap:
    def __init__(self, game, tile_size=16, seed=None):
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {}
        self.offgrid_tiles = []
        self.seed = seed if seed is not None else random.randint(0, 1000000)

        # Generate initial chunks around the starting area
        for x in range(-3, 4):
            for y in range(-3, 4):
                chunk_data = self.generate_chunk(x, y)
                for tile in chunk_data:
                    self.tilemap[str(tile[0][0]) + ';' + str(tile[0][1])] = {
                        'type': tile[1],
                        'variant': 1,
                        'pos': tile[0]
                    }
        self.create_stone_wall(-4)

    def generate_chunk(self, x, y):
        chunk_data = []
        for y_pos in range(CHUNK_SIZE):
            for x_pos in range(CHUNK_SIZE):
                target_x = x * CHUNK_SIZE + x_pos
                target_y = y * CHUNK_SIZE + y_pos
                tile_type = 'empty'
                # Generate height using Perlin noise
                base_height = noise.pnoise1(target_x * 0.1, octaves=4, base=self.seed)
                detail_height = noise.pnoise1(target_x * 0.05, octaves=2, base=self.seed + 1)
                secondary_height = noise.pnoise1(target_x * 0.02, octaves=6, base=self.seed + 2)
                height = int((base_height + 0.5 * detail_height + 0.3 * secondary_height) * 15)
                if target_y > 8 - height:
                    tile_type = 'stone'
                elif target_y == 8 - height:
                    tile_type = 'grass'
                if height > 4 and target_y == 8 - height + 1 and random.random() > 0.7:
                    tile_type = 'grass'
                if tile_type != 'empty':
                    chunk_data.append([[target_x, target_y], tile_type])
        return chunk_data

    def create_stone_wall(self, x_position):
        # Create a vertical stone wall at the specified x position
        for y in range(-CHUNK_SIZE * 10, CHUNK_SIZE * 10):
            for x in range(x_position, x_position + 1):
                self.tilemap[str(x) + ';' + str(y)] = {
                    'type': 'stone',
                    'variant': 1,
                    'pos': (x, y)
                }

    def generate_around_player(self, player_pos):
        # Determine the chunk the player is currently in
        player_chunk_x = player_pos[0] // (self.tile_size * CHUNK_SIZE)
        player_chunk_y = player_pos[1] // (self.tile_size * CHUNK_SIZE)
        chunks_to_generate = []

        # Identify chunks around the player that need to be generated
        for x in range(player_chunk_x - 2, player_chunk_x + 3):
            for y in range(player_chunk_y - 2, player_chunk_y + 3):
                loc = str(x * CHUNK_SIZE) + ';' + str(y * CHUNK_SIZE)
                if loc not in self.tilemap:
                    chunks_to_generate.append((x, y))

        # Generate the identified chunks
        for chunk in chunks_to_generate:
            chunk_data = self.generate_chunk(chunk[0], chunk[1])
            for tile in chunk_data:
                self.tilemap[str(tile[0][0]) + ';' + str(tile[0][1])] = {
                    'type': tile[1],
                    'variant': 1,
                    'pos': tile[0]
                }

    def tiles_around(self, pos):
        # Get tiles around a given position
        tiles = []
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        for offset in NEIGHBOR_OFFSETS:
            check_loc = str(tile_loc[0] + offset[0]) + ';' + str(tile_loc[1] + offset[1])
            if check_loc in self.tilemap:
                tiles.append(self.tilemap[check_loc])
        return tiles

    def solid_check(self, pos):
        # Check if a tile at a given position is solid
        tile_loc = str(int(pos[0] // self.tile_size)) + ';' + str(int(pos[1] // self.tile_size))
        if tile_loc in self.tilemap:
            if self.tilemap[tile_loc]['type'] in PHYSICS_TILES:
                return self.tilemap[tile_loc]

    def physics_rects_around(self, pos):
        # Get the physical rectangles of tiles around a given position
        rects = []
        for tile in self.tiles_around(pos):
            if tile['type'] in PHYSICS_TILES:
                rects.append(pygame.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size))
        return rects

    def render(self, surf, offset=(0, 0)):
        # Generate tiles around the player before rendering
        self.generate_around_player((offset[0] + surf.get_width() // 2, offset[1] + surf.get_height() // 2))
        # Render offgrid tiles
        for tile in self.offgrid_tiles:
            surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))
        # Render tiles in the tilemap
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))
