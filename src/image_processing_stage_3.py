import math
from io import BytesIO

import numpy as np
import cv2
from cv2.typing import MatLike
import matplotlib.pyplot as plt
import scipy.signal as sp_sig

from src import image_processing

def find_intersection_points_per_row(horizontal_lines: list[tuple[tuple[int,int],tuple[int,int]]], 
                                              vertical_lines: list[tuple[tuple[int,int],tuple[int,int]]]):
    intersection_points_per_row = []
    for row in horizontal_lines:
        intersection_points_in_this_row = []
        for col in vertical_lines:
            intersection_point = line_intersection(row,col)
            intersection_points_in_this_row.append(intersection_point)
        intersection_points_per_row.append(intersection_points_in_this_row)

    return intersection_points_per_row

def line_intersection(line1, line2):
    """
    Finds the intersection point of two lines defined by their endpoints.

    Args:
        line1: A tuple of two points (x1, y1) and (x2, y2) defining the first line.
        line2: A tuple of two points (x3, y3) and (x4, y4) defining the second line.

    Returns:
        A tuple (x, y) representing the intersection point, or None if the lines are parallel or coincident.
    """
    (x1, y1), (x2, y2) = line1
    (x3, y3), (x4, y4) = line2

    # Calculate the determinants
    det = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

    if det == 0:
        # Lines are parallel or coincident
        return None

    # Calculate the intersection point
    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / det
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / det

    return int(px), int(py)


def get_cell_coordinates(horizontal_lines: list,vertical_lines: list):
    intersection_points_per_row = find_intersection_points_per_row(horizontal_lines,vertical_lines)

    cell_coords = []
    i = 0; j = 0
    while True:
        intersection_points_in_this_row = intersection_points_per_row[i]
        try: intersection_points_in_next_row = intersection_points_per_row[i+1]
        except IndexError: break
        while True:
            top_left = intersection_points_in_this_row[j]
            bottom_left = intersection_points_in_next_row[j]
            try: top_right = intersection_points_in_this_row[j+1]
            except IndexError: break
            bottom_right = intersection_points_in_next_row[j+1]
            cell_coords.append((top_left,top_right,bottom_right,bottom_left))
            j += 1
        j = 0
        i += 1

    return cell_coords


def try_to_remove_gridlines(unwarped_base_image: MatLike, unwarped_base_image_larger_contours):
    gridless_image = unwarped_base_image.copy()

    for contour in unwarped_base_image_larger_contours:
        for point in contour:
            x = point[0][0]; y = point[0][1]
            for Y in range(y-3,y+4):
                for X in range(x-3,x+4):
                    try: gridless_image[Y,X] = [255,255,255]
                    except IndexError: continue

    return gridless_image


def get_cells_by_cropping(cell_coords: list, gridless_image: MatLike):
    cell_images = []
    for coords in cell_coords:
        top_left,top_right,bottom_right,bottom_left = coords
        img = gridless_image.copy()
        cell = img[top_left[1]:bottom_left[1], top_left[0]:top_right[0]]
        cell_images.append(cell)

    return cell_images


def process_stage_3(horizontal_lines: list, vertical_lines: list, unwarped_base_image: MatLike, unwarped_base_image_larger_contours):
    cell_coords = get_cell_coordinates(horizontal_lines,vertical_lines)
    gridless_image = try_to_remove_gridlines(unwarped_base_image, unwarped_base_image_larger_contours)
    cell_images = get_cells_by_cropping(cell_coords, gridless_image)
    return cell_images, gridless_image




