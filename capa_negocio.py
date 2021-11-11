from gtts import gTTS
import PyPDF2
from io import BytesIO
from io import StringIO
import re
import pyttsx3
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.layout import LAParams
from pdfminer.converter import TextConverter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pygame import mixer
from pydub import AudioSegment
import os
from datetime import datetime, timedelta
# from nombre_archivo import funcion
#import scrapeador as scr
from db import agregar_libro, buscar_libros_recientes, buscar_datos_audio, \
   buscar_libros_descargados, borrar_audio, guardar_datos_audio, crear_base_datos, crear_tabla_libro
import scrapeador as scr

def iniciar_base():
   crear_base_datos()
   crear_tabla_libro()

def guardar_audio_desde_dispositivo(direccion):
   #NOMBRE DEL ARCHIVO

   nombre = os.path.basename(direccion)
   nombre = nombre[:-4]
   direccion_ogg = convertir_pdf_audio(direccion, nombre)
   #FECHA ACTUAL
   now = datetime.now()
   fecha = now.strftime('%Y-%m-%d %H:%M:%S')
   datos = [nombre, 'user', 'audiobook.png',fecha, 0.0, direccion_ogg]
   agregar_libro(datos)


def agregados_recientes():
   # Base de datos comparar fechas actual y f descarga
   lista_agregados_recientes = []
   fecha_actual = datetime.now()
   dias = timedelta(days=16)
   fecha_buscar = fecha_actual- dias
   fecha_buscar_formateada = fecha_buscar.strftime('%Y-%m-%d %H:%M:%S')
   lista_agregados_recientes = buscar_libros_recientes(fecha_buscar_formateada)
   return lista_agregados_recientes


def libros_descargados():
   # Devuelve una lista con los libros descargados
   lista_libros_descargados = buscar_libros_descargados()
   return lista_libros_descargados


def mostrar_libros_para_descargar(titulo_autor_categ):
   # llama a la funcion scraping
   lista = []
   lista = scr.scraping_lista_libros(titulo_autor_categ)
   return lista


def mostar_datos_audio(id_libro):
   # Devuelve url img, url audio, tiempo
   lista_datos_audio = []
   lista_datos_audio = buscar_datos_audio(id_libro)
   return lista_datos_audio


def buscar_link_descarga(dicc_libro):
   link_descarga = scr.obtener_link(dicc_libro)
   titulo = dicc_libro['titulo']
   url_imagen = dicc_libro['url_img']
   descargar_libro(link_descarga,titulo,url_imagen)


def descargar_libro(link_descarga, titulo_libro,url_imagen):
   # descarga pdf y llama funcion convertir a audio
   nombre_archivo = scr.descargar(link_descarga, titulo_libro)
   direcc = os.path.abspath(nombre_archivo)
   guardar_audio_scrapeado(direcc, titulo_libro, url_imagen)

def guardar_audio_scrapeado(direccion, titulo_libro, url_imagen):
   direccion_ogg = convertir_pdf_audio(direccion, titulo_libro)
   # FECHA ACTUAL
   now = datetime.now()
   fecha = now.strftime('%Y-%m-%d %H:%M:%S')
   datos = [titulo_libro, 'PDFDrive', url_imagen, fecha, 0.0, direccion_ogg]
   agregar_libro(datos)

def borrar_libro(id_audio):
   # Le paso id
   datos_audio = buscar_datos_audio(id_audio)
   borrar_audio(id_audio)
   path_audio = datos_audio[0][3]
   os.remove(path_audio)

def guardar_minutos_audio(idlibro, tiempo, tiempo_total):
   datos_audio = buscar_datos_audio(idlibro)
   tiempo_actualizado = datos_audio[0][2] + tiempo
   if tiempo_actualizado > tiempo_total:
      guardar_datos_audio(idlibro, 0.0)
   else:
      guardar_datos_audio(idlibro, tiempo_actualizado)

def reiniciar_tiempo_audio(id_audio):
   guardar_datos_audio(id_audio, 0.0)



#¡IMPORTANTE! LAS FUNCIONES (convertir_pdf_audio Y limpiar_pdf) SE ACCEDEN SOLO DESDE LA CAPA NEGOCIO
def convertir_pdf_audio(direccion, titulo):

   resource_manager = PDFResourceManager(caching=True)
   our_text = StringIO()
   la_params = LAParams()
   text_converter = TextConverter(resource_manager, our_text, laparams=la_params)

   direccion_nueva = limpiar_pdf(direccion)

   archivo = open(direccion_nueva, 'rb')
   interpreter = PDFPageInterpreter(resource_manager, text_converter)

   for page in PDFPage.get_pages(archivo, pagenos=set(), maxpages=0, password='', caching=True,
                                 check_extractable=True):
      interpreter.process_page(page)

   text = our_text.getvalue()
   archivo.close()
   text_converter.close()
   our_text.close()
   mp3_fp = BytesIO()
   speaker = pyttsx3.init()
   text = text.replace('\n', '')

   nombre_wav = titulo + '.wav'
   speaker.save_to_file(text, nombre_wav)
   speaker.runAndWait()
   nombre_ogg = titulo + '.ogg'
   AudioSegment.from_mp3(nombre_wav).export(nombre_ogg, format='ogg')
   try:
      os.remove(direccion_nueva)
      path_wav = os.path.abspath(nombre_wav)
      os.remove(path_wav)
   except:
      print('Salio mal')
   path_ogg = os.path.abspath(nombre_ogg)
   return path_ogg

def limpiar_pdf(direccion):
   book = open(direccion, 'rb')
   pdfReader = PyPDF2.PdfFileReader(book)
   libro = PyPDF2.PdfFileWriter()

   for pagina in pdfReader.pages:
      libro.addPage(pagina)
      libro.removeLinks()
      libro.removeImages(ignoreByteStringObject=False)
   with open('new.pdf', 'wb') as f:
      libro.write(f)
   path = os.path.abspath(f.name)
   return path





