import cv2
import pytesseract
import json
import re
import os
import unicodedata
import PyPDF2
from PIL import Image
from tkinter import Tk, filedialog, simpledialog, messagebox, Button, Frame

def preprocess_image(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    _, image = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY)
    return image

def extract_text_from_image(image_path):
    image = preprocess_image(image_path)
    text = pytesseract.image_to_string(image, config='--psm 6')
    text = correct_ocr_errors(text)
    return text

def extract_text_from_pdf(pdf_path):
    """Extrae y printa texto de un archivo PDF usando PyPDF2."""
    text = ""
    
    # Abre el archivo PDF en modo lectura binaria
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        
        # Recorre todas las páginas del PDF y extrae el texto
        for page in reader.pages:
            text += page.extract_text()
    
    # Imprime el texto extraído
    
    # Retorna el texto extraído
    return text

def correct_ocr_errors(text):
    """
    Corrige los errores comunes de OCR en el texto extraído, como confundir '0' con '@' y otros casos similares.
    """
    # Reemplazar '@' por '0' en el contexto de precios y números
    text = re.sub(r'@', '0', text)

    # Reemplazar patrones de fecha malinterpretados (p. ej., "87/89/2024")
    text = re.sub(r'(\d{2})/(\d{2})/(\d{4})', r'\1/\2/\3', text)

    # Reemplazar otros errores comunes si es necesario, por ejemplo:
    # Si el OCR confunde "8" con "0", podemos hacerlo en lugares específicos
    # Aquí puedes añadir más reglas según otros problemas que observes

    return text


def extract_total_amount(extracted_text):
    total_pattern = re.compile(r'total\s*[:\s]*\n?\s*\€?\$?\d+[.,]?\d*', re.IGNORECASE)
    match = total_pattern.search(extracted_text)
    if match:
        total_amount = re.search(r'\€?\$?\d+[.,]?\d*', match.group()).group()
        return total_amount
    else:
        return "No encontrado"

def extract_store_name(extracted_text):
    lines = extracted_text.split('\n')
    for line in lines:
        if re.match(r'[A-Z]{2,}', line):
            return line.strip()
    return "No encontrado"

def clean_store_name(store_name):
    store_name = store_name.lower()
    store_name = ''.join(
        c for c in unicodedata.normalize('NFD', store_name)
        if unicodedata.category(c) != 'Mn'
    )
    store_name = re.sub(r'[^a-z\s]', '', store_name)
    return store_name

def clean_total_amount(total_amount):
    total_amount = re.sub(r'[^0-9.]', '', total_amount)
    return total_amount

def process_ticket(file_path):
    """Procesa el ticket dependiendo de si es una imagen o PDF."""
    if file_path.lower().endswith('.pdf'):
        extracted_text = extract_text_from_pdf(file_path)
    else:
        extracted_text = extract_text_from_image(file_path)

    store_name = extract_store_name(extracted_text)
    total_amount = extract_total_amount(extracted_text)

    print(f"Nombre de la tienda: {store_name}")
    print(f"Monto total: {total_amount}")

    save_to_json(store_name, total_amount)

    if "mercadona" in store_name.lower():
        process_mercadona_ticket(extracted_text)

    # Imprimir el texto extraído al final del procesamiento
    print("\nTexto extraído completo:")
    print(extracted_text)

    if "lidl" in store_name.lower():
        process_lidl_ticket(extracted_text)

def parse_line_devolucion(line):
    """
    Analiza una línea del ticket y extrae la cantidad, descripción y precio unitario.
    Devuelve un diccionario con los detalles del artículo o None si no es una línea válida.
    """
    # Modificar la línea para asegurar que haya un espacio entre la cantidad y la descripción
    # Y que el precio esté al final. Incluye soporte para cantidades y precios negativos.
    line = re.sub(r'^(-?\d+)\s*(.*)\s+(-?[\d,.]+)$', r'\1 \2 \3', line)

    # Usar expresión regular para extraer la cantidad y el precio, incluyendo negativos
    match = re.match(r'^(-?\d+)\s+(.*)\s+(-?[\d,.]+)$', line)
    if match:
        try:
            # Extraer la cantidad (primer elemento) y asegurar que sea un número entero
            cantidad = int(match.group(1))
            
            # Extraer la descripción (todo entre cantidad y precio)
            descripcion = match.group(2).strip()
            
            # Extraer el precio (último elemento) y asegurar que sea un número flotante
            precio_unitario = float(match.group(3).replace(',', '.'))
            
            # Crear un diccionario para el artículo
            return {
                "descripcion": descripcion,
                "cantidad": cantidad,
                "precio_unitario": precio_unitario
            }
        except ValueError as e:
            print(f"Error al procesar la línea: {line}. Error: {e}")
            return None
    else:
        print(f"No se pudo hacer match con la línea: {line}")
        return None
    
