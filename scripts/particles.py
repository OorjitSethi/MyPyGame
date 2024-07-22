class Particle:
    def __init__(self, game, p_type, pos, velocity=[0, 0], frame=0):
        self.game = game
        self.type = p_type
        self.pos = list(pos)
        self.velocity = list(velocity)
        self.animation = self.game.assets['particle/' + p_type].copy()
        self.animation.frame = frame

    def update(self):
        kill = False
        if self.animation.done:
            kill = True

        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]

        self.animation.update()

        return kill

    def render(self, surf, offset=(0, 0)):
        img = self.animation.img()
        surf.blit(img, (self.pos[0] - offset[0] - img.get_width() // 2, self.pos[1] - offset[1] - img.get_height() // 2))

class ParticleSystem:
    def __init__(self, game, p_type):
        self.game = game
        self.p_type = p_type
        self.particles = []

    def add_particle(self, pos, p_type=None, velocity=[0, 0], frame=0):
        if p_type is None:
            p_type = self.p_type
        self.particles.append(Particle(self.game, p_type, pos, velocity=velocity, frame=frame))

    def update(self):
        for particle in self.particles.copy():
            if particle.update():
                self.particles.remove(particle)

    def render(self, surf, offset=(0, 0)):
        for particle in self.particles:
            particle.render(surf, offset=offset)
