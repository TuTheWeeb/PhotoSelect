from Image import processALL, error, ImageCode
import FreeSimpleGUI as sg
from pathlib import Path
from Visualizar import visualizar
from collections.abc import Iterable
import os
from multiprocessing import freeze_support
freeze_support()

focus_threshold = 0
blurred_dir = 'borradas'
ok_dir = 'ok'
norm_vector = 70.0
font = ('Arial', 15)
def main_window():
    layout = [
        [sg.Text("Selecione uma pasta para visualizar ou processar:", font=font)],
        [sg.Push(), sg.Input(key="-FOLDER-"), sg.FolderBrowse(target="-FOLDER-", button_text="Selecionar pasta"), sg.Push()],
        [sg.Push(), sg.Button("Processar"), sg.Button("Visualizar Imagens"), sg.Push()]
    ]

    window = sg.Window("PhotosSelect", layout)

    ok: Iterable[tuple[str, float]] | None = None

    while True:
        blur: float = 0.0
        content = window.read()

        if content is None:
            break

        event, values = content

        # Processa as imagens
        if event == "Processar":
            folder: str = str(values["-FOLDER-"])
            if os.path.exists(folder) is False:
                error("Esta pasta não existe!")
            else:
                res, path = processALL(Path(folder))

                if res is False:
                    error("Nenhuma imagem foi processada!")
                else:
                    visualizar(path)

        elif event == "Visualizar Imagens":
            folder: str = (values["-FOLDER-"])

            if os.path.exists(folder) is False:
                error("Esta pasta não existe!")
            elif ok is None:
                visualizar(folder)

        elif event == sg.WIN_CLOSED:
            break

    window.close()


def main():
    _ = sg.theme("dark grey 9")
    main_window()


if __name__ == "__main__":
    main()
