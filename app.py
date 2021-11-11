from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import OneLineIconListItem, MDList, TwoLineListItem, OneLineListItem, ThreeLineListItem
from kivymd.theming import ThemableBehavior
from kivy.properties import StringProperty, ListProperty, ObjectProperty
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.icon_definitions import md_icons
from kivymd.uix.button import MDIconButton, MDRectangleFlatButton, MDFlatButton
from kivy.uix.scrollview import ScrollView
from kivymd.uix.screen import MDScreen
from kivy.animation import Animation
from kivymd.uix.relativelayout import MDRelativeLayout
from pygame import mixer
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.card import MDCard
from kivymd.uix.bottomsheet import MDCustomBottomSheet
from kivy.factory import Factory

from controller.capa_negocio import libros_descargados, guardar_audio_desde_dispositivo,\
    agregados_recientes, mostar_datos_audio, borrar_libro, guardar_minutos_audio, reiniciar_tiempo_audio,\
    mostrar_libros_para_descargar, buscar_link_descarga, iniciar_base
from kivymd.uix.spinner import MDSpinner


import os




#Import solo para testear - INICIO
from kivy.core.window import Window
Window.size = (300,500)
#Import solo para testear - FIN





class Audio(MDRelativeLayout):
    dialog = None
    sonido = None
    mixer.init()
    def reproducir_libro(self, direccion, tiempo):
        #LLEVA UN PARÁMETRO CON LA POSICION EN LA QUE ESTABA
        mixer.music.stop()
        mixer.music.unload()
        self.sonido = mixer.Sound(direccion)
        mixer.music.load(direccion)
        mixer.music.set_volume(0.5)
        mixer.music.play(0,tiempo)
        mixer.music.pause()

    def play_audio(self,*args):
        if mixer.music.get_pos() == -1:
            mixer.music.play()
        else:
            mixer.music.unpause()

    def pausar_audio(self):
        mixer.music.pause()

    def cambiar_icono(self):

        if self.ids.boton_reproductor.icon == 'play-circle-outline':
            self.ids.boton_reproductor.icon = 'pause-circle-outline'
            self.play_audio()
        else:
            self.ids.boton_reproductor.icon = 'play-circle-outline'
            self.pausar_audio()

    def mutear_audio(self):
        mixer.music.set_volume(0.0)
        self.ids.volumen.value = 0

    def subir_volumen_audio(self):
        mixer.music.set_volume(1.0)
        self.ids.volumen.value = 100

    def volumen_slider(self):
        vol = self.ids.volumen.value
        mixer.music.set_volume(vol/100)

    def mostrar_advertencia(self):
        if not self.dialog:
            self.dialog = MDDialog(
                title = '¿Desea detener el audio?',
                text = 'No podrá volver a este punto manualmente',
                buttons=[MDFlatButton(text="CANCELAR", on_release = self.cerrar_advertencia),
                    MDRectangleFlatButton(text="ACEPTAR", on_release = self.parar_audio),],)
        self.dialog.open()

    def cerrar_advertencia(self, obj):
        self.dialog.dismiss()

    def parar_audio(self, obj):
        mixer.music.stop()
        self.ids.boton_reproductor.icon = 'play-circle-outline'
        if obj != None:
            id_audio = Programa.get_running_app().id_audio_actual
            reiniciar_tiempo_audio(id_audio)
            self.dialog.dismiss()

    def obtener_posicion(self):
        return mixer.music.get_pos()

    def obtener_tiempo_total(self):
        return self.sonido.get_length()



class Tab(MDFloatLayout, MDTabsBase):
    '''Class implementing content for a tab.'''
    pass


class ContentNavigationDrawer(MDBoxLayout):
    screen_manager = ObjectProperty()
    nav_drawer = ObjectProperty()

class ItemDrawer(OneLineIconListItem):
    icon = StringProperty()
    text_color = ListProperty((0, 0, 0, 1))


class DrawerList(ThemableBehavior, MDList):
    def set_color_item(self, instance_item):
        """Called when tap on a menu item."""
        # Set the color of the icon and text for the menu item.
        for item in self.children:
            if item.text_color == self.theme_cls.primary_color:
                item.text_color = self.theme_cls.text_color
                break
        instance_item.text_color = self.theme_cls.primary_color

class AgregadosRecientes (ScrollView):
    def buscar_libros_recientes(self):

        recientes = agregados_recientes()

        sm = self.ids['sm_recientes']
        if recientes == []:
            sm.current = 'sin-libros'
        else:
            sm.current = 'libros-recientes'
            self.ids.lista_recientes.clear_widgets()
            for r in recientes:
                app = Programa.get_running_app()
                self.ids.lista_recientes.add_widget(ThreeLineListItem(text=str(r[1]), secondary_text=str(r[2]), tertiary_text = str(r[0]),
                                                                      tertiary_theme_text_color ='Custom', tertiary_text_color = (1,1,1,1),
                                                                      on_press = lambda x: app.abrir_audio(x.text,x.secondary_text, x.tertiary_text)))


