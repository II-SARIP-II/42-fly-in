import pygame
from typing import List
from .parsing import Hub, Connection, Input_Data


class DisplayScreen:
    def __init__(self, input_data: Input_Data):
        pygame.init()
        self.width = 1280
        self.heigh = 720
        self.screen = pygame.display.set_mode((self.width, self.heigh))
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0
        self.input_data = input_data
        self.max_x = self.get_max_x()
        self.max_y = self.get_max_y()
        self.circles = []
        self.lines = []
        self.drones = []
        self.hub_size = 30
        self.start = pygame.Vector2(0,0)
        self.end = pygame.Vector2(0,0)

    def get_all_circles(self):
        for hub in self.input_data.hubs:
            if hub.is_start:
                self.start = pygame.Vector2(self.get_hub_pos(hub.x, hub.y))
            if hub.is_end:
                self.end = pygame.Vector2(self.get_hub_pos(hub.x, hub.y))
            circle = {
                "pos": pygame.Vector2(self.get_hub_pos(hub.x, hub.y)),
                "name": hub.name,
                "is_start": hub.is_start,
                "is_end": hub.is_end,
                "zone": hub.zone,
                "color": hub.color,
                "max_drones": hub.max_drones
            }
            self.circles.append(circle)

    def get_all_lines(self):
        for connection in self.input_data.connections:
            for hub in self.input_data.hubs:
                if hub.name == connection.hub1:
                    h1: Hub = hub
                if hub.name == connection.hub2:
                    h2: Hub = hub
            line = {
                "pos_start": pygame.Vector2(self.get_hub_pos(h1.x, h1.y)),
                "pos_end": pygame.Vector2(self.get_hub_pos(h2.x, h2.y)),
                "max_link_capacity": connection.max_link_capacity
            }
            self.lines.append(line)

    def init_drones(self):
        for i in range(self.input_data.nb_drones):
            drone = {
            "id": i,
            "posX": self.start.x - self.hub_size,
            "posY": self.start.y - self.hub_size
            }
            self.drones.append(drone)

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            self.screen.fill("purple")
            for line in self.lines:
                pygame.draw.line(self.screen, "black", line["pos_start"], line["pos_end"], width=2)
            for circle in self.circles:
                pygame.draw.circle(self.screen, circle["color"], circle["pos"], self.hub_size)
            for drone in self.drones:
                self.screen.blit(self.drone_img, (drone["posX"], drone["posY"]))
            pygame.display.flip()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE] or keys[pygame.K_q]:
                self.running = False

            self.clock.tick(60)

        pygame.quit()

    def get_max_x(self) -> int:
        lsthubx = [hub.x for hub in self.input_data.hubs]
        max_int = max(lsthubx)
        min_int = min(lsthubx)
        return max_int - min_int

    def get_max_y(self) -> int:
        lsthuby = [hub.y for hub in self.input_data.hubs]
        max_int = max(lsthuby)
        min_int = min(lsthuby)
        return max_int - min_int

    def get_hub_pos(self, x, y) -> tuple[int, int]:
        padding = 50
        drawable_width = self.width - (padding * 2)
        drawable_height = self.heigh - (padding * 2)

        scale_x = drawable_width / (self.max_x + 1) if self.max_x > 0 else 0
        scale_y = drawable_height / 2 / (self.max_y + 1) if self.max_y > 0 else 0

        posX = (x * scale_x) + padding
        posY = (y * scale_y) + padding + drawable_height / 2

        return int(posX), int(posY)

    def get_img_drone(self):
        original_img = pygame.image.load("assets/drone.png").convert_alpha()
        self.drone_img = pygame.transform.scale(original_img, (self.hub_size*2, self.hub_size*2))


def display(input_data: Input_Data):
    game = DisplayScreen(input_data)
    game.get_all_circles()
    game.get_all_lines()
    game.get_img_drone()
    game.init_drones()
    game.run()
