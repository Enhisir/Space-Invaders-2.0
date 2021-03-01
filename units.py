import pygame
from globals import load_image


class AnimatedExplosion(pygame.sprite.Sprite):
    VELOCITY = 400
    FPS = 120

    def __init__(self, x: int, y: int, screen: pygame.surface.Surface, *groups):
        super().__init__(*groups)
        columns = 4
        rows = 3
        self.last_update = pygame.time.get_ticks()
        self.cur_frame = 1
        self.last_update = 0
        self.frames = []
        self.sheet = load_image(name="explosion.jpg", screen=screen, colorkey=-1)
        self.rect = pygame.Rect(0, 0, self.sheet.get_width() // columns, self.sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(self.sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def update(self, time: int):
        now = pygame.time.get_ticks()
        self.rect = self.rect.move(0, round(AnimatedExplosion.VELOCITY * time / 1000))
        if now - self.last_update > AnimatedExplosion.FPS:
            self.last_update = now
            if self.cur_frame <= len(self.frames):
                self.cur_frame += 1
            self.image = self.frames[self.cur_frame - 1]
            if self.cur_frame == len(self.frames):
                self.kill()


class Character(pygame.sprite.Sprite):
    VELOCITY: int = None
    POWER: int = None

    def __init__(self, x: int, y: int, screen: pygame.surface.Surface, *group):
        super().__init__(*group)
        self.screen = screen
        self.image = self.get_image(screen)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x, self.rect.y = x, y
        self.hp = 0

    def get_image(self, screen: pygame.surface.Surface) -> pygame.surface.Surface:
        return self.image

    def get_power(self) -> int:
        return self.POWER

    def get_velocity(self) -> int:
        return self.VELOCITY

    def get_health(self) -> int:
        return self.hp

    def hurt(self, other):
        if self.hp > 0:
            self.hp -= other.get_power()


class Player(Character):
    VELOCITY = 600
    POWER = 1

    def __init__(self, x: int, y: int, screen: pygame.surface.Surface, *group):
        super().__init__(x, y, screen, *group)
        self.hp = 3

    def heal(self, hp):
        if self.hp < 3:
            self.hp += hp

    def get_image(self, screen: pygame.surface.Surface) -> pygame.surface.Surface:
        return load_image("player.png", screen)

    def update(self, time: int) -> None:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.rect = self.rect.move(-round(Player.VELOCITY * time / 1000), 0)
        elif keys[pygame.K_d]:
            self.rect = self.rect.move(round(Player.VELOCITY * time / 1000), 0)

        if self.rect.x < 10:
            self.rect.x = 10
        elif self.rect.x + self.rect.w >= self.screen.get_width() - 10:
            self.rect.x = self.screen.get_width() - 10 - self.rect.w


class BaseEnemy(Character):
    VELOCITY = 400
    POWER = 1

    def update(self, time: int) -> None:
        self.rect = self.rect.move(0, round(BaseEnemy.VELOCITY * time / 1000))


class WeakEnemy(BaseEnemy):
    def __init__(self, x: int, y: int, screen: pygame.surface.Surface, *group):
        super(WeakEnemy, self).__init__(x, y, screen, *group)
        self.hp = 1

    def get_image(self, screen: pygame.surface.Surface) -> pygame.surface.Surface:
        return load_image("enemy1.png", screen)


class AltWeakEnemy(BaseEnemy):
    def __init__(self, x: int, y: int, screen: pygame.surface.Surface, *group):
        super(AltWeakEnemy, self).__init__(x, y, screen, *group)
        self.hp = 1

    def get_image(self, screen: pygame.surface.Surface) -> pygame.surface.Surface:
        return load_image("enemy2.png", screen)


class StrongEnemy(BaseEnemy):
    POWER = 2

    def __init__(self, x: int, y: int, screen: pygame.surface.Surface, *group):
        super(StrongEnemy, self).__init__(x, y, screen, *group)
        self.hp = 2

    def get_image(self, screen: pygame.surface.Surface) -> pygame.surface.Surface:
        return load_image("enemy3.png", screen)


class Bullet(Character):
    def __init__(self, x: int, y: int,
                 owner: Character, owner_group: pygame.sprite.Group,
                 screen: pygame.surface.Surface, *group):
        super().__init__(x, y, screen, *group)
        self.owner = owner
        self.owner_group = owner_group
        if isinstance(self.owner, BaseEnemy):
            self.image = pygame.transform.rotate(self.image, 90)
        elif isinstance(self.owner, Player):
            self.image = pygame.transform.rotate(self.image, -90)
        self.rect = self.image.get_rect()
        self.rect.x = x - self.rect.w / 2
        self.rect.y = y

    def get_owner(self) -> Character:
        return self.owner

    def get_velocity(self) -> int:
        if isinstance(self.owner, BaseEnemy):
            return 1500
        elif isinstance(self.owner, Player):
            return -1500

    def get_power(self) -> int:
        return self.owner.POWER

    def get_image(self, screen: pygame.surface.Surface) -> pygame.surface.Surface:
        return load_image("bullet.png", screen)

    def update(self, time: int) -> None:
        self.rect = self.rect.move(0, round(self.get_velocity() * time / 1000))


class MedKit(Character):
    VELOCITY = 400

    def __init__(self, x: int, y: int, screen: pygame.surface.Surface, *groups):
        super().__init__(x, y, screen, *groups)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def get_image(self, screen: pygame.surface.Surface) -> pygame.surface.Surface:
        return pygame.transform.scale(load_image("medkit.png", screen), (50, 50))

    def update(self, time: int) -> None:
        self.rect = self.rect.move(0, round(MedKit.VELOCITY * time / 1000))
