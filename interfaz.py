import tkinter as tk
from tkinter import messagebox, ttk
from biometrico import obtener_asistencias
from biometrico import eliminar_asistencias
from biometrico import get_info
from biometrico import set_time 
from tkinter import filedialog
import openpyxl
import os
from datetime import datetime
import sys
import os

exportar_usb_data = []

def resource_path(*parts):
    """Devuelve la ruta absoluta a un recurso empaquetado (o en desarrollo)."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, *parts)

# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< funciones >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def descargar_asistencia():
    ip = entry_ip.get().strip()
    puerto = entry_puerto.get().strip()
    idDispositivo = entry_id.get().strip()
    # convertir idDispositivo a int si es numérico
    if idDispositivo.isdigit():
        idDispositivo = int(idDispositivo)
    elif idDispositivo == "":
        idDispositivo = 0
    tipo_marcacion = 1  # Valor fijo por ahora

    if not ip or not puerto:
        messagebox.showwarning("Campos requeridos", "Por favor, ingresa la IP y el puerto del dispositivo.")
        return
    try:
        registros = obtener_asistencias(ip, int(puerto))
        tree.delete(*tree.get_children())
        if registros:
            for usuario, fecha, status, punch, uid in registros:
                # dividir fecha en fecha y hora en el primer espacio
                s = str(fecha)
                fecha_str, _, hora_str = s.partition(' ')
                # cambiar formato fecha de AAAA-MM-DD a DD/MM/AAAA
                año_str, mes_str, dia_str = fecha_str.split('-')
                fecha_str = f"{dia_str}/{mes_str}/{año_str}"
                # quitar segundos de hora
                hora_str = hora_str[:5]
                # si no hay espacio, hora_str será '' automáticamente
                tree.insert("", "end", values=(usuario, idDispositivo, tipo_marcacion, fecha_str, hora_str))
                exportar_usb_data.append((usuario, s, idDispositivo, status, punch, 0))
        else:
            messagebox.showinfo("Información", "No se encontraron registros")
    except Exception as e:
        messagebox.showerror("Error", str(e)) 

def exportar_usb():
    if not exportar_usb_data:
        messagebox.showinfo("Información", "No hay datos para exportar.")
        return

    # Preguntar al usuario dónde guardar el archivo, por defecto en carpeta escritorio
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    default_name = f"{ts}_attlog.dat"    
    initial_dir = os.path.join(os.path.expanduser("~"), "Desktop")
    if not os.path.isdir(initial_dir):
        initial_dir = os.path.expanduser("~")
    # Abrir diálogo para guardar archivo, guardar como .dat o .txt
    archivo = filedialog.asksaveasfilename(
        defaultextension=".dat",
        filetypes=[("Archivos de texto", "*.txt")],
        initialfile=default_name,
        initialdir=initial_dir,
        title="Guardar archivo de exportación"
    )

    if archivo:
        try:
            with open(archivo, 'w') as f:
                for registro in exportar_usb_data:
                    #registros separados por tabulación
                    linea = "\t".join(map(str, registro))
                    f.write(linea + "\n")
            messagebox.showinfo("Éxito", f"Datos exportados a:\n{archivo}")
        except Exception as e:
            messagebox.showerror("Error al guardar", f"No se pudo guardar el archivo:\n{e}")
    else:
        messagebox.showinfo("Cancelado", "Guardado cancelado por el usuario.")

def exportar_excel():

    if not tree.get_children():
        messagebox.showinfo("Información", "No hay datos para exportar.")
        return
    
    # Rellena la plantilla existente en assets
    plantilla_path = resource_path("assets", "Plantilla.xlsx")
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

        # Volcar filas del tree (se asume columns = Usuario, Id_Bio, Tipo_marcacion, Fecha, Hora)
        for row_id in tree.get_children():
            values = tree.item(row_id)['values']
            ws.append(values)

        # Preguntar al usuario dónde guardar la copia (por defecto en carpeta escritorio)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        base, ext = os.path.splitext(os.path.basename(plantilla_path))
        default_name = f"{base}_{ts}{ext}"
        # intentar establecer como carpeta inicial el Escritorio del usuario
        initial_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        if not os.path.isdir(initial_dir):
            # si no existe Desktop (por ejemplo en algunos sistemas), usar el home
            initial_dir = os.path.expanduser("~")

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

def eliminar_marcaciones():
    ip = entry_ip.get().strip()
    puerto = entry_puerto.get().strip()

    try:
        if not ip or not puerto:
            messagebox.showwarning("Campos requeridos", "Por favor, ingresa la IP y el puerto del dispositivo.")
            return

        elif not tree.get_children():
            messagebox.showinfo("Información", "No hay marcaciones para eliminar.")
            return

        else:
            confirmacion = messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas eliminar todas las marcaciones del dispositivo?")
            if confirmacion:
                eliminar_asistencias(ip, int(puerto))
                tree.delete(*tree.get_children())
            else:
                messagebox.showinfo("Cancelado", "Eliminación cancelada.")
                return
            
    except Exception as e:
            messagebox.showerror("Error", f"No se pudo conectar al biométrico: {e}")

def obtener_info():
    ip = entry_ip.get().strip()
    puerto = entry_puerto.get().strip()

    if not ip or not puerto:
        messagebox.showwarning("Campos requeridos", "Por favor, ingresa la IP y el puerto del dispositivo.")
        return

    try:
        info = get_info(ip, int(puerto))
       
        if info:
            fila = 0
            for clave, valor in info.items():
                tk.Label(frame_detalle_info, text=f"{clave.replace('_', ' ').title()}:").grid(row=fila, column=0, sticky="e", padx=5)
                tk.Label(frame_detalle_info, text=valor).grid(row=fila, column=1, sticky="w", padx=5)
                fila += 1
        else:
            messagebox.showinfo("Información", "No se pudo obtener la información del dispositivo.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo conectar al biométrico: {e}")

def mostrar_frame_info():
    if frame_tabla.winfo_ismapped():
        frame_tabla.pack_forget()
    frame_info.pack(fill="both", expand=True, padx=10, pady=10)

def mostrar_frame_tabla():
    if frame_info.winfo_ismapped():
        frame_info.pack_forget()
    frame_tabla.pack(fill="both", expand=True, padx=10, pady=10)




#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< interfaz gráfica >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#ventana principal
root = tk.Tk()
root.title("SIGA Asistencias Biométrico")
root.geometry("500x500")

# Frame superior tipo barra de menú visual
frame_menu_superior = tk.Frame(root)
frame_menu_superior.pack(fill="x")

# Subframe para los botones (con margen inferior)
frame_botones_menu = tk.Frame(frame_menu_superior, bg="#e0e0e0")
frame_botones_menu.pack(side="top", fill="x", pady=(0, 2))  # ← separación inferior

# Estilo común para los botones
boton_config = {
    "bg": "#e0e0e0",
    "activebackground": "#d4d4d4",
    "bd": 0,
    "relief": "solid",
    "padx": 10,
    "pady": 6
}

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< validaciones entradas >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#validacion solo puerto
def solo_puerto(char):
    return (char.isdigit() or char == "") and len(char) <= 5

#validacion IP
def solo_ip(char):
    # Permite solo dígitos, puntos o vacío
    return all(c.isdigit() or c == '.' for c in char) or char == ""

#validacion solo idBiometrico
def solo_id_bio(char):
    return (char.isdigit() or char == "") and len(char) <= 3

# Validaciones de entrada
vcmd_ip = (root.register(solo_ip), "%P")
vcmd_puerto = (root.register(solo_puerto), "%P")
vcmd_dispositivo = (root.register(solo_id_bio), "%P")


# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<  conexion >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#frame conexion
frame_conexion = tk.Frame(root)
frame_conexion.pack(pady=10)

#etiquetas y entradas
tk.Label(frame_conexion, text="IP del dispositivo:").grid(row=0, column=0, padx=5)
entry_ip = tk.Entry(frame_conexion, validate="key", validatecommand=vcmd_ip)
entry_ip.grid(row=0, column=1, padx=5)
entry_ip.insert(0, "192.168.1.67")  # Valor por defecto

tk.Label(frame_conexion, text="Puerto:").grid(row=1, column=0, padx=5)
entry_puerto = tk.Entry(frame_conexion, validate="key", validatecommand=vcmd_puerto)
entry_puerto.grid(row=1, column=1, padx=5)
entry_puerto.insert(0, "4370")  # Valor por defecto

tk.Label(frame_conexion, text="Id dispositivo:").grid(row=2, column=0, padx=5)
entry_id = tk.Entry(frame_conexion, validate="key", validatecommand=vcmd_dispositivo)
entry_id.grid(row=2, column=1, padx=5)
entry_id.insert(0, "0")  # Valor por defecto

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< tabla asistencias >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#frame tabla asistencias
frame_tabla = tk.Frame(root)
frame_tabla.pack(fill="both", expand=True, padx=10, pady=10)

#boton descargar asistencias
btn_asistencia = tk.Button(frame_tabla, text="Descargar asistencia", command=descargar_asistencia)
btn_asistencia.pack(pady=10)

#tabla asistencias
frame_tabla_inner = tk.Frame(frame_tabla)
frame_tabla_inner.pack(fill="both", expand=True)
columns = ("Usuario", "Id_Bio", "Tipo_marcacion", "Fecha","Hora")
tree = ttk.Treeview(frame_tabla_inner, columns=columns, show="headings")
tree.heading("Usuario", text="Id usuario")
tree.heading("Id_Bio", text="Id Bio")
tree.heading("Tipo_marcacion", text="Tipo Marcacion")
tree.heading("Fecha", text="Fecha")
tree.heading("Hora", text="Hora")
tree.column("Usuario", width=100, anchor='center')
tree.column("Id_Bio", width=70, anchor='center')
tree.column("Tipo_marcacion", width=100, anchor='center')
tree.column("Fecha", width=70, anchor='center')
tree.column("Hora", width=70, anchor='center')

# Barra de desplazamiento vertical de la tabla asistencias
scrollbar_y = ttk.Scrollbar(frame_tabla_inner, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar_y.set)
scrollbar_y.pack(side="right", fill="y")
tree.pack(side="left", fill="both", expand=True)

#botones exportar y eliminar
frame_botones = tk.Frame(frame_tabla, bg="#e0e0e0")
frame_botones.pack( side="bottom", fill="both")

# Subframe centrado para los botones
contenedor_botones = tk.Frame(frame_botones, bg="#e0e0e0")
contenedor_botones.pack(anchor="center", pady=5)

btn_exportar = tk.Button(contenedor_botones, text="Exportar a Excel", command=exportar_excel)
btn_exportar.pack(side="left", pady=5, padx=5)

btn_exportar_usb = tk.Button(contenedor_botones, text="Exportar para USB", command=exportar_usb)
btn_exportar_usb.pack(side="left", pady=5, padx=5)

btn_eliminar_marcaciones = tk.Button(contenedor_botones, text="Eliminar marcaciones", command=eliminar_marcaciones)
btn_eliminar_marcaciones.pack(side="left", pady=5, padx=5)

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< informacion dispositivo >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#informacion del dispositivo
frame_info = tk.Frame(root)
frame_info.pack_forget()  # Se muestra al hacer clic en el botón correspondiente

#boton obtener info y mostrar en frame_info
btn_info = tk.Button(frame_info, text="Obtener info dispositivo", command=obtener_info)
btn_info.pack(pady=5)

#subframe para mostrar info
frame_detalle_info = tk.Frame(frame_info,bg="#f0f0f0", bd=1, relief="solid")   
frame_detalle_info.pack(pady=10, fill="both", expand=True)

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< barra de menu superior >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

# Lista de botones y sus comandos
botones_menu = [
    ("Información", mostrar_frame_info),
    ("Asistencias", mostrar_frame_tabla),
    ("Usuarios", mostrar_frame_tabla)
]

# Crear botones alineados horizontalmente
for texto, comando in botones_menu:
    btn = tk.Button(frame_botones_menu, text=texto, command=comando, **boton_config)
    btn.pack(side="left", padx=1)


  # Mostrar el frame de info al iniciar
root.mainloop()

# Para crear el ejecutable con PyInstaller, usar el siguiente comando en la terminal:
# pyinstaller --onefile --add-data "assets;assets" --noconsole interfaz.py