import tkinter as tk
from tkinter import messagebox
from Pillow import Image, ImageTk
import cv2
#import imutils
import os
from cn import Conexion
import mediapipe as mp
import subprocess
import mariadb
import sys


def centrar_ventana(root, w, h):
# Obtener el ancho y alto de la pantalla
    ancho_pantalla = root.winfo_screenwidth()
    alto_pantalla = root.winfo_screenheight()

    # Calcular la posición para centrar la ventana
    pos_x = (ancho_pantalla // 2) - (w // 2)
    pos_y = (alto_pantalla // 2) - (h // 2)

    centrado = (f"{w}x{h}+{pos_x}+{pos_y}")
    return centrado

def regresar(DeDonde = 0):
    if DeDonde == 1:
        messagebox.showinfo("Proceso terminado", "Sus credenciales han sido creadas, regresara al menu Principal")

    cap.release()
    ventana.destroy()
    subprocess.run([pathsistema, "menu.py"])    

def registrar_usuario(Agregar = False):

    db = Conexion()
    db.conectar()

    id_usuario = entry_usuario.get()
    nombre_usuario = entry_nombre.get().strip()
    apellidos_usuario = entry_apellidos.get().strip()
    email_usuario = entry_email.get().strip()
    contrasena = entry_contrasena.get()
    confirmar_contrasena = entry_confirmar_contrasena.get()
    telefono_usuario = entry_telefono.get().strip()
    status = 1
    # Imprime los valores antes de llamar a fatiga.py
    print(f"Nombre: {nombre_usuario}, Apellidos: {apellidos_usuario}, Email: {email_usuario}")
    #subprocess.run(["C:/proy28/proy28/Scripts/python.exe", "fatiga.py", nombre_usuario, apellidos_usuario, email_usuario])
    if not id_usuario or not nombre_usuario or not apellidos_usuario or not email_usuario or not contrasena or not confirmar_contrasena or not telefono_usuario:
        messagebox.showerror("Error de registro", "Todos los campos son obligatorios")
        return False
    
    if contrasena != confirmar_contrasena:
        messagebox.showerror("Error de registro", "Las contraseñas no coinciden")
        return False
    
    #messagebox.showinfo("Registro correcto", "¡Usuario registrado exitosamente!")

    if Agregar:
        cadena = f"('{id_usuario}', '{nombre_usuario}', '{apellidos_usuario}', '{contrasena}', '{email_usuario}', '{telefono_usuario}', '{status}')"
        sql = "INSERT INTO personal (idPersonal, nombre, apellidos, password, email, telefono, status) VALUES " + cadena
        #print(sql)

        db.execute_query(sql)

        #db.execute_query("INSERT INTO personal VALUES ('cadena')")
        db.disconnect()
        
        #subprocess.run(["C:/proy28/proy28/Scripts/python.exe", "fatiga.py", nombre_usuario, apellidos_usuario, email_usuario])

    return True
    #subprocess.run([pathsistema, "fatiga.py", nombre_usuario])
    #subprocess.run([pathsistema, "fatiga.py", apellidos_usuario])
    #subprocess.run([pathsistema, "fatiga.py", email_usuario])
    # Llamada a `fatiga.py` pasando las variables
    

def capturar_foto():

    if not registrar_usuario(True):
        return

    count = 0  # Contador para las imágenes capturadas

    while True:
        ret, frame = cap.read()
        if not ret:
            print('No hay rostro')
            cv2.destroyWindow('FotoRecortada')
            break
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

                # Mostrar la cara recortada en una ventana aparte (opcional)
                cv2.imshow('FotoRecortada', face_img)
                # Guardar la imagen del rostro al presionar la tecla 's'                
                img_path = os.path.join(ImagenesPath, f'{entry_usuario.get()}_{entry_apellidos.get()}_{entry_nombre.get()}_{count}.jpg')
                try:
                    cv2.imwrite(img_path, face_img)
                except:
                    ...
                
                print(f'Imagen guardada en: {img_path}')
                
                count += 1
                print(f"Contador={count}")

                if count >20:
                    cv2.destroyWindow('FotoRecortada')
                    cap.release()
                    regresar(1)
                    break

def mostrar_frame():
    ret, frame = cap.read()
    if ret:
        # Dibujar un cuadrado en el centro de la imagen

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

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
    else:
        cv2.putText(frame, "NO HAY CARA DETECTADA", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

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
ventana.title("Registro de Usuario y Captura de Foto")
ventana.geometry(centrar_ventana(ventana, 1100,500))

# Crear los Frames
frame_registro = tk.Frame(ventana, padx=10, pady=10)
frame_registro.grid(row=0, column=0, padx=10, pady=10)

frame_captura = tk.Frame(ventana, padx=10, pady=10)
frame_captura.grid(row=0, column=1, padx=10, pady=10)

# Crear los widgets para el frame de registro
label_usuario = tk.Label(frame_registro, text="Id de usuario:")
label_usuario.grid(row=0, column=0, pady=5)

entry_usuario = tk.Entry(frame_registro)
entry_usuario.grid(row=0, column=1, pady=5)

label_nombre = tk.Label(frame_registro, text="Nombre de usuario:")
label_nombre.grid(row=1, column=0, pady=5)

entry_nombre = tk.Entry(frame_registro)
entry_nombre.grid(row=1, column=1, pady=5)

label_apellidos = tk.Label(frame_registro, text="Apellidos de usuario:")
label_apellidos.grid(row=2, column=0, pady=5)

entry_apellidos = tk.Entry(frame_registro)
entry_apellidos.grid(row=2, column=1, pady=5)

label_email = tk.Label(frame_registro, text="Email:")
label_email.grid(row=3, column=0, pady=5)

entry_email = tk.Entry(frame_registro)
entry_email.grid(row=3, column=1, pady=5)

label_contrasena = tk.Label(frame_registro, text="Contraseña:")
label_contrasena.grid(row=4, column=0, pady=5)

entry_contrasena = tk.Entry(frame_registro, show="*")
entry_contrasena.grid(row=4, column=1, pady=5)

label_confirmar_contrasena = tk.Label(frame_registro, text="Confirmar contraseña:")
label_confirmar_contrasena.grid(row=5, column=0, pady=5)

entry_confirmar_contrasena = tk.Entry(frame_registro, show="*")
entry_confirmar_contrasena.grid(row=5, column=1, pady=5)

label_telefono = tk.Label(frame_registro, text="Telefono:")
label_telefono.grid(row=6, column=0, pady=5)

entry_telefono = tk.Entry(frame_registro)
entry_telefono.grid(row=6, column=1, pady=5)

# Crear los widgets para el frame de captura
lbl_video = tk.Label(frame_captura)
lbl_video.grid(row=0, column=0, padx=10, pady=10)

boton_capturar = tk.Button(frame_captura, text="Registrar Usuario", command=capturar_foto)
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

ImagenesBase =  'Imgbase' 
if not os.path.exists(ImagenesBase):
    os.makedirs(ImagenesBase)
    print('Carpeta Creada')

#face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


mostrar_frame()

# Ejecutar el bucle principal de Tkinter
ventana.mainloop()

# Liberar la captura de video cuando se cierra la ventana
cap.release()
cv2.destroyAllWindows()
