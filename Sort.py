"""
MIT License

Copyright (c) [2025] [TuTheWeeb]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


import FreeSimpleGUI as sg
from pathlib import Path
from Image import ImageCode


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