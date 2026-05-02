import pygame
import pygame.camera
from pygame.locals import *
from ..parsing import Input_Data, ZoneType
from typing import Any, Dict
from .camera import Camera


class DisplayScreen:
    def __init__(self, input_data: Input_Data):
        pygame.init()
        pygame.font.init()
        pygame.camera.init()
        self.font = pygame.font.SysFont('freesansbold', 10)
        self.screen_size = pygame.display.Info()
        self.heigh = self.screen_size.current_w - 150
        self.width = self.screen_size.current_h - 100
        self.screen = pygame.display.set_mode((self.heigh, self.width))
        self.title = pygame.display.set_caption('Fly-In by Pgougne')
        self.clock = pygame.time.Clock()
        self.camera = Camera(input_data.hubs, 1280, 720)
        self.running = True
        self.input_data = input_data
        self.max_x = self.get_max_x()
        self.max_y = self.get_max_y()
        self.current_tick = 0
        self.hub_s = 20
        self.start = pygame.Vector2(0, 0)
        self.end = pygame.Vector2(0, 0)
        self.is_ant = False
        self.dragging = False
        self.stop = False

    def draw_drones_and_counts(self,
                               frame: int,
                               TICKS_PER_UPDATE: int
                               ) -> None:
        cnt_per_hub: Dict[str, int] = {}
        hub_map = {hub.name: hub for hub in self.input_data.hubs}
        print(TICKS_PER_UPDATE)
        for drone in self.input_data.lst_drones:
            if not drone.path:
                continue
            if TICKS_PER_UPDATE < 60 or not self.stop:
                curr_idx = min(self.current_tick, len(drone.path) - 1)
                next_idx = min(self.current_tick + 1, len(drone.path) - 1)

                hub_a = drone.path[curr_idx]
                hub_b = drone.path[next_idx]

                pos_a = pygame.Vector2(self.get_hub_pos(hub_a.x, hub_a.y))
                pos_b = pygame.Vector2(self.get_hub_pos(hub_b.x, hub_b.y))

                is_restricted_move = (hub_b.zone == ZoneType.RESTRICTED
                                      and hub_a != hub_b)
                if hub_a == hub_b:
                    current_pos = pos_a
                    cnt_per_hub[hub_b.name] = cnt_per_hub.get(hub_b.name, 0) + 1
                else:
                    if is_restricted_move and TICKS_PER_UPDATE > 0:
                        t = frame / (TICKS_PER_UPDATE * 2)
                    elif TICKS_PER_UPDATE > 0:
                        t = frame / TICKS_PER_UPDATE
                    else:
                        t = 0

                    current_pos = pos_a.lerp(pos_b, min(t, 1.0))

                img = self.ant if self.is_ant else self.drone_img
                rect = img.get_rect(center=current_pos)
                self.screen.blit(img, rect)
            else:
                hub = drone.path[self.current_tick]
                print(hub.x, hub.y)
                img = self.ant if self.is_ant else self.drone_img
                rect = img.get_rect(center=self.get_hub_pos(hub.x, hub.y))
                self.screen.blit(img, rect)

        for name, count in cnt_per_hub.items():
            hub = hub_map[name]
            p = pygame.Vector2(self.get_hub_pos(hub.x, hub.y))
            if count > 1:
                txt = (self.font.render(str(count), True, (255, 0, 0)
                                        if self.is_ant else (0, 0, 0)))
                self.screen.blit(txt, (p.x + 15, p.y - 15))

    def render_circles(self) -> None:
        for hub in self.input_data.hubs:
            pos = pygame.Vector2(self.get_hub_pos(hub.x, hub.y))
            if not self.is_ant:
                pygame.draw.circle(self.screen,
                                   self._get_valid_color(hub.color),
                                   pos, self.hub_s)
                txt = "md" + str(hub.max_drones)
                text1 = self.font.render(txt, True, (0, 0, 0))
                textRect1 = text1.get_rect()
                x, y = pos
                textRect1.center = (x, y - self.hub_s*2)
                self.screen.blit(text1, textRect1)
            else:
                x, y = pos
                print(x, y)
                if not hub.is_end:
                    self.screen.blit(self.anthill,
                                     (x - (self.hub_s),
                                      y - (self.hub_s)))
                else:
                    self.screen.blit(self.banana,
                                     (x - (self.hub_s),
                                      y - (self.hub_s)))

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

    def render_top_right_corner(self, speed_fps: int) -> None:
        speed_percent = int((60 - speed_fps) * 100 / 60)
        mode = "ANT" if self.is_ant else "NORMAL"

        lines = [
            f"Speed: {speed_percent}%",
            f"Mode: {mode}",
            f"Time: {self.current_tick}"
        ]

        screen_w = self.screen.get_width()
        margin = 20
        y_offset = 20

        for i, line in enumerate(lines):
            color = (0, 0, 0) if not self.is_ant else (255, 255, 255)
            text_surf = self.font.render(line, True, color)
            text_rect = text_surf.get_rect(
                topright=(screen_w - margin, y_offset + (i * 20))
                )
            self.screen.blit(text_surf, text_rect)

    def event_control(self, frame: int, TICKS_PER_UPDATE: int):
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    self.running = False
                case pygame.MOUSEWHEEL:
                    self.camera.zoom(event.y)
                case pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.dragging = True
                case pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.dragging = False
                case pygame.MOUSEMOTION:
                    if self.dragging:
                        dx, dy = event.rel 
                        self.camera.update_screen_coords(dx, dy)
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_ESCAPE:
                            self.running = False
                        case pygame.K_f:
                            self.is_ant = not self.is_ant
                        case pygame.K_DOWN:
                            if TICKS_PER_UPDATE <= 56:
                                TICKS_PER_UPDATE += 3
                        case pygame.K_SPACE:
                            self.stop = not self.stop
                        case pygame.K_UP:
                            if TICKS_PER_UPDATE >= 5:
                                TICKS_PER_UPDATE -= 3
                        case pygame.K_LEFT:
                            if self.current_tick > 0:
                                self.current_tick -= 1
                                frame = 0
                        case pygame.K_RIGHT:
                            max_path = (max(len(d.path)
                                            for d in self.input_data.lst_drones))
                            if self.current_tick < max_path - 1:
                                self.current_tick += 1
                                frame = 0
        return frame, TICKS_PER_UPDATE

    def run(self) -> None:
        frame = 0
        TICKS_PER_UPDATE = 30

        while self.running:
            frame, TICKS_PER_UPDATE = self.event_control(frame, TICKS_PER_UPDATE)
            max_path = max(len(d.path) for d in self.input_data.lst_drones)
            any_moving = self.current_tick < max_path - 1
            print(self.stop)
            if any_moving:
                frame += 1
                if frame >= TICKS_PER_UPDATE and not self.stop:
                    self.current_tick += 1
                    frame = 0
            else:
                frame = 0

            if self.is_ant:
                self.screen.blit(self.sand, (0, 0))
            else:
                self.screen.fill("white")
            self.render_lines()
            self.render_circles()

            self.draw_drones_and_counts(frame, TICKS_PER_UPDATE)
            self.render_top_right_corner(TICKS_PER_UPDATE)
            pygame.display.flip()
            self.clock.tick(60)

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
        return self.camera.get_screen_coords(x, y)

    def get_img_drone(self) -> None:
        original_img = pygame.image.load("assets/drone.png").convert_alpha()
        self.drone_img = pygame.transform.scale(
            original_img, (self.hub_s*2, self.hub_s*2))

    def get_ants_img(self) -> None:
        sand = pygame.image.load("assets/sand-bg.jpg").convert_alpha()
        ant = pygame.image.load("assets/ant.png").convert_alpha()
        ant = pygame.transform.rotate(ant, -90)
        anthill = pygame.image.load("assets/ant-hill.png").convert_alpha()
        banana = pygame.image.load("assets/banana.png").convert_alpha()
        self.sand = pygame.transform.scale(sand,
                                           (self.screen_size.current_w - 150,
                                            self.screen_size.current_h - 100))
        self.ant = pygame.transform.scale(ant,
                                          (self.hub_s*2, self.hub_s*2))
        self.anthill = pygame.transform.scale(anthill,
                                              (self.hub_s*2, self.hub_s*2))
        self.banana = pygame.transform.scale(banana,
                                             (self.hub_s*2, self.hub_s*2))

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
