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
import imagehash
import json

def partition(lista):
    first = []
    second = []
    mapper = iter(lista)
    
    while True:
        # check for the end at the first
        try:
            first = next(mapper)
        except StopIteration:
            yield []
            break
        # check for the end at the second
        try:
            second = next(mapper)
        except StopIteration:
            yield [first]
            break

        yield [first, second]

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

def infile_order(infile: str, delim: str = "_") -> int:
    path = Path(infile).stem
    mat = delim
    if path.find(mat) == -1:
        mat = "_"
    pos = path[path.rfind(mat)+1:]
    return int(pos)

def image_order(image: 'ImageCode', delim: str = "_") -> int:
    path = Path(image.image).stem
    mat = delim
    if path.find(mat) == -1:
        mat = "_"
    pos = path[path.rfind(mat)+1:]
    return int(pos)

def category_order(name: str) -> int:
    pos = name[name.rfind(" ")+1:]
    return int(pos)

def cat_img_order(img: tuple[str, ImageCode]) -> int:
    return category_order(img[0])

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

def file_operation(image_path: str, ok_dir: str = "ok/", tp: bool = False):
    if image_path == "":
        return
    
    path = Path(image_path).parent.parent / ok_dir

    if tp is True:
        shutil.move(image_path, path)
    else:
        shutil.copy(image_path, path)

def file_manager(ok: Iterable[str], ok_dir: str = "ok/", tp: bool = False) -> str:
    first = next(ok)
    first_path = Path(first).parent.parent / ok_dir
    ret: str = str(first_path)
    try:
        if tp is True:
            shutil.move(first, first_path)
        else:
            shutil.copy(first, first_path)
    except:
        print(f"Error moving/copying {first} to {first_path}")
    with Pool() as pool:
        pool.map(file_operation, ok)
    return ret

def move_images(ok: Iterable[str], ok_dir: str = "ok/") -> str:
    os.makedirs(ok_dir, exist_ok=True)
    return file_manager(ok, ok_dir, True)

def copy_images(ok: Iterable[str], ok_dir: str = "ok/") -> str:
    os.makedirs(ok_dir, exist_ok=True)
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

def get_hash(path: str):
    img = Image.open(path)
    return imagehash.average_hash(img), path

def subtract_diff(part: list[tuple[imagehash.ImageHash, str]]):
    if len(part) > 1:
        return part[0][0] - part[1][0], [part[0][1], part[1][1]]
    elif len(part) == 1:
        return 0, [part[0][1]]
    else:
        return 0, []

def similarity_dict(path: 'Path') -> dict[str, list[str]]:
    files = sorted(get_files(path), key=infile_order)
    with Pool() as pool:
        hashes = pool.map(get_hash, files)
        parts = partition(hashes)
        dist = list(pool.map(subtract_diff, parts))
        ret: dict[str, list[str]] = dict()
        cat = 0
        placeholder = []
        average = []
        for i in range(len(dist)):
            if len(dist[i]) == 0:
                continue
            d = dist[i]
            imgs: list[str] = list(d[1])
            average.append(d[0])
            weights = np.arange(1, len(average)+1, 1)
            av = np.average(average, weights=weights)
            da = d[0] - av
            placeholder.extend(imgs)
            if da > 0:
                name = "Grupo " + str(cat+1)
                ret[name] = placeholder
                
                average = []
                placeholder = []
                cat += 1
        
        return ret

def write_similarity(path: 'Path'):
    sim = similarity_dict(path)
    with open(path / "similarity.json", "w") as f:
        json.dump(sim, f)

def processALL(path: 'Path', single=False, focus_threshold: float = 0) -> tuple[bool, str]:
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
        new_path = copy_images(res)
        write_similarity(Path(new_path))
        return True, new_path
    
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
        new_path = move_images(res)
        write_similarity(Path(new_path))
        return True, new_path

