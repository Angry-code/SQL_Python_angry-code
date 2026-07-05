import psycopg2
from psycopg2.sql import SQL, Identifier

def create_db(conn):

    with conn.cursor() as cur:
        cur.execute("""
                    DROP TABLE IF EXISTS client_phone;
                    DROP TABLE IF EXISTS clients;
                    """)  
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS clients(
                    id SERIAL PRIMARY KEY,
                    first_name VARCHAR(40) NOT NULL,
                    last_name VARCHAR(40) NOT NULL,
                    email VARCHAR(100) UNIQUE
                    );
                    """)
        conn.commit()
        
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS client_phone(
                    id SERIAL PRIMARY KEY,
                    phone VARCHAR(20) UNIQUE NOT NULL,
                    client INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE
                    );
        """)
        conn.commit()

def add_client(conn, first_name, last_name, email, phones=None):
    with conn.cursor() as cur:
        cur.execute("""
                    SELECT email 
                    FROM clients
                    WHERE email = %s;
                    """, (email,))
        if len(cur.fetchall()) > 0:
            print('Email уже существует!')
            return
    with conn.cursor() as cur:
        cur.execute("""
                    INSERT INTO clients (first_name, last_name, email)
                    VALUES (%s, %s, %s)
                    RETURNING id;
                    """, (first_name, last_name, email))
        conn.commit()
        print (f'Присвоенный id:', cur.fetchone())   
 
def add_phone(conn, client, phone):
    with conn.cursor() as cur:
        cur.execute("""
                    SELECT phone 
                    FROM client_phone
                    WHERE phone = %s;
                    """, (phone,))
        if len(cur.fetchall()) > 0:
            print('Телефон уже существует!')
            return
    with conn.cursor() as cur:
        cur.execute("""
                    SELECT id 
                    FROM clients
                    WHERE id = %s;
                    """, (client,))
        if len(cur.fetchall()) == 0:
            print('Клиента нет в базе!')
            return    
    with conn.cursor() as cur:
        cur.execute("""
                    INSERT INTO client_phone (client, phone)
                    VALUES (%s, %s)
                    RETURNING id;
                    """, (client, phone))
        conn.commit()
        print (f'Id нового телефона:', cur.fetchone())

def change_client(conn, client_id, first_name=None, last_name=None, email=None, phones=None):
    with conn.cursor() as cur:
        cur.execute("""
                    SELECT id 
                    FROM clients
                    WHERE id = %s;
                    """, (client_id,))
        if len(cur.fetchall()) == 0:
            print('Клиента нет в базе!')
            return
    atributes_client = {'first_name' : first_name, 'last_name' : last_name, 'email' : email}
    for key, value in atributes_client.items():
        if value:
            with conn.cursor() as cur:
                cur.execute(SQL("UPDATE clients SET {} = %s WHERE id = %s").format(Identifier(key)), (value, client_id))
                conn.commit()    
    with conn.cursor() as cur:
        cur.execute("""
                    SELECT id, first_name, last_name, email
                    FROM clients
                    WHERE id = %s;
                    """, (client_id,))
        print(f'Измененные данные:', cur.fetchone())

def delete_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
                    SELECT phone 
                    FROM client_phone
                    WHERE phone=%s AND client=%s;
                    """, (phone, client_id,))
        if len(cur.fetchall()) == 0:
            print('Номера нет в базе!')
            return
    with conn.cursor() as cur:
        cur.execute("""
			DELETE FROM client_phone
			WHERE phone=%s AND client=%s;
			""", (client_id, phone))
        
        print (f'Телефон {phone} удален из базы',cur.fetchall())

def delete_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute("""
                    SELECT id 
                    FROM clients
                    WHERE id = %s;
                    """, (client_id,))
        if len(cur.fetchall()) == 0:
            print('Клиента нет в базе!')
            return
    with conn.cursor() as cur:
        cur.execute("""
			DELETE FROM clients
			WHERE id=%s;
			""", (client_id,))
        print (f'Клиент с id {client_id} удален из базы')

def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    with conn.cursor() as cur:
        cur.execute("""
                    SELECT first_name, last_name, email, phone
                    FROM clients cl
			        LEFT JOIN client_phone ph ON cl.id = ph.client
			        WHERE (%s IS NULL OR cl.first_name = %s)
              AND (%s IS NULL OR cl.last_name = %s)
              AND (%s IS NULL OR cl.email = %s)
              AND (%s IS NULL OR ph.phone = %s);
			""", (first_name, first_name,
                last_name, last_name,
                email, email,
                phone, phone,))
        print(f'Запрашиваемая запись:', cur.fetchall())

if __name__ == '__main__':
    with psycopg2.connect(database="05_psycopg_db", user="postgres", password="angry151786!") as conn:
        create_db(conn)
        add_client(conn,'Petr', 'Petrov', 'PetrovP@bk.ru')
        add_phone(conn, '1', '1233456657')
        #delete_phone (conn, '1', '1233456657')
        #delete_client(conn, '1')
        find_client(conn, None,'Petrov', None, None)

    conn.close()