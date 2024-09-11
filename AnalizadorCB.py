import tkinter as tk
from tkinter import messagebox, ttk
import json
from tkinter.scrolledtext import ScrolledText
from datetime import datetime
import os

# Función para cargar el archivo JSON proporcionado por el usuario
def load_bank_data_by_filename(filename):
    file_with_extension = f"{filename}.json"
    if os.path.exists(file_with_extension):
        try:
            with open(file_with_extension, 'r', encoding='utf-8') as f:
                bank_data = json.load(f)
            return bank_data
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo: {e}")
    else:
        messagebox.showerror("Error", f"El archivo {file_with_extension} no existe.")
    return None

# Calcular el balance de un mes y año dados
def calculate_monthly_balance(bank_data, month, year):
    balance = 0.0
    transactions_in_month = []
    earliest_transaction = None
    latest_transaction = None

    for transaction in bank_data:
        transaction_date_str = transaction['fecha_oper']
        transaction_date = datetime.strptime(transaction_date_str, '%d/%m/%Y')

        # Filtrar las transacciones que estén en el mes y año seleccionados
        if transaction_date.month == month and transaction_date.year == year:
            transactions_in_month.append(transaction)
            balance += float(transaction['importe'].replace(',', '.'))  # Convertir el importe a float
            
            # Determinar la transacción más temprana y más reciente
            if earliest_transaction is None or transaction_date < earliest_transaction:
                earliest_transaction = transaction_date
            if latest_transaction is None or transaction_date > latest_transaction:
                latest_transaction = transaction_date

    # Buscar el saldo más temprano y más reciente
    saldo_final = transactions_in_month[0]['saldo'] if transactions_in_month else 'N/A'
    saldo_inicial = transactions_in_month[-1]['saldo'] if transactions_in_month else 'N/A'

    # Mostrar el balance en una ventana
    show_monthly_balance(transactions_in_month, balance, saldo_inicial, saldo_final, month, year)


# Mostrar el balance mensual en una nueva ventana con scroll
def show_monthly_balance(transactions, balance, saldo_inicial, saldo_final, month, year):
    month_names = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    month_name = month_names[month - 1]

    balance_window = tk.Toplevel()
    balance_window.title(f"Balance de {month_name} {year}")
    balance_window.geometry("500x400")

    scrolled_text = ScrolledText(balance_window, wrap=tk.WORD, width=60, height=20)
    scrolled_text.pack(pady=10, padx=10)

    # Mostrar primero el saldo inicial y final, luego el balance total del mes
    scrolled_text.insert(tk.END, f"Saldo inicial: {saldo_inicial} €\n")
    scrolled_text.insert(tk.END, f"Saldo final: {saldo_final} €\n\n")
    scrolled_text.insert(tk.END, f"Balance total de {month_name} {year}: {balance:.2f} €\n\n")

    # Luego mostrar las transacciones
    scrolled_text.insert(tk.END, "Transacciones del mes:\n\n")
    for item in transactions:
        scrolled_text.insert(tk.END, f"Fecha: {item['fecha_oper']}\n")
        scrolled_text.insert(tk.END, f"Concepto: {item['concepto']}\n")
        scrolled_text.insert(tk.END, f"Importe: {item['importe']} €\n")
        scrolled_text.insert(tk.END, f"Saldo: {item['saldo']} €\n\n")

    scrolled_text.config(state=tk.DISABLED)


# Ventana para seleccionar el mes y año
def ask_month_and_year_to_calculate_balance(bank_data):
    month_window = tk.Toplevel()
    month_window.title("Seleccionar Mes y Año")

    tk.Label(month_window, text="Selecciona el mes:").pack(pady=5)
    month_combobox = ttk.Combobox(month_window, values=list(range(1, 13)))
    month_combobox.pack(pady=5)

    current_year = datetime.now().year
    tk.Label(month_window, text="Selecciona el año:").pack(pady=5)
    year_combobox = ttk.Combobox(month_window, values=list(range(current_year - 10, 2031)))
    year_combobox.pack(pady=5)

    def submit_date():
        try:
            selected_month = int(month_combobox.get())
            selected_year = int(year_combobox.get())
            calculate_monthly_balance(bank_data, selected_month, selected_year)
        except ValueError:
            messagebox.showerror("Error", "Por favor selecciona un mes y un año válidos.")

    submit_button = tk.Button(month_window, text="Calcular Balance", command=submit_date)
    submit_button.pack(pady=10)

# Ventana para ingresar el nombre del archivo
def ask_for_filename():
    filename_window = tk.Toplevel()
    filename_window.title("Ingresar nombre del archivo")

    tk.Label(filename_window, text="Nombre del archivo (sin .json):").pack(pady=5)
    filename_entry = tk.Entry(filename_window)
    filename_entry.pack(pady=5)

    submit_button = tk.Button(filename_window, text="Cargar Archivo", command=lambda: load_bank_data_and_start(filename_entry.get()))
    submit_button.pack(pady=10)
# Filtrar transacciones por concepto
def filter_transactions_by_concept(bank_data, concept):
    filtered_transactions = [item for item in bank_data if concept.lower() in item['concepto'].lower()]
    if filtered_transactions:
        show_filtered_transactions(filtered_transactions)
    else:
        messagebox.showinfo("Filtro de Transacciones", "No se encontraron transacciones con ese concepto.")
    
def show_filtered_transactions(transactions):
    transactions_window = tk.Toplevel()
    transactions_window.title("Transacciones Filtradas")
    transactions_window.geometry("500x400")

    scrolled_text = ScrolledText(transactions_window, wrap=tk.WORD, width=60, height=20)
    scrolled_text.pack(pady=10, padx=10)

    for item in transactions:
        scrolled_text.insert(tk.END, f"Fecha: {item['fecha_oper']}\n")
        scrolled_text.insert(tk.END, f"Concepto: {item['concepto']}\n")
        scrolled_text.insert(tk.END, f"Importe: {item['importe']} €\n")
        scrolled_text.insert(tk.END, f"Saldo: {item['saldo']} €\n\n")

    scrolled_text.config(state=tk.DISABLED)

