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
from Image import get_files, write_similarity
import os
from threading import Thread
from multiprocessing import Process
from time import sleep

def start_worker(window, path: 'Path'):
    thread = Thread(target=write_similarity, args=(path,), daemon=True)
    thread.start()
    thread.join()

    while True:
        if os.path.exists(path / "similarity.json"):
            window.write_event_value("file_done", None)
            break
    window.close()

def agrupar(path: 'Path', font=('Arial', 15)):
    layout = [
        [sg.Push(), sg.Text("Operação de agrupamento em andamento..."), sg.Push()]
    ]

    window = sg.Window("PhotosSelect", layout)
    
    thread = Thread(target=start_worker, args=(window, path))
    thread.start()
    try:
        while True:
            content = window.read()

            if content is None:
                break

            event, _ = content


            if event == sg.WIN_CLOSED:
                break
            elif event == "file_done":
                break

        window.close()
    except:
        return