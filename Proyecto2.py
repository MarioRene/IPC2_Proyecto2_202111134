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
    
    def __getitem__(self, index):
        if index >= self.longitud:
            raise IndexError("Índice fuera de rango")
        actual = self.cabeza
        for _ in range(index):
            actual = actual.siguiente
        return actual.dato

    def sum(self):
        total = 0
        actual = self.cabeza
        while actual:
            total += actual.dato
            actual = actual.siguiente
        return total

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

    def pop(self, index=0):
        if index >= self.longitud:
            raise IndexError("Índice fuera de rango")
        
        if index == 0:
            dato = self.cabeza.dato
            self.cabeza = self.cabeza.siguiente
        else:
            actual = self.cabeza
            for _ in range(index - 1):
                actual = actual.siguiente
            dato = actual.siguiente.dato
            actual.siguiente = actual.siguiente.siguiente
        
        self.longitud -= 1
        return dato
    
    def obtener_por_indice(self, index):
        if index >= self.longitud:
            raise IndexError("Índice fuera de rango")
        actual = self.cabeza
        for _ in range(index):
            actual = actual.siguiente
        return actual.dato

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
    
    def eliminar_primer_cliente(self):
        """Elimina y retorna el primer cliente (FIFO)."""
        if not self.cabeza:
            return None
        cliente = self.cabeza.dato
        self.cabeza = self.cabeza.siguiente
        if self.cabeza:
            self.cabeza.anterior = None
        else:
            self.cola = None
        self.longitud -= 1
        return cliente

    def __getitem__(self, index):
        if index >= self.longitud:
            raise IndexError("Índice fuera de rango")
        
        if index < self.longitud // 2:
            actual = self.cabeza
            for _ in range(index):
                actual = actual.siguiente
        else:
            actual = self.cola
            for _ in range(self.longitud - 1 - index):
                actual = actual.anterior
                
        return actual.dato

class Par:
    def __init__(self, clave, valor):
        self.clave = clave
        self.valor = valor
    
    def __iter__(self):
        """Permite desempaquetar el Par como una tupla (clave, valor)"""
        yield self.clave
        yield self.valor

class ParCaracterValor:
    def __init__(self, caracter, valor):
        self.caracter = caracter
        self.valor = valor

class DiccionarioPersonalizado:
    def __init__(self, capacidad=10):
        self.capacidad = capacidad
        self.tabla = ListaEnlazada()
        self.tamano = 0
        
        # Inicialización sin estructuras nativas
        contador = 0
        while contador < capacidad:
            self.tabla.agregar(ListaEnlazada())
            contador += 1

        # Tabla de caracteres completamente manual
        self.char_map = ListaEnlazada()
        self._inicializar_tabla_caracteres()

    def _inicializar_tabla_caracteres(self):
        self.char_map = ListaEnlazada()
        
        # Fabricamos los caracteres uno por uno usando MiCaracter
        self._agregar_rango(MiCaracter('a'), MiCaracter('z'), 97)  # Minúsculas
        self._agregar_rango(MiCaracter('A'), MiCaracter('Z'), 65)  # Mayúsculas
        self._agregar_rango(MiCaracter('0'), MiCaracter('9'), 48)  # Dígitos
        
        # Caracteres especiales
        especiales = ListaEnlazada()
        especiales.agregar(MiCaracter(' '))
        especiales.agregar(MiCaracter('!'))
        especiales.agregar(MiCaracter('@'))
        especiales.agregar(MiCaracter('#'))
        especiales.agregar(MiCaracter('$'))
        especiales.agregar(MiCaracter('%'))
        especiales.agregar(MiCaracter('&'))
        especiales.agregar(MiCaracter('*'))
        especiales.agregar(MiCaracter('('))
        especiales.agregar(MiCaracter(')'))
        especiales.agregar(MiCaracter('-'))

    def _siguiente_caracter(self, char):
        """Devuelve el siguiente caracter en la secuencia ASCII usando solo estructuras personalizadas"""
        # Inicializar tabla de transición si no existe
        if not hasattr(self, '_tabla_transicion'):
            self._inicializar_tabla_transicion()
        
        # Buscar en la lista enlazada
        actual = self._tabla_transicion.cabeza
        while actual is not None:
            par = actual.dato  # Objeto ParCaracterValor
            if par.caracter.igual_a(char):
                return par.valor
            actual = actual.siguiente
        
        return MiCaracter('?')  # Caracter por defecto

    def _inicializar_tabla_transicion(self):
        """Inicializa la tabla de transición de caracteres"""
        self._tabla_transicion = ListaEnlazada()
        
        # Minúsculas (a-z)
        self._agregar_transicion('a', 'b')
        self._agregar_transicion('b', 'c')
        self._agregar_transicion('c', 'd')
        self._agregar_transicion('d', 'e')
        self._agregar_transicion('e', 'f')
        self._agregar_transicion('f', 'g')
        self._agregar_transicion('g', 'h')
        self._agregar_transicion('h', 'i')
        self._agregar_transicion('i', 'j')
        self._agregar_transicion('j', 'k')
        self._agregar_transicion('k', 'l')
        self._agregar_transicion('l', 'm')
        self._agregar_transicion('m', 'n')
        self._agregar_transicion('n', 'o')
        self._agregar_transicion('o', 'p')
        self._agregar_transicion('p', 'q')
        self._agregar_transicion('q', 'r')
        self._agregar_transicion('r', 's')
        self._agregar_transicion('s', 't')
        self._agregar_transicion('t', 'u')
        self._agregar_transicion('u', 'v')
        self._agregar_transicion('v', 'w')
        self._agregar_transicion('w', 'x')
        self._agregar_transicion('x', 'y')
        self._agregar_transicion('y', 'z')
        self._agregar_transicion('z', 'A')  # Fin de minúsculas
        
        # Mayúsculas (A-Z)
        self._agregar_transicion('A', 'B')
        self._agregar_transicion('B', 'C')
        self._agregar_transicion('C', 'D')
        self._agregar_transicion('D', 'E')
        self._agregar_transicion('E', 'F')
        self._agregar_transicion('F', 'G')
        self._agregar_transicion('G', 'H')
        self._agregar_transicion('H', 'I')
        self._agregar_transicion('I', 'J')
        self._agregar_transicion('J', 'K')
        self._agregar_transicion('K', 'L')
        self._agregar_transicion('L', 'M')
        self._agregar_transicion('M', 'N')
        self._agregar_transicion('N', 'O')
        self._agregar_transicion('O', 'P')
        self._agregar_transicion('P', 'Q')
        self._agregar_transicion('Q', 'R')
        self._agregar_transicion('R', 'S')
        self._agregar_transicion('S', 'T')
        self._agregar_transicion('T', 'U')
        self._agregar_transicion('U', 'V')
        self._agregar_transicion('V', 'W')
        self._agregar_transicion('W', 'X')
        self._agregar_transicion('X', 'Y')
        self._agregar_transicion('Y', 'Z')
        self._agregar_transicion('Z', '0')  # Fin de mayúsculas
        
        # Dígitos (0-9)
        self._agregar_transicion('0', '1')
        self._agregar_transicion('1', '2')
        self._agregar_transicion('2', '3')
        self._agregar_transicion('3', '4')
        self._agregar_transicion('4', '5')
        self._agregar_transicion('5', '6')
        self._agregar_transicion('6', '7')
        self._agregar_transicion('7', '8')
        self._agregar_transicion('8', '9')
        self._agregar_transicion('9', ' ')  # Fin de dígitos

    def _agregar_transicion(self, actual, siguiente):
        """Agrega una transición entre caracteres"""
        par = ParCaracterValor(
            MiCaracter(actual),
            MiCaracter(siguiente)
        )
        self._tabla_transicion.agregar(par)

    def _agregar_rango(self, inicio, fin, codigo_base):
        """Agrega un rango de caracteres continuos"""
        codigo = codigo_base
        char_actual = inicio
        
        while not char_actual.igual_a(fin):
            self.char_map.agregar(ParCaracterValor(char_actual, MiNumero(codigo)))
            codigo += 1
            char_actual = self._siguiente_caracter(char_actual)
        
        # Agregar el último caracter del rango
        self.char_map.agregar(ParCaracterValor(fin, MiNumero(codigo)))

    def _get_char_code(self, char):
        actual = self.char_map.cabeza
        while actual is not None:
            par = actual.dato  # Objeto ParCaracterValor
            if par.caracter.igual_a(char):  # Usa comparación personalizada
                return par.valor.a_entero()  # Convierte MiNumero a entero
            actual = actual.siguiente
        return MiNumero(0)  # Usamos MiNumero para consistencia

    def _verificar_metodo(self, obj, metodo):
        # Sistema de verificación sin hasattr()
        # Requiere que todos los objetos tengan un método 'tiene_metodo'
        if obj is None:
            return False
        return obj.tiene_metodo(metodo)

    def _es_string(self, obj):
        # Caso especial para strings nativos
        if isinstance(obj, str):  # Esto es temporal solo para la transición
            return True
        if not self._verificar_metodo(obj, 'es_string'):
            return False
        return obj.es_string()

    def _iguales(self, obj1, obj2):
        if not self._verificar_metodo(obj1, 'igual_a'):
            return False
        return obj1.igual_a(obj2)

    def _es_numero(self, obj):
        if not self._verificar_metodo(obj, 'es_numero'):
            return False
        return obj.es_numero()

    def _hash_string(self, clave):
        hash_val = 0
        i = 0
        while i < len(clave):  # Cambiado de clave.longitud() a len(clave)
            char_val = self._get_char_code(clave.obtener_caracter(i))
            hash_val = (hash_val * 31 + char_val) % self.capacidad
            i += 1
        return hash_val

    def _hash(self, clave):
        if isinstance(clave, str):  # Caso especial para strings nativos
            return self._hash_string(MiString(clave))
        if self._es_string(clave):
            return self._hash_string(clave)
        elif self._es_numero(clave):
            # Convertir MiNumero a entero antes de aplicar módulo
            num = clave.a_entero() if hasattr(clave, 'a_entero') else clave
            return num % self.capacidad
        else:
            return clave.hash_personalizado() % self.capacidad

    def agregar(self, clave, valor):
        indice = self._hash(clave)
        bucket = self.tabla[indice]
        
        actual = bucket.cabeza
        while actual is not None:
            if actual.dato.clave.igual_a(clave):
                actual.dato.valor = valor
                return
            actual = actual.siguiente
        
        bucket.agregar(Par(clave, valor))
        self.tamano += 1

    def obtener(self, clave):
        indice = self._hash(clave)
        lista_bucket = self.tabla.obtener_por_indice(indice)  #Método personalizado
        
        actual = lista_bucket.cabeza
        while actual is not None:
            if actual.dato.clave.igual_a(clave):  #Comparación personalizada
                return actual.dato.valor
            actual = actual.siguiente
        raise KeyError(clave)
    
    def __contains__(self, clave):
        try:
            self.obtener(clave)
            return True
        except KeyError:
            return False
    
    def items(self):
        items = ListaEnlazada()
        actual_bucket = self.tabla.cabeza
        while actual_bucket is not None:
            actual_elemento = actual_bucket.dato.cabeza
            while actual_elemento is not None:
                items.agregar(Par(actual_elemento.dato.clave, actual_elemento.dato.valor))
                actual_elemento = actual_elemento.siguiente
            actual_bucket = actual_bucket.siguiente
        return items
    
    def __getitem__(self, clave):
        return self.obtener(clave)
    
    def __setitem__(self, clave, valor):
        self.agregar(clave, valor)

