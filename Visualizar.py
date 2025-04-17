import FreeSimpleGUI as sg
import os
import threading
from time import sleep
from Image import ImageCode, copy_images, rotacionar
from Error import error
from Ajuda import ajuda
from Salvar import salvar
from Sort import infile_order
from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor as ThreadPool
from collections.abc import Iterable
from pathlib import Path

def partition(lista, size):
    for i in range(0 , len(lista), size):
        yield lista[i : i+size]

class ImageCollector:
    def __init__(self, path: str) -> None:
        self.path = Path(path)
        if os.path.exists(self.path):
            self.images_path = sorted([os.path.join(self.path, file) for file in os.listdir(self.path)], key=infile_order)
            self.size = len(self.images_path)
            self.part_size = self.get_cpus()
            self.parts = partition(self.images_path, self.part_size)
            self.part = []
            self.get_part()
            self.images: list[ImageCode] = []
            self.current = 0
            self.Rotation = True
            self.ended = False
            self.expand()

        else:
            error("Essa pasta não existe!")
            self.images_path = []
            self.part = []
            self.size = len(self.images_path)
    
    def get_part(self):
        try:
            self.part = next(self.parts) #sorted(next(self.parts), key=infile_order)
        except StopIteration:
            self.part = []

    def load(self, _, stop_event):
        while len(self.images) < self.size:
            if stop_event.is_set():
                error("Terminou!")
                break

            if self.ended:
                #print("Terminou!")
                return
            with Pool(self.part_size) as pool:
                new_images = pool.map(ImageCode, self.part)
                new_images = self.rotate_list(new_images)
                self.images += new_images
                self.get_part()

    def expand(self):
        if len(self.part) == 0:
            return
        
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self.load, args=(self, self.stop_event))
        self.thread.start()
            

    def get_cpus(self):
        cpus = os.cpu_count()
        if cpus is None:
            return 1
        return cpus

    def get(self, i: int = 0):
        while self.current + i >= len(self.images) and len(self.images) != self.size:
            sleep(0.1)
            pass

        if i < 0 and self.current == 0:
            error("Já está na primeira imagem")
            return self.images[self.current]
        elif self.current + i >= len(self.images):
            error("Já está na ultima imagem")
            return self.images[self.current]
        else:
            self.current += i
            return self.images[self.current]

    def next(self) -> ImageCode:
        return self.get(1)
    
    def setter(self, image: ImageCode, i: int = -1) -> int:
        if i < 0:
            i = self.current
        if i <= len(self.images) - 1:
            self.images[i] = image
            return 0
        return -1

    def rotate(self) -> int:
        img = self.images[self.current]
        img.rotation = not img.rotation[0], True
        img = rotacionar(img)
        if img is None:
            return -1
        self.setter(img)
        return 0

    def check_rotation(self, img: ImageCode):
        if img.rotation[1] is False:
            img.rotation = self.Rotation, False
            rotacionar(img)

        return img

    def rotate_list(self, imgs: list[ImageCode] | Iterable[ImageCode]):
        ret = []
        with ThreadPool(self.part_size) as pool:
            ret = pool.map(self.check_rotation, imgs)

        return list(ret)

    #def rotate_all(self):
    #    self.Rotation = not self.Rotation
    #    self.images = self.rotate_list(self.images)

    def prev(self):
        if self.current == 0:
            error("Já está na primeira imagem")
            return self.images[0]
        
        return self.get(-1)
    
    def stop(self):
        self.ended = True


def visualizar(images_path: str, font: tuple[str, int] = ('Arial', 20)) -> None:
    
    size = 816
    collections = ImageCollector(images_path)
    path = Path(collections.get().image).parent
    imgs_size: int = len(os.listdir(path))

    layout = [
        [sg.Push(), sg.Text("Para ajuda aperte 'h'", font=font), sg.Push()],
        [sg.Push(), sg.Button("<"), sg.Button("Selecionar"), sg.Button(">"), sg.Push()],
        [sg.Text("Imagem: " + str(collections.current + 1) + "/" + str(imgs_size), key="-IMAGE-NUMBER-", font=font), sg.Push(), sg.Text(collections.get().name(), key="-NAME-", font=font), sg.Text("Confirmado", key="-SELECTED-", visible=False, font=font), sg.Push()],
        [sg.Push(), sg.Image(data=collections.get().data, key="-IMAGE-"), sg.Push()],
        [sg.Button("Rotacionar"), sg.Push(), sg.Button("Mover Imagens")]
    ]

    window = sg.Window("PhotoSelect Imagens", layout, return_keyboard_events=True, use_default_focus=True)

    if window is None:
        return None

    while True:
        content = window.read()
        if content is None:
            break

        event, _ = content
        if event == sg.WIN_CLOSED:
            collections.stop()
            break
        
        elif event == "Selecionar" or event == "s:39" or event == "s":
            img = collections.get()
            img.selected = not img.selected
            collections.setter(img)
            window["-SELECTED-"].update(visible=img.selected)

        elif event == "Mover Imagens" or event == "Return:36" or event == "c":
            copy_images(collections, ok_dir="Selecionadas")
            salvar()
            break

        elif event == "Rotacionar" or event == "r:27" or event == "r":
            collections.rotate()
            window["-IMAGE-"].update(data=collections.get().data)

        elif event == "<" or event == "Left:113" or event == "Left:37":
            img: ImageCode = collections.prev()
            window["-NAME-"].update(img.name())
            window["-IMAGE-"].update(data=img.data)
            window["-SELECTED-"].update(visible=img.selected)
            window["-IMAGE-NUMBER-"].update("Imagem: " + str(collections.current + 1) + "/" + str(imgs_size))
        elif event == ">" or event == "Right:114" or event == "Right:39":
            img: ImageCode = collections.next()
            window["-NAME-"].update(img.name())
            window["-IMAGE-"].update(data=img.data)
            window["-SELECTED-"].update(visible=img.selected)
            window["-IMAGE-NUMBER-"].update("Imagem: " + str(collections.current + 1) + "/" + str(imgs_size))
        elif event == 'h:43' or event == "h":
            ajuda()

    window.close()
