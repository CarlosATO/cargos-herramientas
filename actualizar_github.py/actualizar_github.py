import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import sys

# --- Configuración ---
REPO_PATH = r"C:\Users\carlo\OneDrive - SOMYL S.A\CARGOS\app"
COMMIT_MESSAGE = "Actualización automática de BASE_DATOS.csv"
# --- Fin Configuración ---

def run_git_command(command_list, output_text):
    """Ejecuta un comando de Git y muestra la salida en el widget de texto."""
    output_text.insert(tk.END, f"Ejecutando: {' '.join(command_list)}\n")
    try:
        result = subprocess.run(command_list, cwd=REPO_PATH, capture_output=True, text=True, check=True, encoding='utf-8')
        if result.stdout:
            output_text.insert(tk.END, "Salida:\n")
            output_text.insert(tk.END, result.stdout)
        if result.stderr:
            output_text.insert(tk.END, "Errores:\n")
            output_text.insert(tk.END, result.stderr)
        output_text.insert(tk.END, "-" * 20 + "\n")
        return True
    except FileNotFoundError:
        messagebox.showerror("Error", f"El comando '{command_list[0]}' no se encontró. ¿Está Git instalado y en el PATH del sistema?")
        return False
    except subprocess.CalledProcessError as e:
        error_message = f"Error al ejecutar {' '.join(command_list)}:\nCódigo de retorno: {e.returncode}\n"
        if e.stdout:
            error_message += f"Salida:\n{e.stdout}\n"
        if e.stderr:
            error_message += f"Errores:\n{e.stderr}\n"
        messagebox.showerror("Error", error_message)
        return False
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error inesperado: {e}")
        return False

def ejecutar_git():
    """Función que se ejecuta al hacer clic en el botón."""
    output_text.delete(1.0, tk.END)  # Limpiar el texto de salida
    output_text.insert(tk.END, f"Cambiando al directorio del repositorio: {REPO_PATH}\n")

    if not os.path.isdir(REPO_PATH):
        messagebox.showerror("Error", f"La ruta del repositorio configurada no existe o no es un directorio.\nRuta configurada: {REPO_PATH}")
        return

    # Cambiar a la rama master
    run_git_command(["git", "checkout", "master"], output_text)

    # Agregar todos los archivos modificados
    if run_git_command(["git", "add", "."], output_text):
        status_result = subprocess.run(["git", "status", "--porcelain"], cwd=REPO_PATH, capture_output=True, text=True)
        if status_result.stdout.strip():
            output_text.insert(tk.END, "Cambios detectados. Realizando commit...\n")
            if run_git_command(["git", "commit", "-m", COMMIT_MESSAGE], output_text):

                # Hacer pull antes del push
                output_text.insert(tk.END, "Actualizando rama local desde el repositorio remoto...\n")
                if not run_git_command(["git", "pull", "origin", "master"], output_text):
                    output_text.insert(tk.END, "Error al hacer 'git pull'. Deteniendo proceso.\n")
                    return

                # Push
                output_text.insert(tk.END, "Realizando push a GitHub...\n")
                if run_git_command(["git", "push", "origin", "master"], output_text):
                    output_text.insert(tk.END, "\n¡Proceso completado exitosamente!\n")
                    messagebox.showinfo("Éxito", "¡Proceso de Git completado!")
                else:
                    output_text.insert(tk.END, "\nError durante el 'git push'. Revisa los mensajes anteriores.\n")
                    messagebox.showerror("Error", "Error durante el 'git push'.")
            else:
                output_text.insert(tk.END, "\nError durante el 'git commit'. No se intentará hacer push.\n")
                messagebox.showerror("Error", "Error durante el 'git commit'.")
        else:
            output_text.insert(tk.END, "No se detectaron cambios para hacer commit.\n")
            output_text.insert(tk.END, "\nProceso completado (sin cambios para subir).\n")
            messagebox.showinfo("Información", "No se detectaron cambios para subir.")
    else:
        output_text.insert(tk.END, "\nError durante el 'git add'. El proceso se ha detenido.\n")
        messagebox.showerror("Error", "Error durante el 'git add'.")

# --- Configuración de la ventana principal ---
window = tk.Tk()
window.title("Automatización de Git")
window.geometry("600x400")  # Tamaño inicial de la ventana

# --- Botón para ejecutar el proceso de Git ---
boton_ejecutar = tk.Button(window, text="Ejecutar Git", command=ejecutar_git)
boton_ejecutar.pack(pady=20)

# --- Área de texto para mostrar la salida ---
output_text = tk.Text(window, height=15, width=70)
output_text.pack(pady=10, padx=10)

# --- Bucle principal de Tkinter ---
window.mainloop()