def parse_line(line):
    """
    Analiza una línea del ticket y extrae la cantidad, descripción y precio unitario.
    Devuelve un diccionario con los detalles del artículo o None si no es una línea válida.
    """
    # Modificar la línea para asegurar que haya un espacio entre la cantidad y la descripción
    # Y que el precio esté al final
    line = re.sub(r'^(\d)(\d*)\s*(.*)\s+([\d,.]+)$', r'\1 \2 \3 \4', line)

    # Usar expresión regular para extraer la cantidad y el precio
    match = re.match(r'^(\d+)\s+(.*)\s+([\d,.]+)$', line)
    print(line)
    if match:
        try:
            # Extraer la cantidad (primer elemento)
            cantidad = int(match.group(1))
            
            # Extraer la descripción (todo entre cantidad y precio)
            descripcion = match.group(2).strip()
            
            # Extraer el precio (último elemento)
            precio_unitario = float(match.group(3).replace(',', '.'))
            precio_unitario = precio_unitario / cantidad
            # Crear un diccionario para el artículo
            return {
                "descripcion": descripcion,
                "cantidad": cantidad,
                "precio_unitario": precio_unitario
            }
        except ValueError as e:
            print(f"Error al procesar la línea: {line}. Error: {e}")
            return None
    else:
        print(f"No se pudo hacer match con la línea: {line}")
        return None


def process_mercadona_ticket(extracted_text):
    """Procesa un ticket de Mercadona y guarda los detalles en un archivo JSON."""
    items = []
    precio_total = 0.0

    # Extraer la fecha de compra
    date_pattern = re.compile(r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}')
    match = date_pattern.search(extracted_text)
    fecha_compra = match.group() if match else "Fecha no encontrada"

    lines = extracted_text.split('\n')
    start_reading_items = False

    for line in lines:
        # Detectar la sección de ítems
        if "Descripción P. Unit Importe" in line:
            start_reading_items = True
            continue
        
        if start_reading_items:
            # Detectar el final de la sección de ítems
            if line.startswith("TOTAL"):
                break
            
            # Procesar la línea
            item = parse_line(line)
            if item:
                # Calcular el precio total
                precio_total += item["cantidad"] * item["precio_unitario"]
                items.append(item)

    # Verificar si hay items antes de guardar
    if items:
        # Crear el diccionario de datos del ticket de Mercadona
        mercadona_data = {
            "id": get_next_id(),  # ID único
            "fecha_compra": fecha_compra,  # Añadir la fecha de compra al JSON
            "items": items,
            "precio_total": round(precio_total, 2)
        }

        # Guardar los datos de Mercadona en un archivo JSON
        if os.path.exists('mercadona_tickets.json'):
            with open('mercadona_tickets.json', 'r+', encoding='utf-8') as file:
                file_data = json.load(file)
                file_data.append(mercadona_data)
                file.seek(0)
                json.dump(file_data, file, indent=4, ensure_ascii=False)
        else:
            with open('mercadona_tickets.json', 'w', encoding='utf-8') as file:
                json.dump([mercadona_data], file, indent=4, ensure_ascii=False)
        print("Datos del ticket de Mercadona guardados en mercadona_tickets.json")
    else:
        print("No se encontraron artículos en el ticket de Mercadona.")

def get_next_id():
    """Obtiene el próximo ID único para el ticket de Mercadona."""
    if os.path.exists('mercadona_tickets.json'):
        with open('mercadona_tickets.json', 'r', encoding='utf-8') as file:
            file_data = json.load(file)
            return len(file_data) + 1
    else:
        return 1

def normalize_string(s):
    """Convierte una cadena a minúsculas y elimina tildes."""
    s = s.lower()
    s = ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn'
    )
    return s
