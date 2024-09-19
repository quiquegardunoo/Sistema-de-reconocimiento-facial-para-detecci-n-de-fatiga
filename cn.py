#from tkinter import messagebox

import mysql.connector
from mysql.connector import Error
import mariadb

class Conexion():

    # Configuramos la clase.
    def __init__(self, host='localhost', user='root', password='', database='iaunir',):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.cn = None  

    def conectar(self):
        try:
            self.cn = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            if self.cn.is_connected():
                print(f"Conectado a la base de datos {self.database}")

        except Error as e:
            print(f"Error al conectar a la base de datos: {e}")

    def disconnect(self):
        if self.cn is not None and self.cn.is_connected():
            self.cn.close()
            print(f"Desconectado de la base de datos {self.database}")

    def execute_query(self, query):
        cursor = None
        ok = False
        try:
            cursor = self.cn.cursor()
            cursor.execute(query)
            self.cn.commit()
            print("Consulta ejecutada con éxito")
            ok = True
        except Error as e:
            print(f"Error al ejecutar la consulta: {e}")
            ok = False
        finally:
            if cursor is not None:
                cursor.close()
        return ok

    def fetch_results(self, query):
        cursor = None
        results = None
        try:
            cursor = self.cn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
        except Error as e:
            print(f"Error al recuperar los resultados: {e}")
        finally:
            if cursor is not None:
                cursor.close()
        return results

