from AntiSpoofing.test import test
import cv2
import utils

cam = cv2.VideoCapture(0)
count = 0
nomeAtt = ''
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
# lista de todos os rostos que a camera detectar dentro do loop
rostos = []

while True:

    _, img = cam.read()
    # inverte a camera
    img = cv2.flip(img, 1)

    # diminui a imagem para 1/4 do tamanho pra agilizar o processo
    imgS = img

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    # Desenha o retangulo no rosto
    for (x, y, w, h) in faces:

        if test(imgS, 'AntiSpoofing/resources/anti_spoof_models', 0) == 1:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        else:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)


    cv2.imshow('Webcam', img)
    cv2.waitKey(1)

