import pygame as pg
from random import choice, randrange
from time import sleep

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
            pg.image.load(f"assets\dino\dino_{i}.png").convert_alpha()
            for i in range(3, 5)
        ]
        self.duck = [
            pg.image.load(f"assets\dino\dino_{i}.png").convert_alpha()
            for i in range(7, 9)
        ]
        self.rect = self.image.get_rect(
            center=(
                WIDTH / 7,
                ground_level - self.image.get_height() / 2,
            )
        )

        # # To make hitbox slightly smaller than the image itself
        # self.rect.w *= 0.9
        # self.rect.h *= 0.9

        self.gravity = 0
        self.animation_index = 0
        self.state = "walk"

    def get_input(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_SPACE] and self.rect.bottom >= ground_level:
            self.gravity = -20
        if keys[pg.K_DOWN]:
            self.state = "duck"
        else:
            self.state = "walk"

    def apply_gravity(self):
        self.gravity += 1
        self.rect.y += self.gravity
        if self.rect.bottom > ground_level:
            self.rect.bottom = ground_level

    def collide_check(self, sprite_group):
        return pg.sprite.spritecollide(dino, sprite_group, False)

    def animate_walk(self):
        if self.animation_index >= len(self.walk):
            self.animation_index = 0
        self.image = self.walk[int(self.animation_index)]
        self.rect = self.image.get_rect(center=self.rect.center)

    def animate_duck(self):
        if self.animation_index >= len(self.duck):
            self.animation_index = 0
        self.image = self.duck[int(self.animation_index)]
        self.rect = self.image.get_rect(center=self.rect.center)

    def animate(self):
        self.animation_index += 0.05
        if self.state == "walk":
            self.animate_walk()
        elif self.state == "duck":
            self.animate_duck()

    def update(self):
        self.animate()
        self.get_input()
        self.apply_gravity()
        # pg.draw.rect(screen, "Green", self.rect)

    def reset(self):
        self.__init__()


obstacle_imgs = (
    [pg.image.load(f"assets\cacti\cacti_small_{i}.png") for i in range(1, 4)]
    + [pg.image.load(f"assets\cacti\cacti_small_{i}.png") for i in range(1, 3)]
    + [pg.image.load(f"assets\cacti\cacti_small_{i}.png") for i in range(1, 2)]
)


class Obstacle(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = choice(obstacle_imgs)
        self.rect = self.image.get_rect(
            center=(WIDTH, ground_level - self.image.get_height() / 2)
        )

    def move(self):
        self.rect.x -= 8
        if self.rect.right < 0:
            self.kill()
            del self

    def update(self):
        self.move()


class Cloud(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pg.image.load("assets\cloud.png").convert_alpha()
        self.rect = self.image.get_rect(
            center=(WIDTH * 1.5, randrange(50, HEIGHT // 2 - 50))
        )

    def move(self):
        self.rect.x -= 3
        if self.rect.right < 0:
            self.kill()
            del self

    def update(self):
        self.move()


def handleEvents(scene):
    for event in pg.event.get():
        if event.type == pg.QUIT:
            raise SystemExit
        if (scene == "main") and (event.type == obstacle_event):
            obstacles.add(Obstacle())
        if (scene == "main") and (event.type == cloud_event):
            clouds.add(Cloud())


# Player
player_group = pg.sprite.GroupSingle()
dino = Player()
player_group.add(dino)

# Obstacles
obstacle_event = pg.USEREVENT + 1
pg.time.set_timer(obstacle_event, 1300)
obstacles = pg.sprite.Group()
obstacles.add(Obstacle())

# Clouds
cloud_event = pg.USEREVENT + 2
pg.time.set_timer(cloud_event, 2000)
clouds = pg.sprite.Group()
clouds.add(Cloud())

temp = pg.font.SysFont(None, 50)
temp_text = temp.render("Game Over", True, "White")

scene = "main"
while True:

    handleEvents(scene)

    if scene == "main":

        screen.fill("Black")
        screen.blit(ground, ground_pos)

        player_group.update()
        obstacles.update()
        clouds.update()

        clouds.draw(screen)
        obstacles.draw(screen)
        player_group.draw(screen)

        if dino.collide_check(obstacles):
            scene = "game_over"

    elif scene == "game_over":
        screen.blit(temp_text, (0, 0))
        dino.reset()
        obstacles.empty()
        clouds.empty()
        scene = "main"

    clock.tick(60)
    pg.display.flip()
