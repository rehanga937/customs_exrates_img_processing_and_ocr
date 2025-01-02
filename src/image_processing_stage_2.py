import math
from io import BytesIO

import numpy as np
import cv2
from cv2.typing import MatLike
import matplotlib.pyplot as plt
import scipy.signal as sp_sig

from src import image_processing


def get_histogram(frequencies: list, max_axis_value: int) -> BytesIO:
    """Plots the frequencies as a histogram for visualization.

    Args:
        frequencies (list): _description_
        max_axis_value (int): something like max_x or max_y must come here

    Returns:
        BytesIO: image of the plot
    """
    x_axis = list(range(max_axis_value+1))
    plt.bar(x_axis, frequencies, color='skyblue', edgecolor='black')
    plt.xlabel('Axis')
    plt.ylabel('Frequency')
    plt.title('Histogram of Detected Contour Points (Larger)')
    plot_bytes_io = BytesIO()
    plt.savefig(plot_bytes_io, format='png')
    plt.close()
    plot_bytes_io.seek(0)
    return plot_bytes_io


def get_table_lines(frequncies: list, image_shape, vertical: bool, min_ratio_of_highest_prominence: float = 0.25) -> list:
    """Uses scipy signal library peak detection to identify peaks and their width (the width is used because the lines may not be perfectly vertical or horizontal)

    Args:
        frequncies (list): x_frequencies when searching for vertical lines, y_frequencies otherwise
        image_shape (_type_): enter the image.shape property here
        vertical (bool): Is the search for vertical lines (columns) or horizontal lines (rows)?
        min_ratio_of_highest_prominence (float, optional): _description_. Defaults to 0.25. This will determine the lower bound of prominence for a peak to be identified as a ratio of the most prominent peak.

    Returns:
        list: list of lines (each line is represented by 2 points - the starting and ending point). Lines are sorted ascending.
    """

    image_height = image_shape[0]
    image_width = image_shape[1]

    if vertical == True:
        primary_limit = image_height
        min_distance_between_peaks = int(primary_limit*(50/3000))
    else:
        primary_limit = image_width
        min_distance_between_peaks = int(primary_limit*(30/2000))

    peaks, properties = sp_sig.find_peaks(frequncies, prominence=1, distance=min_distance_between_peaks, width=1)

    peaks_with_properties = []

    for i in range(0,len(peaks)):
        peak = peaks[i]
        dictionary = {}
        dictionary['prominence'] = properties['prominences'][i]
        # dictionary['widths'] = properties['widths'][i]
        dictionary['left_ips'] = properties['left_ips'][i]
        dictionary['right_ips'] = properties['right_ips'][i]
        peaks_with_properties.append((peak,dictionary))

    peaks_with_properties.sort(key=lambda x: x[1]['prominence'], reverse=True)
    max_prominence_item = peaks_with_properties[0][1]['prominence']

    lines = []

    for peak in peaks_with_properties:
        prominence = peak[1]['prominence']
        if prominence < max_prominence_item*min_ratio_of_highest_prominence: break
        left_ips = peak[1]['left_ips']
        right_ips = peak[1]['right_ips']
        if vertical: lines.append(((round(left_ips),0),(round(right_ips),primary_limit)))
        else: lines.append(((0,round(left_ips)),(primary_limit,round(right_ips))))

    # sort the lines, and in case lines at the table edges weren't detected -  add them
    if vertical: 
        lines.sort(key=lambda x: x[0][0])
        if lines[0][0][0] > 20: lines.insert(0,((0, 0), (0, image_height)))
        if image_width - lines[-1][0][0] > 20: lines.append(((image_width, 0), (image_width, image_height)))
    else:
        lines.sort(key=lambda x: x[0][1])
        if lines[0][0][1] > 20: lines.insert(0,((0, 0), (image_width, 0)))
        if image_height - lines[-1][0][1] > 20: lines.append(((0, image_height), (image_width, image_height)))

    return lines


def process_stage_2(unwarped_base_image: MatLike) -> tuple[list, list, BytesIO, BytesIO, MatLike, MatLike]:
    """Identifies the row and column gridlines from the unwarped base image. 
    Primary expected return are the lists of these 2 sets of lines, other images of the processing stages are also returned for debugging and analysis.
    The lines are identified by getting the frequencies of the points comprising the larger contours across the vertical and horizontal axes.
    A peak detection algorithm from scipy signal library can be used to identify the location of peaks and their widths (widths bcuz lines may not be perfectly vertical/horizontal)

    Args:
        unwarped_base_image (MatLike): image containing just the table (4 corners of the table must be the corners of the image)

    Returns:
        tuple[list, list, BytesIO, BytesIO, MatLike, MatLike]: vertical_lines,horizontal_lines,plot_for_columns,plot_for_rows,unwarped_base_image_with_larger_contours,unwarped_base_image_with_all_contours
    """

    larger_contours, unwarped_base_image_with_larger_contours, unwarped_base_image_with_all_contours = image_processing.get_larger_contours_from_image(unwarped_base_image)

    # get the frequencies (x_frequencies,y_frequencies) of the larger_contours points in the x and y axes of the image
    points = set()
    max_x = 0; max_y = 0
    x_frequencies_dict = {}; y_frequencies_dict = {}

    for contour in larger_contours:
        for point in contour:
            x = point[0][0] # for some reason a 'point' is nested inside an array
            y = point[0][1]
            if (x,y) in points: continue # avoid duplicates
            points.add((x,y))
            if x not in x_frequencies_dict.keys(): x_frequencies_dict[x] = 1
            else: x_frequencies_dict[x] += 1
            if y not in y_frequencies_dict.keys(): y_frequencies_dict[y] = 1
            else: y_frequencies_dict[y] += 1
            max_x = max(max_x,x)
            max_y = max(max_y,y)

    x_frequencies = []; y_frequencies = []
    for _ in range(0,max_x+1): x_frequencies.append(0)
    for _ in range(0,max_y+1): y_frequencies.append(0)

    for value in x_frequencies_dict.keys(): x_frequencies[value] = x_frequencies_dict[value]
    for value in y_frequencies_dict.keys(): y_frequencies[value] = y_frequencies_dict[value]

    plot_for_columns = get_histogram(x_frequencies,max_x)
    plot_for_rows = get_histogram(y_frequencies,max_y)

    # now that we have the frequencies, we can use a peak detection algorithm to determine the column and row lines
    vertical_lines = []
    min_ratio_of_highest_prominence = 0.25
    while len(vertical_lines) < 7:
        vertical_lines = get_table_lines(x_frequencies,unwarped_base_image.shape,True,min_ratio_of_highest_prominence)
        min_ratio_of_highest_prominence -= 0.01
    horizontal_lines = get_table_lines(y_frequencies,unwarped_base_image.shape,False)

    # visual representation of identified row and column lines
    image_with_final_grid = unwarped_base_image.copy()
    for line in horizontal_lines:
        cv2.line(image_with_final_grid, line[0], line[1], (0,0,255), 3)
    for line in vertical_lines:
        cv2.line(image_with_final_grid, line[0], line[1], (0,0,255), 3)

    return vertical_lines,horizontal_lines,plot_for_columns,plot_for_rows,unwarped_base_image_with_larger_contours,unwarped_base_image_with_all_contours,larger_contours

