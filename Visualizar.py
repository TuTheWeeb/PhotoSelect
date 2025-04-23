from math import inf
import FreeSimpleGUI as sg
import os
import threading
from time import sleep
from Image import ImageCode, copy_images, rotacionar, category_order, cat_img_order
from Error import error
from Ajuda import ajuda
from Salvar import salvar
from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor as ThreadPool
from collections.abc import Iterable
from pathlib import Path
import json


class ImageCollector:
    def __init__(self, path: str) -> None:
        self.path = Path(path)
        if os.path.exists(self.path) and os.path.exists(self.path / "similarity.json"):
            with open(self.path / "similarity.json", "r") as f:
                self.categories = json.load(f)
            self.categories_name = sorted(self.categories.keys(), key=category_order)
            self.size = self.get_size()
            self.images: list[tuple[str, ImageCode]] = []
            self.Rotation = False
            self.ended = False
            self.parts = self.get_parts()
            self.current = 0
            self.Rotation = True
            self.update = False
            self.expand()
        else:
            error("Essa pasta não existe!")
            self.images_path = []
            self.part = ("null", ["null"])
            self.size = len(self.images_path)

    def get_size(self):
        ret: int = 0
        for i in self.categories:
            ret += len(self.categories[i])
        return ret

    def open_thread(self, category: tuple[str, list[str]]):
        imgs = category[1]
        cat = category[0]
        with ThreadPool() as pool:
            res = pool.map(ImageCode, imgs)
            res = self.rotate_list(res)
            self.images += [(cat, img) for img in res]
            self.images.sort(key=cat_img_order)
            self.update = True

    def open(self, category: tuple[str, list[str]]):
        imgs = category[1]
        cat = category[0]
    
        with ThreadPool() as pool:
            res = list(pool.map(ImageCode, imgs))
            res = self.rotate_list(res)
            self.images += [(cat, img) for img in res]
            self.images.sort(key=cat_img_order)


    def load_thread(self, _, stop_event):
        while len(self.images) < self.size:
            if stop_event.is_set():
                error("Terminou!")
                break
            
            if self.ended:
                return
            with ThreadPool() as pool:
                pool.map(self.open_thread, self.parts)
                self.stop()
                break

    def load(self):
        while len(self.images) < self.size:
            with ThreadPool() as pool:
                pool.map(self.open, self.parts)

    def expand(self):
        #self.load()
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self.load_thread, args=(self, self.stop_event))
        self.thread.start()
            

    def get_cpus(self):
        cpus = os.cpu_count()
        if cpus is None:
            return 1
        return cpus
    
    
    def get_parts(self):
        ret = []
        for i in self.categories:
            ret.append((i, self.categories[i]))
        return ret

    def get(self, i: int = 0):
        while len(self.images) == 0:
            sleep(0.005)
        
        self.current += i
        actual_size = len(self.images)
        
        if self.current < 0:
            error("Já está na primeira imagem")
            self.current = 0
            return self.images[0]

        elif self.current >= self.size:
            error("Já está na ultima imagem")
            self.current = self.size - 1
            return self.images[self.current]

        elif self.current >= actual_size:
            self.current = actual_size - 1
            return self.images[self.current]

        else:
            return self.images[self.current]

    def next(self) -> tuple[str, ImageCode]:
        return self.get(1)
    
    def check_cat(self):
        cat, img = self.get()
        cat1, img1 = self.get(1)
        return cat == cat1

    def reverse_check_cat(self):
        cat, img = self.get()
        cat1, img1 = self.get(-1)
        return cat == cat1

    def next_cat(self) -> tuple[str, ImageCode]:
        actual = self.get()
        while self.current < len(self.images) - 1:
            temp = self.get(1)
            if actual[0] != temp[0]:
                return temp
            
        return self.get()
    
    def prev_cat(self):
        actual = self.get()
        while self.current > 0:
            temp = self.get(-1)
            if actual[0] != temp[0]:
                return temp

        return actual
    
    def setter(self, image: tuple[str, ImageCode], i: int = -1) -> int:
        if i < 0:
            i = self.current
        if i <= len(self.images) - 1:
            self.images[i] = image
            return 0
        return -1

    def rotate(self) -> int:
        cat ,img = self.images[self.current]
        img.rotation = not img.rotation[0], True
        img = rotacionar(img)
        if img is None:
            return -1
        self.setter((cat, img))
        return 0

    def check_rotation(self, img: ImageCode):
        if img.rotation[1] is False:
            img.rotation = self.Rotation, False
            rotacionar(img)
        return img
    
    def rotate_list(self, imgs: Iterable[ImageCode]):
        ret = []
        with ThreadPool() as pool:
            ret = pool.map(self.check_rotation, imgs)
        return ret

    def prev(self):
        if self.current == 0:
            error("Já está na primeira imagem")
            return self.images[0]
        
        return self.get(-1)
    
    def get_selected(self):
        with ThreadPool() as pool:
            return pool.map(lambda x: x[1].image if x[1].selected else "", self.images)
        return [""]
    
    def stop(self):
        self.ended = True


