import cv2

def desenhar_rosto(frame, local, proporcao=1.0):
    """
    :param frame: frame atual da camera
    :param local: coordenadas do rosto
    :param proporcao: define a escala da imagem em relação ao seu tamanho original, padrão=1
    :return:
    """

    top, right, bottom, left = local
    top, right, bottom, left = top*1, right*1, bottom*1, left*1

    cor = (204, 204, 0)

    cv2.rectangle(frame, (left, top), (right, bottom), cor, 2)
    #cv2.rectangle(frame, (left, bottom - 35), (right, bottom), cor, cv2.FILLED)
