import cv2
import face_recognition
import numpy as np

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

    def find_match(name_list, encode_list, img):
        """
            Encontra o rosto atual na lista de chamada
        :param name_list: lista com todos os nomes da chamada
        :param encode_list: lista das fotos dos alunos convertidas em array
        :param img: frame atual da camera
        :return: retorna o nome do aluno no frame atual
        """
        match = 'desconhecido'

        facesFrameAtt = face_recognition.face_locations(img)
        encodesFrameAtt = face_recognition.face_encodings(img, facesFrameAtt)

        for encodeFace, faceLoc in zip(encodesFrameAtt, facesFrameAtt):
            matches = face_recognition.compare_faces(encode_list, encodeFace)
            faceDis = face_recognition.face_distance(encode_list, encodeFace)
            print(faceDis)
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                match = name_list[matchIndex].upper()

            return match
