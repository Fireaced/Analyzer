import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText
import json
import os
from collections import Counter, defaultdict
from datetime import datetime
from tkcalendar import Calendar

def load_tickets_data(filename='mercadona_tickets.json'):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    else:
        messagebox.showerror("Error", f"El archivo {filename} no existe.")
        return []

def calculate_total_expense(tickets_data):
    total_expense = sum(ticket['precio_total'] for ticket in tickets_data)
    messagebox.showinfo("Gasto Total", f"Gasto total: {total_expense} €")

def most_purchased_items(tickets_data):
    item_counter = Counter()
    for ticket in tickets_data:
        for item in ticket['items']:
            item_counter[item['descripcion']] += item['cantidad']
    most_common_items = item_counter.most_common()
    result = "\n".join([f"{item}: {count} veces" for item, count in most_common_items])
    messagebox.showinfo("Productos Más Comprados", result)


def calculate_expense_in_date_range(tickets_data, start_date_str, end_date_str):
    """
    Calcula los gastos en un rango de fechas dado en formato 'dd/mm/yyyy'.
    """
    try:
        # Convertir las fechas de entrada de string a objetos datetime (sin tiempo)
        start_date = datetime.strptime(start_date_str, '%d/%m/%Y').date()
        end_date = datetime.strptime(end_date_str, '%d/%m/%Y').date()

        if start_date > end_date:
            messagebox.showerror("Error", "La fecha de inicio debe ser antes de la fecha de fin.")
            return

        expenses_in_range = 0.0
        for ticket in tickets_data:
            date_str = ticket.get('fecha_compra', None)
            if date_str:
                try:
                    # Convertir la fecha del ticket a un objeto datetime (con tiempo)
                    ticket_datetime = datetime.strptime(date_str, '%d/%m/%Y %H:%M')
                    ticket_date = ticket_datetime.date()

                    if start_date <= ticket_date <= end_date:
                        expenses_in_range += ticket['precio_total']
                except ValueError:
                    print(f"Error al convertir la fecha del ticket '{date_str}'.")

        # Mostrar el resultado
        messagebox.showinfo("Gasto en Rango de Fechas", f"Gasto total entre {start_date_str} y {end_date_str}: {expenses_in_range:.2f} €")
    except ValueError as e:
        messagebox.showerror("Error", f"Error al procesar las fechas. Por favor verifica el formato (dd/mm/yyyy).\n{e}")


def ask_date_range(tickets_data):
    """
    Abre una ventana con un calendario para seleccionar las fechas de inicio y fin.
    """
    def submit_dates():
        start_date_str = cal_start.get_date()
        end_date_str = cal_end.get_date()
        
        try:
            # Validar formato de fechas
            start_date = datetime.strptime(start_date_str, '%d/%m/%Y').date()
            end_date = datetime.strptime(end_date_str, '%d/%m/%Y').date()

            if start_date > end_date:
                messagebox.showerror("Error", "La fecha de inicio debe ser antes de la fecha de fin.")
                return

            # Pasar las fechas en formato de string a la función de cálculo
            calculate_expense_in_date_range(tickets_data, start_date_str, end_date_str)
        except ValueError as e:
            messagebox.showerror("Error", f"Formato de fecha incorrecto. Por favor verifica las fechas.\n{e}")

    # Crear la ventana para la entrada de fechas
    date_window = tk.Toplevel()
    date_window.title("Seleccionar Rango de Fechas")

    tk.Label(date_window, text="Fecha de inicio:").pack(pady=5)
    cal_start = Calendar(date_window, date_pattern='dd/mm/yyyy')
    cal_start.pack(pady=5)

    tk.Label(date_window, text="Fecha de fin:").pack(pady=5)
    cal_end = Calendar(date_window, date_pattern='dd/mm/yyyy')
    cal_end.pack(pady=5)

    submit_button = tk.Button(date_window, text="Calcular Gasto", command=submit_dates)
    submit_button.pack(pady=20)

