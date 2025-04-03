import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random
import xml.etree.ElementTree as ET
from PIL import Image, ImageTk
from graphviz import Digraph
import os
import tempfile

# ==================== ESTRUCTURAS DE DATOS PERSONALIZADAS ====================

class Nodo:
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None

class ListaEnlazada:
    def __init__(self):
        self.cabeza = None
        self.longitud = 0
    
    def agregar(self, dato):
        nuevo_nodo = Nodo(dato)
        if not self.cabeza:
            self.cabeza = nuevo_nodo
        else:
            actual = self.cabeza
            while actual.siguiente:
                actual = actual.siguiente
            actual.siguiente = nuevo_nodo
        self.longitud += 1
    
    def __iter__(self):
        actual = self.cabeza
        while actual:
            yield actual.dato
            actual = actual.siguiente
    
    def __len__(self):
        return self.longitud
    
    def __getitem__(self, index):
        if index >= self.longitud:
            raise IndexError("Índice fuera de rango")
        actual = self.cabeza
        for _ in range(index):
            actual = actual.siguiente
        return actual.dato
    
    def buscar(self, condicion):
        actual = self.cabeza
        while actual:
            if condicion(actual.dato):
                return actual.dato
            actual = actual.siguiente
        return None
    
    def filtrar(self, condicion):
        resultado = ListaEnlazada()
        actual = self.cabeza
        while actual:
            if condicion(actual.dato):
                resultado.agregar(actual.dato)
            actual = actual.siguiente
        return resultado

class NodoDoble:
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None
        self.anterior = None

class ListaDoblementeEnlazada:
    def __init__(self):
        self.cabeza = None
        self.cola = None
        self.longitud = 0
    
    def agregar(self, dato):
        nuevo_nodo = NodoDoble(dato)
        if not self.cabeza:
            self.cabeza = nuevo_nodo
            self.cola = nuevo_nodo
        else:
            nuevo_nodo.anterior = self.cola
            self.cola.siguiente = nuevo_nodo
            self.cola = nuevo_nodo
        self.longitud += 1
    
    def __iter__(self):
        actual = self.cabeza
        while actual:
            yield actual.dato
            actual = actual.siguiente
    
    def __reversed__(self):
        actual = self.cola
        while actual:
            yield actual.dato
            actual = actual.anterior
    
    def __len__(self):
        return self.longitud

class DiccionarioPersonalizado:
    def __init__(self):
        self.tabla = [ListaEnlazada() for _ in range(10)]
        self.tamano = 0
    
    def _hash(self, clave):
        return hash(clave) % len(self.tabla)
    
    def agregar(self, clave, valor):
        indice = self._hash(clave)
        for nodo in self.tabla[indice]:
            if nodo[0] == clave:
                nodo[1] = valor
                return
        self.tabla[indice].agregar((clave, valor))
        self.tamano += 1
    
    def obtener(self, clave):
        indice = self._hash(clave)
        for nodo in self.tabla[indice]:
            if nodo[0] == clave:
                return nodo[1]
        raise KeyError(clave)
    
    def __contains__(self, clave):
        try:
            self.obtener(clave)
            return True
        except KeyError:
            return False
    
    def items(self):
        items = ListaEnlazada()
        for lista in self.tabla:
            for nodo in lista:
                items.agregar(nodo)
        return items

class ConjuntoPersonalizado:
    def __init__(self):
        self.diccionario = DiccionarioPersonalizado()
    
    def agregar(self, elemento):
        self.diccionario.agregar(elemento, True)
    
    def __contains__(self, elemento):
        return elemento in self.diccionario
    
    def __iter__(self):
        for clave, _ in self.diccionario.items():
            yield clave

# ==================== CLASES DEL MODELO (TDA) ====================

class Empresa:
    def __init__(self, id_empresa, nombre, abreviatura):
        self.id = id_empresa
        self.nombre = nombre
        self.abreviatura = abreviatura
        self.puntos_atencion = ListaEnlazada()
        self.transacciones = ListaEnlazada()

class PuntoAtencion:
    def __init__(self, id_punto, nombre, direccion):
        self.id = id_punto
        self.nombre = nombre
        self.direccion = direccion
        self.escritorios = ListaEnlazada()
        self.clientes_en_espera = ListaDoblementeEnlazada()
        self.clientes_atendidos = ListaDoblementeEnlazada()

class EscritorioServicio:
    def __init__(self, id_escritorio, identificacion, encargado):
        self.id = id_escritorio
        self.identificacion = identificacion
        self.encargado = encargado
        self.activo = False
        self.cliente_actual = None
        self.tiempo_restante = 0
        self.punto_atencion = None
        self.clientes_atendidos = ListaDoblementeEnlazada()

class Transaccion:
    def __init__(self, id_transaccion, nombre, tiempo_atencion):
        self.id = id_transaccion
        self.nombre = nombre
        self.tiempo = tiempo_atencion

class Cliente:
    def __init__(self, dpi, nombre):
        self.dpi = dpi
        self.nombre = nombre
        self.transacciones = ListaEnlazada()
        self.tiempo_espera = 0
        self.ticket = None

# ==================== SISTEMA DE ATENCIÓN ====================

