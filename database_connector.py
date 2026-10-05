# prototip/database_connector.py

import pyodbc
from dotenv import load_dotenv
import os

class DatabaseConnector:
    """
    SQL Server veritabanı ile bağlantı kurmak ve yönetmek için kullanılan sınıf.
    """
    def __init__(self):
        # .env dosyasındaki değişkenleri yükle
        load_dotenv()
        
        self.server = os.getenv("DB_SERVER")
        self.database = os.getenv("DB_DATABASE")
        self.conn = None
        self.cursor = None

    def connect(self):
        """
        Veritabanına bir bağlantı kurar.
        """
        if self.conn is None or self.conn.closed:
            try:
                # Windows kimlik doğrulaması için bağlantı dizesi
                conn_str = (
                   f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                   f'SERVER={self.server};'
                   f'DATABASE={self.database};'
                   f'Trusted_Connection=yes;'
                )
                
                self.conn = pyodbc.connect(conn_str)
                self.cursor = self.conn.cursor()
                print("Veritabanı bağlantısı başarıyla kuruldu. ✅")
                return True
            except pyodbc.Error as ex:
                sqlstate = ex.args[0]
                print(f"Veritabanı bağlantı hatası: {sqlstate} ❌")
                print(ex)
                return False
        return True

    def close_connection(self):
        """
        Veritabanı bağlantısını kapatır.
        """
        if self.conn:
            self.conn.close()
            print("Veritabanı bağlantısı kapatıldı. 🚪")

    def get_connection(self):
        """
        Bağlantı nesnesini döndürür.
        """
        return self.conn

    def get_cursor(self):
        """
        Cursor nesnesini döndürür.
        """
        return self.cursor
    
