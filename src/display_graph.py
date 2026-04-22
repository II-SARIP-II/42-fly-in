import pygame
from typing import List
from .parsing import Hub, Connection, Input_Data, ZoneType


class drones:
    def __init__(self):
        self.wait_time = 0


class DisplayScreen:
    def __init__(self, input_data: Input_Data, shortest_path: List[Hub]):
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
        self.hub_size = 10
        self.start = pygame.Vector2(0,0)
        self.end = pygame.Vector2(0,0)
        self.path = shortest_path

    def move_drones(self) -> bool:
        rev_path = self.path[::-1]
        moved_any = False
        for i in range(len(rev_path)):
            current_hub = rev_path[i]

            for connection in self.input_data.connections:

                if connection.hub2 == current_hub:
                    free_space = current_hub.max_drones - len(current_hub.nb_drones_in)
                    if current_hub.is_end:
                        free_space = 999 

                    while free_space > 0 and len(connection.nb_drones_in) > 0:
                        drone = connection.nb_drones_in.pop(0)
                        current_hub.nb_drones_in.append(drone)
                        free_space -= 1
                        moved_any = True

                if connection.hub2 == current_hub:
                    source_hub = connection.hub1
                    line_free_space = connection.max_link_capacity - len(connection.nb_drones_in)

                    while line_free_space > 0 and len(source_hub.nb_drones_in) > 0:
                        drone = source_hub.nb_drones_in.pop(0)
                        connection.nb_drones_in.append(drone)
                        line_free_space -= 1
                        moved_any = True

        return moved_any

    def render_circles(self):
        for hub in self.input_data.hubs:
            pos = pygame.Vector2(self.get_hub_pos(hub.x, hub.y))
            pygame.draw.circle(self.screen, self._get_valid_color(hub.color), pos, self.hub_size)
            txt = "md" + str(hub.max_drones)
            txt += "\ns" + str(hub.score) + "\n"
            text1 = self.font.render(txt, True, (0, 0, 0))
            textRect1 = text1.get_rect()
            x, y = pos
            textRect1.center = (x, y - self.hub_size*2)
            self.screen.blit(text1, textRect1)

            # Drones
            if len(hub.nb_drones_in) > 0:
                self.screen.blit(self.drone_img, pos)
                txt_nb_drones = self.font.render(str(len(hub.nb_drones_in)), True, (0, 0, 0))
                rect_nb_drones = txt_nb_drones.get_rect()
                rect_nb_drones.center = (x + self.hub_size, y + self.hub_size*2)
                self.screen.blit(txt_nb_drones, rect_nb_drones)

    def render_lines(self):
        for connection in self.input_data.connections:
            start = pygame.Vector2(self.get_hub_pos(connection.hub1.x, connection.hub1.y))
            end = pygame.Vector2(self.get_hub_pos(connection.hub2.x, connection.hub2.y))
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

            if len(connection.nb_drones_in) > 0:
                self.screen.blit(self.drone_img, (px, py-10))
                txt_nb_drones = self.font.render(str(len(connection.nb_drones_in)), True, (0, 0, 0))
                rect_nb_drones = txt_nb_drones.get_rect()
                rect_nb_drones.center = (px + self.hub_size, py + self.hub_size*2)
                self.screen.blit(txt_nb_drones, rect_nb_drones)

    def run(self):
        count = 0
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            pygame.font.Font()
            self.screen.fill("white")

            self.render_lines()
            self.render_circles()

            pygame.display.flip()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE] or keys[pygame.K_q]:
                self.running = False

            if self.move_drones():
                count += 1

            self.clock.tick(2)
            print(count)

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

    @staticmethod
    def is_full_hub(element: Hub) -> bool:
        if element.is_end:
            return False
        return element.max_drones - element.nb_drones_in < 0

    @staticmethod
    def is_full_connection(element: Connection):
        return element.max_link_capacity - element.nb_drones_in < 0

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

def display(input_data: Input_Data, path: List[Hub]):
    game = DisplayScreen(input_data, path)
    game.get_img_drone()
    game.run()
    # game.quit()
