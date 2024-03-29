import os
import tarfile
import requests
import asyncio
import urllib.parse
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from telegram import Bot

TOKEN = '5558634309:AAGC9BY28ru907q3hmhWwdS83F31cIjHuiQ'
chat_id = '815189312'

async def send_Error(text, error):
    print("send_error")
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=chat_id, text="Hubo un error al obtener los productos: " + str(text) + ". " + str(error))

def download_and_install_firefox():
    print("Ingresa a download_and_install_firefox")
    # URL directa de Firefox
    firefox_url = "https://download-installer.cdn.mozilla.net/pub/firefox/releases/99.0b8/linux-x86_64/en-US/firefox-99.0b8.tar.bz2"

    # Descargar Firefox
    response = requests.get(firefox_url)
    with open("firefox.tar.bz2", 'wb') as f:
        f.write(response.content)

    # Descomprimir el archivo tar.bz2 por bloques
    block_size = 1024 * 1024  # 1 MB
    with tarfile.open("firefox.tar.bz2", 'r:bz2') as tar_ref:
        while True:
            member = tar_ref.next()
            if member is None:
                break
            if member.isreg():
                print("descompresión firefox")
                block = tar_ref.extractfile(member).read(block_size)
                # Aquí puedes procesar el bloque como lo necesites

    # Eliminar el archivo tar.bz2 después de descomprimir
    os.remove("firefox.tar.bz2")

def download_and_install_geckodriver():
    print("ingresa a donwload_and_install_geckoDriver")
    # URL directa de Geckodriver
    geckodriver_url = "https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-linux64.tar.gz"

    # Descargar Geckodriver
    response = requests.get(geckodriver_url)
    with open("geckodriver.tar.gz", 'wb') as f:
        f.write(response.content)

    # Descomprimir el archivo tar.gz por bloques
    block_size = 1024 * 1024  # 1 MB
    with tarfile.open("geckodriver.tar.gz", 'r:gz') as tar_ref:
        while True:
            member = tar_ref.next()
            if member is None:
                break
            if member.isreg():
                print("descomprime")
                block = tar_ref.extractfile(member).read(block_size)
                # Aquí puedes procesar el bloque como lo necesites

    # Eliminar el archivo tar.gz después de descomprimir
    os.remove("geckodriver.tar.gz")

def ejecutar_codigo():
    try:
        print("Instalador 1")
        # Descargar e instalar Firefox y Geckodriver
        download_and_install_firefox()
        print("Instalador 2")
        download_and_install_geckodriver()
        print("paso los instaladores")

        # Configurar Selenium con Firefox y especificar la ubicación del controlador y del binario de Firefox
        print("firefox 1")
        firefox_options = FirefoxOptions()
        print("firefox 2")
        firefox_options.headless = True  # Para ejecución sin interfaz gráfica
        print("firefox 3")
        firefox_binary = os.path.abspath('./firefox/firefox/firefox')  # Ruta absoluta al binario de Firefox que hemos descargado
        print("firefox 4")
        geckodriver_binary = os.path.abspath('./geckodriver')  # Ruta absoluta al controlador de Geckodriver que hemos descargado
        print("firefox 5")
        driver = webdriver.Firefox(service=FirefoxService(executable_path=geckodriver_binary, firefox_binary=firefox_binary), options=firefox_options)
        print("ejecutó todo lo de firefox")

        # Realizar una solicitud HTTP para obtener el contenido de la página y renderizarlo
        driver.get('https://guatemaladigital.com/')
        print("entro a la pag")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        print("pasó a html")

        # Buscar todos los bloques con la estructura especificada
        bloques = soup.find_all('div', class_='bloque--oferta marco--oferta--item mx-0')
        print("encontró bloques")

        # Crear un conjunto para almacenar productos únicos
        productos_procesados = set()
        print("encontró bloques")

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
            driver.quit()
            
        # Cerrar el navegador
        driver.quit()

    except ValueError:
        asyncio.run(send_Error("2", ValueError))

ejecutar_codigo()
