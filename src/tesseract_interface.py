import subprocess
import cv2
from cv2.typing import MatLike
from io import BytesIO

def get_ocr_of_image(image: MatLike, psm: str = '3') -> str:
    """Takes image (in the format of opencv matlike) and returns string of recognized text

    Args:
        image (matlike): Image (in the format of opencv matlike)
        psm (str, optional): _description_. Defaults to '3' as this is the tesseract default psm.

    Returns:
        str: Recongnized text
    """
    image_bytes_io = __convert_matlike_to_bytesIO(image)
    image_bytes = image_bytes_io.read()
    # result = subprocess.run(['tesseract', 'stdin', 'stdout'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    process = subprocess.Popen(['tesseract', 'stdin', 'stdout', '--psm', psm], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    result = process.communicate(input=image_bytes)
    stdout = result[0]
    output = stdout.decode()
    return output


def __convert_matlike_to_bytesIO(image: MatLike) -> BytesIO:
    """Converts a matlike image (typically from OpenCV) to BytesIO for a png image

    Args:
        image (matlike): matlike image (typically from OpenCV)

    Returns:
        BytesIO: BytesIO representation of a png image
    """
    _,encoded_image = cv2.imencode('.png', image)
    image_bytes_io = BytesIO(encoded_image.tobytes())
    # with open('test.png', 'wb') as file:
    #     file.write(image_bytes.getvalue())
    return image_bytes_io

