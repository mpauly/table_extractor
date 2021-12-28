import cv2
import numpy as np


def filter_contours(contours, shape):
    MINSIZE = 12
    filtered_contours = []
    pre_filtered = []
    x_coords = []
    y_coords = []

    for con in contours:
        # does the shape touch the boundary?
        rect = cv2.boundingRect(con)
        if (
            rect[0] == 0
            or rect[1] == 0
            or rect[2] == shape[1]
            or rect[1] + rect[3] == shape[0]
        ):
            continue
        x_coords.append(rect[0] + 0.5 * rect[2])
        y_coords.append(rect[1] + 0.5 * rect[3])
        pre_filtered.append(con)

    median_y = np.median(np.array(y_coords))

    for i, con in enumerate(pre_filtered):
        rect = cv2.boundingRect(con)

        # is the shape strongly displaced along the y axis
        if np.abs(rect[1] + 0.5 * rect[3] - median_y) > 10:
            continue
        # is the shape too small
        if rect[2] < MINSIZE and rect[3] < MINSIZE:
            continue

        filtered_contours.append(con)
    return filtered_contours
