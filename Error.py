import FreeSimpleGUI as sg

def error(msg: str, font=('Arial', 18)):
    layout = [
        [sg.Text(msg)],
        [sg.Push(), sg.Button("Fechar"), sg.Push()]
    ]

    window = sg.Window("Erro", layout)
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
