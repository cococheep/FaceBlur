import numpy as np
import cv2
import time


def face_detect(frame, trained_model, set_confidence=0.7):
    net = trained_model

    image = frame
    (h, w) = image.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))

    net.setInput(blob)
    detections = net.forward()

    startX = None
    startY = None
    endX = None
    endY = None
    detected_box = []

    # loop over the detections
    for i in range(0, detections.shape[2]):
        # extract the confidence associated with the prediction
        confidence = detections[0, 0, i, 2]

        # detections[0, 0, i, 1] : idx
        # detections[0, 0, i, 2] : confidence
        # detections[0, 0, i, 3:7] : box coordinate

        # filter out weak detections
        if confidence > set_confidence:
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")
            detected_box.append([startX, startY, endX, endY, i])

    # return the output
    return detected_box
