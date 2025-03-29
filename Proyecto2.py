import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random
import xml.etree.ElementTree as ET
from PIL import Image, ImageTk

# ==================== CLASES DEL MODELO (TDA) ====================
class Empresa:
    def __init__(self, id_empresa, nombre, abreviatura):
        self.id = id_empresa
        self.nombre = nombre
        self.abreviatura = abreviatura
        self.puntos_atencion = []
        self.transacciones = []

class PuntoAtencion:
    def __init__(self, id_punto, nombre, direccion):
        self.id = id_punto
        self.nombre = nombre
        self.direccion = direccion
        self.escritorios = []
        self.clientes_en_espera = []
        self.clientes_atendidos = []

class EscritorioServicio:
    def __init__(self, id_escritorio, identificacion, encargado):
        self.id = id_escritorio
        self.identificacion = identificacion
        self.encargado = encargado
        self.activo = False
        self.cliente_actual = None
        self.tiempo_restante = 0

class Transaccion:
    def __init__(self, id_transaccion, nombre, tiempo_atencion):
        self.id = id_transaccion  # Ahora usar números (1, 2, 3...)
        self.nombre = nombre
        self.tiempo = tiempo_atencion

class Cliente:
    def __init__(self, dpi, nombre):
        self.dpi = dpi
        self.nombre = nombre
        self.transacciones = []
        self.tiempo_espera = 0
        self.ticket = None

# ==================== SISTEMA DE ATENCIÓN ====================

class SistemaAtencion:
    def __init__(self):
        self.empresas = []
        self.tickets_generados = set()

    def generar_ticket_unico(self):
        while True:
            ticket = f"{random.randint(100, 999)}-{random.randint(1000, 9999)}"
            if ticket not in self.tickets_generados:
                self.tickets_generados.add(ticket)
                return ticket

    def agregar_empresa(self, empresa):
        self.empresas.append(empresa)

    def asignar_cliente(self, punto_atencion, cliente):
        tiempo_total = sum(t.tiempo for t in cliente.transacciones)
        cliente.tiempo_espera = tiempo_total
        cliente.ticket = self.generar_ticket_unico()
        punto_atencion.clientes_en_espera.append(cliente)
        
        # Tiempo estimado = tiempo de atención + (clientes en espera * 3 minutos)
        tiempo_espera = tiempo_total + (len(punto_atencion.clientes_en_espera) - 1) * 3
        return cliente.ticket, tiempo_espera, tiempo_total

    def activar_escritorio(self, escritorio):
        if not escritorio.activo and escritorio.punto_atencion.clientes_en_espera:
            escritorio.activo = True
            escritorio.cliente_actual = escritorio.punto_atencion.clientes_en_espera.pop(0)
            escritorio.tiempo_restante = sum(t.tiempo for t in escritorio.cliente_actual.transacciones)
            return True
        return False
    
    def cargar_configuracion_xml(self, archivo):
        try:
            tree = ET.parse(archivo)
            root = tree.getroot()
            
            for empresa_xml in root.findall('empresa'):
                empresa = Empresa(
                    empresa_xml.get('id'),
                    empresa_xml.find('nombre').text.strip(),
                    empresa_xml.find('abreviatura').text.strip()
                )
                
                # Cargar puntos de atención
                for punto_xml in empresa_xml.find('listaPuntosAtencion').findall('puntoAtencion'):
                    punto = PuntoAtencion(
                        punto_xml.get('id'),
                        punto_xml.find('nombre').text.strip(),
                        punto_xml.find('direccion').text.strip()
                    )
                    
                    # Cargar escritorios
                    for escritorio_xml in punto_xml.find('listaEscritorios').findall('escritorio'):
                        escritorio = EscritorioServicio(
                            escritorio_xml.get('id'),
                            escritorio_xml.find('identificación').text.strip(),
                            escritorio_xml.find('encargado').text.strip()
                        )
                        punto.escritorios.append(escritorio)
                    
                    empresa.puntos_atencion.append(punto)
                
                # Cargar transacciones
                for trans_xml in empresa_xml.find('listaTransacciones').findall('transaccion'):
                    transaccion = Transaccion(
                        trans_xml.get('id'),
                        trans_xml.find('nombre').text.strip(),
                        int(trans_xml.find('tiempoAtencion').text)
                    )
                    empresa.transacciones.append(transaccion)
                
                self.empresas.append(empresa)
            
            return True
        except Exception as e:
            messagebox.showerror("Error XML", f"Error al cargar archivo de configuración:\n{str(e)}")
            return False
    
    def cargar_estado_inicial_xml(self, archivo):
        try:
            tree = ET.parse(archivo)
            root = tree.getroot()
            
            for config_xml in root.findall('configInicial'):
                empresa_id = config_xml.get('idEmpresa')
                punto_id = config_xml.get('idPunto')
                
                # Buscar empresa y punto
                empresa = next((e for e in self.empresas if e.id == empresa_id), None)
                if not empresa:
                    continue
                    
                punto = next((p for p in empresa.puntos_atencion if p.id == punto_id), None)
                if not punto:
                    continue
                
                # Activar escritorios
                for escritorio_xml in config_xml.find('escritoriosActivos').findall('escritorio'):
                    escritorio_id = escritorio_xml.get('idEscritorio')
                    escritorio = next((e for e in punto.escritorios if e.id == escritorio_id), None)
                    if escritorio:
                        escritorio.activo = True
                
                # Cargar clientes
                for cliente_xml in config_xml.find('listadoClientes').findall('cliente'):
                    cliente = Cliente(
                        cliente_xml.get('dpi'),
                        cliente_xml.find('nombre').text.strip()
                    )
                    
                    # Cargar transacciones del cliente
                    for trans_xml in cliente_xml.find('listadoTransacciones').findall('transaccion'):
                        trans_id = trans_xml.get('idTransaction')
                        cantidad = int(trans_xml.get('cantidad', 1))
                        
                        transaccion = next((t for t in empresa.transacciones if t.id == trans_id), None)
                        if transaccion:
                            for _ in range(cantidad):
                                cliente.transacciones.append(transaccion)
                    
                    punto.clientes_en_espera.append(cliente)
            
            return True
        except Exception as e:
            messagebox.showerror("Error XML", f"Error al cargar estado inicial:\n{str(e)}")
            return False

