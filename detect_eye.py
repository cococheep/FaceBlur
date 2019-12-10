import cv2


def sobel(frame):
    img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    img_sobel_x = cv2.Sobel(img_gray, cv2.CV_64F, 1, 0, ksize=3)
    img_sobel_x = cv2.convertScaleAbs(img_sobel_x)
    img_sobel_y = cv2.Sobel(img_gray, cv2.CV_64F, 0, 1, ksize=3)
    img_sobel_y = cv2.convertScaleAbs(img_sobel_y)

    img_sobel = cv2.addWeighted(img_sobel_x, 1, img_sobel_y, 1, 0)

    return img_sobel


def spot_search(range_x, range_y, edge_frame, mf=10):
    max_edge = 0
    spot = [0, 0]
    for i in range(range_y[0], range_y[1]):
        for j in range(range_x[0], range_x[1]):
            if edge_frame[i][j] > max_edge:
                max_edge = edge_frame[i][j]
                spot = [i * mf, j * mf]

    # spot[0]: y_position, spot[1]: x_position
    return spot


def find_spot(edge_frame, mf=20):
    # Mosaic
    mosaic_factor = mf
    edge_frame = cv2.resize(edge_frame, dsize=(0, 0), fx=0.2, fy=0.2, interpolation=cv2.INTER_AREA)
    edge_frame = cv2.resize(edge_frame, dsize=(0, 0), fx=5, fy=5, interpolation=cv2.INTER_NEAREST)
    edge_frame = cv2.resize(edge_frame, dsize=(0, 0), fx=1.0 / mosaic_factor, fy=1.0 / mosaic_factor, interpolation=cv2.INTER_AREA)

    # divide into four region
    height = edge_frame.shape[0]
    width = edge_frame.shape[1]
    divide_x = width // 2
    divide_y = height // 2

    first_spot = spot_search([0, divide_x], [0, divide_y], edge_frame)
    second_spot = spot_search([divide_x, width], [0, divide_y], edge_frame)

    return first_spot, second_spot


# find the gap between spot and box
def find_gap(spot, box):
    width = box.end_x - box.start_x
    height = box.end_y - box.start_y

    left_gap = spot[1]
    right_gap = width - spot[1]
    upper_gap = spot[0]
    bottom_gap = height - spot[0]

    gap = [left_gap, right_gap, upper_gap, bottom_gap]
    return gap
