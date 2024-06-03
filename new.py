import pygame
import math


OUT_ROAD_MAX_SPEED = 3
ON_TRACK = 0
ON_GRASS = 1
ON_FINISH = 2
OUT_OF_FRAME = -1

class Timer:
    Y = 10
    def __init__(self, color, x, y):
        self.clock = pygame.time.Clock()
        self.time = 0
        self.going = False
        self.coords = (x, Timer.Y)
        Timer.Y += 20
        self.color = color
        self.font = pygame.font.SysFont("Comic Sans", 25)

    def start(self):
        if not self.going:
            self.time = 0
            self.clock.tick()
            self.going = True

    def stop(self):
        self.going = False

    def draw(self, screen):
        if self.going:
            self.clock.tick()
            self.time += self.clock.get_time()
        string = f"{self.time // 60000}:{self.time // 1000 % 60}:{self.time % 1000}"
        surface = self.font.render(string, True, self.color)
        screen.blit(surface, self.coords)


class Car:
    def __init__(self, x, y, direction, acc, dec, friction, max_speed,
                 turn_angle, image, t_color, t_x, t_y):
        self.x = x
        self.y = y
        self.speed = 0
        self.direction = direction
        self.acc = acc
        self.dec = dec
        self.friction = friction
        self.max_speed = max_speed
        self.turn_angle = turn_angle
        self.im = pygame.image.load(image).convert()
        self.im.set_colorkey((255, 255, 255))
        self.timer = Timer(t_color, t_x, t_y)

    def decart(self, direction, length):
        dx = math.cos(math.radians(direction)) * length
        dy = math.sin(math.radians(direction)) * length
        return dx, dy

    def move(self, field):
        place = field.on_the_road(self.x, self.y)
        if place == ON_GRASS:
            self.speed = max(self.speed - self.dec * 2, OUT_ROAD_MAX_SPEED)
        elif place == ON_TRACK:
            self.timer.start()
        elif place == ON_FINISH:
            self.timer.stop()
        dx, dy = self.decart(self.direction, self.speed)
        self.x += dx
        self.y += dy
        self.speed = max(self.speed - self.friction, 0)

    def acceleration(self):
        self.speed = min(self.speed + self.acc, self.max_speed)

    def deceleration(self):
        self.speed = max(self.speed - self.dec, 0)

    def turn_left(self):
        if self.speed != 0:
            self.direction -= self.turn_angle

    def turn_right(self):
        if self.speed != 0:
            self.direction += self.turn_angle

    def draw_pre(self, screen):
        CAR_LEN = 40
        dx, dy = self.decart(self.direction, CAR_LEN // 2)
        pygame.draw.line(screen, (255, 0, 0),
                         (int(self.x - dx), int(self.y - dy)),
                         (int(self.x + dx), int(self.y + dy)),
                         CAR_LEN // 4)

    def draw(self, screen):
        im2 = pygame.transform.rotate(self.im, -self.direction)
        im2_rect = im2.get_rect(center=(self.x, self.y))
        screen.blit(im2, im2_rect)
        self.timer.draw(screen)


class Rival(Car):
    def target_dist(self, angle, step, target_type, field):
        dx, dy = self.decart(angle, step)
        x, y = self.x, self.y
        dist = 0
        road = field.on_the_road(x, y)
        while road != target_type:
            x += dx
            y += dy
            dist += step
            if road == OUT_OF_FRAME:
                return OUT_OF_FRAME
            road = field.on_the_road(x, y)
        return dist

    def follow_target(self, marginal_angle, step, target_type, field):
        turn = 0
        for i in range(0, marginal_angle, 5):
            left = self.target_dist(self.direction + i, step,
                                    target_type, field)
            right = self.target_dist(self.direction - i, step,
                                     target_type, field)
            turn += right - left
        if turn < 0:
            return -1
        elif turn > 0:
            return 1
        return 0


    def act(self, field):
        STEP = 3
        MAX_DISTANCE = STEP * 5
        MIN_DISTANCE = STEP * 3
        #self.speed = 5
        road = field.on_the_road(self.x, self.y)
        if road == ON_TRACK or road == ON_FINISH:
            straight = self.target_dist(self.direction, STEP, ON_GRASS, field)
            if straight > MAX_DISTANCE:
                self.acceleration()
            else:
                if straight < MIN_DISTANCE:
                    self.deceleration()
                target = self.follow_target(30, STEP, ON_GRASS, field)
                if target > 0:
                    self.turn_right()
                elif target < 0:
                    self.turn_left()
        elif road == ON_GRASS:
            self.acceleration()
            target = self.follow_target(90, STEP, ON_TRACK, field)
            if target < 0:
                self.turn_right()
            elif target > 0:
                self.turn_left()
        self.move(field)

    def draw(self, screen):
        pygame.draw.circle(screen, (200, 70, 10), (self.x, self.y), 20, 2)
        super().draw(screen)


class Field:
    def __init__(self, image, car_x, car_y, direction, way):
        self.im = pygame.image.load(image)
        self.start = (car_x, car_y, direction)

    def start_pos(self):
        return self.start

    def on_the_road(self, x, y):
        try:
            color = self.im.get_at((int(x), int(y)))
            if color[0] == color[1] == color[2]:
                return ON_TRACK
            elif color == (255, 0, 255):
                return ON_FINISH
            else:
                return ON_GRASS
        except Exception as e:
            print(e, x, y)
            return OUT_OF_FRAME

    def draw(self, screen):
        screen.blit(self.im, (0, 0))
