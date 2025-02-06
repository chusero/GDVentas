from PIL import Image, ImageTk
import tkinter as tk
import time

def mostrar_logo_carga(root):
    # Crear ventana de splash
    splash = tk.Toplevel(root)
    splash.title("Cargando...")
    splash.geometry("500x300+500+300")
    splash.overrideredirect(True)  # Quitar bordes
    
    # Cargar imagen
    try:
        image = Image.open("logo_carga.png")
        image = image.resize((500, 300), Image.LANCZOS)
        logo = ImageTk.PhotoImage(image)
        
        label_logo = tk.Label(splash, image=logo, bg="white")
        label_logo.image = logo  # Mantener referencia
        label_logo.pack()
        
    except Exception as e:
        print(f"Error cargando logo: {str(e)}")
        label_texto = tk.Label(splash, text="Bienvenido al Sistema", font=("Arial", 20))
        label_texto.pack()

    # Forzar actualización de la ventana
    splash.update()
    
    # Mantener la ventana visible por 2 segundos
    time.sleep(2)
    splash.destroy()
    root.update()  # Actualizar ventana principal