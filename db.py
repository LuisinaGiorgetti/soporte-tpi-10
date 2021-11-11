import mysql.connector



def crear_base_datos():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
    )
    mycursor = mydb.cursor()
    mycursor.execute("CREATE DATABASE IF NOT EXISTS audioteca")
    mydb.close()

def crear_conexion():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database = 'audioteca'
    )

    mycursor = mydb.cursor()
    return mydb,mycursor

def crear_tabla_libro():
    conn,cur = crear_conexion()

    cur.execute("CREATE TABLE if not exists libros (id INT AUTO_INCREMENT PRIMARY KEY,"
                     "titulo VARCHAR(255), autor VARCHAR(255), url_imagen VARCHAR(255), fecha_descarga DATETIME,"
                     "tiempo_audio FLOAT, direccion_audio VARCHAR(255))")

    conn.close()


def agregar_libro(datos: tuple):
    conn, cur = crear_conexion()
    sql_sentencia = 'INSERT INTO libros (titulo,autor,url_imagen,fecha_descarga,tiempo_audio,direccion_audio)' \
                        'VALUES(%s,%s,%s,%s,%s,%s)'
    cur.executemany(sql_sentencia, (datos,))
    conn.commit()
    conn.close()

def buscar_libros_recientes(fecha):
    conn, cur = crear_conexion()
    sql_sentencia = 'SELECT * FROM libros WHERE fecha_descarga > %s'
    cur.execute(sql_sentencia, (fecha,))
    lista_resultado = cur.fetchall() #DEVUELVE UNA LISTA DE TUPLAS
    conn.close()
    return lista_resultado

def buscar_libros_descargados():
    conn, cur = crear_conexion()
    cur.execute('SELECT * FROM libros')
    lista_descargados = cur.fetchall()
    conn.close()
    return lista_descargados

def buscar_datos_audio(id_libro):
    conn, cur = crear_conexion()
    sql_sentencia = 'SELECT id, url_imagen,tiempo_audio,direccion_audio FROM libros WHERE id = %s'
    cur.execute(sql_sentencia, (id_libro,))
    lista_datos_audio = cur.fetchall()
    conn.close()
    return lista_datos_audio

def borrar_audio(id_audio):
    conn, cur = crear_conexion()
    sql_sentencia = 'DELETE FROM libros WHERE id = %s'
    cur.execute(sql_sentencia, (id_audio,))
    conn.commit()
    conn.close()

def guardar_datos_audio(idlibro, tiempo):
    conn, cur = crear_conexion()
    sql_sentencia = 'UPDATE libros SET tiempo_audio = %s WHERE id = %s'
    cur.execute(sql_sentencia, (tiempo, idlibro))
    conn.commit()
    conn.close()










