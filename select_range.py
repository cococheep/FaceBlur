import cv2


class Box:
    start_x = 0
    start_y = 0
    end_x = 0
    end_y = 0
    move = False

    def __init__(self, window_height, window_width):
        self.max_height = int(window_height)
        self.max_width = int(window_width)

    def __delete__(self, instance):
        pass

    def set_start_x(self, x):
        self.start_x = x

    def set_start_y(self, y):
        self.start_y = y

    def set_end_x(self, x):
        self.end_x = x

    def set_end_y(self, y):
        self.end_y = y

    def set_move(self, boolean):
        self.move = boolean

    def refresh(self):
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0

    def adjust_box(self, first_gap, second_gap, first_spot, second_spot):
        first_spot = first_spot[0] + self.start_y, first_spot[1] + self.start_x
        second_spot = second_spot[0] + self.start_y, second_spot[1] + self.start_x

        def new_box(gap, spot, w, h):
            start_x = spot[1] - gap[0] if spot[1] - gap[0] > 0 else 0
            end_x = spot[1] + gap[1] if spot[1] + gap[1] < w else w - 1
            start_y = spot[0] - gap[2] if spot[0] - gap[2] > 0 else 0
            end_y = spot[0] + gap[3] if spot[0] + gap[3] < h else h - 1

            return [start_x, end_x, start_y, end_y]

        first_box = new_box(first_gap, first_spot, self.max_width, self.max_height)
        second_box = new_box(second_gap, second_spot, self.max_width, self.max_height)

        self.start_x = (first_box[0] + second_box[0]) // 2
        self.end_x = (first_box[1] + second_box[1]) // 2
        self.start_y = (first_box[2] + second_box[2]) // 2
        self.end_y = (first_box[3] + second_box[3]) // 2


def select_range(event, x, y, flag, param):
    frame = param[0]
    box = param[1]
    h = frame.shape[0]
    w = frame.shape[1]

    # mouse button down
    if event == cv2.EVENT_LBUTTONDOWN:
        box.set_move(True)
        box.set_start_x(x)
        box.set_start_y(y)
        box.set_end_x(x)
        box.set_end_y(y)

    # mouse button moving
    elif event == cv2.EVENT_MOUSEMOVE:
        if box.move:
            # Mouse Inside window
            if x < w and y < h:
                box.set_end_x(x)
                box.set_end_y(y)

            # Mouse outside left border
            elif x >= w and y < h:
                box.set_end_x(w - 1)
                box.set_end_y(y)

            # Mouse outside bottom border
            elif x < w and y >= h:
                box.set_end_x(x)
                box.set_end_y(h - 1)

            # Mouse outside both border
            else:
                box.set_end_x(w - 1)
                box.set_end_y(h - 1)

    # Mouse button up
    elif event == cv2.EVENT_LBUTTONUP:
        box.set_move(False)
        # Mouse inside window
        if x < w and y < h:
            box.set_end_x(x)
            box.set_end_y(y)

        # Mouse outside left border
        elif x >= w and y < h:
            box.set_end_x(w - 1)
            box.set_end_y(y)

        # Mouse outside bottom border
        elif x < w and y >= h:
            box.set_end_x(x)
            box.set_end_y(h - 1)

        # Mouse outside both border
        else:
            box.set_end_x(w - 1)
            box.set_end_y(h - 1)


# draw the box
def draw_box(box, frame, lc=(255, 0, 0)):
    line_size = 5
    line_color = lc

    start_x = box.start_x
    start_y = box.start_y
    end_x = box.end_x
    end_y = box.end_y

    for x in range(start_x, end_x):
        # upper line of box
        for y in range(start_y, start_y + line_size):
            frame[y, x] = line_color
        # bottom line of box
        for y in range(end_y - line_size, end_y):
            frame[y, x] = line_color

    for y in range(start_y + line_size, end_y - line_size):
        # left line of box
        for x in range(start_x, start_x + line_size):
            frame[y, x] = line_color
        # right line of box
        for x in range(end_x - line_size, end_x):
            frame[y, x] = line_color


def blur(box, frame, rate, border=10):
    sx = box.start_x
    sy = box.start_y
    ex = box.end_x
    ey = box.end_y

    width = ex - sx
    height = ey - sy

    br = rate // border
    crop = frame[sy:ey, sx:ex]
    blur_crop = cv2.blur(crop, (rate, rate))
    frame[sy:ey, sx:ex] = blur_crop

    return frame
