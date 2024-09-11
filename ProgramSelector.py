import tkinter as tk
import subprocess
import os

def run_ticket_analyzer():
    # Cambiar al nombre del ejecutable correspondiente
    exe_path = os.path.join(os.getcwd(), "TicketAnalyzer.exe")
    if os.path.exists(exe_path):
        subprocess.run([exe_path])
    else:
        print(f"No se encontró {exe_path}")

def run_analizador_datos():
    # Cambiar al nombre del ejecutable correspondiente
    exe_path = os.path.join(os.getcwd(), "AnalizadorDatos.exe")
    if os.path.exists(exe_path):
        subprocess.run([exe_path])
    else:
        print(f"No se encontró {exe_path}")

def run_analizador_cb():
    # Cambiar al nombre del ejecutable correspondiente
    exe_path = os.path.join(os.getcwd(), "AnalizadorCB.exe")
    if os.path.exists(exe_path):
        subprocess.run([exe_path])
    else:
        print(f"No se encontró {exe_path}")

# Crear la ventana principal
def main():
    root = tk.Tk()
    root.title("Program Selector")

    # Botones para seleccionar el programa
    btn_ticket_analyzer = tk.Button(root, text="Ticket Analyzer", command=run_ticket_analyzer)
    btn_ticket_analyzer.pack(pady=10)

    btn_analizador_datos = tk.Button(root, text="Analizador de Datos", command=run_analizador_datos)
    btn_analizador_datos.pack(pady=10)

    btn_analizador_cb = tk.Button(root, text="Analizador de Cuentas Bancarias", command=run_analizador_cb)
    btn_analizador_cb.pack(pady=10)

    # Configuración de la ventana
    root.geometry("300x200")
    root.mainloop()

if __name__ == "__main__":
    main()
