import os

def create_output_directories():
    """Makes the folder structures for the program output if not already created.
    """
    os.makedirs('output', exist_ok=True)
    os.makedirs('images_for_debugging_and_analysis', exist_ok=True)
    os.makedirs(os.path.join('images_for_debugging_and_analysis','1_base_image'), exist_ok=True)
    os.makedirs(os.path.join('images_for_debugging_and_analysis','2_image_with_all_contours'), exist_ok=True)
    os.makedirs(os.path.join('images_for_debugging_and_analysis','3_image_with_larger_contours'), exist_ok=True)
    os.makedirs(os.path.join('images_for_debugging_and_analysis','4_larger_contours_mask_image'), exist_ok=True)
    os.makedirs(os.path.join('images_for_debugging_and_analysis','5_retr_external_img'), exist_ok=True)
    os.makedirs(os.path.join('images_for_debugging_and_analysis','6_table_corner_image'), exist_ok=True)
    os.makedirs(os.path.join('images_for_debugging_and_analysis','7_unwarped_base_image'), exist_ok=True)
    os.makedirs(os.path.join('images_for_debugging_and_analysis','8_unwarped_base_image_with_all_contours'), exist_ok=True)
    os.makedirs(os.path.join('images_for_debugging_and_analysis','9_unwarped_base_image_with_larger_contours'), exist_ok=True)
    os.makedirs(os.path.join('images_for_debugging_and_analysis','10_plot_for_rows'), exist_ok=True)
    os.makedirs(os.path.join('images_for_debugging_and_analysis','11_plot_for_columns'), exist_ok=True)
    os.makedirs(os.path.join('images_for_debugging_and_analysis','12_image_with_final_grid'), exist_ok=True)
    os.makedirs(os.path.join('images_for_debugging_and_analysis','13_gridless_image'), exist_ok=True)
    os.makedirs(os.path.join('images_for_debugging_and_analysis','14_cells'), exist_ok=True)


def write_debug_images():
    pass


    