def get_unique_products(tickets_data):
    """
    Obtiene una lista de productos únicos comprados en los tickets.
    """
    product_set = set()
    for ticket in tickets_data:
        for item in ticket['items']:
            product_set.add(item['descripcion'])
    return sorted(list(product_set))  # Ordenar para mejor visualización

def find_product_purchases(tickets_data, selected_product):
    """
    Encuentra el historial de compras para un producto y calcula la cantidad total comprada.
    """
    purchases = []
    total_quantity = 0

    for ticket in tickets_data:
        for item in ticket['items']:
            if item['descripcion'] == selected_product:
                purchases.append(ticket['fecha_compra'])
                total_quantity += item['cantidad']  # Sumar la cantidad de productos comprados

    if purchases:
        dates = "\n".join(purchases)
        messagebox.showinfo("Historial de Compras", f"Producto: {selected_product}\nCantidad total comprada: {total_quantity}\nFechas:\n{dates}")
    else:
        messagebox.showinfo("Historial de Compras", f"No se encontraron compras para {selected_product}.")


def ask_product(tickets_data):
    """
    Abre una ventana con un desplegable para seleccionar un producto.
    """
    def submit_product():
        selected_product = product_combobox.get()
        if selected_product:
            find_product_purchases(tickets_data, selected_product)
        else:
            messagebox.showerror("Error", "Por favor, selecciona un producto.")

    # Crear la ventana para seleccionar producto
    product_window = tk.Toplevel()
    product_window.title("Seleccionar Producto")

    # Cargar la lista de productos únicos
    unique_products = get_unique_products(tickets_data)

    tk.Label(product_window, text="Selecciona un producto:").pack(pady=5)
    product_combobox = ttk.Combobox(product_window, values=unique_products, width=40)
    product_combobox.pack(pady=5)
    product_combobox.current(0)  # Preseleccionar el primer producto

    submit_button = tk.Button(product_window, text="Buscar", command=submit_product)
    submit_button.pack(pady=20)

def ask_month_and_product(tickets_data):
    """
    Abre una ventana para seleccionar el mes, año y producto.
    """
    def submit_month_and_product():
        month_str = month_combobox.get().strip()
        year_str = year_combobox.get().strip()
        selected_product = product_combobox.get()

        try:
            # Mapear el mes a su número correspondiente (por ejemplo, 'Enero' -> 1)
            month_mapping = {
                'Enero': 1, 'Febrero': 2, 'Marzo': 3, 'Abril': 4, 'Mayo': 5,
                'Junio': 6, 'Julio': 7, 'Agosto': 8, 'Septiembre': 9, 'Octubre': 10,
                'Noviembre': 11, 'Diciembre': 12
            }

            # Obtener el número del mes seleccionado
            month_number = month_mapping.get(month_str)
            year = int(year_str)

            # Llamar a la función que calcula la cantidad comprada
            calculate_product_in_month(tickets_data, month_number, year, selected_product)
        except ValueError as e:
            messagebox.showerror("Error", f"Error al procesar los datos. Por favor verifica tu selección.\n{e}")

    # Obtener la lista de productos únicos
    products = set()
    for ticket in tickets_data:
        for item in ticket['items']:
            products.add(item['descripcion'])
    
    # Crear la ventana para la selección de mes, año y producto
    month_window = tk.Toplevel()
    month_window.title("Seleccionar Mes, Año y Producto")

    # Desplegable para seleccionar el mes
    tk.Label(month_window, text="Seleccionar Mes:").pack(pady=5)
    month_combobox = ttk.Combobox(month_window, values=[
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ])
    month_combobox.pack(pady=5)

    # Desplegable para seleccionar el año
    tk.Label(month_window, text="Seleccionar Año:").pack(pady=5)
    current_year = datetime.now().year
    year_combobox = ttk.Combobox(month_window, values=[str(year) for year in range(current_year - 1, 2031)])
    year_combobox.pack(pady=5)

    # Desplegable para seleccionar el producto
    tk.Label(month_window, text="Seleccionar Producto:").pack(pady=5)
    product_combobox = ttk.Combobox(month_window, values=list(products))
    product_combobox.pack(pady=5)

    # Botón para enviar
    submit_button = tk.Button(month_window, text="Calcular Cantidad", command=submit_month_and_product)
    submit_button.pack(pady=20)

