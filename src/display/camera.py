from ..parsing import Hub


class Camera:
    def __init__(self,
                 hubs: list[Hub],
                 screen_width: int,
                 screen_height: int
                 ) -> None:
        '''
        Initialiazed camera class to fit perfetly the graph in the window.
        Params:
            hubs: list[Hub] = List of hubs to get all possible positions
            screen_width: int = the screen width of the window
            screen_height: int = the screen height of the window
        '''
        self.screen_width = screen_width
        self.screen_height = screen_height
        margin = 50
        self.add_x: int = 0
        self.add_y: int = 0

        logical_xs = [hub.x for hub in hubs]
        logical_ys = [-hub.y for hub in hubs]

        min_x, max_x = min(logical_xs), max(logical_xs)
        min_y, max_y = min(logical_ys), max(logical_ys)

        logical_width = max(1, max_x - min_x)
        logical_height = max(1, max_y - min_y)

        scale_x = (self.screen_width - 2 * margin) / logical_width
        scale_y = (self.screen_height - 2 * margin) / logical_height
        self.scale = min(scale_x, scale_y)

        self.hub_radius = min(int(self.scale * 0.2), margin - 20)
        self.drone_radius = min(int(self.scale * 0.1), margin - 25)

        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2

        self.offset_x = (self.screen_width / 2) - (center_x * self.scale)
        self.offset_y = (self.screen_height / 2) + (center_y * self.scale)

    def get_screen_coords(self,
                          logical_x: float,
                          logical_y: float
                          ) -> tuple[int, int]:
        '''
        get the coords of anything with in the window like hub, connection drones etc.
        Params:
            logical_x: float = the x of the target to position
            logical_y: float = the y of the target to position
        Return values:
            tuple[int, int] = the translated coords of target in the projection (x, y) 
        '''
        screen_x = int(logical_x * self.scale + self.offset_x + self.add_x)
        screen_y = int(-logical_y * self.scale + self.offset_y + self.add_y)
        return screen_x, screen_y

    def update_screen_coords(self, add_x: int, add_y: int) -> None:
        '''
        for the mouse movement, to translate everything
        Params:
            add_x: int = the x value to add
            add_y: int = the y value to add
        '''
        self.add_x += add_x
        self.add_y += add_y

    def zoom(self, scroll: int) -> None:
        '''
        for the mouse scroll, to zoom
        Params:
            scroll: int = the scroll value to add
        '''
        self.scale += scroll
