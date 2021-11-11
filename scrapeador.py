"""SCRAPING A PAGINA PDFDRIVE PARA LA APLICACIÓN TPI
    VERSION: 1.3 corregido obtener links
    Este archivo contiene 3 funciones pincipales
    SCARIPNG  A PDFDRIVE
    OBTENER LINKS
    DESCARGAR LIBRO
    AUTORES: GRUPO 10 LUISINA GIORGETTI - URIEL ALVAREZ
    """
from urllib import request
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.chrome.options import Options
import requests
from selenium.webdriver.common.by import By

# Función que toma Titulo/autor/categoria del libro para scrapear. Devuelve un dicionario de libros encontrados
def scraping_lista_libros(titulo_autor_categoria):
    options = Options()
    options.headless = True
    #options.add_argument('ignore-certificate-errors')#nuevo

    driver = webdriver.Chrome(executable_path="C:\\chromedriver.exe",
                              chrome_options=options)  # Ubicación del webdriver en mi maquina


    #driver = webdriver.Chrome(chrome_options=options)

    driver.get("https://www.pdfdrive.com/")  # Dirección de la pagina

    # Campo de Buscador de libros
    libro = driver.find_element_by_xpath('//*[@id="q"]')  # Busco el campo buscador
    libro.send_keys(titulo_autor_categoria)  # Ingreso el libro que quiero buscar
    libro.send_keys(Keys.ENTER)  # Ingreso un ENTER ya que por defecto no se hace
    time.sleep(2)  # Pongo un retardo para que espere3 segundos y no haga todo inmediato

    # Defino una lista que contendra diccionarios
    libros_organizados_datos = []

    # La esctructura de los diccionarios sera: (Titulo: "El principito", Info:"96 Pages·2013·787 KB·9,713 Downloads·Spanish", URL_IMG: "https://www.pdfdrive.com/el-principito-e39414902.JPG", URL_HTML: "https://www.pdfdrive.com/el-principito-e39414902.html")

    # Extracción de los libros
    libros = driver.find_element_by_class_name("files-new").find_elements_by_xpath(
        "//li[@onclick]")  # Extraigo el Div de los libros encontrados y luego los separo en una lista
    for libro in libros:
        # titulo del libro
        item = libro.find_element_by_class_name('file-left').find_element_by_tag_name('img')
        tit = item.get_attribute('title')

        # informacion adicional del libro
        item = libro.find_element_by_class_name('file-right').find_element_by_class_name('file-info')
        info = item.text

        # Url Imagen del libro
        item = libro.find_element_by_class_name('file-left').find_element_by_tag_name('img')
        imag = item.get_attribute('src')

        # Url del la pagina HTM para luego scrapear el link de descarga
        item = libro.find_element_by_class_name('file-left').find_element_by_tag_name('a')
        html_lib = item.get_attribute('href')

        # Ahora guardo todo en un dicionario y lo agrego a la lista
        diccionario = {"titulo": tit, "info": info, "url_img": imag, "url_html": html_lib}

        libros_organizados_datos.append(diccionario)

    time.sleep(30)
    driver.close()
    return libros_organizados_datos


# Funcion que obtiene el link de descarga al archivo PDF. Esta funcion recibe como parametro un diccionario de libro
def obtener_link(diccionario):
    link = diccionario['url_html']
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(executable_path="C:\\chromedriver.exe",
                              chrome_options=options)  # Ubicación del webdriver en mi maquina

  #  driver=webdriver.Chrome(executable_path="C:\\chromedriver.exe")

    driver.get(link)
    time.sleep(10)

    # click en "descargar"
    boton = driver.find_element_by_xpath('//*[@id="download-button-link"]')
    boton.click()

     # obtener el link del PDF
    time.sleep(10) #AQUUUII borrar
    pdf_link = driver.find_element(By.CLASS_NAME, 'text-center').find_element(By.TAG_NAME, 'a')
    link = pdf_link.get_attribute("href")
    return link


# Funcion descargar libro dado un link, es necesario mandar como parametra diccionario para formatear el nombre con el que se descarga
def descargar(link, titulo):
    url = link
    myfile = requests.get(url)

    nombre_archivo = titulo + '.pdf'

    open(nombre_archivo, 'wb').write(myfile.content)
    return nombre_archivo