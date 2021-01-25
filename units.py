import pygame
from globals import load_image


class Character(pygame.sprite.Sprite):
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

    def get_health(self) -> int:
        return self.hp

    def hurt(self, other):
        if self.hp > 0:
            self.hp -= other.POWER


class Player(Character):
    VELOCITY = 500
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
    VELOCITY = 500
    POWER = 1

    def __init__(self, x: int, y: int, screen: pygame.surface.Surface, *group):
        super(BaseEnemy, self).__init__(x, y, screen, *group)
        self.hp = 3

    def update(self, time: int) -> None:
        self.rect = self.rect.move(0, BaseEnemy.VELOCITY * time / 1000)
        if self.rect.y >= self.screen.get_height() or self.hp == 0:
            self.kill()


class WeakEnemy(BaseEnemy):
    def get_image(self, screen: pygame.surface.Surface) -> pygame.surface.Surface:
        return load_image("enemy1.png", screen)


class AltWeakEnemy(BaseEnemy):
    def get_image(self, screen: pygame.surface.Surface) -> pygame.surface.Surface:
        return load_image("enemy2.png", screen)


class StrongEnemy(BaseEnemy):
    POWER = 2

    def get_image(self, screen: pygame.surface.Surface) -> pygame.surface.Surface:
        return load_image("enemy3.png", screen)


class Bullet(Character):
    def __init__(self, x: int, y: int, power: int, velocity: int, screen: pygame.surface.Surface, *group):
        super().__init__(x, y, screen, *group)
        self.all_sprites = group[0]
        self.hp = 1
        self.power = power
        self.velocity = velocity

    def get_image(self, screen: pygame.surface.Surface) -> pygame.surface.Surface:
        image = pygame.Surface((10, 20))
        image.fill(pygame.color.Color("yellow"))
        return image

    def update(self, time: int) -> None:
        self.rect = self.rect.move(0, self.velocity * time / 1000)
        if self.rect.y >= self.screen.get_height() or self.hp == 0:
            self.kill()

        # for item in self.all_sprites.sprites():
        #     if item is not self and pygame.sprite.collide_mask():
        #         pass
