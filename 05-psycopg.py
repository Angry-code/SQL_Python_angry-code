import psycopg2

def create_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
                    DROP TABLE client_phone;
                    DROP TABLE clients;
                    """)
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS clients(
                    client_id SERIAL PRIMARY KEY,
                    first_name VARCHAR(40) UNIQUE,
                    last_name VARCHAR(40) UNIQUE,
                    email VARCHAR(100)
                    );
                    """)
        conn.commit()
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS client_phone(
                    phone VARCHAR(20) NOT NULL,
                    client_id INTEGER NOT NULL REFERENCES clients(client_id)
                    );
        """)
        conn.commit()

def add_client(conn, first_name, last_name, email, phones=None):
    with conn.cursor() as cur:
        cur.execute("""
                    INSERT INTO clients (first_name, last_name, email)
                    VALUES (%s, %s, %s)
                    RETURNING client_id, first_name, last_name, email;
                    """, (first_name, last_name, email))
        print (cur.fetchone())   

def add_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
                    INSERT INTO client_phone (client_id, phone)
                    VALUES (%s, %s)
                    RETURNING client_id, phone;
                    """, (client_id, phone))
        print (cur.fetchone())

def change_client(conn, client_id, first_name=None, last_name=None, email=None, phones=None):
    with conn.cursor() as cur:
        cur.execute("""
			UPDATE clients
			SET first_name=%s, last_name=%s, email=%s;
			WHERE client_id=%s
			RETURNING client_id, first_name, last_name, email;
			""", (first_name, last_name, email,))

def delete_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
			DELETE FROM client_phone
			WHERE client_id=%s;
			""", (client_id,))
        print (cur.fetchall())

def delete_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute("""
			DELETE FROM clients
			WHERE client_id=%s;
			""", (client_id,))
        print (cur.fetchall())

def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    with conn.cursor() as cur:
        cur.execute("""
			SELECT c.first_name, c.last_name, c.email, p.number FROM clients c
			LEFT JOIN client_phone p ON c.client_id = p.client_id
			WHERE c.first_name=%s OR c.last_name=%s OR c.email=%s OR p.phone=%s;
			""", (first_name, last_name, email, phone,))
        return cur.fetchone()[0]


with psycopg2.connect(database="05_psycopg_db", user="postgres", password="angry151786!") as conn:
    
    print (add_client(conn,'Tom', 'Adoms', 'adom@mail.ru'))
    print (add_phone(conn, '1', '89109467816'))
    print (delete_phone (conn, '1', '89109467816'))
    print (delete_client(conn, '1'))
    
    conn.commit()
    

    conn.close()