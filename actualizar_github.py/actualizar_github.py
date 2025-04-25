import os
import subprocess
import tkinter as tk
from tkinter import messagebox

# Ruta del repositorio Git
REPO_PATH = r"C:\Users\carlo\OneDrive - SOMYL S.A\CARGOS\app"  # <-- Aquí tu ruta real

# Función para mostrar conflictos
def mostrar_conflictos(repo_path, output_widget):
    """Verifica y muestra archivos en conflicto en una ventana nueva."""
    conflict_check = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=U"],
        cwd=repo_path,
        capture_output=True,
        text=True
    )

    archivos_conflictivos = conflict_check.stdout.strip().splitlines()

    if archivos_conflictivos:
        output_widget.insert(tk.END, "⚠️ Conflictos detectados:\n")
        for archivo in archivos_conflictivos:
            output_widget.insert(tk.END, f" - {archivo}\n")

        # Crear una nueva ventana para mostrar conflictos
        ventana_conflictos = tk.Toplevel()
        ventana_conflictos.title("Conflictos detectados")
        ventana_conflictos.geometry("400x300")

        label = tk.Label(ventana_conflictos, text="Archivos en conflicto:", font=("Arial", 12, "bold"))
        label.pack(pady=10)

        lista_conflictos = tk.Listbox(ventana_conflictos, width=60, height=10)
        for archivo in archivos_conflictivos:
            lista_conflictos.insert(tk.END, archivo)
        lista_conflictos.pack(padx=10, pady=10)

        cerrar_btn = tk.Button(ventana_conflictos, text="Cerrar", command=ventana_conflictos.destroy)
        cerrar_btn.pack(pady=10)

        messagebox.showerror("Conflictos detectados", "Resuelve los conflictos antes de continuar.")
        return True  # Hay conflictos
    else:
        return False  # No hay conflictos

# Función principal para ejecutar comandos Git
def ejecutar_git():
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, f"Cambiando al directorio del repositorio: {REPO_PATH}\n")

    if not os.path.isdir(REPO_PATH):
        messagebox.showerror("Error", f"La ruta del repositorio configurada no existe o no es un directorio.\nRuta configurada: {REPO_PATH}")
        return

    # Verificar si hay conflictos antes de proceder
    if mostrar_conflictos(REPO_PATH, output_text):
        return  # Detener ejecución si hay conflictos

    # Aquí sigue el flujo normal de git (checkout, add, commit, push)
    try:
        # Ejemplo de git pull
        subprocess.run(["git", "pull"], cwd=REPO_PATH, check=True)
        output_text.insert(tk.END, "✅ Pull realizado exitosamente.\n")

        # Ejemplo de git add
        subprocess.run(["git", "add", "."], cwd=REPO_PATH, check=True)
        output_text.insert(tk.END, "✅ Cambios añadidos.\n")

        # Ejemplo de git commit
        subprocess.run(["git", "commit", "-m", "Commit automático desde la aplicación"], cwd=REPO_PATH, check=True)
        output_text.insert(tk.END, "✅ Cambios comiteados.\n")

        # Ejemplo de git push
        subprocess.run(["git", "push"], cwd=REPO_PATH, check=True)
        output_text.insert(tk.END, "✅ Cambios enviados al repositorio remoto.\n")

        messagebox.showinfo("Éxito", "Operación Git completada correctamente.")

    except subprocess.CalledProcessError as e:
        output_text.insert(tk.END, f"❌ Error al ejecutar comando Git: {e}\n")
        messagebox.showerror("Error Git", f"Ocurrió un error al ejecutar un comando Git.\n{e}")

# Crear ventana principal
ventana = tk.Tk()
ventana.title("Gestor de Git")
ventana.geometry("600x400")

# Área de texto para mostrar mensajes
output_text = tk.Text(ventana, height=20, width=70)
output_text.pack(pady=10)

# Botón para ejecutar Git
boton_ejecutar = tk.Button(ventana, text="Ejecutar Git", command=ejecutar_git)
boton_ejecutar.pack(pady=10)

ventana.mainloop()
