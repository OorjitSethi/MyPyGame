import os
import pygame

BASE_IMAGE_PATH = "GameTut/data/images/"

def LoadImage(path):
    image = pygame.image.load(BASE_IMAGE_PATH + path).convert()
    image.set_colorkey((0, 0, 0))
    return image

def LoadImages(path):
    images = []
    for imageName in sorted(os.listdir(BASE_IMAGE_PATH + path)):
        images.append(LoadImage(path + '/' + imageName))
    return images

class Animations:
    def __init__(self, images, img_dur = 5, loop = True):
        self.images = images
        self.img_duration = img_dur
        self.loop = loop
        self.done = False
        self.frame = 0

    def copy(self):
        return Animations(self.images, self.img_duration, self.loop)
    
    def update(self):
        if self.loop:
            self.frame = (self.frame + 1) % (self.img_duration * len(self.images))
        else:
            self.frame = min(self.frame + 1, self.img_duration * len(self.images) - 1)
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.done = True

    def img(self):
        return self.images[int(self.frame / self.img_duration)]
    
