import tkinter as tk
from tkinter import messagebox
import subprocess
import mediapipe as mp

def salir():
    root.destroy()

def new_user():
    root.destroy()
    subprocess.run([pathsistema, "registro.py"])    
    #subprocess.run(["D:/0000/dlibenv/Scripts/python.exe", "registro.py"])    
    #Mostrar la ventana principal nuevamente cuando el segundo script termine
    #root.deiconify()


def login_user():
    root.destroy()
    subprocess.run([pathsistema, "login.py"])    

def centrar_ventana(root, w, h):
# Obtener el ancho y alto de la pantalla
    ancho_pantalla = root.winfo_screenwidth()
    alto_pantalla = root.winfo_screenheight()

    # Calcular la posición para centrar la ventana
    pos_x = (ancho_pantalla // 2) - (w // 2)
    pos_y = (alto_pantalla // 2) - (h // 2)

    centrado = (f"{w}x{h}+{pos_x}+{pos_y}")
    return centrado

# Crear la ventana principal
pathsistema = "/usr/bin/python3"

root = tk.Tk()
root.title("Sistema de Menú en Tkinter")
root.geometry(centrar_ventana(root, 640,400))

# Crear la barra de menús
menu_bar = tk.Menu(root)
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(command=new_user,   label="Registro")
file_menu.add_command(command=login_user, label="Entrar Al Sistema")
file_menu.add_command(command=salir, label="Salir del Sistema")

menu_bar.add_cascade(label="Archivo", menu=file_menu)
# Mostrar la barra de menús en la ventana principal
root.config(menu=menu_bar)

# Iniciar el bucle principal de la interfaz
root.mainloop()
