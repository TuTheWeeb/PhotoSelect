import FreeSimpleGUI as sg

def salvar(font: tuple[str, int] = ('Arial', 20)):
    layout = [
        [sg.Text("As imagens foram movidas com sucesso!", font=font)],
        [sg.Push(), sg.Button("Fechar"), sg.Push()]
    ]

    window = sg.Window("PhotosSelect", layout)

    while True:
        content = window.read()
        if content is None:
            break

        event, _ = content
        if event == sg.WIN_CLOSED:
            break
        elif event == "Fechar":
            break

    window.close()