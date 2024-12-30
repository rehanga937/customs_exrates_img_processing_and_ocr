from io import BytesIO
import src.tesseract_interface as tesseract_interface
import cv2
from cv2.typing import MatLike
from src import image_processing_stage_1
import re
import io
import config


def cell_images_to_csvstring(cell_images: list[MatLike]) -> str:
    """Performs the OCR process on the list of cell images, and collects the detected text into a csv string.

    Args:
        cell_images (list[MatLike]): list of cell images (in order of the table)

    Returns:
        str: csv string of the table represented by the list of cell images
    """

    # separate the cell images by column heading
    country = []
    country_code = []
    currency = []
    currency_code = []
    er = []

    col_counter = -1
    for cell_image in cell_images:
        col_counter += 1
        if col_counter == 0: 
            continue
        if col_counter == 1:
            country.append(cell_image)
        if col_counter == 2:
            country_code.append(cell_image)
        if col_counter == 3:
            currency.append(cell_image)
        if col_counter == 4:
            currency_code.append(cell_image)
        if col_counter == 5:
            er.append(cell_image)
            col_counter = -1

    # lists for holding the ocr results
    country_ocr = []
    country_code_ocr = []
    currency_ocr = []
    currency_code_ocr = []
    er_ocr = []

    # for each type of cell (belonging to a certain column), apply OCR and column-specific regex
    for cell in country:
        string = tesseract_interface.get_ocr_of_image(cell, '7')
        string = string.strip()
        string = re.sub('^[^a-zA-Z0-9.()]+|[^a-zA-Z0-9.()]+$', '', string) # OCR is likely to falsely detect special characters at the start and end of text
        string = string.strip()
        string = string.replace(',','') # commas anywhere in the text must be removed because we are using .csv
        country_ocr.append(string)

    for cell in er:
        string = tesseract_interface.get_ocr_of_image(cell, '7')
        string = string.strip()
        string = re.sub('^[^0-9]+|[^0-9]+$', '', string) # OCR is likely to falsely detect special characters at the start and end of text
        string = string.replace(' ', '') # exchange rates don't have spaces
        string = string.strip()     
        string = string.replace(',','') # commas anywhere in the text must be removed because we are using .csv
        er_ocr.append(string)

    for cell in currency_code:
        string = tesseract_interface.get_ocr_of_image(cell, '7')
        string = string.strip()
        string = re.sub('^[^A-Z]+|[^A-Z]+$', '', string) # OCR is likely to falsely detect special characters at the start and end of text
        string = string.strip()
        string = string.replace(',','') # commas anywhere in the text must be removed because we are using .csv
        currency_code_ocr.append(string)

    for cell in country_code:
        string = tesseract_interface.get_ocr_of_image(cell, '7')
        string = string.strip()
        string = re.sub('^[^A-Z]+|[^A-Z]+$', '', string) # OCR is likely to falsely detect special characters at the start and end of text
        string = string.strip()
        string = string.replace(',','') # commas anywhere in the text must be removed because we are using .csv
        country_code_ocr.append(string)

    for cell in currency:
        string = tesseract_interface.get_ocr_of_image(cell, '7')
        string = string.strip()
        string = re.sub('^[^a-zA-Z0-9.()]+|[^a-zA-Z0-9.()]+$', '', string) # OCR is likely to falsely detect special characters at the start and end of text
        string = string.strip()
        string = string.replace(',','') # commas anywhere in the text must be removed because we are using .csv
        currency_ocr.append(string)

    # collect all into a csv string
    csv_string = ''
    for i in range(0,len(country_ocr)):
        csv_string += f'{country_ocr[i]},{country_code_ocr[i]},{currency_ocr[i]},{currency_code_ocr[i]},{er_ocr[i]}\n'

    return csv_string

def persist_debugging_images_part0(name: str, base_image: MatLike):
    cv2.imwrite(f'images_for_debugging_and_analysis/1_base_image/{name}.png',base_image)

def persist_debugging_images_part1(name: str, unwarped_base_image: MatLike,image_with_all_contours: MatLike,
                                   image_with_larger_contours: MatLike,larger_contours_mask_image: MatLike,
                                   retr_external_img: MatLike,table_corners: tuple):
    cv2.imwrite(f'images_for_debugging_and_analysis/2_unwarped_base_image/{name}.png',unwarped_base_image)
    cv2.imwrite(f'images_for_debugging_and_analysis/3_image_with_all_contours/{name}.png',image_with_all_contours)
    cv2.imwrite(f'images_for_debugging_and_analysis/4_image_with_larger_contours/{name}.png',image_with_larger_contours)
    cv2.imwrite(f'images_for_debugging_and_analysis/5_larger_contours_mask_image/{name}.png',larger_contours_mask_image)
    cv2.imwrite(f'images_for_debugging_and_analysis/6_retr_external_img/{name}.png',retr_external_img)

    top_left,top_right,bottom_right,bottom_left = table_corners

    table_corner_image = unwarped_base_image.copy()
    cv2.circle(table_corner_image,top_left,5,(0,0,255),-1)
    cv2.circle(table_corner_image,top_right,5,(0,0,255),-1)
    cv2.circle(table_corner_image,bottom_right,5,(0,0,255),-1)
    cv2.circle(table_corner_image,bottom_left,5,(0,0,255),-1)
    cv2.imwrite(f'images_for_debugging_and_analysis/7_table_corner_image/{name}.png',table_corner_image)


def persist_debugging_images_part2(name: str, unwarped_base_image: MatLike,vertical_lines: list,horizontal_lines: list,
                                   plot_for_columns: BytesIO,plot_for_rows: BytesIO,
                                   unwarped_base_image_with_larger_contours: MatLike,unwarped_base_image_with_all_contours: MatLike):
    cv2.imwrite(f'images_for_debugging_and_analysis/8_unwarped_base_image_with_all_contours/{name}.png',unwarped_base_image_with_all_contours)
    cv2.imwrite(f'images_for_debugging_and_analysis/9_unwarped_base_image_with_larger_contours/{name}.png',unwarped_base_image_with_larger_contours)

    with open(f'images_for_debugging_and_analysis/10_plot_for_rows/{name}.png','wb') as f: f.write(plot_for_rows.getvalue())
    with open(f'images_for_debugging_and_analysis/11_plot_for_columns/{name}.png','wb') as f: f.write(plot_for_columns.getvalue()) 

    image_with_final_grid = unwarped_base_image.copy()
    for line in horizontal_lines:
        cv2.line(image_with_final_grid, line[0], line[1], (0,0,255), 3)
    for line in vertical_lines:
        cv2.line(image_with_final_grid, line[0], line[1], (0,0,255), 3)

    cv2.imwrite(f'images_for_debugging_and_analysis/12_image_with_final_grid/{name}.png',image_with_final_grid)

def persist_debugging_images_part3(name: str, cell_images: list[MatLike], gridless_image: MatLike):
    cv2.imwrite(f'images_for_debugging_and_analysis/13_gridless_image/{name}.png',gridless_image)
    for i,cell_image in enumerate(cell_images):
        cv2.imwrite(f'images_for_debugging_and_analysis/13_gridless_image/{name}/{i}.png',cell_image)
