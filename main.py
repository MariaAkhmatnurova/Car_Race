import pygame
import math
import random
from new import Field, Car, Rival
import base


WIDTH = 800
HEIGHT = 600
ESCAPE = (1234567890, 1234567890)


class Button:
    def __init__(self, surface, x, y):
        self.surface = surface
        self.rect = self.surface.get_rect(center = (x, y))
        self.is_pushed = False

    def push(self, pos):
        return self.rect.collidepoint(pos)

    def catch(self):
        self.is_pushed = True

    def release(self):
        self.is_pushed = False

    def draw(self, screen):
        if self.is_pushed:
            pygame.draw.rect(screen, (0, 255, 0), self.rect)
        screen.blit(self.surface, self.rect)


class ButtonText(Button):
    def __init__(self, text, x, y):
        font = pygame.font.SysFont("Comic Sans", 25)
        surface = font.render(text, True, (255, 0, 0))
        super().__init__(surface, x, y)


class ButtonPic(Button):
    def __init__(self, pic, x, y):
        im = pygame.image.load(pic).convert()
        im.set_colorkey((255, 255, 255))
        super().__init__(im, x, y)


class ButtonCont:
    def __init__(self, buttons):
        self.buttons = buttons
        self.num = 0

    def push(self, pos):
        for i in range(len(self.buttons)):
            if self.buttons[i].push(pos):
                self.buttons[self.num].release()
                self.buttons[i].catch()
                self.num = i

    def draw(self, screen):
        for but in self.buttons:
            but.draw(screen)

def menu(screen):
    maps = ButtonCont([ButtonText(f"Карта {i}", i * 200, 150)
            for i in range(1, 4)])
    cars = ButtonCont([ButtonPic(f"car_{i}.png", i * 200, 350)
            for i in range(1, 4)])
    start = ButtonText("Старт", 400, 550)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return ESCAPE
            if event.type == pygame.MOUSEBUTTONDOWN:
                maps.push(event.pos)
                cars.push(event.pos)
                if start.push(event.pos):
                    return(maps.num, cars.num)

        screen.fill((255, 255, 255))
        cars.draw(screen)
        maps.draw(screen)
        start.draw(screen)
        pygame.display.update()
        pygame.time.delay(100)


def game(screen, field_num, car_num):
    field = Field(*base.Field[field_num])
    car = Car(*field.start_pos(), *base.Car[car_num], *base.Timer[car_num])
    rival = Rival(*field.start_pos(), *base.Car[car_num], *base.Timer[car_num])
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            car.acceleration()
        if keys[pygame.K_DOWN]:
            car.deceleration()
        if keys[pygame.K_LEFT]:
            car.turn_left()
        if keys[pygame.K_RIGHT]:
            car.turn_right()
        if keys[pygame.K_TAB]:
            car = Car(*field.start_pos(), *base.Car[car_num], *base.Timer[car_num])
        if keys[pygame.K_ESCAPE]:
            return True
        car.move(field)
        rival.act(field)

        screen.fill((0, 0, 0))
        field.draw(screen)
        car.draw(screen)
        rival.draw(screen)
        pygame.display.update()
        pygame.time.delay(100)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    while True:
        res = menu(screen)
        if res == ESCAPE:
            break
        cont = game(screen, *res)
        if not cont:
            break
    pygame.quit()


main()