class LibrosDescargados(ScrollView):
    lista_descargados = ListProperty()
    def buscar_libros_descargados(self):

        libros = libros_descargados()

        sm = self.ids['sm_descargados']
        if libros == []:
            sm.current = 'vacio'
        else:
            sm.current = 'libros-descargados'
            self.ids.lista_descargados.clear_widgets()
            for l in libros:
                app = Programa.get_running_app()
                self.ids.lista_descargados.add_widget(ThreeLineListItem(text=str(l[1]), secondary_text=str(l[2]), tertiary_text = str(l[0]),
                                                                        tertiary_theme_text_color='Custom',tertiary_text_color=(1, 1, 1, 1),
                                                                      on_press = lambda x: app.abrir_audio(x.text,x.secondary_text, x.tertiary_text)))

class BuscarDescargados(MDScreen):

    def mostrar_libros(self, text="", search=False):

        libros = libros_descargados()
        sm = self.ids['sm_buscar']
        if libros == []:
            sm.current = 'buscar_vacio'
        else:
            sm.current = 'buscar_descargados'
            def add_book(titulo, autor, id_libro):
                app = Programa.get_running_app()
                self.ids.rv.data.append({"viewclass": "ListaBuscar", "text": titulo,
                                         "secondary_text": autor,
                                         "on_press": (lambda : app.abrir_audio(titulo,autor, id_libro))})

            self.ids.rv.data = []
            for libro in libros:
                if search:
                    if (text.lower() in libro[1].lower()) or (text.lower() in libro[2].lower()):
                        add_book(libro[1],libro[2], libro[0])
                else:
                    add_book(libro[1],libro[2], libro[0])


class ListaBuscar(TwoLineListItem):
    text = StringProperty()
    secondary_text = StringProperty()


class ListaSugerencias(OneLineListItem):
    texto = StringProperty()


class LibrosPag(MDScreen):
    def agregar_libros(self, input = ''):
        libros = mostrar_libros_para_descargar(input)

        def add_book(titulo,descripcion, url_imagen, url_html):
            self.ids.rv_libros_pag.data.append({"viewclass": "ElementCard", "portada": url_imagen, "titulo": titulo,
                                     "descripcion": descripcion,"url_html":url_html,"callback": lambda x: x})

        self.ids.rv_libros_pag.data = []
        for libro in libros:
            add_book(libro['titulo'],libro['info'], libro['url_img'], libro['url_html'])



class ElementCard(MDCard):
    portada = StringProperty()
    titulo = StringProperty()
    url_html = StringProperty()
    descripcion = StringProperty()


class Archivo(MDBoxLayout):
    popup = None
    def mostrar_ventana_advertencia(self,*args):
        direccion = args[1][0]
        if direccion.endswith('.pdf'):
            if not self.popup:
                self.popup = MDDialog(
                    text="¿Agregar este archivo a la librería?",
                    buttons=[MDFlatButton(text="CANCELAR", on_release = self.cerrar_popup),
                        MDRectangleFlatButton(text="ACEPTAR",
                                              on_release = ( lambda *x:self.convertir_audio(direccion)))])
            self.popup.open()

    def cerrar_popup(self,*args):
        self.popup.dismiss()

    def convertir_audio(self, direccion):
        guardar_audio_desde_dispositivo(direccion)
        self.cerrar_popup()
        app = Programa.get_running_app()
        app.actualizar_listas()


