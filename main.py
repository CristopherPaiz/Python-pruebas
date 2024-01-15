from bs4 import BeautifulSoup
import asyncio
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from telegram import Bot
from webdriver_manager.chrome import ChromeDriverManager

TOKEN = '5558634309:AAGC9BY28ru907q3hmhWwdS83F31cIjHuiQ'
chat_id = '815189312'

async def send_Error(text, error):
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=chat_id, text="Hubo un error al obtener los productos: " + str(text) + ". " + str(error))

def ejecutar_codigo():
    try:
        # Configurar Selenium con Chrome
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Para ejecución sin interfaz gráfica
        # service = ChromeService(executable_path='path/to/chromedriver')  # Reemplaza con la ubicación de tu chromedriver
        # driver = webdriver.Chrome(service=service, options=chrome_options)
        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))

        # Realizar una solicitud HTTP para obtener el contenido de la página y renderizarla
        driver.get('https://guatemaladigital.com/')
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Buscar todos los bloques con la estructura especificada
        bloques = soup.find_all('div', class_='bloque--oferta marco--oferta--item mx-0')

        # Crear un conjunto para almacenar productos únicos
        productos_procesados = set()

        # Definimos la función que comunica a Telegram
        async def send_message(imagen, descripcion, precio_normal, precio_oferta, descuento, enlace):
            urlUnida = "https://guatemaladigital.com" + enlace
            message = f'<b><u>PRODUCTO:</u></b>\n' \
                      f'{descripcion}\n===================================\n' \
                      f'<b><u>Antes:</u></b> Q. {precio_normal}' \
                      f'     <b><u>Ahora:</u></b> Q. {precio_oferta}' \
                      f'     <i><b><u>% {descuento} %</u></b></i>\n' \
                      f'<a href="{urlUnida}">Ver el producto</a>'

            bot = Bot(token=TOKEN)
            await bot.send_photo(chat_id=chat_id, photo=imagen, caption=message, parse_mode='HTML')

        # Iterar a través de los bloques y extraer la información
        for bloque in bloques:
            # 1. Extraer la descripción de la etiqueta <p>
            descripcion = bloque.find('p', class_='cort_not_h').text.strip()

            # Verificar si ya hemos procesado este producto
            if descripcion in productos_procesados:
                continue  # Si ya se procesó, pasamos al siguiente bloque

            try:
                # 2. Extraer el precio normal de la etiqueta <span class="precio">
                precio_normal = bloque.find('span', class_='precio').text.strip()

                # 3. Extraer el precio de oferta de la etiqueta <div class="oferta--boton2">
                precio_oferta = bloque.find('div', class_='oferta--boton2').text.strip()

                # 4. Extraer el src de la etiqueta <img> y procesar la URL
                img_src = bloque.find('img')['src']
                img_src = img_src.replace('/_next/image?url=', '')  # Eliminar "/_next/image?url=" de la imagen
                img_src = urllib.parse.unquote(img_src)  # Decodificar la URL
                img_src = img_src.split('&w=')[0]  # Eliminar "&w=384&q=75" de la imagen

                # 5. Extraer el enlace (href) de la etiqueta <a>
                enlace = bloque.find('a', class_='product--a-oferta')['href']

                # Realizar la operación matemática para verificar el descuento
                precio_normal = float(precio_normal[1:])  # Eliminar el símbolo 'Q' y convertir a float
                precio_oferta = float(precio_oferta[1:])  # Eliminar el símbolo 'Q' y convertir a float

                # Calcular el descuento en porcentaje y redondearlo a 2 decimales
                descuento = round(((precio_normal - precio_oferta) / precio_normal) * 100, 2)

                # Verificar si el descuento es mayor al 55%
                if descuento > 65:
                    asyncio.run(
                        send_message(img_src, descripcion, precio_normal, precio_oferta, descuento, enlace))

                    # Agregamos la descripción al conjunto de productos procesados
                    productos_procesados.add(descripcion)

            except ValueError:
                asyncio.run(send_Error("1", ValueError))
                pass

        # Verificar si no se encontraron productos y enviar un mensaje de error
        if not productos_procesados:
            asyncio.run(send_Error("No se encontraron productos con descuento", None))

        # Cerrar el navegador
        driver.quit()

    except ValueError:
        asyncio.run(send_Error("2", ValueError))

ejecutar_codigo()