# Ventana para ingresar el concepto por el cual se quieren filtrar las transacciones
def ask_concept_to_filter(bank_data):
    concept_window = tk.Toplevel()
    concept_window.title("Filtrar por Concepto")
    
    tk.Label(concept_window, text="Ingresar concepto:").pack(pady=5)
    concept_entry = tk.Entry(concept_window)
    concept_entry.pack(pady=5)

    submit_button = tk.Button(concept_window, text="Filtrar", command=lambda: filter_transactions_by_concept(bank_data, concept_entry.get()))
    submit_button.pack(pady=10)

def calculate_annual_balance(bank_data, year):
    balance = 0.0
    transactions_in_year = []
    earliest_transaction = None
    latest_transaction = None

    for transaction in bank_data:
        transaction_date_str = transaction['fecha_oper']
        transaction_date = datetime.strptime(transaction_date_str, '%d/%m/%Y')

        # Filtrar las transacciones que estén en el año seleccionado
        if transaction_date.year == year:
            transactions_in_year.append(transaction)
            balance += float(transaction['importe'].replace(',', '.'))  # Convertir el importe a float
            
            # Determinar la transacción más temprana y más reciente
            if earliest_transaction is None or transaction_date < earliest_transaction:
                earliest_transaction = transaction_date
            if latest_transaction is None or transaction_date > latest_transaction:
                latest_transaction = transaction_date

    # Buscar el saldo más temprano y más reciente
    saldo_final = transactions_in_year[0]['saldo'] if transactions_in_year else 'N/A'
    saldo_inicial = transactions_in_year[-1]['saldo'] if transactions_in_year else 'N/A'

    # Mostrar el balance anual en una ventana
    show_annual_balance(transactions_in_year, balance, saldo_inicial, saldo_final, year)


# Mostrar el balance anual en una nueva ventana con scroll
def show_annual_balance(transactions, balance, saldo_inicial, saldo_final, year):
    balance_window = tk.Toplevel()
    balance_window.title(f"Balance de {year}")
    balance_window.geometry("500x400")

    scrolled_text = ScrolledText(balance_window, wrap=tk.WORD, width=60, height=20)
    scrolled_text.pack(pady=10, padx=10)

    # Mostrar primero el saldo inicial y final, luego el balance total del año
    scrolled_text.insert(tk.END, f"Saldo inicial: {saldo_inicial} €\n")
    scrolled_text.insert(tk.END, f"Saldo final: {saldo_final} €\n\n")
    scrolled_text.insert(tk.END, f"Balance total de {year}: {balance:.2f} €\n\n")

    # Luego mostrar las transacciones
    scrolled_text.insert(tk.END, "Transacciones del año:\n\n")
    for item in transactions:
        scrolled_text.insert(tk.END, f"Fecha: {item['fecha_oper']}\n")
        scrolled_text.insert(tk.END, f"Concepto: {item['concepto']}\n")
        scrolled_text.insert(tk.END, f"Importe: {item['importe']} €\n")
        scrolled_text.insert(tk.END, f"Saldo: {item['saldo']} €\n\n")

    scrolled_text.config(state=tk.DISABLED)


# Ventana para seleccionar el año
def ask_year_to_calculate_annual_balance(bank_data):
    year_window = tk.Toplevel()
    year_window.title("Seleccionar Año")

    current_year = datetime.now().year
    tk.Label(year_window, text="Selecciona el año:").pack(pady=5)
    year_combobox = ttk.Combobox(year_window, values=list(range(current_year - 10, 2031)))
    year_combobox.pack(pady=5)

    def submit_year():
        try:
            selected_year = int(year_combobox.get())
            calculate_annual_balance(bank_data, selected_year)
        except ValueError:
            messagebox.showerror("Error", "Por favor selecciona un año válido.")

    submit_button = tk.Button(year_window, text="Calcular Balance Anual", command=submit_year)
    submit_button.pack(pady=10)

# Cargar el archivo y comenzar la aplicación
def load_bank_data_and_start(filename):
    bank_data = load_bank_data_by_filename(filename)
    
    if not bank_data:
        return

    # Crear la ventana principal para análisis si el archivo se cargó con éxito
    root = tk.Tk()
    root.title("Analizador de Cuentas Bancarias")

    # Botón para calcular el balance de un mes y año
    btn_calculate_balance = tk.Button(root, text="Calcular Balance Mensual", command=lambda: ask_month_and_year_to_calculate_balance(bank_data))
    btn_calculate_balance.pack(pady=10)
    btn_filter_concept = tk.Button(root, text="Filtrar por Concepto", command=lambda: ask_concept_to_filter(bank_data))
    btn_filter_concept.pack(pady=10)
    btn_calculate_annual_balance = tk.Button(root, text="Calcular Balance Anual", command=lambda: ask_year_to_calculate_annual_balance(bank_data))
    btn_calculate_annual_balance.pack(pady=10)
    # Configurar la ventana
    root.geometry("300x200")
    root.mainloop()

# Función principal
def main():
    root = tk.Tk()
    root.title("Analizador de Cuentas Bancarias")

    # Botón para ingresar el nombre del archivo
    btn_select_file = tk.Button(root, text="Seleccionar archivo", command=ask_for_filename)
    btn_select_file.pack(pady=20)

    # Configurar la ventana
    root.geometry("300x150")
    root.mainloop()

if __name__ == "__main__":
    main()
