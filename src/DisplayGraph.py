import pygame
from typing import List
from .parsing import Hub, Connection, Input_Data, ZoneType


class DisplayScreen:
    def __init__(self, input_data: Input_Data):
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.SysFont('freesansbold', 10)
        self.width = 1280
        self.heigh = 720
        self.screen = pygame.display.set_mode((self.width, self.heigh))
        self.title = pygame.display.set_caption('Fly-In by Pgougne')
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0
        self.input_data = input_data
        self.max_x = self.get_max_x()
        self.max_y = self.get_max_y()
        self.circles = []
        self.lines = []
        self.drones = []
        self.hub_size = 20
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
                "score": hub.score,
                "max_drones": hub.max_drones
            }
            self.circles.append(circle)

    def get_all_lines(self):
        for connection in self.input_data.connections:
            line = {
                "pos_start": pygame.Vector2(self.get_hub_pos(connection.hub1.x, connection.hub1.y)),
                "pos_end": pygame.Vector2(self.get_hub_pos(connection.hub2.x, connection.hub2.y)),
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

    def render_circles(self):
        for circle in self.circles:
            pygame.draw.circle(self.screen, self._get_valid_color(circle["color"]), circle
            ["pos"], self.hub_size)
            txt = "max_drone: " + str(circle["max_drones"])
            txt += "\nscore: " + str(circle["score"])
            # txt += ZoneType.circle["zone"] + "\n"
            text1 = self.font.render(txt, True, (0, 0, 0))
            textRect1 = text1.get_rect()
            x, y = circle["pos"]
            textRect1.center = (x, y - self.hub_size*2)
            self.screen.blit(text1, textRect1)
            

    def render_lines(self):
        for line in self.lines:
            pygame.draw.line(self.screen, "black", line["pos_start"], line["pos_end"], width=2)
            txt = "max_cap: " + str(line["max_link_capacity"])
            text = self.font.render(txt, True, (0, 0, 0))
            textRect1 = text.get_rect()
            xs, ys = line["pos_start"]
            xe, ye = line["pos_end"]
            px = xs + (xs - xe)/2 if xs > xe else xs + (xe - xs)/2
            py = ye + (ys - ye) if ye < ys else ys + (ye - ys)
            textRect1.center = (px, py-10)
            self.screen.blit(text, textRect1)

    def render_drones(self):
        counts = {}
        for drone in self.drones:
            pos = (drone["posX"], drone["posY"])
            counts[pos] = counts.get(pos, 0) + 1
            self.screen.blit(self.drone_img, (drone["posX"], drone["posY"]))

        for (x, y), nb in counts.items():
            if nb > 1:
                text_surf = self.font.render(str(nb), True, (0, 0, 0))
                text_rect = text_surf.get_rect()
                text_rect.center = (x + self.hub_size, y + self.hub_size * 2) 
                self.screen.blit(text_surf, text_rect)

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            pygame.font.Font()
            self.screen.fill("white")

            self.render_lines()
            self.render_circles()
            self.render_drones()

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

    def _get_valid_color(self, color_name: str | None) -> str:
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

    def quit() -> None:
        pygame.font.quit()

def display(input_data: Input_Data):
    game = DisplayScreen(input_data)
    game.get_all_circles()
    game.get_all_lines()
    game.get_img_drone()
    game.init_drones()
    game.run()
    # game.quit()
