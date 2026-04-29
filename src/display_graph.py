import pygame
from .parsing import Hub, Connection, Input_Data
from typing import Dict, Any


class DisplayScreen:
    def __init__(self, input_data: Input_Data):
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.SysFont('freesansbold', 10)
        self.screen_size = pygame.display.Info()
        self.screen = pygame.display.set_mode((
            self.screen_size.current_w - 150,
            self.screen_size.current_h - 100))
        self.title = pygame.display.set_caption('Fly-In by Pgougne')
        self.clock = pygame.time.Clock()
        self.running = True
        self.input_data = input_data
        self.max_x = self.get_max_x()
        self.max_y = self.get_max_y()
        self.current_tick = 0
        self.hub_size = 40
        self.start = pygame.Vector2(0, 0)
        self.end = pygame.Vector2(0, 0)
        self.is_ant = False


    def move_drones(self) -> bool:
        counts_per_hub: Dict[str, int] = {}
        any_drone_moving = False

        for drone in self.input_data.lst_drones:
            if not drone.path:
                continue

            index = min(self.current_tick, len(drone.path) - 1)
            curr_hub = drone.path[index]

            hub_name = curr_hub.name
            counts_per_hub[hub_name] = counts_per_hub.get(hub_name, 0) + 1

            if self.current_tick < len(drone.path) - 1:
                any_drone_moving = True

        hub_map = {hub.name: hub for hub in self.input_data.hubs}

        for name, count in counts_per_hub.items():
            hub = hub_map[name]
            if not self.is_ant:
                pos = pygame.Vector2(self.get_hub_pos(hub.x, hub.y))
                rect = self.drone_img.get_rect(center=(pos.x, pos.y))
                self.screen.blit(self.drone_img, rect)
            else:
                pos = pygame.Vector2(self.get_hub_pos(hub.x, hub.y))
                rect = self.ant.get_rect(center=(pos.x, pos.y))
                self.screen.blit(self.ant, rect)

            if count > 0:
                txt_nb = self.font.render(str(count), True, (0, 0, 0))
                self.screen.blit(txt_nb, (pos.x + 5, pos.y + 5))

        return any_drone_moving

    def render_circles(self) -> None:
        for hub in self.input_data.hubs:
            pos = pygame.Vector2(self.get_hub_pos(hub.x, hub.y))
            if not self.is_ant:
                pygame.draw.circle(self.screen, self._get_valid_color(hub.color),
                                   pos, self.hub_size)
                txt = "md" + str(hub.max_drones)
                text1 = self.font.render(txt, True, (0, 0, 0))
                textRect1 = text1.get_rect()
                x, y = pos
                textRect1.center = (x, y - self.hub_size*2)
                self.screen.blit(text1, textRect1)
            else:
                x, y = pos
                print(x, y)
                if not hub.is_end: 
                    self.screen.blit(self.anthill, (x - (self.hub_size), y  - (self.hub_size)))
                else: 
                    self.screen.blit(self.banana, (x - (self.hub_size), y  - (self.hub_size)))

    def render_lines(self) -> None:
        for connection in self.input_data.connections:
            start = pygame.Vector2(self.get_hub_pos(connection.hub1.x,
                                                    connection.hub1.y))
            end = pygame.Vector2(self.get_hub_pos(connection.hub2.x,
                                                  connection.hub2.y))
            pygame.draw.line(self.screen, "black", start, end, width=2)
            txt = "mc" + str(connection.max_link_capacity)
            text = self.font.render(txt, True, (0, 0, 0))
            textRect1 = text.get_rect()
            xs, ys = start
            xe, ye = end
            px = xs + (xs - xe)/2 if xs > xe else xs + (xe - xs)/2
            py = ye + (ys - ye) if ye < ys else ys + (ye - ys)
            textRect1.center = (px, py-10)
            self.screen.blit(text, textRect1)

    def run(self) -> None:
        frame = 0
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            if not self.is_ant:
                self.screen.fill("white")
            else:
                self.screen.blit(self.sand, (0, 0))
            self.render_lines()
            self.render_circles()
            if self.move_drones():
                if frame == 60:
                    print(self.current_tick)
                    self.current_tick += 1
                    frame = 0 

            pygame.display.flip()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE] or keys[pygame.K_q]:
                self.running = False
            if keys[pygame.K_f]:
                self.is_ant = not self.is_ant

            frame += 1

            self.clock.tick(30)

        pygame.quit()

    def get_max_x(self) -> Any:
        lsthubx = [hub.x for hub in self.input_data.hubs]
        max_int = max(lsthubx)
        min_int = min(lsthubx)
        return max_int - min_int

    def get_max_y(self) -> Any:
        lsthuby = [hub.y for hub in self.input_data.hubs]
        max_int = max(lsthuby)
        min_int = min(lsthuby)
        return max_int - min_int

    def get_hub_pos(self, x: int, y: int) -> tuple[int, int]:
        padding = 50
        drawable_w = self.screen_size.current_w - 150 - (padding * 2)
        drawable_h = self.screen_size.current_h - 100 - (padding * 2)

        scale_x = drawable_w / (self.max_x + 1) if self.max_x > 0 else 0
        scale_y = drawable_h / 2 / (self.max_y + 1) if self.max_y > 0 else 0

        posX = (x * scale_x) + padding
        posY = (y * scale_y) + padding + drawable_h / 2

        return int(posX), int(posY)

    def get_img_drone(self) -> None:
        original_img = pygame.image.load("assets/drone.png").convert_alpha()
        self.drone_img = pygame.transform.scale(
            original_img, (self.hub_size*2, self.hub_size*2))

    
    def get_ants_img(self) -> None:
        sand = pygame.image.load("assets/sand-bg.jpg").convert_alpha()
        ant = pygame.image.load("assets/ant.png").convert_alpha()
        ant = pygame.transform.rotate(ant, -90)
        anthill = pygame.image.load("assets/ant-hill.png").convert_alpha()
        banana = pygame.image.load("assets/banana.png").convert_alpha()
        self.sand = pygame.transform.scale(sand, (self.screen_size.current_w - 150, self.screen_size.current_h - 100))
        self.ant = pygame.transform.scale(ant, (self.hub_size*2, self.hub_size*2))
        self.anthill = pygame.transform.scale(anthill, (self.hub_size*2, self.hub_size*2))
        self.banana = pygame.transform.scale(banana, (self.hub_size*2, self.hub_size*2))


    @staticmethod
    def _get_valid_color(color_name: str | None) -> str:
        """Return a pygame-safe color name with fallback.

        Args:
            color_name: Candidate color name from metadata.

        Returns:
            Valid color string accepted by pygame.
        """
        if not color_name:
            return "gray"

        try:
            pygame.Color(color_name)
            return color_name
        except ValueError:
            return "gray"


def display(input_data: Input_Data) -> None:
    game = DisplayScreen(input_data)

    game.get_img_drone()
    game.get_ants_img()
    game.run()
