import sqlite3

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
        print('La tabla ya ha sido creada')
    else:
        print('Las tablas se han creado correctamente')
    client.commit()
    cursor.close()

def show_table(client, table):
    cursor = client.cursor()
    cursor.execute("SELECT * FROM %s;" % table)
    res = cursor.fetchall()

def agregar_categoria(client):
    nombre_de_categoria = input('Introduce el nombre de la categoria >> ')
    cursor = client.cursor()
    import ipdb; ipdb.set_trace()
    cursor.execute("INSERT INTO categoria VALUES(NULL,'{}')".format(nombre_de_categoria))
    client.commit()
    cursor.close()

if __name__ == '__main__':
    client = connect('restaurante.db')
    create_db(client)
    agregar_categoria(client)
    show_table(client, 'categoria')