class SistemaAtencion:
    def __init__(self):
        self.empresas = ListaEnlazada()  
        self.tickets_generados = ConjuntoPersonalizado()
        self.tiempo_simulado = 0

    def generar_ticket_unico(self):
        while True:
            ticket = f"{random.randint(100, 999)}-{random.randint(1000, 9999)}"
            if ticket not in self.tickets_generados:
                self.tickets_generados.agregar(ticket)
                return ticket

    def agregar_empresa(self, empresa):
        # Verificar si la empresa ya existe
        empresa_existente = next((e for e in self.empresas if e.id == empresa.id), None)
        if not empresa_existente:
            self.empresas.agregar(empresa)
            return True
        return False

    def _crear_cliente_desde_xml(self, cliente_xml, empresa):
        cliente = Cliente(
            cliente_xml.get('dpi'),
            cliente_xml.find('nombre').text.strip()
        )
        
        # Cargar transacciones del cliente
        transacciones = cliente_xml.find('listadoTransacciones')
        if transacciones is not None:
            for trans_xml in transacciones.findall('transaccion'):
                trans_id = trans_xml.get('idTransaccion')
                cantidad = int(trans_xml.get('cantidad', 1))
                
                transaccion = next((t for t in empresa.transacciones if t.id == trans_id), None)
                if transaccion:
                    for _ in range(cantidad):
                        cliente.transacciones.agregar(transaccion)
        
        return cliente

    def asignar_cliente_a_escritorio(self, escritorio, cliente):
        if escritorio.activo and escritorio.cliente_actual is None:
            escritorio.cliente_actual = cliente
            escritorio.tiempo_restante = sum(t.tiempo for t in cliente.transacciones)
            return True
        return False

    def asignar_cliente(self, punto_atencion, cliente):
        # Calcular tiempo total de atención
        tiempo_total = sum(t.tiempo for t in cliente.transacciones)
        
        # Generar ticket único
        cliente.ticket = self.generar_ticket_unico()
        
        # Calcular tiempo de espera estimado
        escritorios_activos = [e for e in punto_atencion.escritorios if e.activo]
        
        if not escritorios_activos:
            tiempo_espera = tiempo_total  # Si no hay escritorios activos
        else:
            # Calcular carga de trabajo por escritorio
            carga_escritorios = [sum(c.tiempo_espera for c in punto_atencion.clientes_en_espera) / len(escritorios_activos)]
            tiempo_espera = max(carga_escritorios) + tiempo_total
        
        cliente.tiempo_espera = tiempo_espera
        punto_atencion.clientes_en_espera.agregar(cliente)
        
        # Intentar asignar inmediatamente a un escritorio disponible
        for escritorio in escritorios_activos:
            if escritorio.cliente_actual is None:
                self.asignar_cliente_a_escritorio(escritorio, cliente)
                break
        
        return cliente.ticket, tiempo_espera, tiempo_total

    def avanzar_tiempo(self, minutos):
        self.tiempo_simulado += minutos
        for empresa in self.empresas:
            for punto in empresa.puntos_atencion:
                # Avanzar tiempo en escritorios activos
                for escritorio in punto.escritorios:
                    if escritorio.activo and escritorio.cliente_actual:
                        escritorio.tiempo_restante -= minutos
                        
                        if escritorio.tiempo_restante <= 0:
                            # Cliente atendido completamente
                            punto.clientes_atendidos.agregar(escritorio.cliente_actual)
                            escritorio.clientes_atendidos.agregar(escritorio.cliente_actual)
                            escritorio.cliente_actual = None
                            
                            # Asignar siguiente cliente si hay
                            if len(punto.clientes_en_espera) > 0:
                                siguiente_cliente = punto.clientes_en_espera[0]
                                punto.clientes_en_espera.cabeza = punto.clientes_en_espera.cabeza.siguiente
                                if punto.clientes_en_espera.cabeza is None:
                                    punto.clientes_en_espera.cola = None
                                self.asignar_cliente_a_escritorio(escritorio, siguiente_cliente)
                
                # Actualizar tiempos de espera estimados
                escritorios_activos = sum(1 for e in punto.escritorios if e.activo)
                if escritorios_activos > 0:
                    tiempo_por_escritorio = sum(c.tiempo_espera for c in punto.clientes_en_espera) / escritorios_activos
                    for i, cliente in enumerate(punto.clientes_en_espera):
                        cliente.tiempo_espera = tiempo_por_escritorio * (i + 1)

    def calcular_tiempos_punto(self, punto):
        tiempos_espera = []
        tiempos_atencion = []
        
        # Recorrer clientes atendidos
        for cliente in punto.clientes_atendidos:
            tiempos_atencion.append(sum(t.tiempo for t in cliente.transacciones))
        
        # Recorrer clientes en espera
        for cliente in punto.clientes_en_espera:
            tiempos_espera.append(cliente.tiempo_espera)
        
        # Calcular estadísticas
        stats = {
            "max_espera": max(tiempos_espera) if tiempos_espera else 0,
            "min_espera": min(tiempos_espera) if tiempos_espera else 0,
            "promedio_espera": sum(tiempos_espera)/len(tiempos_espera) if tiempos_espera else 0,
            "max_atencion": max(tiempos_atencion) if tiempos_atencion else 0,
            "min_atencion": min(tiempos_atencion) if tiempos_atencion else 0,
            "promedio_atencion": sum(tiempos_atencion)/len(tiempos_atencion) if tiempos_atencion else 0,
            "total_clientes": len(tiempos_atencion)
        }
        
        return stats

    def calcular_tiempos_escritorio(self, escritorio):
        tiempos = []
        
        for cliente in escritorio.clientes_atendidos:
            tiempos.append(sum(t.tiempo for t in cliente.transacciones))
        
        stats = {
            "max_atencion": max(tiempos) if tiempos else 0,
            "min_atencion": min(tiempos) if tiempos else 0,
            "promedio_atencion": sum(tiempos)/len(tiempos) if tiempos else 0,
            "total_clientes": len(tiempos)
        }
        
        return stats

    def cargar_configuracion_xml(self, archivo):
        try:
            tree = ET.parse(archivo)
            root = tree.getroot()
            
            if root.tag != 'listaEmpresas':
                raise ValueError("El archivo debe comenzar con <listaEmpresas>")
            
            for empresa_xml in root.findall('empresa'):
                empresa_id = empresa_xml.get('id')
                # Verificar si la empresa ya existe
                empresa_existente = next((e for e in self.empresas if e.id == empresa_id), None)
                
                if empresa_existente:
                    # Actualizar datos de empresa existente
                    empresa_existente.nombre = empresa_xml.find('nombre').text.strip()
                    empresa_existente.abreviatura = empresa_xml.find('abreviatura').text.strip()
                    empresa = empresa_existente
                else:
                    # Crear nueva empresa
                    empresa = Empresa(
                        empresa_id,
                        empresa_xml.find('nombre').text.strip(),
                        empresa_xml.find('abreviatura').text.strip()
                    )
                    self.empresas.agregar(empresa)
                
                # Cargar puntos de atención
                puntos = empresa_xml.find('listaPuntosAtencion')
                if puntos is not None:
                    for punto_xml in puntos.findall('puntoAtencion'):
                        punto_id = punto_xml.get('id')
                        # Verificar si el punto ya existe
                        punto_existente = next((p for p in empresa.puntos_atencion if p.id == punto_id), None)
                        
                        if punto_existente:
                            # Actualizar punto existente
                            punto_existente.nombre = punto_xml.find('nombre').text.strip()
                            punto_existente.direccion = punto_xml.find('direccion').text.strip()
                            punto = punto_existente
                        else:
                            # Crear nuevo punto
                            punto = PuntoAtencion(
                                punto_id,
                                punto_xml.find('nombre').text.strip(),
                                punto_xml.find('direccion').text.strip()
                            )
                            empresa.puntos_atencion.agregar(punto)
                        
                        # Cargar escritorios
                        escritorios = punto_xml.find('listaEscritorios')
                        if escritorios is not None:
                            for esc_xml in escritorios.findall('escritorio'):
                                esc_id = esc_xml.get('id')
                                # Verificar si el escritorio ya existe
                                esc_existente = next((e for e in punto.escritorios if e.id == esc_id), None)
                                
                                if esc_existente:
                                    # Actualizar escritorio existente
                                    esc_existente.identificacion = esc_xml.find('identificacion').text.strip()
                                    esc_existente.encargado = esc_xml.find('encargado').text.strip()
                                else:
                                    # Crear nuevo escritorio
                                    escritorio = EscritorioServicio(
                                        esc_id,
                                        esc_xml.find('identificacion').text.strip(),
                                        esc_xml.find('encargado').text.strip()
                                    )
                                    escritorio.punto_atencion = punto
                                    punto.escritorios.agregar(escritorio)
                
                # Cargar transacciones
                transacciones = empresa_xml.find('listaTransacciones')
                if transacciones is not None:
                    for trans_xml in transacciones.findall('transaccion'):
                        trans_id = trans_xml.get('id')
                        # Verificar si la transacción ya existe
                        trans_existente = next((t for t in empresa.transacciones if t.id == trans_id), None)
                        
                        if trans_existente:
                            # Actualizar transacción existente
                            trans_existente.nombre = trans_xml.find('nombre').text.strip()
                            trans_existente.tiempo = int(trans_xml.find('tiempoAtencion').text)
                        else:
                            # Crear nueva transacción
                            try:
                                tiempo = int(trans_xml.find('tiempoAtencion').text)
                            except ValueError:
                                tiempo = 0
                            
                            trans = Transaccion(
                                trans_id,
                                trans_xml.find('nombre').text.strip(),
                                tiempo
                            )
                            empresa.transacciones.agregar(trans)
            
            return True if len(self.empresas) > 0 else False
            
        except Exception as e:
            messagebox.showerror("Error XML", f"Error al cargar configuración:\n{str(e)}")
            return False
    
    def cargar_estado_inicial_xml(self, archivo):
        try:
            if len(self.empresas) == 0:
                raise ValueError("Primero cargue el archivo de configuración")
                
            tree = ET.parse(archivo)
            root = tree.getroot()
            
            for config_xml in root.findall('configInicial'):
                empresa_id = config_xml.get('idEmpresa')
                punto_id = config_xml.get('idPunto')
                
                empresa = next((e for e in self.empresas if e.id == empresa_id), None)
                if not empresa:
                    continue
                    
                punto = next((p for p in empresa.puntos_atencion if p.id == punto_id), None)
                if not punto:
                    continue
                
                # Activar escritorios
                escritorios_activos = []
                escritorios_xml = config_xml.find('escritoriosActivos')
                if escritorios_xml is not None:
                    for esc_xml in escritorios_xml.findall('escritorio'):
                        esc_id = esc_xml.get('idEscritorio')
                        escritorio = next((e for e in punto.escritorios if e.id == esc_id), None)
                        if escritorio:
                            escritorio.activo = True
                            escritorios_activos.append(escritorio)
                
                # Cargar y distribuir clientes
                clientes_xml = config_xml.find('listadoClientes')
                if clientes_xml is not None and escritorios_activos:
                    for i, cliente_xml in enumerate(clientes_xml.findall('cliente')):
                        cliente = self._crear_cliente_desde_xml(cliente_xml, empresa)
                        punto.clientes_en_espera.agregar(cliente)
                        
                        # Distribuir cliente a escritorio (round-robin)
                        escritorio_asignado = escritorios_activos[i % len(escritorios_activos)]
                        self.asignar_cliente_a_escritorio(escritorio_asignado, cliente)
            
            # Avanzar tiempo para procesar la configuración inicial
            self.avanzar_tiempo(0)
            return True
            
        except Exception as e:
            messagebox.showerror("Error XML", f"Error al cargar estado inicial:\n{str(e)}")
            return False

    def generar_reporte_empresa(self, empresa_id):
        empresa = next((e for e in self.empresas if e.id == empresa_id), None)
        if not empresa:
            return None
            
        dot = Digraph(comment=f'Empresa {empresa.nombre}')
        dot.attr('graph', rankdir='LR', bgcolor='#f0e6ff')
        
        # Nodo principal de la empresa
        dot.node('empresa', 
                f'<<B>Empresa:</B> {empresa.nombre} ({empresa.abreviatura})\n<B>ID:</B> {empresa.id}>',
                shape='box', style='filled', fillcolor='#b399d4', fontcolor='white')
        
        # Puntos de atención
        with dot.subgraph(name='cluster_puntos') as c:
            c.attr(label='Puntos de Atención', color='#8a6dae', fontcolor='#4a3b5f')
            for punto in empresa.puntos_atencion:
                stats = self.calcular_tiempos_punto(punto)
                c.node(f'p{punto.id}', 
                      f'<<B>Punto:</B> {punto.nombre}\n<B>Dirección:</B> {punto.direccion}\n'
                      f'<B>Clientes:</B> {stats["total_clientes"]}\n'
                      f'<B>Espera prom.:</B> {stats["promedio_espera"]:.1f} min>',
                      shape='ellipse', style='filled', fillcolor='#d9c2ff')
                dot.edge('empresa', f'p{punto.id}')
                
                # Escritorios
                with c.subgraph(name=f'cluster_escritorios_{punto.id}') as e:
                    e.attr(label='Escritorios', color='#8a6dae')
                    for escritorio in punto.escritorios:
                        estado = "ACTIVO" if escritorio.activo else "INACTIVO"
                        color = "#4CAF50" if escritorio.activo else "#F44336"
                        stats_esc = self.calcular_tiempos_escritorio(escritorio)
                        e.node(f'e{escritorio.id}',
                              f'<<B>Escritorio:</B> {escritorio.identificacion}\n'
                              f'<B>Encargado:</B> {escritorio.encargado}\n'
                              f'<B>Estado:</B> {estado}\n'
                              f'<B>Atendidos:</B> {stats_esc["total_clientes"]}\n'
                              f'<B>Atención prom.:</B> {stats_esc["promedio_atencion"]:.1f} min>',
                              shape='box', style='filled', fillcolor=color, fontcolor='white')
                        c.edge(f'p{punto.id}', f'e{escritorio.id}')
        
        # Transacciones
        with dot.subgraph(name='cluster_transacciones') as t:
            t.attr(label='Transacciones Disponibles', color='#8a6dae')
            for trans in empresa.transacciones:
                t.node(f't{trans.id}',
                      f'<{trans.nombre}\n<B>Tiempo:</B> {trans.tiempo} min>',
                      shape='note', style='filled', fillcolor='#d9c2ff')
                dot.edge('empresa', f't{trans.id}')
        
        return dot

    def generar_reporte_punto_atencion(self, punto_id):
        punto, empresa = self._buscar_punto(punto_id)
        if not punto:
            return None
            
        dot = Digraph(comment=f'Punto {punto.nombre}')
        dot.attr('graph', bgcolor='#f0e6ff')
        
        # Calcular estadísticas
        stats = self.calcular_tiempos_punto(punto)
        
        # Encabezado con estadísticas
        dot.node('header', 
                f'<<B>Punto de Atención:</B> {punto.nombre}\n'
                f'<B>Empresa:</B> {empresa.nombre}\n'
                f'<B>Dirección:</B> {punto.direccion}\n'
                f'<B>Estadísticas:</B>\n'
                f'• Máx espera: {stats["max_espera"]} min\n'
                f'• Mín espera: {stats["min_espera"]} min\n'
                f'• Promedio espera: {stats["promedio_espera"]:.1f} min\n'
                f'• Máx atención: {stats["max_atencion"]} min\n'
                f'• Mín atención: {stats["min_atencion"]} min\n'
                f'• Promedio atención: {stats["promedio_atencion"]:.1f} min>',
                shape='box', style='filled', fillcolor='#b399d4', fontcolor='white')
        
        # Escritorios
        with dot.subgraph(name='cluster_escritorios') as e:
            e.attr(label='Escritorios', color='#8a6dae')
            for escritorio in punto.escritorios:
                estado = "ACTIVO" if escritorio.activo else "INACTIVO"
                color = "#4CAF50" if escritorio.activo else "#F44336"
                stats_esc = self.calcular_tiempos_escritorio(escritorio)
                
                if escritorio.cliente_actual:
                    cliente_info = f'<B>Cliente actual:</B> {escritorio.cliente_actual.nombre}\n<B>T. restante:</B> {escritorio.tiempo_restante} min'
                else:
                    cliente_info = "Sin cliente asignado"
                
                e.node(f'e{escritorio.id}',
                      f'<<B>Escritorio:</B> {escritorio.identificacion}\n'
                      f'<B>Encargado:</B> {escritorio.encargado}\n'
                      f'<B>Estado:</B> {estado}\n'
                      f'<B>Atendidos:</B> {stats_esc["total_clientes"]}\n'
                      f'<B>Atención prom.:</B> {stats_esc["promedio_atencion"]:.1f} min\n'
                      f'{cliente_info}>',
                      shape='box', style='filled', fillcolor=color, fontcolor='white')
        
        # Cola de clientes
        if len(punto.clientes_en_espera) > 0:
            with dot.subgraph(name='cluster_cola') as c:
                c.attr(label='Clientes en Espera', color='#8a6dae')
                for i, cliente in enumerate(punto.clientes_en_espera):
                    transacciones = "\n".join([f"• {t.nombre} ({t.tiempo} min)" for t in cliente.transacciones])
                    c.node(f'c{i}',
                          f'<<B>Cliente:</B> {cliente.nombre}\n'
                          f'<B>Ticket:</B> {cliente.ticket}\n'
                          f'<B>Tiempo estimado:</B> {cliente.tiempo_espera} min\n'
                          f'<B>Transacciones:</B>\n{transacciones}>',
                          shape='box', style='rounded,filled', fillcolor='#d9c2ff')
                    if i > 0:
                        c.edge(f'c{i-1}', f'c{i}')
        
        return dot

    def _buscar_punto(self, punto_id):
        """Busca un punto de atención por ID y devuelve el punto y su empresa"""
        for empresa in self.empresas:
            for punto in empresa.puntos_atencion:
                if punto.id == punto_id:
                    return punto, empresa
        return None, None
    
    def limpiar_sistema(self):
        """Limpia todos los datos del sistema"""
        self.empresas = ListaEnlazada()
        self.tickets_generados = ConjuntoPersonalizado()
        self.tiempo_simulado = 0