class ConjuntoPersonalizado:
    def __init__(self):
        self.diccionario = DiccionarioPersonalizado()

    def agregar(self, elemento):
        # Versión correcta sin sintaxis nativa
        self.diccionario.agregar(elemento, True)

    def __contains__(self, elemento):
        # Versión sin operador 'in' nativo
        return self.diccionario.obtener(elemento) is not None

    def __iter__(self):
        for par in self.diccionario.items():
            yield par.clave

class MiObjeto:
    def __init__(self):
        self.metodos = ListaEnlazada()
        self._inicializar_metodos()

    def _inicializar_metodos(self):
        self.metodos.agregar('tiene_metodo')
        self.metodos.agregar('es_string')
        self.metodos.agregar('es_numero')
        self.metodos.agregar('igual_a')
        self.metodos.agregar('hash_personalizado')

    def tiene_metodo(self, nombre):
        actual = self.metodos.cabeza
        while actual is not None:
            if actual.dato == nombre:
                return True
            actual = actual.siguiente
        return False

    def es_string(self):
        return False

    def es_numero(self):
        return False

    def igual_a(self, otro):
        # Implementación base que compara referencias
        return self is otro

    def hash_personalizado(self):
        # Implementación base usando id() (último recurso)
        # En una implementación real se reemplazaría esto
        return id(self)


class MiString(MiObjeto):
    def __init__(self, valor=None):
        super().__init__()
        self.caracteres = ListaEnlazada()
        self._agregar_metodos_string()
        
        if valor is not None:
            # Manejar tanto strings nativos como objetos MiString
            if isinstance(valor, str):
                # Construir desde string nativo
                for char in valor:
                    self.caracteres.agregar(MiCaracter(char))
            elif hasattr(valor, 'longitud') and hasattr(valor, 'obtener_caracter'):
                # Construir desde otro MiString o similar
                for i in range(valor.longitud()):
                    self.caracteres.agregar(valor.obtener_caracter(i))
            else:
                raise ValueError("El valor debe ser un string o un objeto con métodos longitud() y obtener_caracter()")

    def __len__(self):
        """Implementación del método especial para que funcione con len()"""
        return self.longitud()

    def a_texto(self):
        """Convierte el MiString a string nativo para la UI"""
        result = ""
        for i in range(self.longitud()):
            result += chr(self.obtener_caracter(i).codigo())
        return result

    def _agregar_metodos_string(self):
        self.metodos.agregar('longitud')
        self.metodos.agregar('obtener_caracter')
        self.metodos.agregar('a_texto')
        self.metodos.agregar('__len__')

    def es_string(self):
        return True

    def longitud(self):
        count = 0
        actual = self.caracteres.cabeza
        while actual is not None:
            count += 1
            actual = actual.siguiente
        return count

    def obtener_caracter(self, index):
        if index < 0 or index >= self.longitud():
            raise IndexError("Índice fuera de rango")
        
        actual = self.caracteres.cabeza
        for _ in range(index):
            actual = actual.siguiente
        return actual.dato

    def igual_a(self, otro):
        if not otro.tiene_metodo('es_string') or not otro.es_string():
            return False
        
        if self.longitud() != otro.longitud():
            return False
        
        for i in range(self.longitud()):
            if not self.obtener_caracter(i).igual_a(otro.obtener_caracter(i)):
                return False
        return True

    def agregar_caracter(self, caracter):
        self.caracteres.agregar(caracter)

    def hash_personalizado(self):
        hash_val = 0
        for i in range(self.longitud()):
            char_val = self.obtener_caracter(i).codigo()
            hash_val = (hash_val * 31 + char_val) % (2**32)
        return hash_val
    
    @staticmethod
    def asegurar_mi_string(valor):
        """Convierte un valor a MiString si no lo es ya"""
        return valor if isinstance(valor, MiString) else MiString(valor)

class MiCaracter(MiObjeto):
    def __init__(self, valor):
        super().__init__()
        self.valor = valor
        self.metodos.agregar('codigo')
        self.metodos.agregar('es_string')
        self.metodos.agregar('es_numero')
        self.metodos.agregar('igual_a')

    def codigo(self):
        # Implementación simplificada - en producción usar tabla personalizada
        return ord(self.valor)

    def igual_a(self, otro):
        if not otro.tiene_metodo('codigo'):
            return False
        return self.codigo() == otro.codigo()

    def es_string(self):
        return False

    def es_numero(self):
        return False

