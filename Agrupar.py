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