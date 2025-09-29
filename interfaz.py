import tkinter as tk
from tkinter import messagebox, ttk
from biometrico import obtener_asistencias

def descargar_asistencia():
    try:
        registros = obtener_asistencias(entry_ip.get(), int(entry_puerto.get()) or 4370)
        tree.delete(*tree.get_children())
        if registros:
            for usuario, fecha in registros:
                tree.insert("", "end", values=(usuario, fecha))
        else:
            messagebox.showinfo("Información", "No se encontraron registros")
    except Exception as e:
        messagebox.showerror("Error", str(e))


#ventana principal
root = tk.Tk()
root.title("Asistencias ZKTeco")
root.geometry("500x500")

# frame para el IP y puerto
frame_conexion = tk.Frame(root)
frame_conexion.pack(pady=10)

tk.Label(frame_conexion, text="IP del dispositivo:").grid(row=0, column=0, padx=5)
entry_ip = tk.Entry(frame_conexion)
entry_ip.grid(row=0, column=1, padx=5)

tk.Label(frame_conexion, text="Puerto:").grid(row=1, column=0, padx=5)
entry_puerto = tk.Entry(frame_conexion)
entry_puerto.grid(row=1, column=1, padx=5)

#botones
btn_asistencia = tk.Button(root, text="Descargar asistencia", command=descargar_asistencia)
btn_asistencia.pack(pady=10)

#tabla
columns = ("Usuario", "Fecha-Hora")
tree = ttk.Treeview(root, columns=columns, show="headings")
tree.heading("Usuario", text="Usuario")
tree.heading("Fecha-Hora", text="Fecha-Hora")
tree.pack(fill="both", expand=True, padx=10, pady=10)

root.mainloop()