class MiNumero(MiObjeto):
    def __init__(self, valor):
        super().__init__()
        self.valor = valor
        # Inicializar métodos disponibles
        self.metodos.agregar('a_entero')
        self.metodos.agregar('__add__')
        self.metodos.agregar('__radd__')
        self.metodos.agregar('__sub__')
        self.metodos.agregar('__rsub__')
        self.metodos.agregar('__mul__')
        self.metodos.agregar('__rmul__')
        self.metodos.agregar('__truediv__')
        self.metodos.agregar('__rtruediv__')
        self.metodos.agregar('__mod__')
        self.metodos.agregar('__rmod__')
        self.metodos.agregar('__ge__')
        self.metodos.agregar('__le__')
        self.metodos.agregar('__gt__')
        self.metodos.agregar('__lt__')
        self.metodos.agregar('__eq__')
        self.metodos.agregar('__ne__')

    def a_entero(self):
        """Convierte el número a entero nativo (únicamente para compatibilidad cuando sea estrictamente necesario)"""
        return self.valor

    # Operaciones aritméticas
    def __add__(self, otro):
        """Suma: implementa el operador +"""
        if isinstance(otro, MiNumero):
            return MiNumero(self.valor + otro.valor)
        elif isinstance(otro, int):
            return MiNumero(self.valor + otro)
        else:
            raise TypeError(f"Tipo no soportado para suma: {type(otro)}")

    def __radd__(self, otro):
        """Suma inversa: implementa el operador + cuando el objeto está a la derecha"""
        return self.__add__(otro)

    def __sub__(self, otro):
        """Resta: implementa el operador -"""
        if isinstance(otro, MiNumero):
            return MiNumero(self.valor - otro.valor)
        elif isinstance(otro, int):
            return MiNumero(self.valor - otro)
        else:
            raise TypeError(f"Tipo no soportado para resta: {type(otro)}")

    def __rsub__(self, otro):
        """Resta inversa: implementa el operador - cuando el objeto está a la derecha"""
        if isinstance(otro, MiNumero):
            return MiNumero(otro.valor - self.valor)
        elif isinstance(otro, int):
            return MiNumero(otro - self.valor)
        else:
            raise TypeError(f"Tipo no soportado para resta: {type(otro)}")

    def __mul__(self, otro):
        """Multiplicación: implementa el operador *"""
        if isinstance(otro, MiNumero):
            return MiNumero(self.valor * otro.valor)
        elif isinstance(otro, int):
            return MiNumero(self.valor * otro)
        else:
            raise TypeError(f"Tipo no soportado para multiplicación: {type(otro)}")

    def __rmul__(self, otro):
        """Multiplicación inversa: implementa el operador * cuando el objeto está a la derecha"""
        return self.__mul__(otro)

    def __truediv__(self, otro):
        """División: implementa el operador /"""
        if isinstance(otro, MiNumero):
            if otro.valor == 0:
                raise ZeroDivisionError("División por cero")
            return MiNumero(self.valor / otro.valor)
        elif isinstance(otro, int):
            if otro == 0:
                raise ZeroDivisionError("División por cero")
            return MiNumero(self.valor / otro)
        else:
            raise TypeError(f"Tipo no soportado para división: {type(otro)}")

    def __rtruediv__(self, otro):
        """División inversa: implementa el operador / cuando el objeto está a la derecha"""
        if isinstance(otro, MiNumero):
            if self.valor == 0:
                raise ZeroDivisionError("División por cero")
            return MiNumero(otro.valor / self.valor)
        elif isinstance(otro, int):
            if self.valor == 0:
                raise ZeroDivisionError("División por cero")
            return MiNumero(otro / self.valor)
        else:
            raise TypeError(f"Tipo no soportado para división: {type(otro)}")

    def __mod__(self, otro):
        """Módulo: implementa el operador %"""
        if isinstance(otro, MiNumero):
            if otro.valor == 0:
                raise ZeroDivisionError("División por cero en módulo")
            return MiNumero(self.valor % otro.valor)
        elif isinstance(otro, int):
            if otro == 0:
                raise ZeroDivisionError("División por cero en módulo")
            return MiNumero(self.valor % otro)
        else:
            raise TypeError(f"Tipo no soportado para módulo: {type(otro)}")

    def __rmod__(self, otro):
        """Módulo inverso: implementa el operador % cuando el objeto está a la derecha"""
        if isinstance(otro, MiNumero):
            if self.valor == 0:
                raise ZeroDivisionError("División por cero en módulo")
            return MiNumero(otro.valor % self.valor)
        elif isinstance(otro, int):
            if self.valor == 0:
                raise ZeroDivisionError("División por cero en módulo")
            return MiNumero(otro % self.valor)
        else:
            raise TypeError(f"Tipo no soportado para módulo: {type(otro)}")

    # Operaciones de comparación
    def __ge__(self, otro):
        """Mayor o igual que: implementa el operador >="""
        if isinstance(otro, MiNumero):
            return self.valor >= otro.valor
        elif isinstance(otro, int):
            return self.valor >= otro
        else:
            raise TypeError(f"Tipo no soportado para comparación: {type(otro)}")

    def __le__(self, otro):
        """Menor o igual que: implementa el operador <="""
        if isinstance(otro, MiNumero):
            return self.valor <= otro.valor
        elif isinstance(otro, int):
            return self.valor <= otro
        else:
            raise TypeError(f"Tipo no soportado para comparación: {type(otro)}")

    def __gt__(self, otro):
        """Mayor que: implementa el operador >"""
        if isinstance(otro, MiNumero):
            return self.valor > otro.valor
        elif isinstance(otro, int):
            return self.valor > otro
        else:
            raise TypeError(f"Tipo no soportado para comparación: {type(otro)}")

    def __lt__(self, otro):
        """Menor que: implementa el operador <"""
        if isinstance(otro, MiNumero):
            return self.valor < otro.valor
        elif isinstance(otro, int):
            return self.valor < otro
        else:
            raise TypeError(f"Tipo no soportado para comparación: {type(otro)}")

    def __eq__(self, otro):
        """Igualdad: implementa el operador =="""
        if isinstance(otro, MiNumero):
            return self.valor == otro.valor
        elif isinstance(otro, int):
            return self.valor == otro
        else:
            return False

    def __ne__(self, otro):
        """Desigualdad: implementa el operador !="""
        return not self.__eq__(otro)

    def es_numero(self):
        """Indica que este objeto es un número"""
        return True

    def igual_a(self, otro):
        """Comparación personalizada para igualdad"""
        return self.__eq__(otro)

    def hash_personalizado(self):
        """Hash personalizado para usar en diccionarios"""
        return hash(self.valor)

    def __str__(self):
        """Representación como string"""
        return str(self.valor)

    def __repr__(self):
        """Representación para depuración"""
        return f"MiNumero({self.valor})"

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
        self.id = MiString(id_transaccion)
        self.nombre = MiString(nombre)
        # Asegurar que el tiempo sea MiNumero
        self.tiempo = tiempo_atencion if isinstance(tiempo_atencion, MiNumero) else MiNumero(tiempo_atencion)

class Cliente:
    def __init__(self, dpi, nombre):
        self.dpi = dpi if isinstance(dpi, MiString) else MiString(dpi)
        self.nombre = nombre if isinstance(nombre, MiString) else MiString(nombre)
        self.transacciones = ListaEnlazada()
        self.tiempo_espera = 0  # Tiempo de espera estimado
        self.tiempo_atencion = 0  # Suma de tiempos de todas las transacciones
        self.ticket = None

    def __str__(self):
        return f"{self.nombre.a_texto()} (DPI: {self.dpi.a_texto()})"

# ==================== SISTEMA DE ATENCIÓN ====================

