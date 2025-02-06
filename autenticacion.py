import tkinter as tk
from tkinter import messagebox
import json
import os
import hashlib

RUTA_USUARIOS = os.path.join(os.path.dirname(__file__), "usuarios.json")

class Autenticacion:
    def __init__(self, root):
        self.root = root
        self.login_window = None
        self.usuario_actual = None  # Nuevo atributo para almacenar el usuario
        self.crear_ventana_login()
        
    def crear_ventana_login(self):
        self.login_window = tk.Toplevel(self.root)
        self.login_window.title("Inicio de Sesión")
        self.login_window.grab_set()
        
        tk.Label(self.login_window, text="Usuario:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_usuario = tk.Entry(self.login_window)
        self.entry_usuario.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(self.login_window, text="Contraseña:").grid(row=1, column=0, padx=5, pady=5)
        self.entry_password = tk.Entry(self.login_window, show="*")
        self.entry_password.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Button(self.login_window, 
                text="Ingresar", 
                command=lambda: self.verificar_credenciales()  # <--- ¡Aquí está el fix!
                ).grid(row=2, columnspan=2, pady=10)

    def verificar_credenciales(self):
        usuarios = self.cargar_usuarios()
        username = self.entry_usuario.get()
        password = hashlib.sha256(self.entry_password.get().encode()).hexdigest()
        
        if username in usuarios and usuarios[username]["password"] == password:
            self.usuario_actual = {  # Asignar el usuario actual
                "username": username,
                "rol": usuarios[username]["rol"]
            }
            self.login_window.destroy()  # Cerrar la ventana de login
        else:
            messagebox.showerror("Error", "Credenciales incorrectas")

    @staticmethod
    def cargar_usuarios():
        try:
            if not os.path.exists(RUTA_USUARIOS) or os.path.getsize(RUTA_USUARIOS) == 0:
                usuarios = {
                    "admin": {
                        "password": hashlib.sha256("admin".encode()).hexdigest(),
                        "rol": "admin"
                    }
                }
                Autenticacion.guardar_usuarios(usuarios)
                return usuarios
                
            with open(RUTA_USUARIOS, "r") as f:
                return json.load(f)
                
        except json.JSONDecodeError:
            messagebox.showwarning("Error", "Archivo corrupto. Se creará uno nuevo.")
            usuarios = {
                "admin": {
                    "password": hashlib.sha256("admin".encode()).hexdigest(),
                    "rol": "admin"
                }
            }
            Autenticacion.guardar_usuarios(usuarios)
            return usuarios

    @staticmethod
    def guardar_usuarios(usuarios):
        with open(RUTA_USUARIOS, "w") as f:
            json.dump(usuarios, f, indent=4)