import cv2
import numpy as np
from scipy.signal import argrelextrema, find_peaks


def horizontal_estimator(imagename):
    im = cv2.imread(imagename, cv2.IMREAD_GRAYSCALE)
    # cut away the first 1000 pixels
    imcut = im[:, 100:]
    sums = np.mean(imcut, axis=1)
    peaks = argrelextrema(sums, np.greater, order=10)[0]
    # peaks, _ = find_peaks(sums, distance=20, height=245)
    peaks = peaks[peaks > 600]
    return list(peaks)


def vertical_estimator(imagename):
    im = cv2.imread(imagename, cv2.IMREAD_GRAYSCALE)
    sums = np.mean(im, axis=0)
    peaks, _ = find_peaks(255 - sums, distance=50, height=50)
    peaks = list(peaks) + [im.shape[1] - 2]
    return list(peaks)
