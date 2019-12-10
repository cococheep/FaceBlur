import cv2
import time
import argparse

from select_range import Box, select_range, draw_box, blur
from detect_eye import sobel, find_gap, find_spot
from detect_face import face_detect

parser = argparse.ArgumentParser()
parser.add_argument('--video', required=True, help='path to video file')
args = parser.parse_args()

video_path = args.video
trained_model = cv2.dnn.readNetFromCaffe("deploy.prototxt.txt", "ssd_300x300.caffemodel")

capture = cv2.VideoCapture(video_path)

# initialize
mode = 1
fps = 30
fps_queue = []
calculated_fps = 0
blur_rate = 20
max_height = capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
max_width = capture.get(cv2.CAP_PROP_FRAME_WIDTH)

box = Box(max_height, max_width)
frame = None
paused_frame = None
first_spot = None
second_spot = None
first_gap = None
second_gap = None
frame_count = 0

while True:
    if capture.get(cv2.CAP_PROP_POS_FRAMES) == capture.get(cv2.CAP_PROP_FRAME_COUNT):
        capture.open(video_path)

    start = time.time()
    # play mode
    if mode == 1:
        box.refresh()
        ret, frame = capture.read()
        paused_frame = frame

    # pause mode
    elif mode == -1:
        frame = paused_frame.copy()
        param = [frame, box]
        cv2.setMouseCallback("Video", select_range, param=param)
        draw_box(box, frame)

    # image track
    elif mode == 0:
        fps = 1000
        frame_count = frame_count + 1
        ret, frame = capture.read()

        # SSD
        if frame_count % 6 == 0:
            detected_faces = face_detect(frame, trained_model, set_confidence=0.5)

            # choose the face between detected faces
            real_face = 0
            for i in range(len(detected_faces)):
                sx = detected_faces[i][0] - box.start_x
                ex = detected_faces[i][2] - box.end_x
                if sx < first_spot[1] < ex or sx < second_spot[1] < ex:
                    real_face = i

            # no face detected
            if not detected_faces:
                print("Lost Face Tracking, Try Again")
                paused_frame = frame
                fps = 30
                mode = -1

            # face detected
            else:
                # set the position of box
                sx = detected_faces[real_face][0]
                sy = detected_faces[real_face][1]
                ex = detected_faces[real_face][2]
                ey = detected_faces[real_face][3]

                # adjust the position into window boundary
                box.set_start_x(sx) if sx > 0 else box.set_start_x(0)
                box.set_start_y(sy) if sy > 0 else box.set_start_y(sy)
                box.set_end_x(ex) if ex < max_width else box.set_end_x(max_width - 1)
                box.set_end_y(ey) if ey < max_height else box.set_end_y(max_height - 1)

                # calculate the gap
                first_gap = find_gap(first_spot, box)
                second_gap = find_gap(second_spot, box)

        # track eyes
        else:
            crop_image = frame.copy()[box.start_y:box.end_y, box.start_x:box.end_x]
            edge = sobel(crop_image)

            first_spot, second_spot = find_spot(edge)  # find new spot
            box.adjust_box(first_gap, second_gap, first_spot, second_spot)  # adjust box
            first_gap = find_gap(first_spot, box)  # find new gap
            second_gap = find_gap(second_spot, box)

        blur(box, frame, blur_rate)

    # pressed enter without pause (exception)
    elif mode == 2:
        mode = 1

    cv2.imshow("Video", frame)

    key = cv2.waitKey(1000 // fps) & 0xFF

    # calculating fps
    working_time = time.time() - start
    fps_queue.append(working_time)
    if len(fps_queue) == 6:
        time_sum = 0
        for i in range(6):
            time_sum = time_sum + fps_queue[i]
        calculated_fps = round((1 / (time_sum / 6)), 2)
        print("fps:", calculated_fps)
        fps_queue = []

    # 'spacebar' button: pause
    if key == 32:
        mode = mode * (-1)

    # 'enter' button: select image
    elif key == 13:
        if box.start_x == box.end_x or box.start_y == box.end_y:
            mode = -1

        else:
            crop_image = paused_frame.copy()[box.start_y:box.end_y, box.start_x:box.end_x]
            edge = sobel(crop_image)
            first_spot, second_spot = find_spot(edge)
            first_gap = find_gap(first_spot, box)
            second_gap = find_gap(second_spot, box)
            mode = mode + 1

    # 'esc' button: exit
    elif key == 27:
        break

capture.release()
cv2.destroyAllWindows()
