import psycopg2
from threading import Lock

class Database:
    
    _instance = None
    
    _lock = Lock()

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(Database, cls).__new__(cls)
                    cls._instance._init_connection()
        return cls._instance

    def _init_connection(self):
        self._conn = psycopg2.connect(
            dbname="resturante_abc123",
            user="postgres",
            password="postgres",
            host="localhost"
        )

    def getConn(self):
        return self._conn