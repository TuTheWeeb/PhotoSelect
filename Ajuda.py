import FreeSimpleGUI as sg

def ajuda(font: tuple[str, int] = ('Arial', 15)):
    layout = [
        [sg.Text(" 1. Rotação:", font=font)],
        [sg.Text("Para rotacionar a imagens aperte 'r'.", font=font)],
        [sg.Text(" 2. Movimentação:", font=font)],
        [sg.Text("Para se movimentar entre as imagens, utilize as setas do teclado.", font=font)],
        [sg.Text("Para movimentar para a proxima imagem, utilize as setas para direita e para esquerda.", font=font)],
        [sg.Text("Para movimentar para o proximo grupo, utilize as setas para cima e para baixo.", font=font)],
        [sg.Text(" 3. Seleção e Confirmação:", font=font)],
        [sg.Text("Para selecionar a imagem aberta aperte 's' e para confirmar aperte 'c'", font=font)],
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
