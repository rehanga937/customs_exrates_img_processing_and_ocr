from io import BytesIO
from PIL import Image

import fitz # this is pymupdf


class TableImageException(Exception):
    """Raised if PDF has no pages or the page has no or more than 1 image, so we can't extract the table image.

    Args:
        Can pass in a string message.
    """
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

def get_table_image_from_pdfbytesio(pdf_bytesio: BytesIO) -> tuple[bytes,str]:
    """Gets image of the table from the PDF.
    Image is expected to be in page 1 of 1-paged PDFs and page 2 of other PDFs.
    If more than one image is found, largest image is returned (sometimes you may get 2nd images like the camscanner logo).
    Image orientation is corrected if necessary.

    Args:
        pdf_bytesio (io.BytesIO): PDF as BytesIO

    Raises:
        TableImageException: If found no or more than one image in the target page.

    Returns:
        tuple[bytes,str]: tuple of bytes representing the image, and its extension without the dot(eg: jpeg, not .jpeg)
    """

    fitz_file = fitz.open("pdf", pdf_bytesio)

    if fitz_file.page_count >= 2:
        interested_page_index = 1
    elif fitz_file.page_count == 1:
        interested_page_index = 0
    else:
        raise TableImageException('PDF file has no pages!')
    page = fitz_file.load_page(interested_page_index) 
    image_list = page.get_images(full=True) 
    if len(image_list) == 0: raise TableImageException('Found no image in PDF target page.')

    largest_image_size = 0
    for image in image_list:
        
        image_ref = image[0] # XREF
        image_name_thingy = image[7]

        # image orientation documentation:
        # https://pymupdf.readthedocs.io/en/latest/app3.html#image-transformation-matrix
        # https://pymupdf.readthedocs.io/en/latest/matrix.html
        bbox, transform = page.get_image_bbox(image_name_thingy, transform=True)
        angle_correction = getAngleTheOriginalImageHasBeenRotatedToDisplayCorrectly(transform)      
        base_image = fitz_file.extract_image(image_ref)
        image_size = base_image["height"] * base_image["width"]
        if image_size > largest_image_size:
            largest_image_size = image_size
            image_bytes: bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_bytes = rotate_bytes_image(image_bytes, float(-angle_correction), image_ext)

    return (image_bytes,image_ext)


def getAngleTheOriginalImageHasBeenRotatedToDisplayCorrectly(transform: fitz.Matrix):
    a = transform.a; b = transform.b; c = transform.c; d = transform.d
    if a > 0: return 0
    if a < 0: return 180
    if b < 0: return -90
    return 90

def rotate_bytes_image(image: bytes, angle_deg: float, image_ext: str) -> bytes:
    img = Image.open(BytesIO(image))
    rotated_image = img.rotate(angle_deg, expand=True)
    result = BytesIO()
    rotated_image.save(result,format=image_ext)
    return result.getvalue()
