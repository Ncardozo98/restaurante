import sqlite3
import logging
import sys
import os
import datetime
import click


# Logger config
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, _NOTHING, DEFAULT = range(10)
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"
COLOR_PATTERN = "%s%s%%s%s" % (COLOR_SEQ, COLOR_SEQ, RESET_SEQ)
LEVEL_COLOR_MAPPING = {
    logging.DEBUG: (BLUE, DEFAULT),
    logging.INFO: (GREEN, DEFAULT),
    logging.WARNING: (YELLOW, DEFAULT),
    logging.ERROR: (RED, DEFAULT),
    logging.CRITICAL: (WHITE, RED),
}
L_RED = '\033[91m'
L_GREEN = '\033[92m'
L_VIOLET = '\033[95m' 
L_BLUE = '\033[94m'
L_YELLOW = '\033[93m'
L_BOLD = '\033[1m'
L_UNDERLINE = '\033[4m'


class Formatter(logging.Formatter):
    def format(self, record):
        record.pid = os.getpid()
        return logging.Formatter.format(self, record)


class ColoredFormatter(Formatter):
    def format(self, record):
        fg_color, bg_color = LEVEL_COLOR_MAPPING.get(record.levelno, (GREEN, DEFAULT))
        record.levelname = COLOR_PATTERN % (30 + fg_color, 40 + bg_color, record.levelname)
        return Formatter.format(self, record)


format = '[ %(asctime)s - %(levelname)s - %(funcName)s() ]: %(message)s'
logging.addLevelName(25, "INFO")
handler = logging.StreamHandler(sys.stdout)
if os.name == 'posix':
    formatter = ColoredFormatter(format)
else:
    formatter = Formatter(format)
handler.setFormatter(formatter)
logging.getLogger().addHandler(handler)
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)



def connect(path):
	client = sqlite3.connect(path)
	return client


def create_db(client):
    try:
        cursor = client.cursor()
        cursor.execute('''
        CREATE TABLE categoria(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre VARCHAR(100) UNIQUE NOT NULL)''')

        cursor.execute("""
        CREATE TABLE plato(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre VARCHAR(100) UNIQUE NOT NULL,
        categoria_id INTEGER UNIQUE NOT NULL,
        FOREIGN KEY(categoria_id) REFERENCES categoria(id))""")
        cursor.execute('INSERT INTO categoria VALUES(1,"HOLA")')
    except sqlite3.OperationalError:
        _logger.warning('La tabla ya ha sido creada')
    else:
        _logger.info('Las tablas se han creado correctamente')
    client.commit()
    cursor.close()


def show_table(client, table):
    cursor = client.cursor()
    cursor.execute("SELECT * FROM %s;" % table)
    res = cursor.fetchall()
    _logger.info(res)


def agregar_categoria(client):
    nombre_de_categoria = input('Introduce el nombre de la categoria >> ')
    cursor = client.cursor()
    cursor.execute("INSERT INTO categoria VALUES(NULL,'{}')".\
        format(nombre_de_categoria))

    client.commit()
    cursor.close()


def agregar_plato(client):

    def take_first(elem):
        return elem[1]

    cursor = client.cursor()
    categs = cursor.execute("SELECT * FROM categoria").fetchall()
    categorias = sorted(categs, key=take_first, reverse=False)
    print("Selecciona el numero de categoría para añadir el plato:")
    categ_dict = {}
    for categoria in categorias:
        categ_dict[categoria[0]] = categoria[1]
        print("[{}] {}".format(categoria[0], categoria[1]))

    categ_input = None
    error = False
    while categ_input not in categ_dict:
        if error:
            _logger.error("La categoria seleccionada no existe")
        categ_input = int(input("> "))
        error = True

    plato = input("¿Nombre del nuevo plato?\n> ")

    try:
        cursor.execute("INSERT INTO plato VALUES (null, '{}', {})".format(plato, categ_input) )
    except sqlite3.IntegrityError:
        _logger.error("El plato '{}' ya existe.".format(plato))
    else:
        _logger.info("Plato '{}' creado correctamente.".format(plato))

    client.commit()
    cursor.close()


def mostrar_menu(client):
    cursor = client.cursor()

    categorias = cursor.execute("SELECT * FROM categoria").fetchall()   
    for categoria in categorias:
        print(categoria[1])
        platos = cursor.execute("SELECT * FROM plato WHERE categoria_id={}".format(categoria[0])).fetchall()
        for plato in platos:
            print("\t{}".format(plato[1]))

    cursor.close()


@click.command()
@click.option('-d', '--db_path',default='restaurante.db')
@click.option('-v', '--verbose', count=True)
def begin(db_path, verbose):
    if verbose == 0:
        lvl = logging.ERROR
    elif verbose == 1:
        lvl = logging.INFO
    else:
        lvl = logging.DEBUG
    _logger.setLevel(lvl)

    client = connect(db_path)
    print("\nBienvenido al gestor del restaurante!")
    create_db(client)
    while True:
        opcion = input("\nIntroduce una opción:\n[1] Agregar una categoría\n[2] Agregar un plato\n[3] Mostrar el menú\n[4] Salir del programa\n\n> ")
        if opcion == "1":
            agregar_categoria(client)
            show_table(client, 'categoria')
        elif opcion == "2":
            agregar_plato(client)
            show_table(client, 'plato')
        elif opcion == "3":
            mostrar_menu(client)
        elif opcion == "4":
            print("Adios!")
            break
        else:
            _logger.erro("Opción incorrecta")
        

if __name__ == '__main__':
    begin()