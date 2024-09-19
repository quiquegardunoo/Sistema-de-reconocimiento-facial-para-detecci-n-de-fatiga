import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import mediapipe as mp

import os
import subprocess

UMBRAL_FOTO = 25000
nombre_usuario = None
apellidos_usuario = None
id_usuario = None

def regresar():
    cap.release()
    ventana.destroy()
    subprocess.run(["C:/proy28/proy28/Scripts/python.exe", "menu.py"])    

def detectarfatiga():
    cap.release()
    ventana.destroy()
    subprocess.run(["C:/proy28/proy28/Scripts/python.exe", "fatiga.py", nombre_usuario, apellidos_usuario, id_usuario])    

def centrar_ventana(root, w, h):
# Obtener el ancho y alto de la pantalla
    ancho_pantalla = root.winfo_screenwidth()
    alto_pantalla = root.winfo_screenheight()

    # Calcular la posición para centrar la ventana
    pos_x = (ancho_pantalla // 2) - (w // 2)
    pos_y = (alto_pantalla // 2) - (h // 2)

    centrado = (f"{w}x{h}+{pos_x}+{pos_y}")
    return centrado

def recortarFoto(frame):
    imagen = cv2.resize(frame, (200, 200))
    return imagen

def comparar_imagenes(imagen1_path):
    global nombre_usuario, apellidos_usuario, id_usuario
    print(imagen1_path)
    imagen1 = cv2.imread(imagen1_path, cv2.IMREAD_GRAYSCALE)
    imagen1 = recortarFoto(imagen1)
    cv2.imwrite(f"Imgbase/entrada.png", imagen1)
    person_list = os.listdir("Imagenes/")
    print(person_list)

    for person in person_list:
        
        imagen2 = cv2.imread(f"Imagenes/{person}",cv2.IMREAD_GRAYSCALE)    
        imagen2 = recortarFoto(imagen2)            
        cv2.imwrite(f"Imgbase/entrada2.png", imagen2)
        # Comparar las imágenes (aquí puedes usar cualquier método de comparación que prefieras)
        diferencia = cv2.absdiff(imagen1, imagen2)
        _, diferencia = cv2.threshold(diferencia, 30, 255, cv2.THRESH_BINARY)
        conteo_diferencias = cv2.countNonZero(diferencia)
        if conteo_diferencias < UMBRAL_FOTO:
            persona = person.split('_')  # Separa por comas
            print(f"Dif: {conteo_diferencias}")
            print(f"Id = {persona[0]} Nombre={persona[2]},{persona[1]}")
            nombre_usuario = persona[2]
            apellidos_usuario = persona[1]
            id_usuario = persona[0]
            return conteo_diferencias < UMBRAL_FOTO
        else:
            print("No coincide...", conteo_diferencias)
            return False
        # Si las diferencias son menores a un umbral, consideramos que las imágenes son similares
    return False
    #return False

def capturar_foto():
    ret, frame = cap.read()
    if not ret:
        print('No hay rostro')
        return
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    results = face_detection.process(frame)

    if results.detections:
        for detection in results.detections:
            # Obtener el cuadro delimitador (bounding box)
            bboxC = detection.location_data.relative_bounding_box
            ih, iw, _ = frame.shape
            x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)
        
            # Recortar la región del rostro
            face_img = frame[y:y+h, x:x+w]
            # Mostrar el rostro detectado en una ventana            
            cv2.imwrite(f"Imgbase/rostroAux.png", face_img)
            if comparar_imagenes("Imgbase/rostroAux.png"):
                messagebox.showinfo("Login correcto", "¡Bienvenido!")
                detectarfatiga()

            else:
                #messagebox.showerror("Error de login", "No se pudo verificar la identidad del usuario")
                ...
            break

        # Guardar la imagen del rostro al presionar la tecla 's'


def mostrar_frame():
    ret, frame = cap.read()
    if ret:
        # Dibujar un cuadrado en el centro de la imagen

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = face_detection.process(frame)

        if results.detections:
            for detection in results.detections:
                mp_drawing.draw_detection(frame, detection)

        # Mostrar la imagen con las detecciones
            #cv2.imshow('Reconocimiento Facial con MediaPipe', frame)

        #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        lbl_video.imgtk = imgtk
        lbl_video.configure(image=imgtk)
    lbl_video.after(10, mostrar_frame)


def mostrar_frame1():
    ret, frame = cap.read()
    if ret:

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))

        print(f"Faces={faces}")
        if len(faces) > 0:
            for (x, y, w, h) in faces:
                # Recortar el primer rostro detectado
                #cv2.putText(frame, str(len(face_data)), org=(50,50), fontFace= cv2.FONT_HERSHEY_COMPLEX, fontScale=1,color=(255,0,0), thickness=1)
                cv2.rectangle(frame,pt1=(x,y),pt2=(x+w,y+h),color=(255,255,0),thickness=2)

                break

        #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        else:
            cv2.putText(frame, "NO HAY CARA DETECTADA", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        lbl_video.imgtk = imgtk
        lbl_video.configure(image=imgtk)
    lbl_video.after(10, mostrar_frame)

global ventana
global cap

pathsistema = "C:/proy28/proy28/scripts/Python.exe"

# Inicializar MediaPipe Face Detection
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

# Configurar la detección de rostros
face_detection = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)

# Crear la ventana principal
ventana = tk.Tk()
#ventana.geometry("900x600")

ventana.title("Registro de Usuario y Captura de Foto")

ventana.geometry(centrar_ventana(ventana, 800,500))

# Crear los Frames
frame_registro = tk.Frame(ventana, padx=10, pady=10)
frame_registro.grid(row=0, column=0, padx=10, pady=10)

frame_captura = tk.Frame(ventana, padx=10, pady=10)
frame_captura.grid(row=0, column=1, padx=10, pady=10)

# Crear los widgets para el frame de captura
lbl_video = tk.Label(frame_captura)
lbl_video.grid(row=0, column=0, padx=10, pady=10)

boton_capturar = tk.Button(frame_captura, text="Validar Usuario", command=capturar_foto)
boton_capturar.grid(row=1, column=0, pady=10)

boton_regresar = tk.Button(frame_captura, text="Regresar", command=regresar)
boton_regresar.grid(row=1, column=1, pady=10)

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