def process_mercadona_return_ticket(extracted_text):
    """Procesa un ticket de devolución de Mercadona y guarda los detalles en un archivo JSON."""
    items = []
    precio_total = 0.0

    # Extraer la fecha de la devolución
    date_pattern = re.compile(r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}')
    match = date_pattern.search(extracted_text)
    fecha_compra = match.group() if match else "Fecha no encontrada"

    lines = extracted_text.split('\n')
    start_reading_items = False

    for line in lines:
        # Detectar la sección de ítems de devolución
        if "Descripción P. Unit Importe" in line:
            start_reading_items = True
            continue
        
        if start_reading_items:
            # Detectar el final de la sección de ítems de devolución
            if line.startswith("TOTAL"):
                break
            
            # Procesar la línea
            item = parse_line_devolucion(line) 
            if item:
                # Convertir cantidad y precio a negativos
                item["cantidad"] = -abs(item["cantidad"])
                item["precio_unitario"] = -abs(item["precio_unitario"])

                # Calcular el precio total en negativo
                precio_total += item["cantidad"] * item["precio_unitario"]
                precio_total = -abs(precio_total)
                items.append(item)

    # Verificar si hay items antes de guardar
    if items:
        # Crear el diccionario de datos del ticket de devolución de Mercadona
        mercadona_return_data = {
            "id": get_next_id(),  # ID único
            "fecha_compra": fecha_compra,  # Añadir la fecha de devolución al JSON
            "items": items,
            "precio_total": round(precio_total, 2)
        }

        # Guardar los datos de devolución de Mercadona en el mismo archivo JSON
        if os.path.exists('mercadona_tickets.json'):
            with open('mercadona_tickets.json', 'r+', encoding='utf-8') as file:
                file_data = json.load(file)
                file_data.append(mercadona_return_data)
                file.seek(0)
                json.dump(file_data, file, indent=4, ensure_ascii=False)
        else:
            with open('mercadona_tickets.json', 'w', encoding='utf-8') as file:
                json.dump([mercadona_return_data], file, indent=4, ensure_ascii=False)
        print("Datos del ticket de devolución de Mercadona guardados en mercadona_tickets.json")
    else:
        print("No se encontraron artículos en el ticket de devolución de Mercadona.")

def save_to_json(merchant_name, total_amount):
    """Guarda los datos normalizados en un archivo JSON."""
    # Normalizar nombre de la tienda
    merchant_name = normalize_string(merchant_name)
    
    # Normalizar el monto total
    total_amount = total_amount.replace(',', '.')
    
    # Crear el diccionario de datos
    data = {'merchant_name': merchant_name, 'total_amount': total_amount}
    
    # Guardar los datos en un archivo JSON
    if os.path.exists('tickets.json'):
        with open('tickets.json', 'r+', encoding='utf-8') as file:
            file_data = json.load(file)
            file_data.append(data)
            file.seek(0)
            json.dump(file_data, file, indent=4, ensure_ascii=False)
    else:
        with open('tickets.json', 'w', encoding='utf-8') as file:
            json.dump([data], file, indent=4, ensure_ascii=False)
    print("Datos guardados en tickets.json")

def manual_input():
    """Permite al usuario ingresar manualmente los datos del ticket."""
    store_name = simpledialog.askstring("Input", "Introduce el nombre de la tienda:")
    total_amount = simpledialog.askstring("Input", "Introduce el monto total (por ejemplo, 10.10):")
    
    if store_name and total_amount:
        save_to_json(store_name, total_amount)
        print(f"Nombre de la tienda: {store_name}")
        print(f"Monto total: {total_amount}")
        messagebox.showinfo("Éxito", "Datos guardados correctamente.")
    else:
        messagebox.showwarning("Error", "Debe ingresar todos los datos.")


def upload_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        process_ticket(file_path)

import pdfplumber

def extraer_transacciones(pdf_path):
    transacciones = []
    id_counter = 1
    fecha_pattern = r"\d{2}/\d{2}/\d{4}"  # Regex para encontrar fechas en formato dd/mm/yyyy

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            texto = page.extract_text()
            if "FECHA OPER CONCEPTO FECHA VALOR IMPORTE SALDO" in texto:
                lines = texto.split('\n')
                start_extraction = False
                for line in lines:
                    if "FECHA OPER CONCEPTO FECHA VALOR IMPORTE SALDO" in line:
                        start_extraction = True
                        continue
                    if start_extraction and line.strip():  # Ignorar líneas vacías
                        # Buscar las dos primeras fechas en la línea
                        fechas = re.findall(fecha_pattern, line)
                        if len(fechas) >= 2:
                            fecha_oper = fechas[0]
                            fecha_valor = fechas[1]
                            
                            # Extraer las partes de la línea basadas en las fechas encontradas
                            partes = re.split(fecha_pattern, line)
                            
                            # El concepto está entre la primera fecha y la segunda fecha
                            concepto = partes[1].strip() if len(partes) > 2 else ""
                            
                            # El resto es después de la segunda fecha
                            resto = line.split(fecha_valor)[-1].strip()

                            # Dividir el resto para obtener importe y saldo
                            partes_resto = resto.split()
                            if len(partes_resto) >= 2:
                                importe = partes_resto[-2]  # Penúltimo valor
                                saldo = partes_resto[-1]    # Último valor
                                
                                # Crear un diccionario para la transacción
                                transaccion = {
                                    "id": id_counter,
                                    "fecha_oper": fecha_oper,
                                    "concepto": concepto,
                                    "fecha_valor": fecha_valor,
                                    "importe": importe,
                                    "saldo": saldo
                                }
                                
                                # Incrementar el contador de ID
                                id_counter += 1
                                
                                # Añadir la transacción a la lista
                                transacciones.append(transaccion)

    return transacciones