# ==================== INTERFAZ GRÁFICA ====================
class MobileAppSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Atención a Clientes")
        self.root.geometry("360x640")
        self.root.resizable(False, False)
        
        # Configurar estilos primero
        self._configure_styles()
        
        # Sistema de atención - Inicia vacío
        self.sistema = SistemaAtencion()
        
        # Variables de control
        self.transaction_vars = DiccionarioPersonalizado()
        
        # Crear interfaz
        self._create_widgets()
        self._create_menu()

    def _configure_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.bg_color = "#f0e6ff"
        self.primary_color = "#b399d4"
        self.secondary_color = "#d9c2ff"
        self.accent_color = "#8a6dae"
        self.text_color = "#4a3b5f"
        
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TLabel', background=self.bg_color, foreground=self.text_color)
        self.style.configure('TButton', 
                          background=self.primary_color, 
                          foreground='white', 
                          font=('Helvetica', 10, 'bold'), 
                          padding=10)
        self.style.map('TButton', 
                     background=[('active', self.accent_color), ('pressed', self.accent_color)])

    def _create_menu(self):
        menubar = tk.Menu(self.root)
        
            # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Cargar Configuración XML", command=self._load_config_xml)
        file_menu.add_command(label="Cargar Estado Inicial XML", command=self._load_initial_state_xml)
        file_menu.add_command(label="Guardar Configuración", command=self._save_config_xml)
        file_menu.add_separator()
        file_menu.add_command(label="Nueva Empresa", command=self._crear_empresa)
        file_menu.add_command(label="Nuevo Punto de Atención", command=self._crear_punto_atencion)
        file_menu.add_command(label="Nuevo Escritorio", command=self._crear_escritorio)
        file_menu.add_separator()
        file_menu.add_command(label="Limpiar Todo", command=self._limpiar_todo)
        file_menu.add_command(label="Salir", command=self.root.quit)
        
        # Menú Reportes
        report_menu = tk.Menu(menubar, tearoff=0)
        report_menu.add_command(label="Reporte de Empresa", command=self._generar_reporte_empresa)
        report_menu.add_command(label="Reporte de Punto", command=self._generar_reporte_punto)
        report_menu.add_command(label="Reporte de Colas", command=self._generar_reporte_colas)
        
        # Menú Simulación
        sim_menu = tk.Menu(menubar, tearoff=0)
        sim_menu.add_command(label="Simular 5 minutos", command=lambda: self._simular_tiempo(5))
        sim_menu.add_command(label="Simular 15 minutos", command=lambda: self._simular_tiempo(15))
        
        # Menú Ayuda
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Acerca de", command=self._mostrar_acerca_de)
        
        menubar.add_cascade(label="Archivo", menu=file_menu)
        menubar.add_cascade(label="Reportes", menu=report_menu)
        menubar.add_cascade(label="Simulación", menu=sim_menu)
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        
        self.root.config(menu=menubar)

    def _mostrar_acerca_de(self):
        acerca_de = """
===== DATOS DEL ESTUDIANTE =====
Nombre: Mario Rene Merida Taracena
Carné: 202111134
Curso: Introducción a la Programación y Computación 2
Carrera: Ingeniería en Ciencias y Sistemas
Semestre: 1er semestre - 2025
Enlace a la documentación: https://github.com/MarioRene/IPC2_Proyecto2_202111134.git
            """
        messagebox.showinfo("Acerca de", acerca_de)

    def _crear_empresa(self):
        # Ventana para ingresar datos de la nueva empresa
        dialog = tk.Toplevel(self.root)
        dialog.title("Nueva Empresa")
        dialog.geometry("300x200")
        dialog.resizable(False, False)
        
        tk.Label(dialog, text="ID de Empresa:").pack(pady=(10, 0))
        id_entry = tk.Entry(dialog)
        id_entry.pack(pady=5)
        
        tk.Label(dialog, text="Nombre:").pack()
        nombre_entry = tk.Entry(dialog)
        nombre_entry.pack(pady=5)
        
        tk.Label(dialog, text="Abreviatura:").pack()
        abreviatura_entry = tk.Entry(dialog)
        abreviatura_entry.pack(pady=5)
        
        def guardar_empresa():
            id_empresa = id_entry.get().strip()
            nombre = nombre_entry.get().strip()
            abreviatura = abreviatura_entry.get().strip()
            
            if not id_empresa or not nombre or not abreviatura:
                messagebox.showerror("Error", "Todos los campos son obligatorios")
                return
                
            # Verificar si la empresa ya existe
            empresa_existente = next((e for e in self.sistema.empresas if e.id == id_empresa), None)
            if empresa_existente:
                messagebox.showerror("Error", f"Ya existe una empresa con ID {id_empresa}")
                return
                
            # Crear nueva empresa
            nueva_empresa = Empresa(id_empresa, nombre, abreviatura)
            self.sistema.empresas.agregar(nueva_empresa)
            messagebox.showinfo("Éxito", "Empresa creada correctamente")
            self._update_ui_after_load()
            dialog.destroy()
        
        tk.Button(dialog, text="Guardar", command=guardar_empresa).pack(pady=10)

    def _crear_punto_atencion(self):
        if len(self.sistema.empresas) == 0:
            messagebox.showwarning("Advertencia", "Primero debe crear una empresa")
            return
            
        # Ventana para seleccionar empresa y crear punto
        dialog = tk.Toplevel(self.root)
        dialog.title("Nuevo Punto de Atención")
        dialog.geometry("300x250")
        dialog.resizable(False, False)
        
        tk.Label(dialog, text="Seleccione la empresa:").pack(pady=(10, 0))
        
        empresa_var = tk.StringVar()
        empresas = [emp.nombre for emp in self.sistema.empresas]
        empresa_combobox = ttk.Combobox(dialog, textvariable=empresa_var, values=empresas, state="readonly")
        empresa_combobox.pack(pady=5)
        empresa_combobox.current(0)
        
        tk.Label(dialog, text="ID del Punto:").pack()
        id_entry = tk.Entry(dialog)
        id_entry.pack(pady=5)
        
        tk.Label(dialog, text="Nombre:").pack()
        nombre_entry = tk.Entry(dialog)
        nombre_entry.pack(pady=5)
        
        tk.Label(dialog, text="Dirección:").pack()
        direccion_entry = tk.Entry(dialog)
        direccion_entry.pack(pady=5)
        
        def guardar_punto():
            empresa_nombre = empresa_var.get()
            id_punto = id_entry.get().strip()
            nombre = nombre_entry.get().strip()
            direccion = direccion_entry.get().strip()
            
            if not empresa_nombre or not id_punto or not nombre or not direccion:
                messagebox.showerror("Error", "Todos los campos son obligatorios")
                return
                
            # Buscar la empresa seleccionada
            empresa = next((e for e in self.sistema.empresas if e.nombre == empresa_nombre), None)
            if not empresa:
                messagebox.showerror("Error", "Empresa no encontrada")
                return
                
            # Verificar si el punto ya existe
            punto_existente = next((p for p in empresa.puntos_atencion if p.id == id_punto), None)
            if punto_existente:
                messagebox.showerror("Error", f"Ya existe un punto con ID {id_punto} en esta empresa")
                return
                
            # Crear nuevo punto
            nuevo_punto = PuntoAtencion(id_punto, nombre, direccion)
            empresa.puntos_atencion.agregar(nuevo_punto)
            messagebox.showinfo("Éxito", "Punto de atención creado correctamente")
            self._update_ui_after_load()
            dialog.destroy()
        
        tk.Button(dialog, text="Guardar", command=guardar_punto).pack(pady=10)

    def _crear_escritorio(self):
        if len(self.sistema.empresas) == 0:
            messagebox.showwarning("Advertencia", "Primero debe crear una empresa")
            return
            
        # Ventana para seleccionar empresa, punto y crear escritorio
        dialog = tk.Toplevel(self.root)
        dialog.title("Nuevo Escritorio")
        dialog.geometry("300x300")
        dialog.resizable(False, False)
        
        tk.Label(dialog, text="Seleccione la empresa:").pack(pady=(10, 0))
        
        empresa_var = tk.StringVar()
        empresas = [emp.nombre for emp in self.sistema.empresas]
        empresa_combobox = ttk.Combobox(dialog, textvariable=empresa_var, values=empresas, state="readonly")
        empresa_combobox.pack(pady=5)
        empresa_combobox.current(0)
        empresa_combobox.bind("<<ComboboxSelected>>", lambda e: self._actualizar_puntos_combobox(dialog, empresa_var.get()))
        
        tk.Label(dialog, text="Seleccione el punto:").pack()
        
        self.punto_var = tk.StringVar()
        self.punto_combobox = ttk.Combobox(dialog, textvariable=self.punto_var, state="readonly")
        self.punto_combobox.pack(pady=5)
        self._actualizar_puntos_combobox(dialog, empresas[0])
        
        tk.Label(dialog, text="ID del Escritorio:").pack()
        id_entry = tk.Entry(dialog)
        id_entry.pack(pady=5)
        
        tk.Label(dialog, text="Identificación:").pack()
        identificacion_entry = tk.Entry(dialog)
        identificacion_entry.pack(pady=5)
        
        tk.Label(dialog, text="Encargado:").pack()
        encargado_entry = tk.Entry(dialog)
        encargado_entry.pack(pady=5)
        
        def guardar_escritorio():
            empresa_nombre = empresa_var.get()
            punto_nombre = self.punto_var.get()
            id_escritorio = id_entry.get().strip()
            identificacion = identificacion_entry.get().strip()
            encargado = encargado_entry.get().strip()
            
            if not empresa_nombre or not punto_nombre or not id_escritorio or not identificacion or not encargado:
                messagebox.showerror("Error", "Todos los campos son obligatorios")
                return
                
            # Buscar la empresa y punto seleccionados
            empresa = next((e for e in self.sistema.empresas if e.nombre == empresa_nombre), None)
            if not empresa:
                messagebox.showerror("Error", "Empresa no encontrada")
                return
                
            punto = next((p for p in empresa.puntos_atencion if p.nombre == punto_nombre), None)
            if not punto:
                messagebox.showerror("Error", "Punto de atención no encontrado")
                return
                
            # Verificar si el escritorio ya existe
            escritorio_existente = next((e for e in punto.escritorios if e.id == id_escritorio), None)
            if escritorio_existente:
                messagebox.showerror("Error", f"Ya existe un escritorio con ID {id_escritorio} en este punto")
                return
                
            # Crear nuevo escritorio
            nuevo_escritorio = EscritorioServicio(id_escritorio, identificacion, encargado)
            nuevo_escritorio.punto_atencion = punto
            punto.escritorios.agregar(nuevo_escritorio)
            messagebox.showinfo("Éxito", "Escritorio creado correctamente")
            self._update_ui_after_load()
            dialog.destroy()
        
        tk.Button(dialog, text="Guardar", command=guardar_escritorio).pack(pady=10)

    def _actualizar_puntos_combobox(self, dialog, empresa_nombre):
        empresa = next((e for e in self.sistema.empresas if e.nombre == empresa_nombre), None)
        if empresa:
            puntos = [p.nombre for p in empresa.puntos_atencion]
            self.punto_combobox['values'] = puntos
            if puntos:
                self.punto_combobox.current(0)

    def _save_config_xml(self):
        if len(self.sistema.empresas) == 0:
            messagebox.showwarning("Advertencia", "No hay datos para guardar")
            return
            
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xml",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )
        
        if filepath:
            try:
                # Crear estructura XML
                root = ET.Element("listaEmpresas")
                
                for empresa in self.sistema.empresas:
                    empresa_elem = ET.SubElement(root, "empresa", id=empresa.id)
                    
                    ET.SubElement(empresa_elem, "nombre").text = empresa.nombre
                    ET.SubElement(empresa_elem, "abreviatura").text = empresa.abreviatura
                    
                    # Puntos de atención
                    puntos_elem = ET.SubElement(empresa_elem, "listaPuntosAtencion")
                    for punto in empresa.puntos_atencion:
                        punto_elem = ET.SubElement(puntos_elem, "puntoAtencion", id=punto.id)
                        ET.SubElement(punto_elem, "nombre").text = punto.nombre
                        ET.SubElement(punto_elem, "direccion").text = punto.direccion
                        
                        # Escritorios
                        escritorios_elem = ET.SubElement(punto_elem, "listaEscritorios")
                        for escritorio in punto.escritorios:
                            esc_elem = ET.SubElement(escritorios_elem, "escritorio", id=escritorio.id)
                            ET.SubElement(esc_elem, "identificacion").text = escritorio.identificacion
                            ET.SubElement(esc_elem, "encargado").text = escritorio.encargado
                    
                    # Transacciones
                    transacciones_elem = ET.SubElement(empresa_elem, "listaTransacciones")
                    for trans in empresa.transacciones:
                        trans_elem = ET.SubElement(transacciones_elem, "transaccion", id=trans.id)
                        ET.SubElement(trans_elem, "nombre").text = trans.nombre
                        ET.SubElement(trans_elem, "tiempoAtencion").text = str(trans.tiempo)
                
                # Guardar XML
                tree = ET.ElementTree(root)
                tree.write(filepath, encoding='utf-8', xml_declaration=True)
                messagebox.showinfo("Éxito", f"Configuración guardada en:\n{filepath}")
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar la configuración:\n{str(e)}")

    def _simular_tiempo(self, minutos):
        self.sistema.avanzar_tiempo(minutos)
        messagebox.showinfo("Simulación", f"Se avanzó {minutos} minutos en la simulación")
        self._update_ui_after_load()

    def _limpiar_todo(self):
        """Limpia todos los datos cargados"""
        self.sistema.limpiar_sistema()
        self._update_ui_after_load()
        messagebox.showinfo("Información", "Todos los datos han sido limpiados")
    
    def _generar_reporte_empresa(self):
        if len(self.sistema.empresas) == 0:
            messagebox.showwarning("Advertencia", "No hay empresas cargadas")
            return
            
        empresa_id = self.sistema.empresas[0].id
        dot = self.sistema.generar_reporte_empresa(empresa_id)
        
        if dot:
            self._mostrar_reporte(dot, f"reporte_empresa_{empresa_id}")
    
    def _generar_reporte_punto(self):
        if len(self.sistema.empresas) == 0 or len(self.sistema.empresas[0].puntos_atencion) == 0:
            messagebox.showwarning("Advertencia", "No hay puntos de atención cargados")
            return
            
        punto_id = self.sistema.empresas[0].puntos_atencion[0].id
        dot = self.sistema.generar_reporte_punto_atencion(punto_id)
        
        if dot:
            self._mostrar_reporte(dot, f"reporte_punto_{punto_id}")
    
    def _generar_reporte_colas(self):
        if len(self.sistema.empresas) == 0:
            messagebox.showwarning("Advertencia", "No hay datos cargados")
            return
            
        dot = Digraph(comment='Colas de Espera')
        dot.attr('graph', rankdir='LR', bgcolor='#f0e6ff')
        
        for empresa in self.sistema.empresas:
            for punto in empresa.puntos_atencion:
                if len(punto.clientes_en_espera) > 0:
                    with dot.subgraph(name=f'cluster_{punto.id}') as c:
                        c.attr(label=f'{empresa.nombre} - {punto.nombre}', color='#8a6dae')
                        for i, cliente in enumerate(punto.clientes_en_espera):
                            c.node(f'{punto.id}_c{i}',
                                  f'<{cliente.nombre}\nTicket: {cliente.ticket}\nTiempo: {cliente.tiempo_espera} min>',
                                  shape='box', style='filled', fillcolor='#d9c2ff')
                            if i > 0:
                                c.edge(f'{punto.id}_c{i-1}', f'{punto.id}_c{i}')
        
        self._mostrar_reporte(dot, "reporte_colas")
    
    def _mostrar_reporte(self, dot, filename):
        try:
            temp_dir = tempfile.mkdtemp()
            filepath = os.path.join(temp_dir, filename)
            
            dot.format = 'png'
            dot.render(filepath, view=False, cleanup=True)
            
            report_window = tk.Toplevel(self.root)
            report_window.title("Visualización de Reporte")
            report_window.geometry("800x600")
            
            img = Image.open(filepath + '.png')
            img = ImageTk.PhotoImage(img)
            
            label = tk.Label(report_window, image=img)
            label.image = img
            label.pack(expand=True, fill='both')
            
            ttk.Button(
                report_window,
                text="Guardar Reporte",
                command=lambda: self._guardar_reporte(filepath + '.png')
            ).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el reporte:\n{str(e)}")
    
    def _guardar_reporte(self, temp_file):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if filepath:
            try:
                import shutil
                shutil.copy(temp_file, filepath)
                messagebox.showinfo("Éxito", f"Reporte guardado en:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el reporte:\n{str(e)}")
    
    def _load_config_xml(self):
        filepath = filedialog.askopenfilename(
            title="Seleccionar archivo de configuración",
            filetypes=[("XML files", "*.xml")]
        )
        if filepath:
            if self.sistema.cargar_configuracion_xml(filepath):
                messagebox.showinfo("Éxito", "Configuración cargada correctamente")
                self._update_ui_after_load()
            else:
                messagebox.showwarning("Advertencia", "No se cargaron empresas del archivo")
    
    def _load_initial_state_xml(self):
        if len(self.sistema.empresas) == 0:
            messagebox.showwarning("Advertencia", "Primero cargue el archivo de configuración")
            return
            
        filepath = filedialog.askopenfilename(
            title="Seleccionar archivo de estado inicial",
            filetypes=[("XML files", "*.xml")]
        )
        if filepath:
            if self.sistema.cargar_estado_inicial_xml(filepath):
                messagebox.showinfo("Éxito", "Estado inicial cargado correctamente")
                self._update_ui_after_load()
    
    def _update_ui_after_load(self):
        # Limpiar combobox existentes
        self.company_combo['values'] = []
        self.point_combo['values'] = []
        self.company_combo.set('')
        self.point_combo.set('')
        
        # Limpiar checkboxes de transacciones
        for widget in self.transactions_frame.winfo_children():
            widget.destroy()
        
        self.transaction_vars = DiccionarioPersonalizado()
        
        # Actualizar con nuevos datos si existen
        if len(self.sistema.empresas) > 0:
            self.company_combo['values'] = [emp.nombre for emp in self.sistema.empresas]
            self.company_combo.current(0)
            self._update_points_combo()
            
            # Actualizar transacciones de la primera empresa (por defecto)
            if len(self.sistema.empresas[0].transacciones) > 0:
                for trans in self.sistema.empresas[0].transacciones:
                    var = tk.IntVar()
                    self.transaction_vars.agregar(trans.id, (var, trans))
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

    def _create_widgets(self):
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self._create_header()
        
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self._create_selection_controls()
        
        self._create_transaction_controls()
        
        self.request_button = ttk.Button(
            self.content_frame, 
            text="Solicitar Atención", 
            command=self._handle_service_request
        )
        self.request_button.pack(pady=20, fill=tk.X)
        
        self._create_footer()

    def _create_header(self):
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
        ttk.Label(
            self.content_frame, 
            text="Seleccione la empresa:", 
            font=('Helvetica', 12)
        ).pack(pady=(0, 5))
        
        self.company_combo = ttk.Combobox(
            self.content_frame,
            state="readonly"
        )
        self.company_combo.pack(fill=tk.X, pady=(0, 15))
        self.company_combo.bind("<<ComboboxSelected>>", self._update_points_combo)
        
        ttk.Label(
            self.content_frame, 
            text="Seleccione el punto de atención:", 
            font=('Helvetica', 12)
        ).pack(pady=(0, 5))
        
        self.point_combo = ttk.Combobox(
            self.content_frame,
            state="readonly"
        )
        self.point_combo.pack(fill=tk.X, pady=(0, 15))

    def _update_points_combo(self, event=None):
        """Actualiza el combobox de puntos cuando se selecciona una empresa"""
        empresa_nombre = self.company_combo.get()
        if not empresa_nombre:
            return
            
        empresa = next((emp for emp in self.sistema.empresas if emp.nombre == empresa_nombre), None)
        if empresa:
            puntos = [p.nombre for p in empresa.puntos_atencion]
            self.point_combo['values'] = puntos
            if puntos:
                self.point_combo.current(0)

    def _create_transaction_controls(self):
        ttk.Label(
            self.content_frame, 
            text="Transacciones disponibles:", 
            font=('Helvetica', 12)
        ).pack(pady=(0, 5))
        
        self.transactions_frame = ttk.Frame(self.content_frame)
        self.transactions_frame.pack(fill=tk.X)

    def _create_footer(self):
        footer_frame = ttk.Frame(self.main_frame)
        footer_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.status_label = ttk.Label(
            footer_frame, 
            text="Listo para solicitar atención", 
            font=('Helvetica', 10)
        )
        self.status_label.pack()

    def _handle_service_request(self):
        if not self._validate_selections():
            return
            
        selected_trans = self._get_selected_transactions()
        if len(selected_trans) == 0:
            messagebox.showerror("Error", "Seleccione al menos una transacción")
            return
            
        ticket, wait_time, service_time = self._process_client_request(selected_trans)
        
        self._show_ticket(ticket, wait_time, service_time)
        self.status_label.config(text=f"Ticket {ticket} generado")

    def _validate_selections(self):
        if not self.company_combo.get():
            messagebox.showerror("Error", "Seleccione una empresa")
            return False
        if not self.point_combo.get():
            messagebox.showerror("Error", "Seleccione un punto de atención")
            return False
        return True

    def _get_selected_transactions(self):
        selected = ListaEnlazada()
        for item in self.transaction_vars.items():
            trans_id, (var, trans) = item
            if var.get() == 1:
                selected.agregar(trans)
        return selected

    def _process_client_request(self, transactions):
        cliente = Cliente("123456789", "Cliente Ejemplo")
        for trans in transactions:
            cliente.transacciones.agregar(trans)
        
        # Buscar la empresa seleccionada
        empresa_seleccionada = next(
            (emp for emp in self.sistema.empresas if emp.nombre == self.company_combo.get()),
            None
        )
        
        if not empresa_seleccionada:
            messagebox.showerror("Error", "Empresa no encontrada")
            return None, 0, 0
            
        # Buscar el punto de atención seleccionado
        punto = next(
            (p for p in empresa_seleccionada.puntos_atencion if p.nombre == self.point_combo.get()),
            None
        )
        
        if not punto:
            messagebox.showerror("Error", "Punto de atención no encontrado")
            return None, 0, 0
        
        return self.sistema.asignar_cliente(punto, cliente)
    
    def _show_ticket(self, ticket, wait_time, service_time):
        if ticket is None:  # Si hubo error en el proceso
            return
            
        ticket_window = tk.Toplevel(self.root)
        ticket_window.title("Ticket de Atención")
        ticket_window.geometry("320x480")
        ticket_window.resizable(False, False)
        ticket_window.configure(bg=self.bg_color)
        
        ticket_frame = ttk.Frame(ticket_window)
        ticket_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
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

if __name__ == "__main__":
    root = tk.Tk()
    app = MobileAppSimulator(root)
    root.mainloop()