def calculate_product_in_month(tickets_data, month, year, selected_product):
    """
    Calcula la cantidad de un producto comprado en un mes y año específico.
    """
    total_quantity = 0
    relevant_dates = []

    # Iterar sobre los tickets para encontrar las compras del mes y producto seleccionados
    for ticket in tickets_data:
        date_str = ticket.get('fecha_compra', None)
        if date_str:
            try:
                # Convertir la fecha del ticket a un objeto datetime
                ticket_datetime = datetime.strptime(date_str, '%d/%m/%Y %H:%M')

                # Verificar si el mes y año coinciden con el mes y año seleccionados
                if ticket_datetime.month == month and ticket_datetime.year == year:
                    for item in ticket['items']:
                        if item['descripcion'] == selected_product:
                            total_quantity += item['cantidad']
                            relevant_dates.append(ticket['fecha_compra'])

            except ValueError as ve:
                print(f"Error al convertir la fecha del ticket '{date_str}': {ve}")

    if relevant_dates:
        dates_str = "\n".join(relevant_dates)
        messagebox.showinfo("Resultado", f"Producto: {selected_product}\nCantidad comprada en {month}/{year}: {total_quantity}\nFechas:\n{dates_str}")
    else:
        messagebox.showinfo("Resultado", f"No se encontraron compras de {selected_product} en {month}/{year}.")

def calculate_monthly_ticket(tickets_data, month, year):
    """
    Calcula el ticket de gasto para un mes y año específicos.
    """
    monthly_summary = defaultdict(lambda: {'cantidad': 0, 'precio_unitario': 0, 'precio_total': 0})
    total_expense = 0

    # Filtrar los tickets por el mes y el año
    for ticket in tickets_data:
        date_str = ticket.get('fecha_compra', None)
        if date_str:
            try:
                ticket_datetime = datetime.strptime(date_str, '%d/%m/%Y %H:%M')
                ticket_month = ticket_datetime.month
                ticket_year = ticket_datetime.year

                if ticket_month == month and ticket_year == year:
                    for item in ticket['items']:
                        descripcion = item['descripcion']
                        cantidad = item['cantidad']
                        precio_unitario = abs(item['precio_unitario'])
                        precio_total = cantidad * abs(precio_unitario)

                        # Acumular la cantidad, precio unitario y precio total
                        monthly_summary[descripcion]['cantidad'] += cantidad
                        monthly_summary[descripcion]['precio_unitario'] = precio_unitario
                        monthly_summary[descripcion]['precio_total'] += precio_total

                        total_expense += precio_total
            except ValueError as ve:
                print(f"Error al procesar la fecha: {ve}")

    # Crear una ventana de texto con scroll para mostrar el ticket
    if monthly_summary:
        ticket_window = tk.Toplevel()
        ticket_window.title(f"Ticket Mensual - {month}/{year}")
        ticket_window.geometry("400x400")

        # Crear el widget ScrolledText para el ticket
        scrolled_text = ScrolledText(ticket_window, wrap=tk.WORD, width=50, height=20)
        scrolled_text.pack(pady=10, padx=10)

        # Construir el contenido del ticket
        ticket_str = ""
        for descripcion, data in monthly_summary.items():
            ticket_str += f"Producto: {descripcion}\n"
            ticket_str += f"  Cantidad comprada: {data['cantidad']}\n"
            ticket_str += f"  Precio por unidad: {data['precio_unitario']:.2f} €\n"
            ticket_str += f"  Total gastado: {data['precio_total']:.2f} €\n\n"

        ticket_str += f"\nCoste total del mes: {total_expense:.2f} €"

        # Insertar el texto en el widget ScrolledText
        scrolled_text.insert(tk.END, ticket_str)

        # Desactivar la edición del texto para que solo se pueda ver
        scrolled_text.config(state=tk.DISABLED)
    else:
        messagebox.showinfo("Ticket Mensual", "No se encontraron compras en el mes seleccionado.")

