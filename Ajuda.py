import FreeSimpleGUI as sg

def ajuda(font: tuple[str, int] = ('Arial', 20)):
    layout = [
        [sg.Text(" 1. Rotação:", font=font)],
        [sg.Text("Para rotacionar as imagens aperte 'r' para rotacionar somente a que está aberta ou 'R' para rotacionar todas as imagens menos as que já foram rotacionadas.", font=font)],
        [sg.Text(" 2. Movimentação:", font=font)],
        [sg.Text("Para se movimentar entre as imagens, utilize as setas do teclado.", font=font)],
        [sg.Text(" 3. Seleção e Confirmação:", font=font)],
        [sg.Text("Para selecionar a imagem aberta aperte 's' e para confirmar aperte 'Enter'", font=font)],
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
