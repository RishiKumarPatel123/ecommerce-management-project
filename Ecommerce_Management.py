import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys

# -- CONFIGERATION -- 
# Hum Local host ki jagah 127.0.0.1 use karenge taaki IPv6 (::1) ka error na aaye
DB_HOST = '127.0.0.1'
DB_USER = 'postgres'
DB_PORT = '5432'
TARGET_DB = 'ecommerce_project'

def get_connection (db_name, user_password, print_error =  False):
    """Connection banane ki koshish karta hai"""
    try:
        conn = psycopg2.connect(
            host = DB_HOST,
            user = DB_USER,
            password = user_password,
            database = db_name,
            port = DB_PORT
        )
        return conn
    except Error as e:
        if print_error:
            print(f"Connection fail Hua: {e}")
        return None

def setup_database_and_table():
    """Database Setup karta hai aur password handle karta hai"""
    print("\n --- System Check & Setup ---")

    # 1. Pehle bina password (Empty String) ke try karein
    password = ''
    print(f"Connectig to PostgreSQL as user '{DB_USER}' (Trying empty Password)...") 
    conn = get_connection('postgres',password,print_error=False)

    # 2. Agar fail hua, to iska matlab password ZAROORI hai.
    if conn is None:
        print("\n SERVER NEEDS A PASSWORD")
        print("Aapka database ki setting password maang rahi hain.")
        print("Zyadatar default password 'postgres', 'admin','1234' ya 'root' hota hai.")
        while True:
            password = input("\n> Kripya password enter karein (ya 'exit' likhiye):").strip()
            if password.lower() == 'exit':
                sys.exit()

            print(f"Trying Password : '{password}'...")
            conn = get_connection('postgres',password,print_error=True)
            if conn:
                print("Password Accepted!")
                break
            else:
                print("Galat password, phir se try karein. ")

    # 3. Check/ Create database
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    # Check if database exists
    cursor.execute(f"SELECT 1 from pg_catalog.pg_database WHERE datname = '{TARGET_DB}'")
    exists = cursor.fetchone()

    if not exists:
        print(f"Creating database '{TARGET_DB}'...")
        cursor.execute(f"CREATE DATABASE {TARGET_DB}")
    
    else :
        print(f"Database '{TARGET_DB}' pehele se hai ")
        cursor.close()
        conn.close()
    
    # 4. Create Table
    conn = get_connection(TARGET_DB,password)
    cursor = conn.cursor()

    create_table_query = """
    CREATE TABLE IF NOT EXISTS ecommerce(
        product_id INTEGER PRIMARY KEY,
        product_name VARCHAR(50) Not Null,
        total_amount INTEGER not null, 
		payment_mode VARCHAR(20) not null,
        city VARCHAR(20) not null
        );
        """
    cursor.execute(create_table_query)
    conn.commit()
    print("Table 'ecommerce' ready hai.")
    cursor.close()
    conn.close()

    return password

# Global variable to storeworking password
current_password = ''
def create_main_connection():
    """Baaki functions ke liye connection """
    try:
        return psycopg2.connect(
            host = DB_HOST,
            user = DB_USER,
            password = current_password,
            database = TARGET_DB,
            port = DB_PORT


        )
    except Error as e:
        print(f"Connection Error: {e}")
        return None 

# --- Main Function ---
def add_product():
    conn = create_main_connection()
    if conn:
        cursor = conn.cursor()
        try:
            print("\n --- Add Another Order --- ")
            product_id = int(input("Enter Product ID: "))
            product_name = input("Enter Product Name: ")
            total_amount = int(input("Enter Total Amount: "))
            payment_mode = input("Enter Payment Mode: ")
            city = input("Enter Name of City: ")

            cursor.execute("INSERT INTO ecommerce (product_id,product_name,total_amount,payment_mode,city) VALUES (%s,%s,%s,%s,%s)",
                           (product_id,product_name,total_amount,payment_mode,city)
            )
            conn.commit()
            print("Order added Successfully! ")
        except Error as e:
            print(f"Error : {e}")
        
        finally:
            conn.close()

def view_product():
    conn = create_main_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM ecommerce ORDER BY product_id ASC")
            rows = cursor.fetchall()
            print(f"\n {'ProductID':<10}{'Product Name':<15}{'Total Amount':<10} {'Payment Mode':<20}{'City':<10}")
            print("-"*70)
            for row in rows:
                print(f"{row[0]:<10} {row[1]:<20} {row[2]:<10} {row[3]:<20}{row[4]:<10}")
        except Error as e:
            print(f"Error: {e}")
        finally:
            conn.close()

def search_product():
    conn = create_main_connection()
    if conn:
        cursor = conn.cursor()
        try:
            product_id = int(input("\n Enter ProductID: "))
            cursor.execute("SELECT * FROM ecommerce WHERE product_id = %s",(product_id,))
            result = cursor.fetchone()
            if result:
                print(f"\n Found: Product Name: {result[1]},Total Amount: {result[2]},Payment Mode: {result[3]},City:{result[4]}")
            else :
                print("Order not Found! ")
        except Error as e:
            print(f"Error : {e}")
        finally:
            conn.close()

def update_product():
    conn = create_main_connection()
    if conn:
        cursor = conn.cursor()
        try:
            product_id = input("\n Enter ProductID To update: ")
            cursor.execute("SELECT * FROM ecommerce WHERE  product_id = %s",(product_id,))
            if not cursor.fetchone():
                print("Order not Found! ")
                return
            print("Enter new details (Leave Blank to keep old):")
            new_product_name  = input("New Product Name: ")
            new_total_amount = input("New Total Amount: ")
            new_payment_mode = input("New Pament Mode: ")
            new_city = input("Enter New City Name: ")

            if new_product_name:
                cursor.execute("UPDATE ecommerce SET product_name = %s WHERE product_id = %s",(new_product_name,product_id))
            
            if new_total_amount:
                cursor.execute("UPDATE ecommerce SET total_amount = %s WHERE product_id = %s",(new_total_amount,product_id))
            
            if new_payment_mode:
                cursor.execute("UPDATE ecommerce SET payment_mode = %s WHERE product_id = %s",(new_payment_mode,product_id))
            
            if new_city:
                cursor.execute("UPDATE ecommerce SET city = %s WHERE product_id = %s",(new_city,product_id))
            conn.commit()
            print("Updated Successsfully! ")
        
        except Error as e:
            print(f"Error : {e}")
        finally:
            conn.close()

def delete_product():
    conn = create_main_connection()
    if conn:
        cursor = conn.cursor()
        try:
            product_id = input("\n Enter ProductID to delete; ")
            cursor.execute("DELETE FROM ecommerce where product_id = %s",(product_id,))
            conn.commit()
            if cursor.rowcount >0:
                print("Deleted Successfully! ")
            else:
                print("Student not Found! ")
        finally :
            conn.close()

def main():
    global current_password
    current_password = setup_database_and_table()

    while True:
        print("\n" + "="*35)
        print("ECOMMERCE MANAGEMENT SYSTEM")
        print("="*35)
        print("1. Add Another Record")
        print("2. View All Record")
        print("3. Search Any Record")
        print("4. Update Record")
        print("5. Delete Record") 
        print("6. Exit")

        choice = input("Enter Choice (1-6): ")

        if   choice == '1': add_product()
        elif choice == '2': view_product()
        elif choice == '3': search_product()
        elif choice == '4' : update_product()
        elif choice == '5': delete_product()
        elif choice == '6': break
        else:
            print("Invalid Choice ! ")               
if __name__ == "__main__":
    main()


    