def save_transactions_to_json(transactions, json_filename):
    with open(json_filename, 'w') as json_file:
        json.dump(transactions, json_file, indent=4)

def import_bank_statement():
    json_filename = simpledialog.askstring("Guardar como", "Ingrese el nombre del archivo JSON:")
    
    if json_filename:
        json_filename = json_filename + ".json"
        pdf_path = filedialog.askopenfilename(
            title="Seleccionar archivo PDF",
            filetypes=(("PDF files", "*.pdf"), ("all files", "*.*"))
        )
        
        if pdf_path:
            transactions = extraer_transacciones(pdf_path)
            save_transactions_to_json(transactions, json_filename)
            print(f"Transacciones guardadas en {json_filename}")

def upload_return_file():
    """Permite al usuario seleccionar un archivo de devolución para procesar."""
    file_path = filedialog.askopenfilename()
    if file_path:
        extracted_text = extract_text_from_pdf(file_path)
        process_mercadona_return_ticket(extracted_text)

def process_lidl_ticket(extracted_text):
    """Procesa un ticket de Lidl y guarda los detalles en un archivo JSON."""
    items = []
    precio_total = 0.0

    # Extraer la fecha de compra
    date_pattern = re.compile(r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}')
    match = date_pattern.search(extracted_text)
    fecha_compra = match.group() if match else "Fecha no encontrada"

    lines = extracted_text.split('\n')
    start_reading_items = False

    for line in lines:
        # Ignorar cualquier línea que contenga "Total" para evitar agregarla como un producto
        if "Total" in line:
            break

        # Detectar la sección de ítems y extraer toda la descripción antes del precio
        match = re.match(r'(.+?)\s+(\d+[.,]\d{2})', line)
        if match:
            try:
                # Extraer la descripción completa (todo el texto antes del precio)
                descripcion = match.group(1).strip()
                precio_unitario = float(match.group(2).replace(',', '.'))

                # Crear un diccionario para el artículo, asumiendo cantidad 1
                item = {
                    "descripcion": descripcion,
                    "cantidad": 1,  # Asumimos cantidad 1 si no se especifica explícitamente
                    "precio_unitario": precio_unitario
                }
                items.append(item)
                precio_total += precio_unitario
            except ValueError as e:
                print(f"Error al procesar la línea: {line}. Error: {e}")
                continue

    # Verificar si hay items antes de guardar
    if items:
        # Crear el diccionario de datos del ticket de Lidl
        lidl_data = {
            "id": get_next_id_lidl(),  # ID único
            "fecha_compra": fecha_compra,  # Añadir la fecha de compra al JSON
            "items": items,
            "precio_total": round(precio_total, 2)
        }

        # Guardar los datos del ticket de Lidl en un archivo JSON
        if os.path.exists('lidl_tickets.json'):
            with open('lidl_tickets.json', 'r+', encoding='utf-8') as file:
                file_data = json.load(file)
                file_data.append(lidl_data)
                file.seek(0)
                json.dump(file_data, file, indent=4, ensure_ascii=False)
        else:
            with open('lidl_tickets.json', 'w', encoding='utf-8') as file:
                json.dump([lidl_data], file, indent=4, ensure_ascii=False)
        print("Datos del ticket de Lidl guardados en lidl_tickets.json")
    else:
        print("No se encontraron artículos en el ticket de Lidl.")



def get_next_id_lidl():
    """Obtiene el próximo ID único para el ticket de Lidl."""
    if os.path.exists('lidl_tickets.json'):
        with open('lidl_tickets.json', 'r', encoding='utf-8') as file:
            file_data = json.load(file)
            return len(file_data) + 1
    else:
        return 1

def upload_lidl_file():
    """Permite al usuario seleccionar un archivo de ticket de Lidl para procesar."""
    file_path = filedialog.askopenfilename()
    if file_path:
        extracted_text = extract_text_from_pdf(file_path)
        process_lidl_ticket(extracted_text)


def create_button(parent, text, command):
    button = Button(parent, text=text, command=command)
    button.pack(fill='x', padx=10, pady=5)

def main():
    root = Tk()
    root.title("Ticket Analyzer")
    
    button_frame = Frame(root)
    button_frame.pack(padx=20, pady=20)

    create_button(button_frame, "Importar Ticket automaticamente", upload_file)
    create_button(button_frame, "Importar Cuenta Bancaria", import_bank_statement)
    create_button(button_frame, "Importar Devolución", upload_return_file)

    root.mainloop()

if __name__ == "__main__":
    main()