class Programa(MDApp):
    paginas = []
    id_audio_actual = 0

    def on_start(self):
        self.theme_cls.primary_palette = "Orange"
        self.theme_cls.accent_palette = "DeepOrange"
        iniciar_base()

    def abrir_pag_leer(self):
        self.root.ids.screen_manager.transition.direction = 'left'
        self.root.ids.screen_manager.current = 'buscar'
        self.agregar_lista('buscar')
        left_action_items = [['arrow-left', lambda x: self.volver_atras()]]
        self.root.ids.toolbar.left_action_items = left_action_items


    def abrir_ventana_borrar(self):
        # FUNCIÓN QUE TRAE UNA LISTA [TÍTULO, AUTOR] DE LOS LIBROS DESCARGADOS
        self.root.ids.lista_borrar.clear_widgets()
        libros = libros_descargados()
        for l in libros:
            self.root.ids.lista_borrar.add_widget(ThreeLineListItem(text=str(l[1]), secondary_text=str(l[2]),
                                                                    tertiary_text = str(l[0]),
                                                                    tertiary_theme_text_color='Custom',tertiary_text_color=(1, 1, 1, 1),))

    def set_selection_mode(self, instance_selection_list, mode):
        if mode:
            left_action_items = [["close", lambda x: instance_selection_list.unselected_all()]]
            right_action_items = [["trash-can", lambda x: self.borrar_libro(instance_selection_list)]]
            self.root.ids.toolbar.md_bg_color = self.theme_cls.accent_color
        else:
            left_action_items = [['menu', lambda x: self.root.ids.nav_drawer.set_state("open")]]
            right_action_items = [['book-open-page-variant-outline', lambda x: self.abrir_pag_leer()]]
            self.root.ids.toolbar.md_bg_color = self.theme_cls.primary_color

        Animation(d=0.2).start(self.root.ids.toolbar)
        self.root.ids.toolbar.left_action_items = left_action_items
        self.root.ids.toolbar.right_action_items = right_action_items

    def borrar_libro(self, seleccion):
        for item in seleccion.get_selected_list_items():
            seleccion.remove_widget(item)
            borrar_libro(item.instance_item.tertiary_text)
        left_action_items = [['menu', lambda x: self.root.ids.nav_drawer.set_state("open")]]
        right_action_items = [['book-open-page-variant-outline', lambda x: self.abrir_pag_leer()]]
        self.root.ids.toolbar.md_bg_color = self.theme_cls.primary_color
        Animation(d=0.2).start(self.root.ids.toolbar)
        self.root.ids.toolbar.left_action_items = left_action_items
        self.root.ids.toolbar.right_action_items = right_action_items
        self.actualizar_listas()


    def abrir_audio(self, titulo, autor, id_libro):
        datos_audio = []
        datos_audio = mostar_datos_audio(id_libro)
        self.id_audio_actual = datos_audio[0][0]
        self.agregar_lista('reproductor_audio')
        left_action_items = [['arrow-left', lambda x: self.volver_atras()]]
        right_action_items = [['']]
        self.root.ids.toolbar.left_action_items = left_action_items
        self.root.ids.toolbar.right_action_items = right_action_items
        self.root.ids.screen_manager.current = 'reproductor_audio'
        self.root.ids.titulo_autor.text = titulo + ' - ' + autor
        a = self.root.ids['audio']
        s = datos_audio[0][3]
        t = datos_audio[0][2]
        a.reproducir_libro(s,t)



    def descargar_audio(self, titulo,descripcion, portada,url_html):
        dicc_opcion = {'titulo': titulo,'info':descripcion,'url_img':portada,'url_html': url_html}
        buscar_link_descarga(dicc_opcion)
        self.custom_sheet.dismiss()



    def pre_visualizacion(self, portada, titulo, descripcion, url_html):
        bottom_sheet = Factory.ContentCustomSheet()
        bottom_sheet.portada = portada
        bottom_sheet.titulo = titulo
        bottom_sheet.descripcion = descripcion
        bottom_sheet.url_html = url_html
        self.custom_sheet = MDCustomBottomSheet(screen=bottom_sheet)
        self.custom_sheet.open()

    def agregar_lista(self, ventana):
        #AGREGA A UNA LISTA EL NOMBRE DE LAS VENTANAS QUE VA RECORRIENDO
        self.root.ids.screen_manager.transition.direction = 'left'
        self.paginas.append(ventana)


    def volver_atras(self):
        #VUELVE A LA VENTANA ANTERIOR
        ventana_anterior = self.paginas.pop()
        self.root.ids.screen_manager.transition.direction = 'right'

        if ventana_anterior == 'reproductor_audio':
            a = self.root.ids['audio']
            pos = a.obtener_posicion()
            tiempo_tot = a.obtener_tiempo_total()
            guardar_minutos_audio(self.id_audio_actual, pos/1000, tiempo_tot)
            a.parar_audio(None)

        if self.paginas == []:
            self.root.ids.screen_manager.current = 'inicio'
            left_action_items = [['menu', lambda x: self.root.ids.nav_drawer.set_state("open")]]
            right_action_items = [['book-open-page-variant-outline', lambda x: self.abrir_pag_leer()]]
            self.root.ids.toolbar.left_action_items = left_action_items
            self.root.ids.toolbar.right_action_items = right_action_items
            self.actualizar_listas()
        else:
            ultima_pagina = self.paginas[-1]
            self.root.ids.screen_manager.current = ultima_pagina

    def actualizar_listas(self):
        ld = self.root.ids['libros_descargados']
        ld.buscar_libros_descargados()
        lr = self.root.ids['libros_recientes']
        lr.buscar_libros_recientes()
        lb = self.root.ids['libros_buscados']
        lb.mostrar_libros()



Programa().run()







