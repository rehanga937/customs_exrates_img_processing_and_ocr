import math

import numpy as np
import cv2
from cv2.typing import MatLike

from src import image_processing


def distance_between_2coords(a,b) -> float:
    a0 = a[0]; a1 = a[1]; b0 = b[0]; b1 = b[1]
    term1 = (b0 - a0)*(b0 - a0)
    term2 = (b1 - a1)*(b1 - a1)
    return math.sqrt(term1 + term2)

def __find_corners_of_table(external_contours,base_image_width,base_image_height):
    """Use the outer contour points detected to infer the 4 corners of the table"""
    top_left_min_dist = 1000000; top_right_min_dist = 1000000; bottom_left_min_dist = 1000000; bototom_right_min_dist = 1000000

    for contour in external_contours:
        for point in contour:
            x = point[0][0]
            y = point[0][1]
            dist = distance_between_2coords((x,y),(0,0))
            if dist < top_left_min_dist: 
                top_left = (x,y)
                top_left_min_dist = dist
            dist = distance_between_2coords((x,y),(base_image_width,0))
            if dist < top_right_min_dist: 
                top_right = (x,y)
                top_right_min_dist = dist
            dist = distance_between_2coords((x,y),(base_image_width,base_image_height))
            if dist < bototom_right_min_dist:  
                bottom_right = (x,y)
                bototom_right_min_dist = dist
            dist = distance_between_2coords((x,y),(0,base_image_height))
            if dist < bottom_left_min_dist:  
                bottom_left = (x,y)
                bottom_left_min_dist = dist
    
    return top_left,top_right,bottom_right,bottom_left


def process_stage_1(base_image: MatLike) -> tuple[MatLike,MatLike,MatLike,MatLike,MatLike,tuple]:
    """This takes the base image ripped from the PDF, applies a bilateral filter to it and unwarps the table to 
    correct for angle when it was scanned/photographed (perspective transform).

    The primary expected return is the unwarped_base_image - which contains the perspective transformed table.
    However 4 other MatLike objects are returned in case they are needed for debugging and analysis.
    The final return is a tuple of 4 points representing the 4 corners of the table (the points themselves are tuples of x,y format). This is also for the purpose of debugging and analysis.

    Args:
        base_image (MatLike): the base image ripped from the PDF

    Returns:
        tuple[MatLike,MatLike,MatLike,MatLike,MatLike,tuple]: unwarped_base_image,image_with_all_contours,image_with_larger_contours,larger_contours_mask_image,retr_external_img, points of the 4 table corners
    """


    base_image_height,base_image_width,base_image_channels = base_image.shape

    # Apply bilateral filter. It keeps edges sharp while removing noise. Example: https://docs.opencv.org/4.x/d4/d13/tutorial_py_filtering.html
    bfilter = cv2.bilateralFilter(base_image, 13, 20, 20)

    larger_contours, image_with_larger_contours, image_with_all_contours = image_processing.get_larger_contours_from_image(bfilter)

    # Create mask of the points comprising the larger_contours
    larger_contours_mask_image = np.zeros((base_image_height,base_image_width,3), np.uint8)
    larger_contours_mask_image = cv2.cvtColor(larger_contours_mask_image,cv2.COLOR_BGR2GRAY)
    cv2.drawContours(larger_contours_mask_image, larger_contours, -1, (255), 3)

    # Find the outer contour(s) points using the mask
    ext_contours,hierachy = cv2.findContours(larger_contours_mask_image.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    retr_external_img = base_image.copy()
    cv2.drawContours(retr_external_img, ext_contours, -1, (255), 3)

    # Use the outer contour points detected to infer the 4 corners of the table
    top_left,top_right,bottom_right,bottom_left = __find_corners_of_table(ext_contours,base_image_width,base_image_height)

    # Unwarp the base image using the identified table corners
    pts1 = np.float32([top_left,top_right,bottom_left,bottom_right])
    pts2 = np.float32([[0,0],[base_image_width,0],[0,base_image_height],[base_image_width,base_image_height]])
    M = cv2.getPerspectiveTransform(pts1,pts2)
    ## might as well apply unwarping to the bilateral-filtered base_image
    unwarped_base_image = cv2.warpPerspective(bfilter,M,(base_image_width,base_image_height))

    return unwarped_base_image,image_with_all_contours,image_with_larger_contours,larger_contours_mask_image,retr_external_img,(top_left,top_right,bottom_right,bottom_left)





