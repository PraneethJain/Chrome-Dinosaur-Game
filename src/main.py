import pygame as pg
from random import randrange

pg.init()

WIDTH, HEIGHT = 800, 400
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Dinosaur Game")
icon = pg.image.load("assets\dino\dino_1.png").convert()
pg.display.set_icon(icon)
clock = pg.time.Clock()

ground = pg.image.load("assets\ground.png").convert()
ground_level = HEIGHT - ground.get_height()
ground_pos = (0, ground_level)


class Player(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pg.image.load("assets\dino\dino_1.png")
        self.walk = [
            pg.image.load(f"assets\dino\dino_{i}.png").convert_alpha() for i in range(1, 5)
        ]
        self.rect = self.image.get_rect(
            center=(
                WIDTH / 7,
                ground_level - self.image.get_height() / 2,
            )
        )
        self.gravity = 0
        self.animation_index = 0

    def get_input(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_SPACE] and self.rect.bottom >= ground_level:
            self.gravity = -15

    def apply_gravity(self):
        self.gravity += 1
        self.rect.y += self.gravity
        if self.rect.bottom > ground_level:
            self.rect.bottom = ground_level

    def animate(self):
        self.animation_index += 0.05
        if self.animation_index >= len(self.walk):
            self.animation_index = 0
        self.image = self.walk[int(self.animation_index)]

    def update(self):
        self.animate()
        self.get_input()
        self.apply_gravity()


dino = pg.sprite.GroupSingle()
dino.add(Player())

while True:

    screen.fill("Black")
    screen.blit(ground, ground_pos)

    dino.update()
    dino.draw(screen)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            raise SystemExit

    clock.tick(60)
    pg.display.flip()
