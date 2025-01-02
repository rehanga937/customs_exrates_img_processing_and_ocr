import os
import subprocess
import traceback
from datetime import datetime

from src import webscrape
from src import get_table_image
from src import image_processing
from src import image_processing_stage_1
from src import image_processing_stage_2
from src import image_processing_stage_3
from src import output
from src import create_dir_structure
import config


def process_link(name,pdf_link):
        
    # download the pdf
    pdf_bytesio = webscrape.download_pdf_as_bytesio(pdf_link)

    # get the table image from PDF
    try: image_bytes,_  = get_table_image.get_table_image_from_pdfbytesio(pdf_bytesio)
    except get_table_image.TableImageException:
        print('Table image exception')
        print(f'\033[31m{name} NOK!\033[0m')
        return
    
    # convert image to OpenCV matlike. This is our base image.
    base_image = image_processing.convert_bytes_to_openCV_matlike(image_bytes)
    output.persist_debugging_images_part0(name,base_image)

    # perform 1st stage of processing, mainly to get the image of just the table - cropped and perspective transformed to compensate for scanner/photograph angle
    unwarped_base_image,image_with_all_contours,image_with_larger_contours,larger_contours_mask_image,retr_external_img,table_corners = image_processing_stage_1.process_stage_1(base_image)
    output.persist_debugging_images_part1(name,unwarped_base_image,image_with_all_contours,image_with_larger_contours,larger_contours_mask_image,retr_external_img,table_corners)

    # 2nd stage of processing - identifying the row and column gridlines from the unwarped base image
    vertical_lines,horizontal_lines,plot_for_columns,plot_for_rows,unwarped_base_image_with_larger_contours,unwarped_base_image_with_all_contours,larger_contours_of_unwarped_base_image = image_processing_stage_2.process_stage_2(unwarped_base_image)
    output.persist_debugging_images_part2(name,unwarped_base_image,vertical_lines,horizontal_lines,plot_for_columns,plot_for_rows,unwarped_base_image_with_larger_contours,unwarped_base_image_with_all_contours)

    # 3rd stage - extract and get a list of individual cell images
    cell_images, gridless_image = image_processing_stage_3.process_stage_3(horizontal_lines,vertical_lines,unwarped_base_image,larger_contours_of_unwarped_base_image)
    output.persist_debugging_images_part3(name,cell_images,gridless_image)

    csv_string = output.cell_images_to_csvstring(cell_images)
    
    os.makedirs('output', exist_ok=True)
    with open(f'output/{name}.csv', 'wt') as f:
        f.write(csv_string)

    print(f'\033[32m{name} OK!\033[0m')

def main():
    print(f'MAIN START {datetime.now()}')
    # make sure the playwright browser is installed
    subprocess.run(['playwright','install','chromium'])
    subprocess.run(['playwright','install-deps']) # precaution - if runtime environment is something like a lightweight OS we might get the error "host system is missing dependencies to run browsers"

    create_dir_structure.create_output_directories()

    # collect all links
    check_older_pages_when_webscraping = config.check_older_pages_when_webscraping
    links = webscrape.collect_links(check_older_pages_when_webscraping); links = links[0:]

    # for each link
    for name,pdf_link in links:
        print(name)
        try: process_link(name,pdf_link)   
        except:
            print(traceback.format_exc())
            print(f'\033[31m{name} NOK!\033[0m')

    print(f'MAIN END {datetime.now()}')

main()