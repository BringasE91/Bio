import tkinter as tk
from tkinter import messagebox, ttk
from biometrico import obtener_asistencias
from tkinter import filedialog
import openpyxl
import os
from datetime import datetime

def descargar_asistencia():
    ip = entry_ip.get().strip()
    puerto = entry_puerto.get().strip()
    idDispositivo = entry_id.get().strip()
    # convertir idDispositivo a int si es numérico
    if idDispositivo.isdigit():
        idDispositivo = int(idDispositivo)
    elif idDispositivo == "":
        idDispositivo = 0
    tipo_marcacion = "Digital"  # Valor fijo por ahora

    if not ip or not puerto:
        messagebox.showwarning("Campos requeridos", "Por favor, ingresa la IP y el puerto del dispositivo.")
        return
    try:
        registros = obtener_asistencias(ip, int(puerto))
        tree.delete(*tree.get_children())
        if registros:
            for usuario, fecha in registros:
                # dividir fecha en fecha y hora en el primer espacio
                s = str(fecha)
                fecha_str, _, hora_str = s.partition(' ')
                # si no hay espacio, hora_str será '' automáticamente
                tree.insert("", "end", values=(usuario, idDispositivo, tipo_marcacion, fecha_str, hora_str))
        else:
            messagebox.showinfo("Información", "No se encontraron registros")
    except Exception as e:
        messagebox.showerror("Error", str(e)) 


def exportar_excel():
    # Rellenar la plantilla existente en assets/Plantilla.xlsx (no crear archivo nuevo)
    plantilla_path = os.path.join(os.path.dirname(__file__), "assets", "Plantilla.xlsx")
    if not os.path.exists(plantilla_path):
        messagebox.showerror("Plantilla no encontrada", f"No se encontró la plantilla en:\n{plantilla_path}")
        return

    try:
        wb = openpyxl.load_workbook(plantilla_path)
        ws = wb.active

        # Limpiar filas existentes debajo del encabezado (suponiendo encabezado en la fila 1)
        if ws.max_row >= 2:
            for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
                for cell in row:
                    cell.value = None

        # Volcar filas del tree (suponiendo que tree tiene 4 columnas: Usuario, Id_Bio, Fecha, Hora)
        for row_id in tree.get_children():
            row = tree.item(row_id)['values']
            ws.append(row)
        # Preguntar al usuario dónde guardar la copia (por defecto en carpeta assets)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        base, ext = os.path.splitext(os.path.basename(plantilla_path))
        default_name = f"{base}_{ts}{ext}"
        initial_dir = os.path.dirname(plantilla_path)

        archivo = filedialog.asksaveasfilename(
            defaultextension=ext,
            filetypes=[("Archivos Excel", "*.xlsx")],
            initialdir=initial_dir,
            initialfile=default_name,
            title="Guardar copia de la plantilla como"
        )

        if archivo:
            wb.save(archivo)
            messagebox.showinfo("Éxito", f"Copia guardada en:\n{archivo}")
        else:
            messagebox.showinfo("Cancelado", "Guardado cancelado por el usuario.")
    except Exception as e:
        messagebox.showerror("Error al guardar", f"No se pudo actualizar la plantilla:\n{e}")


#validacion solo puerto y idBiometrico
def solo_puerto(char):
    return (char.isdigit() or char == "") and len(char) <= 5

#validacion IP
def solo_ip(char):
    # Permite solo dígitos, puntos o vacío
    return all(c.isdigit() or c == '.' for c in char) or char == ""

#validacion solo idBiometrico
def solo_id_bio(char):
    return (char.isdigit() or char == "") and len(char) <= 3


#ventana principal
root = tk.Tk()
root.title("Asistencias ZKTeco")
root.geometry("500x500")

vcmd_ip = (root.register(solo_ip), "%P")
vcmd_puerto = (root.register(solo_puerto), "%P")
vcmd_dispositivo = (root.register(solo_id_bio), "%P")

# frame para el IP y puerto
frame_conexion = tk.Frame(root)
frame_conexion.pack(pady=10)

tk.Label(frame_conexion, text="IP del dispositivo:").grid(row=0, column=0, padx=5)
entry_ip = tk.Entry(frame_conexion, validate="key", validatecommand=vcmd_ip)
entry_ip.grid(row=0, column=1, padx=5)

tk.Label(frame_conexion, text="Puerto:").grid(row=1, column=0, padx=5)
entry_puerto = tk.Entry(frame_conexion, validate="key", validatecommand=vcmd_puerto)
entry_puerto.grid(row=1, column=1, padx=5)
entry_puerto.insert(0, "4370")  # Valor por defecto

tk.Label(frame_conexion, text="Id dispositivo:").grid(row=2, column=0, padx=5)
entry_id = tk.Entry(frame_conexion, validate="key", validatecommand=vcmd_dispositivo)
entry_id.grid(row=2, column=1, padx=5)
entry_id.insert(0, "0")  # Valor por defecto

#botones
btn_asistencia = tk.Button(root, text="Descargar asistencia", command=descargar_asistencia)
btn_asistencia.pack(pady=10)

btn_exportar = tk.Button(root, text="Exportar a Excel", command=exportar_excel)
btn_exportar.pack(pady=10)

#tabla
columns = ("Usuario", "Id_Bio", "Tipo_marcacion", "Fecha","Hora")
frame_tabla = tk.Frame(root)
frame_tabla.pack(fill="both", expand=True, padx=10, pady=10)

tree = ttk.Treeview(frame_tabla, columns=columns, show="headings")
tree.heading("Usuario", text="Usuario")
tree.heading("Id_Bio", text="Id-Bio")
tree.heading("Tipo_marcacion", text="Tipo Marcacion")
tree.heading("Fecha", text="Fecha")
tree.heading("Hora", text="Hora")
tree.column("Usuario", width=100, anchor='w')
tree.column("Id_Bio", width=50, anchor='center', stretch=False)
tree.column("Tipo_marcacion", width=50, anchor='center')
tree.column("Fecha", width=100, anchor='center')
tree.column("Hora", width=100, anchor='center')

# Barra de desplazamiento vertical
scrollbar_y = ttk.Scrollbar(frame_tabla, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar_y.set)
scrollbar_y.pack(side="right", fill="y")
tree.pack(side="left", fill="both", expand=True)

root.mainloop()