from collections.abc import Iterable
import os
import cv2
from cv2.typing import MatLike
import numpy as np
import shutil
from PIL import Image
from concurrent.futures import ThreadPoolExecutor as Pool
from pathlib import Path
from io import BytesIO
from Error import error


class ImageCode:
    def __init__(self, image: str = "null", blur: float = 0.0, size: int = 720):
        self.image: str = image
        self.data: bytes = bytes()
        self.visibility: bool = True
        self.rotation: tuple[bool, bool] = False, False
        self.selected: bool = False
        self.size: int = size
        self.blur: float = blur
        self.load_data()

    def load_data(self) -> None:
        if self.image == "null":
            return
        self.data = conversion(self, self.size)

    def name(self):
        return Path(self.image).stem

def conversion(image: ImageCode, size: int = 720) -> bytes:
    try:
        # Open the JPEG image from bytes
        img = Image.open(image.image)
        proportion = img.size[0] / img.size[1]
        img = img.resize((int(size*proportion), size))
        # Create a BytesIO object to store the PNG data
        png_buffer = BytesIO()
        # Save the image as PNG to the buffer
        img = img.save(png_buffer, format="PNG")
        # Get the PNG data from the buffer
        png_data = png_buffer.getvalue()
        return png_data
    except:
        error("Não conseguiu converter a imagem de JPG para PNG. por favor, verifique se a imagem: " + image.image + " está correta.")
        return bytes()


def rotacionar(image: ImageCode) -> ImageCode:
    img = Image.open(BytesIO(image.data))
    w, h = img.size
    correction: float = 1.0

    if w > h:
        img = img.rotate(90, expand=True)
        correction = 1.45
    else:
        img = img.rotate(-90, expand=True)
        correction = 1/1.45

    img = img.crop((0, 0, h, w))
    img = img.resize((int(h/correction), int(w/correction)))

    png_buffer = BytesIO()
    img.save(png_buffer, format="PNG")
    image.data = png_buffer.getvalue()
    return image


def normalize(image, value: float = 1.0) -> MatLike:
   total = np.average(image)
   if total < 70:
       image = cv2.multiply(image, value/total)
   return image


def mask_center(image, mask_radius_percentage=0.75, mask_value=0):
    """
    Masks the center of a grayscale image with a specified value.

    Args:
        image (numpy.ndarray): The input grayscale image (OpenCV format).
        mask_radius_percentage (float): The radius of the mask as a percentage of the smaller image dimension.
                                       Defaults to 0.25 (25%).
        mask_value (int): The grayscale value of the mask. Defaults to 0 (black).

    Returns:
        numpy.ndarray: The image with the center masked.
    """

    height, width = image.shape[:2]
    center_x, center_y = width // 2, height // 2
    radius = int(min(width, height) * mask_radius_percentage)

    mask = np.zeros_like(image)
    cv2.circle(mask, (center_x, center_y), radius, mask_value)

    masked_image = cv2.bitwise_and(image, cv2.bitwise_not(mask))
    masked_part = cv2.bitwise_and(mask, mask)
    masked_part[masked_part > 0 ] = mask_value

    masked_image = cv2.bitwise_or(masked_image, masked_part)

    return masked_image


def process_image(infile: str) -> tuple[str, float]:
    """Processes a single image to determine blurriness."""
    try:
        image = np.fromfile(infile, dtype=np.uint8)
        image = cv2.imdecode(image, cv2.IMREAD_GRAYSCALE)
        size = 720
        w, h = image.shape
        prop = w / h
        w, h = size, int(size*prop)
        image = cv2.resize(image, (w, h))

        laplacian = cv2.Laplacian(image, cv2.CV_64F)
        laplacian_masked_075 = mask_center(laplacian)
        laplacian_masked_025 = mask_center(laplacian, 0.25)
        
        blur: float = float(laplacian.var())
        blur_masked_075: float = float(laplacian_masked_075.var())
        blur_masked_025: float = float(laplacian_masked_025.var())
        return infile, blur + blur_masked_075*2.0 + blur_masked_025*1.5
    except Exception as e:
        error(f"Erro processando {infile}: {e}")
        return "null", 0.0

def Ok(path: str, dir: str):
    return Path(path).parent / dir

def file_manager(ok: Iterable[str], ok_dir: str = "ok/", tp: bool = False) -> str:
    ret: str = ""
    for image in ok:
        if image == "":
            continue
        
        path = Path(image).parent.parent / ok_dir
        ret = str(path)

        if tp is True:
            shutil.move(image, path)
        else:
            shutil.copy(image, path)
    return ret

def move_images(ok: Iterable[str], ok_dir: str = "ok/") -> str:
    return file_manager(ok, ok_dir, True)

def copy_images(ok: Iterable[str], ok_dir: str = "ok/") -> str:
    return file_manager(ok, ok_dir, False)


def get_files(path: 'Path') -> list[str]:
    if len(os.listdir(path)) == 0:
        return []

    return [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.JPG') or f.endswith('.jpg') or f.endswith('.jpeg') or f.endswith('.png') or f.endswith('.PNG')]


def find_name(path: str) -> str:
    pt_direita = path.rfind("/")
    pt_esquerda = path.rfind("\\")
    if path.rfind("\\") > path.rfind("/"):
        path = path[pt_esquerda+1:]
    else:
        path = path[pt_direita+1:]

    return path


def find_path(path: str) -> str:
    py_path = Path(path)
    return str(py_path.parent)


def createFolders(path: str = "./", ok_dir: str = "ok/") -> None:
    try:
        p = Path(path)
        res = p.parent / ok_dir
        os.makedirs(res, exist_ok=True)
    except OSError as e:
        error(f"Erro na hora de criar pastas: {e}")

def Blur(images: list[tuple[str, float]]) -> float:
    return sum([img[1] for img in images]) / len(images)

def filtrar_imagem(img: tuple[str, float], mean_blur: float) -> str:
    if img[1] >= mean_blur:
        return img[0]
    return ""

def processALL(path: 'Path', div=2, single=False, focus_threshold: float = 0) -> tuple[bool, str]:
    files = get_files(path)
    size = len(files)

    # create folders if they dont exist already
    createFolders(str(path))
    variance_results: Iterable[tuple[str, float]] = []

    if single:
        variance_results = list(map(process_image, files))
        mean_blur = Blur(variance_results)
        mean_blur += mean_blur * focus_threshold
        
        res = map(lambda x: filtrar_imagem(x, mean_blur), variance_results)

        return True, copy_images(res)
    
    # get the number of cores
    processes = os.cpu_count()

    if processes is None:
        return False, ""
    
    mean_blur: float = 0.0

    # Use a pool of worker processes
    with Pool(processes) as pool:
        variance_results = list(pool.map(process_image, files))

        if not variance_results:
            return False, ""
        
        mean_blur = Blur(variance_results)
        mean_blur += mean_blur * focus_threshold
        res = pool.map(lambda x: filtrar_imagem(x, mean_blur), variance_results)
        
        return True, move_images(res)

