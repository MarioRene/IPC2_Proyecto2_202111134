import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import random

class MobileAppSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Atención a Clientes")
        self.root.geometry("360x640")  # Tamaño similar a un móvil
        self.root.resizable(False, False)
        
        # Paleta de colores morado pastel
        self.bg_color = "#f0e6ff"  # Morado muy claro
        self.primary_color = "#b399d4"  # Morado pastel
        self.secondary_color = "#d9c2ff"  # Morado más claro
        self.accent_color = "#8a6dae"  # Morado más oscuro
        self.text_color = "#4a3b5f"  # Morado oscuro para texto
        
        # Configurar estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configurar colores para los widgets
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TLabel', background=self.bg_color, foreground=self.text_color)
        self.style.configure('TButton', background=self.primary_color, foreground='white', 
                            font=('Helvetica', 10, 'bold'), padding=10)
        self.style.map('TButton', 
                      background=[('active', self.accent_color), ('pressed', self.accent_color)])
        
        # Crear la interfaz
        self.create_widgets()
        
    def create_widgets(self):
        # Frame principal
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self.header_frame = ttk.Frame(self.main_frame, style='TFrame')
        self.header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.logo_label = ttk.Label(self.header_frame, text="Soluciones Guatemaltecas", 
                                   font=('Helvetica', 16, 'bold'), style='TLabel')
        self.logo_label.pack()
        
        self.subtitle_label = ttk.Label(self.header_frame, text="Sistema de Atención", 
                                      font=('Helvetica', 12), style='TLabel')
        self.subtitle_label.pack()
        
        # Separador
        ttk.Separator(self.main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=20, pady=5)
        
        # Contenido principal
        self.content_frame = ttk.Frame(self.main_frame, style='TFrame')
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Selección de empresa
        self.company_label = ttk.Label(self.content_frame, text="Seleccione la empresa:", 
                                     font=('Helvetica', 12), style='TLabel')
        self.company_label.pack(pady=(0, 5))
        
        self.company_combo = ttk.Combobox(self.content_frame, values=["Banco Industrial", "Tigo", "Claro", "Municipalidad"])
        self.company_combo.pack(fill=tk.X, pady=(0, 15))
        
        # Selección de punto de atención
        self.point_label = ttk.Label(self.content_frame, text="Seleccione el punto de atención:", 
                                   font=('Helvetica', 12), style='TLabel')
        self.point_label.pack(pady=(0, 5))
        
        self.point_combo = ttk.Combobox(self.content_frame, values=["Centro Comercial Miraflores", "Plaza Fontabella", "Centro Histórico"])
        self.point_combo.pack(fill=tk.X, pady=(0, 15))
        
        # Transacciones disponibles
        self.transactions_label = ttk.Label(self.content_frame, text="Transacciones disponibles:", 
                                          font=('Helvetica', 12), style='TLabel')
        self.transactions_label.pack(pady=(0, 5))
        
        # Frame para checkbuttons
        self.transactions_frame = ttk.Frame(self.content_frame, style='TFrame')
        self.transactions_frame.pack(fill=tk.X)
        
        # Lista de transacciones (simuladas)
        self.transactions = [
            {"id": 1, "name": "Retiro de efectivo", "time": 5},
            {"id": 2, "name": "Depósito", "time": 7},
            {"id": 3, "name": "Consulta de saldo", "time": 3},
            {"id": 4, "name": "Pago de servicios", "time": 10}
        ]
        
        self.selected_transactions = []
        self.check_vars = []
        
        for i, trans in enumerate(self.transactions):
            var = tk.IntVar()
            self.check_vars.append(var)
            cb = tk.Checkbutton(self.transactions_frame, text=f"{trans['name']} ({trans['time']} min)", 
                               variable=var, onvalue=trans['id'], offvalue=0,
                               bg=self.bg_color, fg=self.text_color, selectcolor=self.secondary_color,
                               activebackground=self.bg_color, activeforeground=self.text_color,
                               font=('Helvetica', 10))
            cb.pack(anchor=tk.W, pady=2)
        
        # Botón de solicitud
        self.request_button = ttk.Button(self.content_frame, text="Solicitar Atención", 
                                       command=self.request_service)
        self.request_button.pack(pady=20, fill=tk.X)
        
        # Footer
        self.footer_frame = ttk.Frame(self.main_frame, style='TFrame')
        self.footer_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.status_label = ttk.Label(self.footer_frame, text="Listo para solicitar atención", 
                                    font=('Helvetica', 10), style='TLabel')
        self.status_label.pack()
        
    def request_service(self):
        # Validar selecciones
        company = self.company_combo.get()
        point = self.point_combo.get()
        
        if not company or not point:
            messagebox.showerror("Error", "Por favor seleccione una empresa y un punto de atención")
            return
            
        # Obtener transacciones seleccionadas
        selected = []
        total_time = 0
        for i, var in enumerate(self.check_vars):
            if var.get() > 0:
                selected.append(self.transactions[i])
                total_time += self.transactions[i]['time']
                
        if not selected:
            messagebox.showerror("Error", "Por favor seleccione al menos una transacción")
            return
            
        # Generar número de atención
        ticket_number = f"{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        
        # Mostrar resultados en una nueva ventana
        self.show_ticket(ticket_number, total_time)
        
    def show_ticket(self, ticket_number, total_time):
        # Crear ventana de ticket
        ticket_window = tk.Toplevel(self.root)
        ticket_window.title("Ticket de Atención")
        ticket_window.geometry("320x480")
        ticket_window.resizable(False, False)
        ticket_window.configure(bg=self.bg_color)
        
        # Frame principal
        ticket_frame = ttk.Frame(ticket_window, style='TFrame')
        ticket_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Logo
        logo_label = ttk.Label(ticket_frame, text="Soluciones Guatemaltecas", 
                             font=('Helvetica', 14, 'bold'), style='TLabel')
        logo_label.pack(pady=(0, 10))
        
        # Separador
        ttk.Separator(ticket_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        # Información del ticket
        ttk.Label(ticket_frame, text="Su número de atención es:", 
                 font=('Helvetica', 12), style='TLabel').pack(pady=(10, 5))
        
        ttk.Label(ticket_frame, text=ticket_number, 
                 font=('Helvetica', 24, 'bold'), foreground=self.accent_color, 
                 background=self.bg_color).pack(pady=(0, 20))
        
        ttk.Label(ticket_frame, text="Tiempo estimado de espera:", 
                 font=('Helvetica', 12), style='TLabel').pack(pady=(10, 5))
        
        avg_wait = random.randint(5, 15)  # Simular tiempo de espera promedio
        ttk.Label(ticket_frame, text=f"{avg_wait} minutos", 
                 font=('Helvetica', 16), foreground=self.accent_color, 
                 background=self.bg_color).pack(pady=(0, 10))
        
        ttk.Label(ticket_frame, text="Tiempo estimado de atención:", 
                 font=('Helvetica', 12), style='TLabel').pack(pady=(10, 5))
        
        ttk.Label(ticket_frame, text=f"{total_time} minutos", 
                 font=('Helvetica', 16), foreground=self.accent_color, 
                 background=self.bg_color).pack(pady=(0, 20))
        
        # Botón de cierre
        close_button = ttk.Button(ticket_frame, text="Cerrar", 
                                command=ticket_window.destroy)
        close_button.pack(pady=20, fill=tk.X)
        
        # Actualizar estado en la ventana principal
        self.status_label.config(text=f"Ticket generado: {ticket_number}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MobileAppSimulator(root)
    root.mainloop()
