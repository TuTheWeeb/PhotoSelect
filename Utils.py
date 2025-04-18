from pathlib import Path
from Image import ImageCode

def infile_order(infile: str, delim: str = "_") -> int:
    path = Path(infile).stem
    mat = delim
    if path.find(mat) == -1:
        mat = "_"
    pos = path[path.rfind(mat)+1:]
    return int(pos)

def image_order(image: ImageCode, delim: str = "_") -> int:
    path = Path(image.image).stem
    mat = delim
    if path.find(mat) == -1:
        mat = "_"
    pos = path[path.rfind(mat)+1:]
    return int(pos)

def partition(lista, size):
    for i in range(0 , len(lista), size):
        yield lista[i : i+size]