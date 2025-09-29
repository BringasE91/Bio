import tkinter as tk
from tkinter import messagebox, ttk
from biometrico import obtener_asistencias

def descargar_asistencia():
    try:
        registros = obtener_asistencias()
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

#botones
btn_asistencia = tk.Button(root, text="Descargar asistencia")
btn_asistencia.pack(pady=10)

#tabla
columns = ("Usuario", "Fecha-Hora")
tree = ttk.Treeview(root, columns=columns, show="headings")
tree.heading("Usuario", text="Usuario")
tree.heading("Fecha-Hora", text="Fecha-Hora")
tree.pack(fill="both", expand=True, padx=10, pady=10)

root.mainloop()