def visualizar(images_path: str, font: tuple[str, int] = ('Arial', 15)) -> None:

    collections = ImageCollector(images_path)

    layout = [
        [sg.Push(), sg.Text("Para ajuda aperte 'h'", font=font), sg.Push()],
        [sg.Push(), sg.Button("<"), sg.Button("Selecionar"), sg.Button(">"), sg.Push()],
        [sg.Push(), sg.Text(collections.get()[1].name(), key="-NAME-", font=font), sg.Text(collections.get()[0], key="-CATEGORY-", font=font), sg.Push()],
        [sg.Text("Imagem: " + str(collections.current + 1) + "/" + str(collections.size), key="-IMAGE-NUMBER-", font=font), sg.Push(), sg.Text("Confirmado", key="-SELECTED-", visible=False, font=font)],
        [sg.Push(), sg.Image(data=collections.get()[1].data, key="-IMAGE-"), sg.Push()],
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

        if event == "Selecionar" or event == "s:39" or event == "s":
            cat, img = collections.get()
            img.selected = not img.selected
            collections.setter((cat, img))
            window["-SELECTED-"].update(visible=img.selected)

        elif event == "Mover Imagens" or event == "Return:36" or event == "c":
            copy_images(collections.get_selected(), ok_dir="Selecionadas/")
            salvar()
            break

        elif event == "Rotacionar" or event == "r:27" or event == "r":
            collections.rotate()
            window["-IMAGE-"].update(data=collections.get()[1].data)

        elif event == "Up:38" or event == "Up:111":
            cat, img = collections.next_cat()
            window["-NAME-"].update(img.name())
            window["-CATEGORY-"].update(cat)
            window["-IMAGE-"].update(data=img.data)
            window["-SELECTED-"].update(visible=img.selected)
            window["-IMAGE-NUMBER-"].update("Imagem: " + str(collections.current + 1) + "/" + str(collections.size))

        elif event == "Down:40" or event == "Down:116":
            cat, img = collections.prev_cat()
            window["-NAME-"].update(img.name())
            window["-CATEGORY-"].update(cat)
            window["-IMAGE-"].update(data=img.data)
            window["-SELECTED-"].update(visible=img.selected)
            window["-IMAGE-NUMBER-"].update("Imagem: " + str(collections.current + 1) + "/" + str(collections.size))

        elif event == "<" or event == "Left:113" or event == "Left:37":
            cat, img = collections.prev()
            window["-NAME-"].update(img.name())
            window["-CATEGORY-"].update(cat)
            window["-IMAGE-"].update(data=img.data)
            window["-SELECTED-"].update(visible=img.selected)
            window["-IMAGE-NUMBER-"].update("Imagem: " + str(collections.current + 1) + "/" + str(collections.size))
        elif event == ">" or event == "Right:114" or event == "Right:39":
            cat, img = collections.next()
            window["-NAME-"].update(img.name())
            window["-CATEGORY-"].update(cat)
            window["-IMAGE-"].update(data=img.data)
            window["-SELECTED-"].update(visible=img.selected)
            window["-IMAGE-NUMBER-"].update("Imagem: " + str(collections.current + 1) + "/" + str(collections.size))
        elif event == 'h:43' or event == "h":
            ajuda()

    window.close()
