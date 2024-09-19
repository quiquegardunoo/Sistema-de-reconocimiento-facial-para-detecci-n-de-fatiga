import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import mediapipe as mp
import pyttsx3
import os
#from pydub.generators import Sine
#import simpleaudio as sa
import numpy as np
import subprocess
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import sys

# Umbrales para la detección de ojos cerrados y boca abierta
EYE_AR_THRESH = 0.40
MOUTH_AR_THRESH = 0.50

# Puntos de referencia para los ojos y la boca
left_eye_indices = [33, 160, 158, 133, 153, 144]
right_eye_indices = [362, 385, 387, 263, 373, 380]
mouth_indices = [78, 308, 13, 14]

# Inicializar pyttsx3
engine = pyttsx3.init()

def reproducir_alerta():
    engine.say("Alerta de sueño, haz una pausa y descansa")
    engine.runAndWait()
    

def reproducir_alerta2():
    engine.say("Alerta de fatiga, haz una pausa y descansa")
    engine.runAndWait()


def centrar_ventana(root, w, h):
# Obtener el ancho y alto de la pantalla
    ancho_pantalla = root.winfo_screenwidth()
    alto_pantalla = root.winfo_screenheight()

    # Calcular la posición para centrar la ventana
    pos_x = (ancho_pantalla // 2) - (w // 2)
    pos_y = (alto_pantalla // 2) - (h // 2)

    centrado = (f"{w}x{h}+{pos_x}+{pos_y}")
    return centrado


def salir():
    cap.release()
    ventana.destroy()
    subprocess.run([pathsistema, "menu.py"])    

def alarma():
    ...
    # Generar un tono de 440 Hz (La4) con una duración de 3 segundos
    #duration = 1000  # Duración en milisegundos
    #frequency = 440  # Frecuencia en Hz

    # Crear un tono de onda sinusoidal
    #tone = Sine(frequency).to_audio_segment(duration=duration)

    # Convertir el AudioSegment a bytes
    #raw_data = tone.raw_data

    # Configurar parámetros del audio
    #num_channels = tone.channels
    #bytes_per_sample = tone.sample_width
    #sample_rate = tone.frame_rate

    # Crear un WaveObject desde los bytes
    #play_obj = sa.play_buffer(raw_data, num_channels, bytes_per_sample, sample_rate)
    #play_obj.wait_done()  # Esperar a que termine la reproducción

# Función para calcular la relación de aspecto del ojo
def eye_aspect_ratio(landmarks, eye_points):
    left = np.linalg.norm(landmarks[eye_points[1]] - landmarks[eye_points[5]])
    right = np.linalg.norm(landmarks[eye_points[2]] - landmarks[eye_points[4]])
    top = np.linalg.norm(landmarks[eye_points[0]] - landmarks[eye_points[3]])
    ear = (left + right) / (2.0 * top)
    return ear

# Función para calcular la relación de aspecto de la boca
def mouth_aspect_ratio(landmarks, mouth_points):
    horizontal = np.linalg.norm(landmarks[mouth_points[0]] - landmarks[mouth_points[1]])
    vertical = np.linalg.norm(landmarks[mouth_points[2]] - landmarks[mouth_points[3]])
    mar = vertical / horizontal
    return mar
    
# Variables para manejar el tiempo de la alarma de ojos cerrados
alarma_activa = False
alarma_activa2 = False
tiempo_inicio_alarma = 0
tiempo_inicio_alarma2 = 0
alert_count = 0
alert_count2 = 0
imagenes_capturadas = []  # Lista para almacenar las imágenes capturadas

# Función para capturar el frame actual y guardarlo en la lista de imágenes
def capturar_foto(frame, count):
    filename = f'alerta_{count}.jpg'
    cv2.imwrite(filename, frame)
    imagenes_capturadas.append(filename)

# Obtener argumentos pasados
nombre_usuario = sys.argv[1]
apellidos_usuario = sys.argv[2]
id_usuario = sys.argv[3]

print(f"Nombre Usuario: {nombre_usuario}")
print(f"Apellidos Usuario: {apellidos_usuario}")
print(f"ID Usuario: {id_usuario}")

# Configuración del correo
def enviar_correo(nombre_usuario, apellidos_usuario, id_usuario):
    from_email = "ricrd86proyectos@gmail.com"
    to_email = "ricrd86@gmail.com"
    subject = "Alerta de Sueño"
    body = f"Se ha detectado que {nombre_usuario} {apellidos_usuario} con ID: {id_usuario} ha mostrado señales de fatiga más de 3 veces. Las imágenes adjuntas corresponden a los momentos de alerta."

    # Crear el mensaje
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Adjuntar el cuerpo del mensaje
    msg.attach(MIMEText(body, 'plain'))

    # Adjuntar las fotos capturadas
    for img_path in imagenes_capturadas:
        with open(img_path, 'rb') as img:
            mime_base = MIMEBase('application', 'octet-stream')
            mime_base.set_payload(img.read())
            encoders.encode_base64(mime_base)
            mime_base.add_header('Content-Disposition', f'attachment; filename={os.path.basename(img_path)}')
            msg.attach(mime_base)

    # Configuración del servidor SMTP
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email, "epal myhk uwtu zlmv")  # Asegúrate de usar una contraseña de aplicación o habilitar aplicaciones menos seguras

    # Enviar el correo
    text = msg.as_string()
    server.sendmail(from_email, to_email, text)
    server.quit()
    print(f"Correo enviado exitosamente a {nombre_usuario} {apellidos_usuario} {id_usuario}.") 
    
    # Limpiar las imágenes después de enviar el correo
    imagenes_capturadas.clear()
   
def mostrar_frame():
    global alarma_activa, alarma_activa2, tiempo_inicio_alarma, tiempo_inicio_alarma2, alert_count, alert_count2
    ret, frame = cap.read()
    #calert = 0
    if ret:
        # Dibujar un cuadrado en el centro de la imagen

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Procesar la imagen con Face Mesh
        results = face_mesh.process(frame)
        if results.multi_face_landmarks:
    
            sonarAlarma = False
            tipo = 0
            for face_landmarks in results.multi_face_landmarks:
                # Dibujar puntos clave en la imagen
                #mp_drawing.draw_landmarks(image, face_landmarks, mp_face_mesh.FACEMESH_CONTOURS, drawing_spec, drawing_spec)

                # Obtener coordenadas de los puntos de los ojos y la boca
                landmarks = np.array([(lm.x, lm.y) for lm in face_landmarks.landmark])

                # Calcular la relación de aspecto de los ojos
                left_eye_ear = eye_aspect_ratio(landmarks, left_eye_indices)
                right_eye_ear = eye_aspect_ratio(landmarks, right_eye_indices)
                ear = round((left_eye_ear + right_eye_ear) / 2.0,2)
                # Calcular la relación de aspecto de la boca
                mar = round(mouth_aspect_ratio(landmarks, mouth_indices),2)
                print(f"Ojos={ear}, Boca={mar}")


                # Verificar si los ojos están cerrados
                if ear < EYE_AR_THRESH:
                    tipo = 1
                    alarma()
                    cv2.putText(frame, 'Ojos Cerrados{:.2f}'.format(ear), (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    
                    if not alarma_activa:
                       alarma_activa = True
                       tiempo_inicio_alarma = time.time()  # Iniciar el conteo de tiempo
                        
                    # Si la alarma está activa por más de 3 segundos
                    elif time.time() - tiempo_inicio_alarma > 3:
                        reproducir_alerta()  # Reproducir alerta de sonido
                        capturar_foto(frame, alert_count) # Capturar foto del frame actual
                        alarma_activa = False  # Resetear la alarma si los ojos están abiertos
                        alert_count += 1
                        
                    if alert_count >= 3:
                        enviar_correo(nombre_usuario, apellidos_usuario, id_usuario)
                        alert_count = 0 # Reiniciar el conteo de alertas
                     
                else:
                    alarma_activa = False  # Resetear la alarma si los ojos están abiertos
                    cv2.putText(frame, 'Ojos Abiertos{:.2f}'.format(ear), (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)


                # Verificar si la boca está abierta
                if mar > MOUTH_AR_THRESH:
                    tipo = 2
                    alarma()
                    cv2.putText(frame, 'Boca Abierta{:.2f}'.format(mar), (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    
                    if not alarma_activa2:
                       alarma_activa2 = True
                       tiempo_inicio_alarma2 = time.time()  # Iniciar el conteo de tiempo
                        
                    # Si la alarma está activa por más de 3 segundos
                    elif time.time() - tiempo_inicio_alarma2 > 5:
                        reproducir_alerta2()  # Reproducir alerta de sonido
                        capturar_foto(frame, alert_count2)  # Capturar foto del frame actual
                        alarma_activa2 = False  # Resetear la alarma si los ojos están abiertos
                        alert_count2 += 1
                        
                    if alert_count2 >= 3:
                        enviar_correo(nombre_usuario, apellidos_usuario, id_usuario)
                        alert_count2 = 0 # Reiniciar el conteo de alertas
                    
                else:
                    alarma_activa2 = False  # Resetear la alarma si los ojos están abiertos
                    cv2.putText(frame, 'Boca Cerrada{:.2f}'.format(mar), (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)


            #cv2.imshow('Detección de fatiga', frame)
            #if sonarAlarma:
            #    alarma()
            #    sonarAlarma = False
        else:
            cv2.putText(frame, "NO HAY CARA DETECTADA", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        lbl_video.imgtk = imgtk
        lbl_video.configure(image=imgtk)
    lbl_video.after(10, mostrar_frame)


global ventana
pathsistema = "C:/proy28/proy28/scripts/Python.exe"

# Inicializar MediaPipe Face Detection
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

# Configurar la detección de rostros
face_detection = mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)

# Crear la ventana principal
ventana = tk.Tk()
#ventana.geometry("900x600")

ventana.title("Deteccion")
ventana.geometry(centrar_ventana(ventana, 960,600))

# Crear los Frames
frame_registro = tk.Frame(ventana, padx=10, pady=10)
frame_registro.grid(row=0, column=0, padx=10, pady=10)

frame_captura = tk.Frame(ventana, padx=10, pady=10)
frame_captura.grid(row=0, column=1, padx=10, pady=10)

# Crear los widgets para el frame de captura
lbl_video = tk.Label(frame_captura)
lbl_video.grid(row=0, column=0, padx=10, pady=10)

boton_capturar = tk.Button(frame_captura, text="Regresar", command=salir)
boton_capturar.grid(row=1, column=0, pady=10)

# Cargar clasificadores
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades  + 'haarcascade_eye.xml')


mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Configurar la captura de video con OpenCV
#cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
# Ajustar parametros de la camara
cap.set(3,600)#(ancho,cantidad)
cap.set(4,400)#(alto,canntidad)
cap.set(10,200)#(brillo,cantidad brillo)

ImagenesPath = 'Imagenes' 

if not os.path.exists(ImagenesPath):
    os.makedirs(ImagenesPath)
    print('Carpeta Creada')

#face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


mostrar_frame()

# Ejecutar el bucle principal de Tkinter
ventana.mainloop()

# Liberar la captura de video cuando se cierra la ventana
cap.release()
cv2.destroyAllWindows()