# ==================== INTERFAZ GRÁFICA ====================
class MobileAppSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Atención a Clientes - Versión 2")
        self.root.geometry("360x640")
        self.root.resizable(False, False)
        
        # Paleta de colores morado pastel
        self.bg_color = "#f0e6ff"
        self.primary_color = "#b399d4"
        self.secondary_color = "#d9c2ff"
        self.accent_color = "#8a6dae"
        self.text_color = "#4a3b5f"
        
        # Configurar estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self._configure_styles()
        
        # Sistema de atención
        self.sistema = SistemaAtencion()
        self._cargar_datos_ejemplo()
        
        # Variables de control
        self.transaction_vars = {}  # Diccionario para manejar transacciones
        
        # Crear interfaz
        self._create_widgets()

        # Menu Superior
        self._create_menu()

    def _create_menu(self):
        menubar = tk.Menu(self.root)
        
        # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Cargar Configuración XML", command=self._load_config_xml)
        file_menu.add_command(label="Cargar Estado Inicial XML", command=self._load_initial_state_xml)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.root.quit)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        
        self.root.config(menu=menubar)
    
    def _load_config_xml(self):
        filepath = filedialog.askopenfilename(
            title="Seleccionar archivo de configuración",
            filetypes=[("XML files", "*.xml")]
        )
        if filepath:
            if self.sistema.cargar_configuracion_xml(filepath):
                messagebox.showinfo("Éxito", "Configuración cargada correctamente")
                self._update_ui_after_load()
    
    def _load_initial_state_xml(self):
        filepath = filedialog.askopenfilename(
            title="Seleccionar archivo de estado inicial",
            filetypes=[("XML files", "*.xml")]
        )
        if filepath:
            if self.sistema.cargar_estado_inicial_xml(filepath):
                messagebox.showinfo("Éxito", "Estado inicial cargado correctamente")
                self._update_ui_after_load()
    
    def _update_ui_after_load(self):
        """Actualiza los combobox después de cargar datos"""
        if self.sistema.empresas:
            self.company_combo['values'] = [emp.nombre for emp in self.sistema.empresas]
            if self.sistema.empresas[0].puntos_atencion:
                self.point_combo['values'] = [p.nombre for p in self.sistema.empresas[0].puntos_atencion]
            
            # Actualizar transacciones
            for widget in self.transactions_frame.winfo_children():
                widget.destroy()
            
            self.transaction_vars = {}
            for trans in self.sistema.empresas[0].transacciones:
                var = tk.IntVar()
                self.transaction_vars[trans.id] = (var, trans)
                cb = tk.Checkbutton(
                    self.transactions_frame, 
                    text=f"{trans.nombre} ({trans.tiempo} min)", 
                    variable=var, 
                    onvalue=1,
                    offvalue=0,
                    bg=self.bg_color, 
                    fg=self.text_color, 
                    selectcolor=self.secondary_color,
                    font=('Helvetica', 10)
                )
                cb.pack(anchor=tk.W, pady=2)

    def _configure_styles(self):
        """Configura los estilos de los widgets."""
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TLabel', background=self.bg_color, foreground=self.text_color)
        self.style.configure('TButton', 
                          background=self.primary_color, 
                          foreground='white', 
                          font=('Helvetica', 10, 'bold'), 
                          padding=10)
        self.style.map('TButton', 
                     background=[('active', self.accent_color), ('pressed', self.accent_color)])
    def _cargar_datos_ejemplo(self):
        """Carga datos iniciales para pruebas."""
        empresa = Empresa("EMP-001", "Banco Industrial", "BI")
        
        # Puntos de atención
        punto1 = PuntoAtencion("PT-001", "Centro Comercial Miraflores", "Zona 11")
        punto2 = PuntoAtencion("PT-002", "Plaza Fontabella", "Zona 10")
        empresa.puntos_atencion.extend([punto1, punto2])
        
        # Escritorios
        punto1.escritorios.append(EscritorioServicio("ES-001", "E1", "Juan Pérez"))
        punto1.escritorios.append(EscritorioServicio("ES-002", "E2", "María Gómez"))
        
        # Transacciones (ahora con IDs numéricos para evitar el error)
        transacciones = [
            Transaccion(1, "Retiro de efectivo", 5),
            Transaccion(2, "Depósito", 7),
            Transaccion(3, "Consulta de saldo", 3),
            Transaccion(4, "Pago de servicios", 10)
        ]
        empresa.transacciones.extend(transacciones)
        
        self.sistema.agregar_empresa(empresa)

    def _create_widgets(self):
        """Construye la interfaz gráfica."""
        # Frame principal
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self._create_header()
        
        # Contenido principal
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Combobox para empresa y punto
        self._create_selection_controls()
        
        # Checkboxes para transacciones
        self._create_transaction_controls()
        
        # Botón de solicitud
        self.request_button = ttk.Button(
            self.content_frame, 
            text="Solicitar Atención", 
            command=self._handle_service_request
        )
        self.request_button.pack(pady=20, fill=tk.X)
        
        # Footer
        self._create_footer()

    def _create_header(self):
        """Crea el encabezado de la aplicación."""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(
            header_frame, 
            text="Soluciones Guatemaltecas", 
            font=('Helvetica', 16, 'bold')
        ).pack()
        
        ttk.Label(
            header_frame, 
            text="Sistema de Atención - V2", 
            font=('Helvetica', 12)
        ).pack()
        
        ttk.Separator(self.main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=20, pady=5)

    def _create_selection_controls(self):
        """Crea los controles para seleccionar empresa y punto."""
        ttk.Label(
            self.content_frame, 
            text="Seleccione la empresa:", 
            font=('Helvetica', 12)
        ).pack(pady=(0, 5))
        
        self.company_combo = ttk.Combobox(
            self.content_frame, 
            values=[emp.nombre for emp in self.sistema.empresas]
        )
        self.company_combo.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(
            self.content_frame, 
            text="Seleccione el punto de atención:", 
            font=('Helvetica', 12)
        ).pack(pady=(0, 5))
        
        self.point_combo = ttk.Combobox(
            self.content_frame, 
            values=[p.nombre for p in self.sistema.empresas[0].puntos_atencion]
        )
        self.point_combo.pack(fill=tk.X, pady=(0, 15))

    def _create_transaction_controls(self):
        """Crea los checkboxes para seleccionar transacciones."""
        ttk.Label(
            self.content_frame, 
            text="Transacciones disponibles:", 
            font=('Helvetica', 12)
        ).pack(pady=(0, 5))
        
        transactions_frame = ttk.Frame(self.content_frame)
        transactions_frame.pack(fill=tk.X)
        
        # Usamos un diccionario para mapear IDs a objetos Transaccion
        self.transaction_vars = {}
        for trans in self.sistema.empresas[0].transacciones:
            var = tk.IntVar()
            self.transaction_vars[trans.id] = (var, trans)
            cb = tk.Checkbutton(
                transactions_frame, 
                text=f"{trans.nombre} ({trans.tiempo} min)", 
                variable=var, 
                onvalue=1,  # Usamos 1/0 en lugar de los IDs
                offvalue=0,
                bg=self.bg_color, 
                fg=self.text_color, 
                selectcolor=self.secondary_color,
                font=('Helvetica', 10)
            )
            cb.pack(anchor=tk.W, pady=2)

    def _create_footer(self):
        """Crea el pie de página con el estado."""
        footer_frame = ttk.Frame(self.main_frame)
        footer_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.status_label = ttk.Label(
            footer_frame, 
            text="Listo para solicitar atención", 
            font=('Helvetica', 10)
        )
        self.status_label.pack()

    def _handle_service_request(self):
        """Maneja la solicitud de atención del cliente."""
        # Validar selecciones
        if not self._validate_selections():
            return
            
        # Obtener transacciones seleccionadas
        selected_trans = self._get_selected_transactions()
        if not selected_trans:
            messagebox.showerror("Error", "Seleccione al menos una transacción")
            return
            
        # Procesar solicitud
        ticket, wait_time, service_time = self._process_client_request(selected_trans)
        
        # Mostrar ticket
        self._show_ticket(ticket, wait_time, service_time)
        self.status_label.config(text=f"Ticket {ticket} generado")

    def _validate_selections(self):
        """Valida que se hayan seleccionado empresa y punto."""
        if not self.company_combo.get() or not self.point_combo.get():
            messagebox.showerror("Error", "Seleccione empresa y punto de atención")
            return False
        return True

    def _get_selected_transactions(self):
        """Obtiene las transacciones seleccionadas usando el nuevo enfoque."""
        selected = []
        for trans_id, (var, trans) in self.transaction_vars.items():
            if var.get() == 1:  # Verificamos si el checkbox está marcado
                selected.append(trans)
        return selected

    def _process_client_request(self, transactions):
        """Procesa la solicitud del cliente en el sistema."""
        cliente = Cliente("123456789", "Cliente Ejemplo")
        cliente.transacciones = transactions
        
        punto = next(
            p for p in self.sistema.empresas[0].puntos_atencion 
            if p.nombre == self.point_combo.get()
        )
        
        return self.sistema.asignar_cliente(punto, cliente)
    
    def _show_ticket(self, ticket, wait_time, service_time):
        """Muestra el ticket de atención en una nueva ventana."""
        ticket_window = tk.Toplevel(self.root)
        ticket_window.title("Ticket de Atención")
        ticket_window.geometry("320x480")
        ticket_window.resizable(False, False)
        ticket_window.configure(bg=self.bg_color)
        
        ticket_frame = ttk.Frame(ticket_window)
        ticket_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Contenido del ticket
        ttk.Label(
            ticket_frame, 
            text="Soluciones Guatemaltecas", 
            font=('Helvetica', 14, 'bold')
        ).pack(pady=(0, 10))
        
        ttk.Separator(ticket_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        ttk.Label(
            ticket_frame, 
            text="Su número de atención es:", 
            font=('Helvetica', 12)
        ).pack(pady=(10, 5))
        
        ttk.Label(
            ticket_frame, 
            text=ticket, 
            font=('Helvetica', 24, 'bold'), 
            foreground=self.accent_color
        ).pack(pady=(0, 20))
        
        # Tiempos estimados
        time_labels = [
            ("Tiempo estimado de espera:", wait_time),
            ("Tiempo estimado de atención:", service_time)
        ]
        
        for label, time in time_labels:
            ttk.Label(
                ticket_frame, 
                text=label, 
                font=('Helvetica', 12)
            ).pack(pady=(10, 5))
            
            ttk.Label(
                ticket_frame, 
                text=f"{time} minutos", 
                font=('Helvetica', 16), 
                foreground=self.accent_color
            ).pack(pady=(0, 10))
        
        ttk.Button(
            ticket_frame, 
            text="Cerrar", 
            command=ticket_window.destroy
        ).pack(pady=20, fill=tk.X)

    def request_service(self):
        # Validar selecciones
        empresa_nombre = self.company_combo.get()
        punto_nombre = self.point_combo.get()
        
        if not empresa_nombre or not punto_nombre:
            messagebox.showerror("Error", "Seleccione empresa y punto de atención")
            return
            
        # Obtener transacciones seleccionadas
        selected = []
        for i, var in enumerate(self.check_vars):
            if var.get() > 0:
                trans = next(t for t in self.sistema.empresas[0].transacciones if t.id == var.get())
                selected.append(trans)
                
        if not selected:
            messagebox.showerror("Error", "Seleccione al menos una transacción")
            return
            
        # Crear cliente
        cliente = Cliente("123456789", "Cliente Ejemplo")
        cliente.transacciones = selected
        
        # Obtener punto de atención
        empresa = self.sistema.empresas[0]  # Simplificado para ejemplo
        punto = next(p for p in empresa.puntos_atencion if p.nombre == punto_nombre)
        
        # Asignar cliente al sistema
        ticket, tiempo_espera, tiempo_atencion = self.sistema.asignar_cliente(punto, cliente)
        
        # Mostrar ticket
        self.show_ticket(ticket, tiempo_espera, tiempo_atencion)
        
        # Actualizar estado
        self.status_label.config(text=f"Ticket {ticket} generado")

if __name__ == "__main__":
    root = tk.Tk()
    app = MobileAppSimulator(root)
    root.mainloop()
