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

        self.jump_sound = pg.mixer.Sound("assets\sounds\jump.wav")
        self.duck_sound = pg.mixer.Sound("assets\sounds\duck.wav")

        # # To make hitbox slightly smaller than the image itself
        # self.rect.w *= 0.9
        # self.rect.h *= 0.9

        self.gravity = 0
        self.animation_index = 0
        self.state = "walk"
        self.done = False

    def get_input(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_SPACE] and self.rect.bottom >= ground_level:
            self.jump()
        if keys[pg.K_DOWN]:
            self.state = "duck"
        else:
            self.state = "walk"

    def apply_gravity(self):
        self.gravity += 1
        self.rect.y += self.gravity
        if self.rect.bottom > ground_level:
            self.rect.bottom = ground_level

    def jump(self):
        self.gravity = -20
        self.jump_sound.play()

    def collide_obstacles(self):
        return pg.sprite.spritecollide(dino, obstacles, False)

    def collide_ptera(self):
        collided_pteras = pg.sprite.spritecollide(self, pteras, False)
        if collided_pteras:
            if close_to(self.rect.bottom, collided_pteras[0].rect.top):
                self.jump()
            else:
                return True

    def animate_walk(self):
        if self.animation_index >= len(self.walk):
            self.animation_index = 0
        self.image = self.walk[int(self.animation_index)]
        if not self.done:
            self.rect = self.image.get_rect(center=self.rect.center)
            self.done = True

    def animate_duck(self):
        if self.animation_index >= len(self.duck):
            self.animation_index = 0
        self.image = self.duck[int(self.animation_index)]
        if self.done:
            self.rect = self.image.get_rect(center=self.rect.center)
            self.duck_sound.play()
            self.done = False

    def animate(self):
        self.animation_index += 0.05
        if self.state == "walk":
            self.animate_walk()
        elif self.state == "duck":
            self.animate_duck()

    def update(self):
        # pg.draw.rect(screen, "pink", self.rect)
        self.animate()
        self.get_input()
        self.apply_gravity()

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
            center=(WIDTH, ground_level - self.image.get_height() // 2+2)
        )

        # To make the hitbox slightly smaller
        self.rect.w *= 0.8
        self.rect.h *= 0.8

    def move(self):
        self.rect.x -= 8
        if self.rect.right < 0:
            self.kill()
            del self

    def update(self):
        # pg.draw.rect(screen, "green", self.rect)
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


class Ptera(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pg.image.load("assets\ptera\ptera_1.png")
        self.fly = [pg.image.load(f"assets\ptera\ptera_{i}.png") for i in range(1, 3)]
        self.rect = self.image.get_rect(midleft=(WIDTH, HEIGHT // 1.5))
        # To make the hitbox slightly smaller
        self.rect.w *= 0.8
        self.rect.h *= 0.8
        self.animation_index = 0
        self.exist_sound = pg.mixer.Sound("assets\sounds\ptera.wav")
        self.exist_sound.play()

    def animate(self):
        self.animation_index += 0.05
        if self.animation_index >= len(self.fly):
            self.animation_index = 0
        self.image = self.fly[int(self.animation_index)]

    def move(self):
        self.rect.x -= 10
        if self.rect.right < 0:
            self.kill()
            del self

    def update(self):
        # pg.draw.rect(screen, "red", self.rect)
        self.animate()
        self.move()


class Button(pg.sprite.Sprite):
    def __init__(
        self,
        center_pos=(WIDTH // 2, HEIGHT // 2),
    ) -> None:
        super().__init__()
        self.image = pg.image.load("assets\\restart_button.png").convert_alpha()
        self.rect = self.image.get_rect(center=center_pos)
        self.click_sound = pg.mixer.Sound("assets\sounds\click.wav")

    def pressed(self):
        if self.rect.collidepoint(pg.mouse.get_pos()) and any(pg.mouse.get_pressed()):
            self.click_sound.play()
            return True
        return False


def handleEvents(scene):
    for event in pg.event.get():
        if event.type == pg.QUIT:
            raise SystemExit
        if scene == "main":
            if event.type == obstacle_event:
                obstacles.add(Obstacle())
            if event.type == cloud_event:
                clouds.add(Cloud())
            if event.type == ptera_event:
                pteras.add(Ptera())


def close_to(a, b):
    return abs(a - b) < 8


def update_score():
    global score
    score += 1/60
    
def show_score(score):
    score=str(int(score))
    score_surf = font.render(score,True,"white")
    screen.blit(score_surf,(WIDTH-score_surf.get_width()-10,10))


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

# Pteras
ptera_event = pg.USEREVENT + 3
pg.time.set_timer(ptera_event, 4700)
pteras = pg.sprite.Group()

# Buttons
button_group = pg.sprite.Group()
button = Button()
button_group.add(button)

# Score
font = pg.font.Font("assets\\fonts\\regular.ttf",30)
score = 0

scene = "main"
while True:

    handleEvents(scene)

    if scene == "main":

        screen.fill("Black")
        screen.blit(ground, ground_pos)

        player_group.update()
        obstacles.update()
        clouds.update()
        pteras.update()
        update_score()

        clouds.draw(screen)
        obstacles.draw(screen)
        pteras.draw(screen)
        player_group.draw(screen)
        show_score(score)        
        

        if dino.collide_obstacles() or dino.collide_ptera():
            scene = "game_over"

    elif scene == "game_over":
        button_group.draw(screen)
        if button.pressed():
            dino.reset()
            obstacles.empty()
            clouds.empty()
            pteras.empty()
            score = 0
            scene = "main"

    clock.tick(60)
    pg.display.flip()