class SistemaAtencion:
    def __init__(self):
        self.empresas = ListaEnlazada()
        self.tickets_generados = ConjuntoPersonalizado()
        self.tiempo_simulado = 0
        self.escritorios_activos = ListaEnlazada()

    def simular_atencion_completa(self, punto_id):
        """Simula la atención completa de todos los clientes en un punto de atención"""
        punto, empresa = self._buscar_punto(punto_id)
        if not punto:
            raise ValueError("Punto de atención no encontrado")
        
        # Avanzar tiempo hasta que no haya clientes en espera
        while punto.clientes_en_espera.longitud > 0:
            self.avanzar_tiempo(1)  # Avanzar de 1 en 1 minuto
            
        # Calcular estadísticas del punto
        stats_punto = self.calcular_tiempos_punto(punto)
        
        # Calcular estadísticas por escritorio
        stats_escritorios = ListaEnlazada()
        for escritorio in punto.escritorios:
            stats = self.calcular_tiempos_escritorio(escritorio)
            stats_escritorios.agregar({
                'escritorio': escritorio,
                'stats': stats
            })
        
        return {
            'punto': punto,
            'empresa': empresa,
            'stats_punto': stats_punto,
            'stats_escritorios': stats_escritorios
        }   

    def activar_escritorio(self, escritorio):
        """Activa un escritorio y lo añade a la pila LIFO."""
        if not escritorio.activo:
            escritorio.activo = True
            self.escritorios_activos.agregar(escritorio)
            return True
        return False

    def desactivar_escritorio(self):
        """Desactiva el último escritorio activado (LIFO)."""
        if len(self.escritorios_activos) == 0:
            return None
        
        escritorio = self.escritorios_activos[-1]  # Último elemento
        self.escritorios_activos.pop()  # Eliminar de la pila
        escritorio.activo = False
        escritorio.cliente_actual = None
        return escritorio

    def generar_ticket_unico(self):
        intentos = 0
        max_intentos = 100  # Prevenir bucles infinitos
        
        while intentos < max_intentos:
            # Generar parte numérica aleatoria
            parte1 = random.randint(100, 999)
            parte2 = random.randint(1000, 9999)
            ticket = f"{parte1}-{parte2}"
            
            # Verificar si el ticket ya existe
            if not self._ticket_existe(ticket):
                self.tickets_generados.agregar(ticket)
                return ticket
            
            intentos += 1
        
        raise RuntimeError("No se pudo generar un ticket único después de múltiples intentos")

    def _ticket_existe(self, ticket):
        """Verifica si un ticket ya existe en el sistema"""
        return ticket in self.tickets_generados.diccionario

    def agregar_empresa(self, empresa):
        # Verificar si la empresa ya existe
        empresa_existente = None
        for e in self.empresas:
            if e.id.igual_a(empresa.id):
                empresa_existente = e
                break
        
        if not empresa_existente:
            self.empresas.agregar(empresa)
            return True
        return False

    def _crear_cliente_desde_xml(self, cliente_xml, empresa):
        dpi = MiString(cliente_xml.get('dpi'))
        nombre = MiString(cliente_xml.find('nombre').text.strip())
        
        cliente = Cliente(dpi, nombre)
        
        # Cargar transacciones
        transacciones = cliente_xml.find('listadoTransacciones')
        if transacciones is not None:
            for trans_xml in transacciones.findall('transaccion'):
                trans_id = MiString(trans_xml.get('idTransaccion'))
                cantidad = int(trans_xml.get('cantidad', 1))
                
                transaccion = self._buscar_transaccion(empresa, trans_id)
                if transaccion:
                    for _ in range(cantidad):
                        cliente.transacciones.agregar(transaccion)
        
        # Calcular tiempo total como MiNumero
        tiempo_total = MiNumero(0)
        actual = cliente.transacciones.cabeza
        while actual is not None:
            tiempo_trans = actual.dato.tiempo
            if not isinstance(tiempo_trans, MiNumero):
                tiempo_trans = MiNumero(int(tiempo_trans))
            tiempo_total += tiempo_trans
            actual = actual.siguiente
        
        cliente.tiempo_atencion = tiempo_total
        cliente.tiempo_espera = MiNumero(0)  # Se calculará después
        cliente.ticket = self.generar_ticket_unico()
        
        return cliente

    def asignar_cliente_a_escritorio(self, escritorio, cliente):
        if escritorio.activo and escritorio.cliente_actual is None:
            escritorio.cliente_actual = cliente
            escritorio.tiempo_restante = sum(t.tiempo.a_entero() if hasattr(t.tiempo, 'a_entero') else t.tiempo 
                                      for t in cliente.transacciones)
            return True
        return False

    def asignar_cliente(self, punto_atencion, cliente):
        try:
            # Verificar tipos
            if not isinstance(cliente.dpi, MiString) or not isinstance(cliente.nombre, MiString):
                raise ValueError("Los datos del cliente deben ser MiString")
            
            # Calcular tiempo total de atención
            tiempo_total = sum(t.tiempo.a_entero() if hasattr(t.tiempo, 'a_entero') else t.tiempo 
                          for t in cliente.transacciones)
            
            # Generar ticket único
            cliente.ticket = self.generar_ticket_unico()
            
            # Contar escritorios activos
            escritorios_activos = sum(1 for e in punto_atencion.escritorios if e.activo)
            
            if escritorios_activos == 0:
                raise ValueError("No hay escritorios activos en este punto de atención")
            
            # Calcular tiempo de espera estimado
            tiempo_espera = 0
            if len(punto_atencion.clientes_en_espera) > 0:
                # Sumar tiempos de los clientes en la misma "fila virtual"
                posicion = len(punto_atencion.clientes_en_espera)
                fila_virtual = posicion // escritorios_activos
                
                for i in range(fila_virtual * escritorios_activos, posicion):
                    if i < len(punto_atencion.clientes_en_espera):
                        cliente_anterior = punto_atencion.clientes_en_espera[i]
                        tiempo_cliente = sum(t.tiempo.a_entero() if hasattr(t.tiempo, 'a_entero') else t.tiempo 
                                      for t in cliente_anterior.transacciones)
                        tiempo_espera += tiempo_cliente
            
            cliente.tiempo_espera = tiempo_espera
            
            # Agregar cliente al final de la cola
            punto_atencion.clientes_en_espera.agregar(cliente)
            
            # Intentar asignar a escritorio disponible
            for escritorio in punto_atencion.escritorios:
                if escritorio.activo and escritorio.cliente_actual is None:
                    self.asignar_cliente_a_escritorio(escritorio, cliente)
                    break
            
            return cliente.ticket, cliente.tiempo_espera, tiempo_total
        
        except Exception as e:
            error_msg = f"Error al asignar cliente: {str(e)}"
            print(error_msg)
            raise RuntimeError(error_msg)

    def avanzar_tiempo(self, minutos):
        if len(self.escritorios_activos) == 0:
            raise ValueError("No hay escritorios activos para simular.")
        
        # Convertir minutos a MiNumero si es necesario
        minutos_mi = minutos if isinstance(minutos, MiNumero) else MiNumero(minutos)
        self.tiempo_simulado = self.tiempo_simulado + minutos_mi
        
        for empresa in self.empresas:
            for punto in empresa.puntos_atencion:
                for escritorio in punto.escritorios:
                    if escritorio.activo and escritorio.cliente_actual:
                        escritorio.tiempo_restante = escritorio.tiempo_restante - minutos_mi
                        
                        # Usar comparación personalizada
                        if escritorio.tiempo_restante <= MiNumero(0):
                            punto.clientes_atendidos.agregar(escritorio.cliente_actual)
                            escritorio.clientes_atendidos.agregar(escritorio.cliente_actual)
                            escritorio.cliente_actual = None
                            
                            # Asignar siguiente cliente (FIFO)
                            if len(punto.clientes_en_espera) > 0:
                                siguiente_cliente = punto.clientes_en_espera[0]
                                punto.clientes_en_espera.pop(0)
                                self.asignar_cliente_a_escritorio(escritorio, siguiente_cliente)

    def calcular_tiempos_punto(self, punto):
        tiempos_espera = ListaEnlazada()
        tiempos_atencion = ListaEnlazada()
        
        for cliente in punto.clientes_atendidos:
            tiempo = sum(t.tiempo.a_entero() if hasattr(t.tiempo, 'a_entero') else t.tiempo 
                    for t in cliente.transacciones)
            tiempos_atencion.agregar(tiempo)
            tiempo_espera = cliente.tiempo_espera.a_entero() if hasattr(cliente.tiempo_espera, 'a_entero') else cliente.tiempo_espera
            tiempos_espera.agregar(tiempo_espera - tiempo)
        
        for cliente in punto.clientes_en_espera:
            tiempo_espera = cliente.tiempo_espera.a_entero() if hasattr(cliente.tiempo_espera, 'a_entero') else cliente.tiempo_espera
            tiempos_espera.agregar(tiempo_espera)
        
        def maximo(lista):
            max_val = 0
            for item in lista:
                val = item.a_entero() if hasattr(item, 'a_entero') else item
                if val > max_val:
                    max_val = val
            return max_val
        
        def minimo(lista):
            if len(lista) == 0:
                return 0
            min_val = float('inf')
            for item in lista:
                val = item.a_entero() if hasattr(item, 'a_entero') else item
                if val < min_val:
                    min_val = val
            return min_val
        
        def promedio(lista):
            if len(lista) == 0:
                return 0
            total = 0
            count = 0
            for item in lista:
                val = item.a_entero() if hasattr(item, 'a_entero') else item
                total += val
                count += 1
            return total / count
        
        stats = {
            "max_espera": maximo(tiempos_espera),
            "min_espera": minimo(tiempos_espera),
            "promedio_espera": promedio(tiempos_espera),
            "max_atencion": maximo(tiempos_atencion),
            "min_atencion": minimo(tiempos_atencion),
            "promedio_atencion": promedio(tiempos_atencion),
            "total_clientes": len(punto.clientes_atendidos)
        }
        
        return stats

    def calcular_tiempos_escritorio(self, escritorio):
        tiempos = ListaEnlazada()
        
        for cliente in escritorio.clientes_atendidos:
            tiempo = sum(t.tiempo.a_entero() if hasattr(t.tiempo, 'a_entero') else t.tiempo 
                    for t in cliente.transacciones)
            tiempos.agregar(tiempo)

        def maximo(lista):
            max_val = 0
            for item in lista:
                val = item.a_entero() if hasattr(item, 'a_entero') else item
                if val > max_val:
                    max_val = val
            return max_val
        
        def minimo(lista):
            if len(lista) == 0:
                return 0
            min_val = float('inf')
            for item in lista:
                val = item.a_entero() if hasattr(item, 'a_entero') else item
                if val < min_val:
                    min_val = val
            return min_val
        
        def promedio(lista):
            if len(lista) == 0:
                return 0
            total = 0
            count = 0
            for item in lista:
                val = item.a_entero() if hasattr(item, 'a_entero') else item
                total += val
                count += 1
            return total / count
        
        stats = {
            "max_atencion": maximo(tiempos),
            "min_atencion": minimo(tiempos),
            "promedio_atencion": promedio(tiempos),
            "total_clientes": len(escritorio.clientes_atendidos)
        }
        
        return stats

    def cargar_configuracion_xml(self, filepath):
        try:
            # Parsear el XML usando ElementTree (esto es temporal para la transición)
            tree = ET.parse(filepath)
            root = tree.getroot()
            
            # Limpiar el sistema antes de cargar nueva configuración
            self.limpiar_sistema()
            
            # Procesar cada empresa en el XML
            for empresa_xml in root.findall('empresa'):
                id_empresa = empresa_xml.get('id')
                nombre = empresa_xml.find('nombre').text.strip()
                abreviatura = empresa_xml.find('abreviatura').text.strip()
                
                # Crear la empresa usando MiString para los textos
                empresa = Empresa(
                    MiString(id_empresa),
                    MiString(nombre),
                    MiString(abreviatura)
                )
                
                # Procesar puntos de atención
                puntos_xml = empresa_xml.find('listaPuntosAtencion')
                if puntos_xml is not None:
                    for punto_xml in puntos_xml.findall('puntoAtencion'):
                        id_punto = punto_xml.get('id')
                        nombre_punto = punto_xml.find('nombre').text.strip()
                        direccion = punto_xml.find('direccion').text.strip()
                        
                        punto = PuntoAtencion(
                            MiString(id_punto),
                            MiString(nombre_punto),
                            MiString(direccion)
                        )
                        
                        # Procesar escritorios
                        escritorios_xml = punto_xml.find('listaEscritorios')
                        if escritorios_xml is not None:
                            for escritorio_xml in escritorios_xml.findall('escritorio'):
                                id_escritorio = escritorio_xml.get('id')
                                identificacion = escritorio_xml.find('identificacion').text.strip()
                                encargado = escritorio_xml.find('encargado').text.strip()
                                
                                escritorio = EscritorioServicio(
                                    MiString(id_escritorio),
                                    MiString(identificacion),
                                    MiString(encargado)
                                )
                                punto.escritorios.agregar(escritorio)
                        
                        empresa.puntos_atencion.agregar(punto)
                
                # Procesar transacciones
                transacciones_xml = empresa_xml.find('listaTransacciones')
                if transacciones_xml is not None:
                    for trans_xml in transacciones_xml.findall('transaccion'):
                        id_trans = trans_xml.get('id')
                        nombre_trans = trans_xml.find('nombre').text.strip()
                        tiempo = int(trans_xml.find('tiempoAtencion').text.strip())
                        
                        transaccion = Transaccion(
                            MiString(id_trans),
                            MiString(nombre_trans),
                            MiNumero(tiempo)
                        )
                        empresa.transacciones.agregar(transaccion)
                
                self.empresas.agregar(empresa)
            
            return len(self.empresas) > 0
            
        except Exception as e:
            error_msg = f"Error al cargar configuración XML: {str(e)}"
            print(error_msg)
            return False

    def cargar_estado_inicial_xml(self, archivo):
        try:
            if len(self.empresas) == 0:
                raise ValueError("Primero cargue el archivo de configuración")
                
            tree = ET.parse(archivo)
            root = tree.getroot()
            
            for config_xml in root.findall('configInicial'):
                empresa_id = MiString(config_xml.get('idEmpresa'))
                punto_id = MiString(config_xml.get('idPunto'))
                
                # Buscar empresa y punto
                empresa = self._buscar_empresa_por_id(empresa_id)
                if not empresa:
                    continue
                    
                punto = self._buscar_punto_por_id(empresa, punto_id)
                if not punto:
                    continue
                
                # Activar escritorios
                escritorios_activos = ListaEnlazada()
                escritorios_xml = config_xml.find('escritoriosActivos')
                if escritorios_xml is not None:
                    for esc_xml in escritorios_xml.findall('escritorio'):
                        esc_id = MiString(esc_xml.get('idEscritorio'))
                        escritorio = self._buscar_escritorio_por_id(punto, esc_id)
                        
                        if escritorio:
                            escritorio.activo = True
                            escritorio.tiempo_restante = MiNumero(0)
                            escritorios_activos.agregar(escritorio)
                            self.escritorios_activos.agregar(escritorio)
                
                # Cargar clientes
                clientes_xml = config_xml.find('listadoClientes')
                if clientes_xml is not None:
                    for cliente_xml in clientes_xml.findall('cliente'):
                        cliente = self._crear_cliente_desde_xml(cliente_xml, empresa)
                        punto.clientes_en_espera.agregar(cliente)
                
                # Calcular tiempos de espera y asignar clientes
                if len(escritorios_activos) > 0:
                    self._calcular_tiempos_espera(punto, escritorios_activos)
                    self._asignar_clientes_iniciales(punto, escritorios_activos)
            
            return True
            
        except Exception as e:
            messagebox.showerror("Error XML", f"Error al cargar estado inicial:\n{str(e)}")
            return False

    def _calcular_tiempos_espera(self, punto, escritorios_activos):
        """Calcula los tiempos de espera para todos los clientes en el punto"""
        if punto.clientes_en_espera.longitud == 0:
            return
        
        # Inicializar tiempos acumulados con MiNumero
        tiempos_acumulados = ListaEnlazada()
        for _ in range(escritorios_activos.longitud):
            tiempos_acumulados.agregar(MiNumero(0))
        
        # Procesar clientes
        index = 0
        actual_cliente = punto.clientes_en_espera.cabeza
        while actual_cliente is not None:
            escritorio_idx = index % escritorios_activos.longitud
            cliente = actual_cliente.dato
            
            # Asignar tiempo de espera (asegurando que sea MiNumero)
            cliente.tiempo_espera = tiempos_acumulados[escritorio_idx]
            
            # Calcular tiempo del cliente
            tiempo_cliente = MiNumero(0)
            actual_trans = cliente.transacciones.cabeza
            while actual_trans is not None:
                tiempo_trans = actual_trans.dato.tiempo
                if not isinstance(tiempo_trans, MiNumero):
                    tiempo_trans = MiNumero(tiempo_trans)
                tiempo_cliente = tiempo_cliente + tiempo_trans
                actual_trans = actual_trans.siguiente
            
            # Actualizar tiempo acumulado
            tiempos_acumulados[escritorio_idx] = tiempos_acumulados[escritorio_idx] + tiempo_cliente
            
            # Siguiente cliente
            actual_cliente = actual_cliente.siguiente
            index += 1

    def _asignar_clientes_iniciales(self, punto, escritorios_activos):
        """Asigna los clientes a los escritorios activos"""
        if not escritorios_activos or punto.clientes_en_espera.longitud == 0:
            return
        
        # Asignar clientes a escritorios en orden round-robin
        for i in range(punto.clientes_en_espera.longitud):
            escritorio = escritorios_activos[i % escritorios_activos.longitud]
            if escritorio.cliente_actual is None:
                cliente = punto.clientes_en_espera[i]
                self.asignar_cliente_a_escritorio(escritorio, cliente)
                
                # Calcular tiempo restante como MiNumero
                tiempo_total = MiNumero(0)
                actual_trans = cliente.transacciones.cabeza
                while actual_trans is not None:
                    tiempo_trans = actual_trans.dato.tiempo
                    if not isinstance(tiempo_trans, MiNumero):
                        tiempo_trans = MiNumero(tiempo_trans)
                    tiempo_total = tiempo_total + tiempo_trans
                    actual_trans = actual_trans.siguiente
                
                escritorio.tiempo_restante = tiempo_total
                
                # Eliminar cliente de la cola (simulado)
                punto.clientes_en_espera.pop(i)
                break

    def generar_reporte_empresa(self, empresa_id):
        empresa = None
        for e in self.empresas:
            if e.id.igual_a(empresa_id):
                empresa = e
                break
        if not empresa:
            return None
            
        # Crear nombre de archivo seguro
        safe_filename = f"reporte_empresa_{empresa.id.a_texto()}"
        safe_filename = ''.join(c for c in safe_filename if c.isalnum() or c in ('_', '-'))
        
        dot = Digraph(comment=f'Empresa {empresa.nombre.a_texto()}',
                    filename=safe_filename)
        dot.attr('graph', rankdir='LR', bgcolor='#f0e6ff')
        
        # Nodo principal de la empresa
        empresa_label = f'''<<B>Empresa:</B> {empresa.nombre.a_texto()} ({empresa.abreviatura.a_texto()})
    <B>ID:</B> {empresa.id.a_texto()}>'''
        
        dot.node('empresa', empresa_label,
                shape='box', style='filled', fillcolor='#b399d4', fontcolor='white')
        
        # Puntos de atención
        with dot.subgraph(name='cluster_puntos') as c:
            c.attr(label='Puntos de Atención', color='#8a6dae', fontcolor='#4a3b5f')
            for punto in empresa.puntos_atencion:
                stats = self.calcular_tiempos_punto(punto)
                
                punto_label = f'''<<B>Punto:</B> {punto.nombre.a_texto()}
    <B>Dirección:</B> {punto.direccion.a_texto()}
    <B>Clientes:</B> {stats["total_clientes"]}
    <B>Espera prom.:</B> {stats["promedio_espera"]:.1f} min>'''
                
                punto_id = f'p{punto.id.a_texto()}'
                c.node(punto_id, punto_label,
                    shape='ellipse', style='filled', fillcolor='#d9c2ff')
                dot.edge('empresa', punto_id)
                
                # Escritorios
                with c.subgraph(name=f'cluster_escritorios_{punto.id.a_texto()}') as e:
                    e.attr(label='Escritorios', color='#8a6dae')
                    for escritorio in punto.escritorios:
                        estado = "ACTIVO" if escritorio.activo else "INACTIVO"
                        color = "#4CAF50" if escritorio.activo else "#F44336"
                        stats_esc = self.calcular_tiempos_escritorio(escritorio)
                        
                        escritorio_label = f'''<<B>Escritorio:</B> {escritorio.identificacion.a_texto()}
    <B>Encargado:</B> {escritorio.encargado.a_texto()}
    <B>Estado:</B> {estado}
    <B>Atendidos:</B> {stats_esc["total_clientes"]}
    <B>Atención prom.:</B> {stats_esc["promedio_atencion"]:.1f} min>'''
                        
                        escritorio_id = f'e{escritorio.id.a_texto()}'
                        e.node(escritorio_id, escritorio_label,
                            shape='box', style='filled', fillcolor=color, fontcolor='white')
                        c.edge(punto_id, escritorio_id)
        
        # Transacciones
        with dot.subgraph(name='cluster_transacciones') as t:
            t.attr(label='Transacciones Disponibles', color='#8a6dae')
            for trans in empresa.transacciones:
                trans_label = f'''<{trans.nombre.a_texto()}
    <B>Tiempo:</B> {trans.tiempo.a_entero()} min>'''
                
                trans_id = f't{trans.id.a_texto()}'
                t.node(trans_id, trans_label,
                    shape='note', style='filled', fillcolor='#d9c2ff')
                dot.edge('empresa', trans_id)
        
        return dot

    def generar_reporte_punto_atencion(self, punto_id):
        punto, empresa = self._buscar_punto(punto_id)
        if not punto:
            return None
            
        # Crear nombre de archivo seguro
        safe_filename = f"reporte_punto_{punto.id.a_texto()}"
        safe_filename = ''.join(c for c in safe_filename if c.isalnum() or c in ('_', '-'))
        
        dot = Digraph(comment=f'Punto {punto.nombre.a_texto()}',
                    filename=safe_filename)
        dot.attr('graph', bgcolor='#f0e6ff')
        
        # Calcular estadísticas del punto
        stats_punto = self.calcular_tiempos_punto(punto)
        
        # Contar escritorios activos/inactivos
        escritorios_activos = sum(1 for e in punto.escritorios if e.activo)
        escritorios_inactivos = len(punto.escritorios) - escritorios_activos
        
        # Encabezado con estadísticas
        header_text = f'''<<B>Punto de Atención:</B> {punto.nombre.a_texto()}
    <B>Empresa:</B> {empresa.nombre.a_texto()}
    <B>Dirección:</B> {punto.direccion.a_texto()}
    <B>Escritorios:</B> {escritorios_activos} activos, {escritorios_inactivos} inactivos
    <B>Clientes atendidos:</B> {stats_punto["total_clientes"]}

    <B>Tiempos de espera:</B>
    • Promedio: {stats_punto["promedio_espera"]:.1f} min
    • Máximo: {stats_punto["max_espera"]} min
    • Mínimo: {stats_punto["min_espera"]} min

    <B>Tiempos de atención:</B>
    • Promedio: {stats_punto["promedio_atencion"]:.1f} min
    • Máximo: {stats_punto["max_atencion"]} min
    • Mínimo: {stats_punto["min_atencion"]} min>'''
        
        dot.node('header', header_text,
                shape='box', style='filled', fillcolor='#b399d4', fontcolor='white')
        
        # Escritorios
        with dot.subgraph(name='cluster_escritorios') as e:
            e.attr(label='Escritorios de Servicio', color='#8a6dae')
            for escritorio in punto.escritorios:
                stats_esc = self.calcular_tiempos_escritorio(escritorio)
                
                estado = "ACTIVO" if escritorio.activo else "INACTIVO"
                color = "#4CAF50" if escritorio.activo else "#F44336"
                
                esc_text = f'''<<B>Escritorio:</B> {escritorio.identificacion.a_texto()}
    <B>Encargado:</B> {escritorio.encargado.a_texto()}
    <B>Estado:</B> {estado}
    <B>Clientes atendidos:</B> {stats_esc["total_clientes"]}

    <B>Tiempos de atención:</B>
    • Promedio: {stats_esc["promedio_atencion"]:.1f} min
    • Máximo: {stats_esc["max_atencion"]} min
    • Mínimo: {stats_esc["min_atencion"]} min>'''
                
                esc_id = f'e{escritorio.id.a_texto()}'
                dot.node(esc_id, esc_text,
                        shape='box', style='filled', fillcolor=color, fontcolor='white')
        
        return dot

    def _buscar_punto(self, punto_id):
        """Busca un punto de atención por ID y devuelve el punto y su empresa"""
        for empresa in self.empresas:
            for punto in empresa.puntos_atencion:
                if punto.id.igual_a(punto_id):
                    return punto, empresa
        return None, None
    
    def limpiar_sistema(self):
        """Limpia todos los datos del sistema"""
        self.empresas = ListaEnlazada()
        self.tickets_generados = ConjuntoPersonalizado()
        self.tiempo_simulado = 0
        self.escritorios_activos = ListaEnlazada()

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
        self.dpi_var = tk.StringVar()
        self.nombre_var = tk.StringVar()
        
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
            empresa_existente = None
            for e in self.sistema.empresas:
                if e.id == id_empresa:
                    empresa_existente = e
                    break
                    
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
        empresas = ListaEnlazada()
        for emp in self.sistema.empresas:
            empresas.agregar(emp.nombre)
            
        valores = []
        actual = empresas.cabeza
        while actual:
            valores.append(actual.dato)
            actual = actual.siguiente
        empresa_combobox = ttk.Combobox(dialog, textvariable=empresa_var, values=valores, state="readonly")
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
            empresa = None
            for e in self.sistema.empresas:
                if e.nombre == empresa_nombre:
                    empresa = e
                    break
                    
            if not empresa:
                messagebox.showerror("Error", "Empresa no encontrada")
                return
                
            # Verificar si el punto ya existe
            punto_existente = None
            for p in empresa.puntos_atencion:
                if p.id == id_punto:
                    punto_existente = p
                    break
                    
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
        empresas = ListaEnlazada()
        for emp in self.sistema.empresas:
            empresas.agregar(emp.nombre)
            
        empresa_combobox = ttk.Combobox(dialog, textvariable=empresa_var, values=list(empresas), state="readonly")
        empresa_combobox.pack(pady=5)
        empresa_combobox.current(0)
        empresa_combobox.bind("<<ComboboxSelected>>", lambda e: self._actualizar_puntos_combobox(dialog, empresa_var.get()))
        
        tk.Label(dialog, text="Seleccione el punto:").pack()
        
        self.punto_var = tk.StringVar()
        self.punto_combobox = ttk.Combobox(dialog, textvariable=self.punto_var, state="readonly")
        self.punto_combobox.pack(pady=5)
        self._actualizar_puntos_combobox(dialog, self.sistema.empresas[0].nombre if len(self.sistema.empresas) > 0 else "")
        
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
            empresa = None
            for e in self.sistema.empresas:
                if e.nombre == empresa_nombre:
                    empresa = e
                    break
                    
            if not empresa:
                messagebox.showerror("Error", "Empresa no encontrada")
                return
                
            punto = None
            for p in empresa.puntos_atencion:
                if p.nombre == punto_nombre:
                    punto = p
                    break
                    
            if not punto:
                messagebox.showerror("Error", "Punto de atención no encontrado")
                return
                
            # Verificar si el escritorio ya existe
            escritorio_existente = None
            for e in punto.escritorios:
                if e.id == id_escritorio:
                    escritorio_existente = e
                    break
                    
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
        empresa = None
        for e in self.sistema.empresas:
            if e.nombre == empresa_nombre:
                empresa = e
                break
                
        if empresa:
            puntos = ListaEnlazada()
            for p in empresa.puntos_atencion:
                puntos.agregar(p.nombre)
                
            self.punto_combobox['values'] = list(puntos)
            if len(puntos) > 0:
                self.punto_combobox.current(0)

    def _solicitar_datos_cliente(self):
        """Muestra un diálogo para ingresar los datos del cliente"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Datos del Cliente")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        
        # Variables para almacenar los datos
        self.dpi_var = tk.StringVar()
        self.nombre_var = tk.StringVar()
        
        # Frame principal
        main_frame = ttk.Frame(dialog)
        main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        # Campos del formulario
        ttk.Label(main_frame, text="DPI del Cliente:").pack(anchor=tk.W)
        dpi_entry = ttk.Entry(main_frame, textvariable=self.dpi_var)
        dpi_entry.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(main_frame, text="Nombre del Cliente:").pack(anchor=tk.W)
        nombre_entry = ttk.Entry(main_frame, textvariable=self.nombre_var)
        nombre_entry.pack(fill=tk.X, pady=(0, 20))
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Aceptar", 
                command=lambda: self._procesar_datos_cliente(dialog)).pack(side=tk.RIGHT, padx=5)
        
        # Establecer foco en el primer campo
        dpi_entry.focus_set()
        
        return dialog

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
        try:
            # Verificar si hay algo que simular
            hay_que_simular = False
            for empresa in self.sistema.empresas:
                for punto in empresa.puntos_atencion:
                    if punto.clientes_en_espera.longitud > 0:
                        hay_que_simular = True
                        break
                    for escritorio in punto.escritorios:
                        if escritorio.activo and escritorio.cliente_actual:
                            hay_que_simular = True
                            break
            
            if not hay_que_simular:
                messagebox.showinfo("Información", "No hay clientes en espera o escritorios activos para simular")
                return
                
            # Realizar la simulación
            self.sistema.avanzar_tiempo(minutos)
            messagebox.showinfo("Simulación", f"Se avanzó {minutos} minutos en la simulación")
            
            # Actualizar la interfaz
            self._update_ui_after_load()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error durante la simulación:\n{str(e)}")

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
        dot.attr('graph', rankdir='TB', bgcolor='#f0e6ff')
        
        for empresa in self.sistema.empresas:
            for punto in empresa.puntos_atencion:
                if punto.clientes_en_espera.longitud > 0 or punto.clientes_atendidos.longitud > 0:
                    with dot.subgraph(name=f'cluster_{punto.id.a_texto()}') as c:
                        c.attr(label=f'{empresa.nombre.a_texto()} - {punto.nombre.a_texto()}', 
                            color='#8a6dae', fontcolor='#4a3b5f')
                        
                        # Escritorios activos
                        escritorios_activos = ListaEnlazada()
                        actual_escritorio = punto.escritorios.cabeza
                        while actual_escritorio is not None:
                            if actual_escritorio.dato.activo:
                                escritorios_activos.agregar(actual_escritorio.dato)
                            actual_escritorio = actual_escritorio.siguiente
                        
                        for i in range(len(escritorios_activos)):
                            escritorio = escritorios_activos[i]
                            estado = "Atendiendo"
                            if escritorio.cliente_actual:
                                cliente_actual = escritorio.cliente_actual.nombre.a_texto()
                                tiempo_restante = escritorio.tiempo_restante
                                estado = f"Atendiendo a: {cliente_actual} ({tiempo_restante} min restantes)"
                            
                            c.node(f'esc_{punto.id.a_texto()}_{i}',
                                f'<<B>Escritorio {i+1}:</B> {escritorio.identificacion.a_texto()}\n{estado}>',
                                shape='box', style='filled', fillcolor='#4CAF50', fontcolor='white')
                        
                        # Cola de clientes en espera
                        if punto.clientes_en_espera.longitud > 0:
                            with c.subgraph(name=f'cola_{punto.id.a_texto()}') as cola:
                                cola.attr(label='Clientes en Espera', color='#8a6dae')
                                actual_cliente = punto.clientes_en_espera.cabeza
                                i = 0
                                while actual_cliente is not None:
                                    cliente = actual_cliente.dato
                                    transacciones = ListaEnlazada()
                                    actual_trans = cliente.transacciones.cabeza
                                    while actual_trans is not None:
                                        trans_text = f"• {actual_trans.dato.nombre.a_texto()} ({actual_trans.dato.tiempo.a_entero()} min)"
                                        transacciones.agregar(trans_text)
                                        actual_trans = actual_trans.siguiente
                                    
                                    trans_text = "\n".join(transacciones)
                                    
                                    # Calcular tiempo de espera acumulado
                                    tiempo_espera = 0
                                    temp_cliente = punto.clientes_en_espera.cabeza
                                    j = 0
                                    while j < i and temp_cliente is not None:
                                        tiempo_cliente = temp_cliente.dato.tiempo_espera.a_entero() if hasattr(temp_cliente.dato.tiempo_espera, 'a_entero') else temp_cliente.dato.tiempo_espera
                                        tiempo_espera += tiempo_cliente
                                        temp_cliente = temp_cliente.siguiente
                                        j += 1
                                    
                                    cola.node(f'cli_{punto.id.a_texto()}_{i}',
                                            f'<<B>Cliente {i+1}:</B> {cliente.nombre.a_texto()}\n'
                                            f'<B>Ticket:</B> {cliente.ticket}\n'
                                            f'<B>Tiempo estimado:</B> {tiempo_espera} min\n'
                                            f'<B>Transacciones:</B>\n{trans_text}>',
                                            shape='box', style='rounded,filled', fillcolor='#d9c2ff')
                                    if i > 0:
                                        cola.edge(f'cli_{punto.id.a_texto()}_{i-1}', f'cli_{punto.id.a_texto()}_{i}')
                                    
                                    actual_cliente = actual_cliente.siguiente
                                    i += 1
        
        self._mostrar_reporte(dot, "reporte_colas")
    
    def _mostrar_reporte(self, dot, filename):
        try:
            # Crear nombre de archivo seguro
            safe_filename = ''.join(c for c in filename if c.isalnum() or c in ('_', '-'))
            temp_dir = tempfile.mkdtemp()
            filepath = os.path.join(temp_dir, safe_filename)
            
            dot.format = 'png'
            dot.render(filepath, view=False, cleanup=True)
            
            report_window = tk.Toplevel(self.root)
            report_window.title("Visualización de Reporte")
            report_window.geometry("800x600")
            
            img_path = filepath + '.png'
            if os.path.exists(img_path):
                img = Image.open(img_path)
                img = ImageTk.PhotoImage(img)
                
                label = tk.Label(report_window, image=img)
                label.image = img
                label.pack(expand=True, fill='both')
                
                ttk.Button(
                    report_window,
                    text="Guardar Reporte",
                    command=lambda: self._guardar_reporte(img_path)
                ).pack(pady=10)
            else:
                messagebox.showerror("Error", "No se pudo generar la imagen del reporte")
                
        except Exception as e:
            error_msg = f"No se pudo generar el reporte:\n{str(e)}"
            messagebox.showerror("Error", error_msg)
            print(error_msg)  # Para depuración
    
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
        # Limpiar comboboxes
        self.company_combo['values'] = []
        self.point_combo['values'] = []
        
        # Limpiar datos de escritorios si existen
        if hasattr(self, 'escritorios_data'):
            self.escritorios_data = []
        
        # Limpiar checkboxes de transacciones
        for widget in self.transactions_frame.winfo_children():
            widget.destroy()
        
        # Reiniciar el diccionario de variables de transacciones
        self.transaction_vars = DiccionarioPersonalizado()
        
        # Actualizar con nuevos datos si existen
        if len(self.sistema.empresas) > 0:
            # Preparar lista de nombres de empresas para el combobox
            nombres_empresas = []
            for emp in self.sistema.empresas:
                nombres_empresas.append(emp.nombre.a_texto() if hasattr(emp.nombre, 'a_texto') else emp.nombre)
            
            # Configurar el combobox de empresas
            self.company_combo['values'] = nombres_empresas
            if nombres_empresas:
                self.company_combo.current(0)
            
            # Actualizar combobox de puntos de atención
            self._update_points_combo()
            
            # Cargar transacciones de la primera empresa (por defecto)
            if (len(self.sistema.empresas) > 0 and 
                len(self.sistema.empresas[0].transacciones) > 0):
                
                for trans in self.sistema.empresas[0].transacciones:
                    var = tk.IntVar()
                    
                    # Usar MiString como clave en el diccionario
                    clave = trans.id
                    valor = (var, trans)
                    self.transaction_vars.agregar(clave, valor)
                    
                    # Crear el texto para el Checkbutton
                    nombre_trans = trans.nombre.a_texto() if hasattr(trans.nombre, 'a_texto') else trans.nombre
                    tiempo_trans = trans.tiempo.a_entero() if hasattr(trans.tiempo, 'a_entero') else trans.tiempo
                    texto_trans = f"{nombre_trans} ({tiempo_trans} min)"
                    
                    cb = tk.Checkbutton(
                        self.transactions_frame, 
                        text=texto_trans,
                        variable=var,
                        onvalue=1,
                        offvalue=0,
                        bg=self.bg_color,
                        fg=self.text_color,
                        selectcolor=self.secondary_color,
                        font=('Helvetica', 10)
                    )
                    cb.pack(anchor=tk.W, pady=2)
        
        # Actualizar estado de la interfaz
        if len(self.sistema.empresas) > 0:
            self.status_label.config(text="Configuración cargada correctamente")
        else:
            self.status_label.config(text="Listo para cargar configuración")
        
        # Actualizar combobox de escritorios
        self._update_escritorios_combobox()

    def _create_widgets(self):
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self._create_header()
        
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self._create_selection_controls()
        self._create_transaction_controls()
        self._create_escritorios_controls()
        
        self.request_button = ttk.Button(
            self.content_frame, 
            text="Solicitar Atención", 
            command=self._handle_service_request
        )
        self.request_button.pack(pady=20, fill=tk.X)
        
        self._create_footer()

    def _create_escritorios_controls(self):
        """Crea los controles para gestionar escritorios"""
        self.escritorios_frame = ttk.Frame(self.content_frame)
        self.escritorios_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(self.escritorios_frame, 
                text="Gestión de Escritorios", 
                font=('Helvetica', 12)).pack(anchor=tk.W)
        
        # Frame para los controles de escritorios
        controls_frame = ttk.Frame(self.escritorios_frame)
        controls_frame.pack(fill=tk.X, pady=5)
        
        # Combobox para seleccionar escritorio
        self.escritorio_var = tk.StringVar()
        self.escritorio_combo = ttk.Combobox(controls_frame, 
                                            textvariable=self.escritorio_var, 
                                            state="readonly")
        self.escritorio_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Botones de acción
        self.activar_btn = ttk.Button(controls_frame, 
                                    text="Activar", 
                                    command=self._activar_escritorio,
                                    state=tk.DISABLED)
        self.activar_btn.pack(side=tk.LEFT, padx=5)
        
        self.desactivar_btn = ttk.Button(controls_frame, 
                                        text="Desactivar", 
                                        command=self._desactivar_escritorio,
                                        state=tk.DISABLED)
        self.desactivar_btn.pack(side=tk.LEFT, padx=5)
        
        # Actualizar lista de escritorios
        self._update_escritorios_combobox()

    def _update_escritorios_combobox(self):
        """Actualiza el combobox con los escritorios disponibles"""
        self.escritorios_data = []  # Lista para mantener los datos completos
        escritorios_textos = []     # Lista para los textos mostrados en el combobox
        
        for empresa in self.sistema.empresas:
            for punto in empresa.puntos_atencion:
                for escritorio in punto.escritorios:
                    # Convertir MiString a string usando a_texto() si es necesario
                    empresa_nombre = empresa.nombre.a_texto() if hasattr(empresa.nombre, 'a_texto') else empresa.nombre
                    punto_nombre = punto.nombre.a_texto() if hasattr(punto.nombre, 'a_texto') else punto.nombre
                    escritorio_id = escritorio.identificacion.a_texto() if hasattr(escritorio.identificacion, 'a_texto') else escritorio.identificacion
                    
                    texto = f"{empresa_nombre} - {punto_nombre}: {escritorio_id}"
                    escritorios_textos.append(texto)
                    self.escritorios_data.append((empresa, punto, escritorio))
        
        if escritorios_textos:
            self.escritorio_combo['values'] = escritorios_textos
            self.escritorio_combo.current(0)
            self._update_escritorio_status()
        else:
            self.escritorio_combo['values'] = []
            self.activar_btn.config(state=tk.DISABLED)
            self.desactivar_btn.config(state=tk.DISABLED)

    def _update_escritorio_status(self, event=None):
        """Actualiza el estado de los botones según el escritorio seleccionado"""
        seleccion = self.escritorio_combo.current()
        if seleccion == -1:  # No hay selección
            self.activar_btn.config(state=tk.DISABLED)
            self.desactivar_btn.config(state=tk.DISABLED)
            return
            
        # Obtener los datos del escritorio seleccionado
        empresa, punto, escritorio = self.escritorios_data[seleccion]
        
        if escritorio.activo:
            self.activar_btn.config(state=tk.DISABLED)
            self.desactivar_btn.config(state=tk.NORMAL)
        else:
            self.activar_btn.config(state=tk.NORMAL)
            self.desactivar_btn.config(state=tk.DISABLED)

    def _activar_escritorio(self):
        """Activa el escritorio seleccionado"""
        seleccion = self.escritorio_combo.current()
        if seleccion == -1:
            messagebox.showerror("Error", "No hay ningún escritorio seleccionado")
            return
            
        empresa, punto, escritorio = self.escritorios_data[seleccion]
        
        if self.sistema.activar_escritorio(escritorio):
            messagebox.showinfo("Éxito", f"Escritorio {escritorio.identificacion.a_texto()} activado")
            self._update_escritorio_status()
            self._update_escritorios_combobox()
        else:
            messagebox.showerror("Error", "No se pudo activar el escritorio (¿Ya está activo?)")

    def _desactivar_escritorio(self):
        """Desactiva el escritorio seleccionado"""
        seleccion = self.escritorio_combo.current()
        if seleccion == -1:
            messagebox.showerror("Error", "No hay ningún escritorio seleccionado")
            return
            
        empresa, punto, escritorio = self.escritorios_data[seleccion]
        
        escritorio_desactivado = self.sistema.desactivar_escritorio(escritorio)
        if escritorio_desactivado:
            messagebox.showinfo("Éxito", f"Escritorio {escritorio.identificacion.a_texto()} desactivado")
            self._update_escritorio_status()
            self._update_escritorios_combobox()
        else:
            messagebox.showerror("Error", "No se pudo desactivar el escritorio (¿Ya está inactivo?)")

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
        empresa_nombre = self.company_combo.get()
        puntos = ListaEnlazada()
        
        for emp in self.sistema.empresas:
            if emp.nombre.a_texto() == empresa_nombre:
                for p in emp.puntos_atencion:
                    puntos.agregar(p.nombre.a_texto())
                break
                
        self.point_combo['values'] = list(puntos)
        if len(puntos) > 0:
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

    def _validate_selections(self):
        """Valida que se hayan seleccionado empresa y punto de atención válidos"""
        # Verificar que hay empresas cargadas
        if len(self.sistema.empresas) == 0:
            messagebox.showerror("Error", "No hay empresas cargadas en el sistema.")
            return False
        
        # Verificar que se seleccionó una empresa
        if not self.company_combo.get():
            messagebox.showerror("Error", "Seleccione una empresa")
            return False
        
        # Verificar que se seleccionó un punto de atención
        if not self.point_combo.get():
            messagebox.showerror("Error", "Seleccione un punto de atención")
            return False
        
        return True

    def _handle_service_request(self):
        try:
            # Validar selecciones primero
            if not self._validate_selections():
                return
                
            # Obtener transacciones seleccionadas
            selected_trans = self._get_selected_transactions()
            if len(selected_trans) == 0:
                messagebox.showerror("Error", "Seleccione al menos una transacción")
                return
                
            # Obtener empresa y punto seleccionados
            empresa_nombre = self.company_combo.get()
            punto_nombre = self.point_combo.get()
            
            empresa = None
            for emp in self.sistema.empresas:
                if emp.nombre.a_texto() == empresa_nombre:
                    empresa = emp
                    break
                    
            if not empresa:
                messagebox.showerror("Error", f"Empresa no encontrada: {empresa_nombre}")
                return
                
            punto = None
            for p in empresa.puntos_atencion:
                if p.nombre.a_texto() == punto_nombre:
                    punto = p
                    break
                    
            if not punto:
                messagebox.showerror("Error", f"Punto de atención no encontrado: {punto_nombre}")
                return
                
            # Mostrar diálogo para ingresar datos del cliente
            dialog = self._solicitar_datos_cliente()
            self.root.wait_window(dialog)  # Esperar hasta que se cierre el diálogo
            
            # Verificar si se ingresaron datos
            if not self.dpi_var.get() or not self.nombre_var.get():
                return  # El usuario canceló o no ingresó datos
                
            # Crear nuevo cliente con los datos ingresados
            cliente = Cliente(
                MiString(self.dpi_var.get()),
                MiString(self.nombre_var.get())
            )
            
            # Asignar transacciones seleccionadas
            for trans in selected_trans:
                cliente.transacciones.agregar(trans)
                
            # Procesar la solicitud
            ticket, wait_time, service_time = self.sistema.asignar_cliente(punto, cliente)
            if ticket:
                self._show_ticket(ticket, wait_time, service_time)
                self.status_label.config(text=f"Ticket {ticket} generado")
                
        except Exception as e:
            error_msg = f"Ocurrió un error al procesar la solicitud:\n{str(e)}"
            messagebox.showerror("Error", error_msg)
            print(error_msg)  # Log para depuración

    def _procesar_datos_cliente(self, dialog):
        """Procesa los datos ingresados del cliente"""
        dpi = self.dpi_var.get().strip()
        nombre = self.nombre_var.get().strip()
        
        if not dpi or not nombre:
            messagebox.showerror("Error", "Debe ingresar tanto DPI como nombre del cliente")
            return
            
        # Validar formato de DPI (ejemplo básico)
        if len(dpi) < 5 or not any(c.isdigit() for c in dpi):
            messagebox.showerror("Error", "El DPI ingresado no es válido")
            return
            
        dialog.destroy()

    def _get_selected_transactions(self):
        selected = ListaEnlazada()
        
        # Versión con iteración manual
        actual = self.transaction_vars.items().cabeza
        while actual is not None:
            par = actual.dato
            # Dos formas válidas:
            # 1. Accediendo directamente a los atributos
            var, trans = par.valor
            # 2. Desempaquetando como tupla
            # _, (var, trans) = par
            
            if var.get() == 1:
                selected.agregar(trans)
            actual = actual.siguiente
        
        return selected

    def _process_client_request(self, punto, transactions):
        """Procesa la solicitud del cliente en el punto especificado"""
        cliente = Cliente("123456789", "Cliente Ejemplo")  # Datos de ejemplo
        for trans in transactions:
            cliente.transacciones.agregar(trans)
        
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
        
        time_labels = ListaEnlazada()
        time_labels.agregar(("Tiempo estimado de espera:", wait_time))
        time_labels.agregar(("Tiempo estimado de atención:", service_time))
        
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
