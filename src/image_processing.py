import math

import numpy as np
import cv2
from cv2.typing import MatLike


def get_larger_contours_from_image(image: MatLike) -> tuple[list,MatLike,MatLike]:
    """Returns just the contours with larger area from the image that is passed in.
    2 additional MatLikes are returned for debugging and analysis.
    Hopefully the larger contours only represent the cells and table structures, not words/letters.

    Args:
        image (MatLike): _description_

    Returns:
        tuple[list,MatLike,MatLike]: larger_contours, image_with_larger_contours, image_with_all_contours
    """


    image_height,image_width,image_channels = image.shape
    image_area = image_height * image_width

    # apply canny edge detection and get all contour points
    edged = cv2.Canny(image, 30, 180)
    all_contours,hierachy = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    image_with_all_contours = image.copy()
    cv2.drawContours(image_with_all_contours, all_contours, -1, (0,0,255), 3)

    # get the larger contours only
    # (hopefully those representing cells, and not words/letters)
    all_contours_sorted = sorted(all_contours, key=cv2.contourArea, reverse=True)
    larger_contours = []
    for contour in all_contours_sorted:
        x,y,w,h = cv2.boundingRect(contour)
        area_of_boundingRect = w*h
        if area_of_boundingRect/image_area < 0.00086: break
        larger_contours.append(contour)
    image_with_larger_contours = image.copy()
    cv2.drawContours(image_with_larger_contours, larger_contours, -1, (0,0,255), 3)

    return larger_contours, image_with_larger_contours, image_with_all_contours

def convert_bytes_to_openCV_matlike(bytes: bytes) -> MatLike:
    """Converts the bytes of an image read from somwhere (like a stream or the file system)
    into a matlike object that OpenCV likes.

    Args:
        bytes (bytes): bytes of an image that is read from the file system or similar

    Returns:
        matlike: matlike image
    """
    numpy_array = np.fromstring(bytes, np.uint8)
    img = cv2.imdecode(numpy_array, cv2.IMREAD_COLOR)
    return img
