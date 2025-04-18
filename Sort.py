import FreeSimpleGUI as sg
from pathlib import Path
from Image import ImageCode
from Utils import image_order


def sort(images: list[ImageCode], font: tuple[str, int] = ('Arial', 20)) -> list[ImageCode]:
    layout = [
        [sg.Push(), sg.Text("Deseja usar um delimitador para ordenar? Caso não saiba aperte Sim sem digitar", font=font), sg.Push()],
        [sg.Text("Delimitador: ", font=font), sg.Input(key="-DELIM-"), sg.Push()],
        [sg.Push(), sg.Button("Sim"), sg.Push(), sg.Button("Não"), sg.Push()],
    ]

    window = sg.Window("PhotosSelect", layout)

    while True:
        content = window.read()

        if content is None:
            break

        event, _ = content

        if event == sg.WIN_CLOSED:
            break
        elif event == "Sim":
            delim: str = str(window["-DELIM-"])
            

            images = sorted(images, key=image_order)
            break
        elif event == "Não":
            break
    window.close()
    return images