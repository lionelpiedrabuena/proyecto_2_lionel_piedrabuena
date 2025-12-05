import mysql.connector
from mysql.connector import Error
from datetime import date

# Conexión a MySQL
try:
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        port="3306",
        password="administrador",
        database="Ventas_online"
    )
    if conexion.is_connected():
        print("Conexión exitosa.")
        cursor = conexion.cursor()
except Error as error:
    print("Error durante la conexión:", error)
    exit()

# Validaciones
def pedir_entero_positivo(mensaje: str) -> int:
    while True:
        try:
            n = int(input(mensaje))
            if n >= 0:
                return n
            print("Debe ser un entero no negativo.")
        except ValueError:
            print("Entrada inválida.")

def pedir_float_positivo(mensaje: str) -> float:
    while True:
        try:
            n = float(input(mensaje))
            if n >= 0:
                return n
            print("Debe ser un número positivo.")
        except ValueError:
            print("Entrada inválida.")

def existe_producto(cod: int) -> bool:
    cursor.execute("SELECT 1 FROM Productos WHERE codigo_producto = %s", (cod,))
    return cursor.fetchone() is not None

def existe_cliente(dni: int) -> bool:
    cursor.execute("SELECT 1 FROM Clientes WHERE dni_cliente = %s", (dni,))
    return cursor.fetchone() is not None

def pausa():
    input("\nPresione ENTER para continuar...")

# === PRODUCTOS ===
def agregar_producto():
    print("\n--- AGREGAR PRODUCTO ---")
    while True:
        cod = pedir_entero_positivo("Código del producto: ")
        if existe_producto(cod):
            print("El código ya existe.")
        else:
            break
    nombre = input("Nombre: ")
    precio = pedir_float_positivo("Precio: ")
    stock = pedir_entero_positivo("Stock: ")
    cursor.execute(
        "INSERT INTO Productos VALUES (%s, %s, %s, %s)",
        (cod, nombre, precio, stock)
    )
    conexion.commit()
    print("Producto agregado.")
    pausa()

def actualizar_producto():
    print("\n--- ACTUALIZAR PRODUCTO ---")
    cod = pedir_entero_positivo("Código: ")
    if not existe_producto(cod):
        print("Producto no encontrado.")
        pausa()
        return
    nombre = input("Nuevo nombre: ")
    precio = pedir_float_positivo("Nuevo precio: ")
    stock = pedir_entero_positivo("Nuevo stock: ")
    cursor.execute(
        "UPDATE Productos SET nombre_producto=%s, precio=%s, stock=%s WHERE codigo_producto=%s",
        (nombre, precio, stock, cod)
    )
    conexion.commit()
    print("Producto actualizado.")
    pausa()

def ver_productos():
    print("\n--- PRODUCTOS ---")
    cursor.execute("SELECT * FROM Productos")
    for p in cursor.fetchall():
        print(f"Cod: {p[0]} | {p[1]} | ${p[2]:.2f} | Stock: {p[3]}")
    pausa()

def eliminar_producto():
    cod = pedir_entero_positivo("Código a eliminar: ")
    if not existe_producto(cod):
        print("Producto no existe.")
        pausa()
        return
    cursor.execute("DELETE FROM Productos WHERE codigo_producto = %s", (cod,))
    conexion.commit()
    print("Producto eliminado.")
    pausa()

# === CLIENTES ===
def registrar_cliente():
    print("\n--- REGISTRAR CLIENTE ---")
    dni = pedir_entero_positivo("DNI: ")
    if existe_cliente(dni):
        print("DNI ya registrado.")
        pausa()
        return
    nombre = input("Nombre: ")
    apellido = input("Apellido: ")
    email = input("Email: ")
    cursor.execute(
        "INSERT INTO Clientes VALUES (%s, %s, %s, %s)",
        (dni, nombre, apellido, email)
    )
    conexion.commit()
    print("Cliente registrado.")
    pausa()

def ver_clientes():
    print("\n--- CLIENTES ---")
    cursor.execute("SELECT * FROM Clientes")
    for c in cursor.fetchall():
        print(f"DNI: {c[0]} | {c[1]} {c[2]} | {c[3]}")
    pausa()