def ask_month_and_year_for_ticket(tickets_data):
    """
    Abre una ventana para seleccionar el mes y año para generar el ticket.
    """
    def submit_month_and_year():
        month_str = month_combobox.get().strip()
        year_str = year_combobox.get().strip()

        try:
            # Mapear el mes a su número correspondiente
            month_mapping = {
                'Enero': 1, 'Febrero': 2, 'Marzo': 3, 'Abril': 4, 'Mayo': 5,
                'Junio': 6, 'Julio': 7, 'Agosto': 8, 'Septiembre': 9, 'Octubre': 10,
                'Noviembre': 11, 'Diciembre': 12
            }

            # Obtener el número del mes seleccionado
            month_number = month_mapping.get(month_str)
            year = int(year_str)

            # Llamar a la función que genera el ticket del mes
            calculate_monthly_ticket(tickets_data, month_number, year)
        except ValueError as e:
            messagebox.showerror("Error", f"Error al procesar los datos. Por favor verifica tu selección.\n{e}")

    # Crear la ventana para la selección de mes y año
    month_window = tk.Toplevel()
    month_window.title("Seleccionar Mes y Año")

    # Desplegable para seleccionar el mes
    tk.Label(month_window, text="Seleccionar Mes:").pack(pady=5)
    month_combobox = ttk.Combobox(month_window, values=[
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ])
    month_combobox.pack(pady=5)

    # Desplegable para seleccionar el año
    tk.Label(month_window, text="Seleccionar Año:").pack(pady=5)
    current_year = datetime.now().year
    year_combobox = ttk.Combobox(month_window, values=[str(year) for year in range(current_year - 10, 2031)])
    year_combobox.pack(pady=5)

    # Botón para enviar
    submit_button = tk.Button(month_window, text="Generar Ticket", command=submit_month_and_year)
    submit_button.pack(pady=20)


def main():
    root = tk.Tk()
    root.title("Analizador de Tickets Mercadona")

    # Cargar los datos
    tickets_data = load_tickets_data()

    if not tickets_data:
        messagebox.showerror("Error", "No hay datos de tickets para analizar.")
        return

    # Botón para calcular el gasto total
    btn_total_expense = tk.Button(root, text="Gasto Total", command=lambda: calculate_total_expense(tickets_data))
    btn_total_expense.pack(pady=10)

    # Botón para ver los productos más comprados
    btn_most_purchased = tk.Button(root, text="Productos Más Comprados", command=lambda: most_purchased_items(tickets_data))
    btn_most_purchased.pack(pady=10)

    # Botón para calcular el gasto por rango de fecha
    btn_expense_by_date = tk.Button(root, text="Gasto por Rango de Fecha", command=lambda: ask_date_range(tickets_data))
    btn_expense_by_date.pack(pady=10)

    # Botón para generar el ticket del mes
    btn_ticket_by_month = tk.Button(root, text="Ticket Mensual", command=lambda: ask_month_and_year_for_ticket(tickets_data))
    btn_ticket_by_month.pack(pady=10)
    
     # Botón para buscar la cantidad comprada de un producto en un mes y año
    btn_product_in_month = tk.Button(root, text="Cantidad de Producto por Mes/Año", command=lambda: ask_month_and_product(tickets_data))
    btn_product_in_month.pack(pady=10)

    # Configurar la ventana
    root.geometry("300x300")
    root.mainloop()

if __name__ == "__main__":
    main()