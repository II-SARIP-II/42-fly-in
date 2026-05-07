from ..parsing import Input_Data, ZoneType, Drone, Hub
from .camera import Camera

import pygame
from typing import Any, Dict


class DisplayScreen:
    def __init__(self, input_data: Input_Data, total_move: Dict[int, int]):
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.SysFont('freesansbold', 30)
        self.screen_size = pygame.display.Info()
        self.width = self.screen_size.current_w - 150
        self.heigh = self.screen_size.current_h - 100
        self.screen = pygame.display.set_mode((self.width, self.heigh))
        self.title = pygame.display.set_caption('Fly-In by Pgougne')
        self.clock = pygame.time.Clock()
        self.camera = Camera(input_data.hubs, self.width, self.heigh)
        self.running = True
        self.input_data = input_data
        self.max_x = self.get_max_x()
        self.max_y = self.get_max_y()
        self.current_tick = 0
        self.hub_s = self.heigh/42
        self.start = pygame.Vector2(0, 0)
        self.end = pygame.Vector2(0, 0)
        self.is_ant = False
        self.dragging = False
        self.stop = False
        self.debug_print = False
        self.print_names = True
        self.total_move = total_move

    def display_drones_movement(self,
                                frame: int,
                                TICKS_PER_UPDATE: int,
                                drone: Drone,
                                cnt_per_hub: Dict[str, int],
                                ) -> None:
        curr_idx = min(self.current_tick, len(drone.path) - 1)
        next_idx = min(self.current_tick + 1, len(drone.path) - 1)

        hub_a = drone.path[curr_idx]
        hub_b = drone.path[next_idx]
        pos_a = pygame.Vector2(self.get_hub_pos(hub_a.x, -hub_a.y))
        pos_b = pygame.Vector2(self.get_hub_pos(hub_b.x, -hub_b.y))

        if hub_b.zone == ZoneType.RESTRICTED:
            if hub_a != hub_b:
                pos_b = pygame.Vector2(self.get_hub_pos(
                    (hub_b.x + hub_a.x)/2, (-hub_b.y + -hub_a.y)/2))

            else:
                if self.current_tick >= 1:
                    pos_bef_a = drone.path[min(
                        self.current_tick - 1,
                        len(drone.path) - 1)]
                    cnt_per_hub[hub_b.name] = (cnt_per_hub.get(hub_b.name, 0)
                                               + 1)
                    pos_a = pygame.Vector2(self.get_hub_pos(
                        (hub_a.x + pos_bef_a.x)/2,
                        (-hub_a.y + -pos_bef_a.y)/2))
        else:
            cnt_per_hub[hub_b.name] = (cnt_per_hub.get(hub_b.name, 0) + 1)
        t = frame / TICKS_PER_UPDATE
        current_pos = pos_a.lerp(pos_b, min(t, 1.0))
        img = self.ant if self.is_ant else self.drone_img
        rect = img.get_rect(center=current_pos)
        self.screen.blit(img, rect)

    def display_freezed_drones(self,
                               drone: Drone,
                               cnt_per_hub: Dict[str, int]
                               ) -> bool:
        if len(drone.path) > self.current_tick:
            hub = drone.path[self.current_tick]
        else:
            hub = drone.path[-1]
        if (hub.zone == ZoneType.RESTRICTED
                and hub != drone.path[self.current_tick - 1]):
            curr_idx = min(self.current_tick - 1, len(drone.path) - 1)
            next_idx = min(self.current_tick, len(drone.path) - 1)

            hub_a = drone.path[curr_idx]
            hub_b = drone.path[next_idx]
            img = self.ant if self.is_ant else self.drone_img
            rect = img.get_rect(center=self.get_hub_pos(
                (hub_b.x + hub_a.x)/2, (-hub_b.y + -hub_a.y)/2))
            self.screen.blit(img, rect)
            return True
        cnt_per_hub[hub.name] = (cnt_per_hub.get(hub.name, 0) + 1)
        img = self.ant if self.is_ant else self.drone_img
        rect = img.get_rect(center=self.get_hub_pos(hub.x, -hub.y))
        self.screen.blit(img, rect)
        return False

    def txt_multiple_drones(self,
                            cnt_per_hub: Dict[str, int],
                            hub_map: Dict[str, Hub]
                            ) -> None:
        for name, count in cnt_per_hub.items():
            hub = hub_map[name]
            p = pygame.Vector2(self.get_hub_pos(hub.x, -hub.y))
            if count > 1:
                txt = (self.font.render(str(count), True, (255, 0, 0)
                                        if self.is_ant else (0, 0, 0)))
                self.screen.blit(txt, (p.x + self.hub_s, p.y + self.hub_s))

    def draw_drones_and_counts(self,
                               frame: int,
                               TICKS_PER_UPDATE: int
                               ) -> None:
        cnt_per_hub: Dict[str, int] = {}
        hub_map = {hub.name: hub for hub in self.input_data.hubs}
        for drone in self.input_data.lst_drones:
            if not drone.path:
                continue

            if not self.stop:
                self.display_drones_movement(frame,
                                             TICKS_PER_UPDATE,
                                             drone, cnt_per_hub)
            else:
                if self.display_freezed_drones(drone, cnt_per_hub):
                    continue

        self.txt_multiple_drones(cnt_per_hub, hub_map)

    def blocked_zone(self, hx: int, hy: int, color: str) -> None:
        start = pygame.Vector2(self.get_hub_pos(hx, hy))
        end = pygame.Vector2(self.get_hub_pos(hx, hy))
        sx, sy = start
        start = (sx - self.hub_s, sy - self.hub_s)
        ex, ey = end
        end = (ex + self.hub_s, ey + self.hub_s)
        line_color = "black" if color != "black" else "white"
        pygame.draw.line(self.screen, line_color, start, end, width=4)

        start = pygame.Vector2(self.get_hub_pos(hx, hy))
        sx, sy = start
        start = sx + self.hub_s, sy - self.hub_s
        end = pygame.Vector2(self.get_hub_pos(hx, hy))
        ex, ey = end
        end = ex - self.hub_s, ey + self.hub_s
        pygame.draw.line(self.screen, line_color, start, end, width=4)

    def render_circles(self) -> None:
        for hub in self.input_data.hubs:
            pos = pygame.Vector2(self.get_hub_pos(hub.x, -hub.y))
            if not self.is_ant:
                if hub.color == "rainbow":
                    RAINBOW = [
                        (255, 0, 0),
                        (255, 40, 0),
                        (255, 80, 0),
                        (255, 127, 0),
                        (255, 160, 0),
                        (255, 200, 0),
                        (255, 255, 0),
                        (200, 255, 0),
                        (160, 255, 0),
                        (120, 255, 0),
                        (60, 255, 0),
                        (0, 255, 0),
                        (0, 200, 50),
                        (0, 130, 100),
                        (0, 70, 200),
                        (0, 0, 255),
                        (30, 0, 200),
                        (75, 0, 130),
                        (110, 0, 170),
                        (148, 0, 211)
                    ]
                    thickness = self.hub_s / len(RAINBOW)
                    for i, color in enumerate(RAINBOW):
                        radius = self.hub_s - thickness * i
                        if radius > 0:
                            pygame.draw.circle(self.screen, color, pos, radius)
                else:
                    pygame.draw.circle(self.screen,
                                       self._get_valid_color(hub.color),
                                       pos, self.hub_s)
                if hub.zone == ZoneType.BLOCKED:
                    self.blocked_zone(hub.x, hub.y, hub.color)
                if self.print_names:
                    name = self.font.render(hub.name, True, (0, 0, 0))
                    nameRect = name.get_rect()
                    x, y = self.get_hub_pos(hub.x, -hub.y)
                    nameRect.center = (x, y + self.hub_s + 5)
                    self.screen.blit(name, nameRect)
                if self.debug_print:
                    txt = "md" + str(hub.max_drones)
                    if hub.zone == ZoneType.RESTRICTED:
                        txt += "\nrestricted"
                    elif hub.zone == ZoneType.PRIORITY:
                        txt += "\npriority"
                    text1 = self.font.render(txt, True, (0, 0, 0))
                    textRect1 = text1.get_rect()
                    x, y = pos
                    textRect1.center = (x, y - self.hub_s*2)
                    self.screen.blit(text1, textRect1)

            else:
                x, y = pos
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
                                                    -connection.hub1.y))
            end = pygame.Vector2(self.get_hub_pos(connection.hub2.x,
                                                  -connection.hub2.y))
            pygame.draw.line(self.screen, "black", start, end, width=2)
            if self.debug_print and not self.is_ant:
                txt = "mc" + str(connection.max_link_capacity)
                text = self.font.render(txt, True, (0, 0, 0))
                textRect1 = text.get_rect()
                xs, ys = start
                xe, ye = end
                px = xs + (xs - xe)/2 if xs > xe else xs + (xe - xs)/2
                py = ye + (ys - ye) if ye < ys else ys + (ye - ys)
                textRect1.center = (px, py-10)
                self.screen.blit(text, textRect1)

    def render_inputs(self) -> None:
        padding = 30
        block_size = self.hub_s * 3
        color_arrow = (255, 255, 255)
        font = pygame.font.SysFont('freesansbold', 60)
        base_points = [(0, 100), (0, 200), (200, 200),
                       (200, 300), (300, 150),
                       (200, 0), (200, 100)]

        def draw_arrow(x_offset: int, y_offset: int, rotation: str) -> None:
            """Draw arrow for layout"""
            points = []
            size = block_size * 0.6
            margin = (block_size - size) / 2

            for px, py in base_points:
                nx, ny = px / 300, py / 300

                if rotation == "left":
                    rx, ry = 1 - nx, 1 - ny
                elif rotation == "down":
                    rx, ry = 1 - ny, nx
                elif rotation == "up":
                    rx, ry = ny, 1 - nx
                else:
                    rx, ry = nx, ny

                final_x = x_offset + margin + (rx * size)
                final_y = y_offset + margin + (ry * size)
                points.append((final_x, final_y))

            pygame.draw.polygon(self.screen, color_arrow, points)

        x, y = padding, self.heigh - block_size - padding
        pygame.draw.rect(self.screen,
                         "gray31", pygame.Rect(x, y, block_size, block_size))
        draw_arrow(x, y, "left")

        x, y = padding * 2 + block_size, self.heigh - block_size - padding
        pygame.draw.rect(self.screen,
                         "gray31", pygame.Rect(x, y, block_size, block_size))
        draw_arrow(x, y, "down")

        x, y = padding * 3 + block_size * 2, self.heigh - block_size - padding
        pygame.draw.rect(self.screen,
                         "gray31", pygame.Rect(x, y, block_size, block_size))
        draw_arrow(x, y, "right")

        x, y = (padding * 2 + block_size,
                self.heigh - block_size * 2 - padding * 2)
        pygame.draw.rect(self.screen,
                         "gray31", pygame.Rect(x, y, block_size, block_size))
        draw_arrow(x, y, "up")

        rect_space = pygame.Rect(self.width/4,
                                 self.heigh - block_size - padding,
                                 self.width/2, block_size)
        pygame.draw.rect(self.screen, "gray31", rect_space)

        txt = font.render("SPACE", True, (255, 255, 255))
        txt_rect = txt.get_rect(center=rect_space.center)
        self.screen.blit(txt, txt_rect)

        rect_f = pygame.Rect(self.width - padding - block_size,
                             self.heigh - block_size - padding,
                             block_size, block_size)
        pygame.draw.rect(self.screen, "gray31", rect_f)
        txt1 = font.render("F", True, (255, 255, 255))
        txt1_rect = txt1.get_rect(center=rect_f.center)
        self.screen.blit(txt1, txt1_rect)

        rect_d = pygame.Rect(self.width - padding*2 - block_size*2,
                             self.heigh - block_size - padding,
                             block_size, block_size)
        pygame.draw.rect(self.screen, "gray31", rect_d)

        txt2 = font.render("D", True, (255, 255, 255))
        txt2_rect = txt2.get_rect(center=rect_d.center)
        self.screen.blit(txt2, txt2_rect)

        rect_n = pygame.Rect(self.width - padding*3 - block_size*3,
                             self.heigh - block_size - padding,
                             block_size, block_size)
        pygame.draw.rect(self.screen, "gray31", rect_n)

        txt3 = font.render("N", True, (255, 255, 255))
        txt3_rect = txt3.get_rect(center=rect_n.center)
        self.screen.blit(txt3, txt3_rect)

    def render_top_right_corner(self, speed_fps: int) -> None:
        speed_percent = int((60 - speed_fps) * 100 / 60)
        mode = "ANT" if self.is_ant else "NORMAL"

        lines = [
            f"Speed: {speed_percent}%",
            f"Mode: {mode}",
            f"Stop: {self.stop}",
            f"Debug: {self.debug_print}",
            f"Names: {self.print_names}",
            f"Score: {self.current_tick}",
            f"Metric Score: {self.total_move[self.current_tick]}"
        ]

        screen_w = self.screen.get_width()
        margin = 30
        y_offset = 30

        for i, line in enumerate(lines):
            color = (0, 0, 0) if not self.is_ant else (255, 255, 255)
            text_surf = self.font.render(line, True, color)
            text_rect = text_surf.get_rect(
                topright=(screen_w - margin, y_offset + (i * 50))
                )
            self.screen.blit(text_surf, text_rect)

    def event_control(self,
                      frame: int,
                      TICKS_PER_UPDATE: int
                      ) -> tuple[int, int]:
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
                            max_path = (max(
                                len(d.path)
                                for d in self.input_data.lst_drones))
                            if self.current_tick < max_path - 1:
                                self.current_tick += 1
                                frame = 0
                        case pygame.K_d:
                            self.debug_print = not self.debug_print
                        case pygame.K_n:
                            self.print_names = not self.print_names
        return frame, TICKS_PER_UPDATE

    def run(self) -> None:
        frame = 0
        TICKS_PER_UPDATE = 30

        while self.running:
            frame, TICKS_PER_UPDATE = self.event_control(frame,
                                                         TICKS_PER_UPDATE)

            max_path = max(len(d.path) for d in self.input_data.lst_drones)
            any_moving = self.current_tick < max_path - 1
            if any_moving and not self.stop:
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
            self.render_inputs()
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

    def get_hub_pos(self, x: float, y: float) -> tuple[int, int]:
        return self.camera.get_screen_coords(x, y)

    def load_imgs(self) -> None:
        original_img = pygame.image.load("assets/drone.png").convert_alpha()
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
        self.drone_img = pygame.transform.scale(
            original_img, (self.hub_s*2, self.hub_s*2))

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

        if color_name == "rainbow":
            return color_name

        try:
            pygame.Color(color_name)
            return color_name
        except ValueError:
            return "gray"


def display(input_data: Input_Data, total_move: Dict[int, int]) -> None:
    game = DisplayScreen(input_data, total_move)
    game.load_imgs()
    game.run()