# === ÓRDENES ===
def mostrar_ordenes_por_cliente():
    print("\n--- ÓRDENES POR CLIENTE ---")
    dni = pedir_entero_positivo("DNI del cliente: ")
    if not existe_cliente(dni):
        print("Cliente no encontrado.")
        pausa()
        return
    query = """
        SELECT o.id_orden, p.nombre_producto, o.cantidad, o.fecha, o.total
        FROM Ordenes o
        JOIN Productos p ON o.codigo_producto = p.codigo_producto
        WHERE o.dni_cliente = %s
        ORDER BY o.fecha DESC
    """
    cursor.execute(query, (dni,))
    ordenes = cursor.fetchall()
    if not ordenes:
        print("No hay órdenes para este cliente.")
    else:
        for o in ordenes:
            print(f"Orden {o[0]}: {o[1]} x{o[2]} | Fecha: {o[3]} | Total: ${o[4]:.2f}")
    pausa()

# === BÚSQUEDAS AVANZADAS ===
def reporte_productos_mas_vendidos():
    print("\n--- PRODUCTOS MÁS VENDIDOS ---")
    query = """
        SELECT p.nombre_producto, SUM(o.cantidad) AS total
        FROM Ordenes o
        JOIN Productos p ON o.codigo_producto = p.codigo_producto
        GROUP BY p.codigo_producto
        ORDER BY total DESC
        LIMIT 1
    """
    cursor.execute(query)
    res = cursor.fetchone()
    if res:
        print(f"Producto más vendido: {res[0]} ({res[1]} unidades vendidas)")
    else:
        print("No hay ventas registradas.")
    pausa()

# === MODIFICACIÓN DE ÓRDENES ===
def modificar_valor_producto():
    print("\n--- AJUSTAR ÓRDENES POR LÍMITE DE CANTIDAD ---")
    cod = pedir_entero_positivo("Código del producto: ")
    if not existe_producto(cod):
        print("Producto no existe.")
        pausa()
        return
    limite = pedir_entero_positivo("Cantidad máxima permitida: ")
    cursor.execute("""
        UPDATE Ordenes
        SET cantidad = %s, total = %s * (SELECT precio FROM Productos WHERE codigo_producto = %s)
        WHERE codigo_producto = %s AND cantidad > %s
    """, (limite, limite, cod, cod, limite))
    conexion.commit()
    print(f"Órdenes ajustadas: {cursor.rowcount} filas modificadas.")
    pausa()

# === MENÚS ===
def menu_productos():
    while True:
        print("\n--- GESTIÓN DE PRODUCTOS ---")
        print("1. Agregar")
        print("2. Actualizar")
        print("3. Ver todos")
        print("4. Eliminar")
        print("5. Volver")
        op = input("Opción: ")
        if op == "1": agregar_producto()
        elif op == "2": actualizar_producto()
        elif op == "3": ver_productos()
        elif op == "4": eliminar_producto()
        elif op == "5": break
        else: print("Opción inválida.")

def menu_clientes():
    while True:
        print("\n--- GESTIÓN DE CLIENTES ---")
        print("1. Registrar")
        print("2. Ver todos")
        print("3. Volver")
        op = input("Opción: ")
        if op == "1": registrar_cliente()
        elif op == "2": ver_clientes()
        elif op == "3": break
        else: print("Opción inválida.")

def menu_ordenes():
    while True:
        print("\n--- PROCESAMIENTO DE ÓRDENES ---")
        print("1. Órdenes por cliente")
        print("2. Volver")
        op = input("Opción: ")
        if op == "1": mostrar_ordenes_por_cliente()
        elif op == "2": break
        else: print("Opción inválida.")

def menu_busquedas():
    while True:
        print("\n--- BÚSQUEDAS AVANZADAS ---")
        print("1. Productos más vendidos")
        print("2. Volver")
        op = input("Opción: ")
        if op == "1": reporte_productos_mas_vendidos()
        elif op == "2": break
        else: print("Opción inválida.")

# === MENÚ PRINCIPAL ===
def menu_principal():
    while True:
        print("\n=== SISTEMA DE VENTAS EN LÍNEA ===")
        print("1. Gestión de Productos")
        print("2. Gestión de Clientes")
        print("3. Procesamiento de Órdenes")
        print("4. Búsquedas Avanzadas")
        print("5. Modificar órdenes por límite")
        print("6. Salir")
        op = input("Opción: ")
        if op == "1": menu_productos()
        elif op == "2": menu_clientes()
        elif op == "3": menu_ordenes()
        elif op == "4": menu_busquedas()
        elif op == "5": modificar_valor_producto()
        elif op == "6":
            print("Saliendo...")
            break
        else:
            print("Opción inválida.")

menu_principal()

# Cerrar conexión
if conexion.is_connected():
    cursor.close()
    conexion.close()
    print("Conexión cerrada.")