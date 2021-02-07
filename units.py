import pygame
from globals import load_image


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

    def get_image(self, screen: pygame.surface.Surface) -> pygame.surface.Surface:
        return load_image("player.png", screen)

    def update(self, time: int) -> None:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.rect = self.rect.move(-Player.VELOCITY * time / 1000, 0)
        elif keys[pygame.K_d]:
            self.rect = self.rect.move(Player.VELOCITY * time / 1000, 0)

        if self.rect.x < 10:
            self.rect.x = 10
        elif self.rect.x + self.rect.w >= self.screen.get_width() - 10:
            self.rect.x = self.screen.get_width() - 10 - self.rect.w


class BaseEnemy(Character):
    VELOCITY = 400
    POWER = 1

    def update(self, time: int) -> None:
        self.rect = self.rect.move(0, BaseEnemy.VELOCITY * time / 1000)


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
        self.rect = self.rect.move(0, self.get_velocity() * time / 1000)
