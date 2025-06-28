from psycopg2.extensions import connection
from typing import List, Dict, Optional

class AdminDAO:
    def __init__(self, db: connection):
        self.db = db

    def get_all_pedidos(self, limit: int = 10, offset: int = 0) -> List[Dict]:
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT 
                p.id,
                u.nome AS cliente_nome,
                sp.descricao AS status,
                p.data_hora,
                p.total
            FROM pedido p
            JOIN usuario u ON p.usuario_id = u.id
            JOIN status_pedido sp ON p.status_id = sp.id
            ORDER BY p.data_hora DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))
        rows = cursor.fetchall()
        cursor.close()
        
        return [{
            'id': row[0],
            'cliente_nome': row[1],
            'status': row[2],
            'data_hora': row[3],
            'total': row[4]
        } for row in rows]

    def count_pedidos(self) -> int:
        cursor = self.db.cursor()
        cursor.execute("SELECT COUNT(*) FROM pedido")
        count = cursor.fetchone()[0]
        cursor.close()
        return count

    def get_estoque(self) -> List[Dict]:
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT 
                e.id,
                i.nome AS item_cardapio,
                e.ingrediente,
                e.quantidade
            FROM estoque e
            JOIN item_cardapio i ON e.item_cardapio_id = i.id
            ORDER BY i.nome, e.ingrediente
        """)
        rows = cursor.fetchall()
        cursor.close()
        
        return [{
            'id': row[0],
            'item_cardapio': row[1],
            'ingrediente': row[2],
            'quantidade': row[3]
        } for row in rows]

    def update_estoque(self, estoque_id: int, quantidade: int) -> bool:
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                UPDATE estoque 
                SET quantidade = %s 
                WHERE id = %s
            """, (quantidade, estoque_id))
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()

    def get_all_usuarios(self) -> List[Dict]:
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT 
                id,
                nome,
                email,
                admin
            FROM usuario
            ORDER BY nome
        """)
        rows = cursor.fetchall()
        cursor.close()
        
        return [{
            'id': row[0],
            'nome': row[1],
            'email': row[2],
            'admin': row[3]
        } for row in rows]

    def update_usuario_admin(self, usuario_id: int, admin: bool) -> bool:
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                UPDATE usuario 
                SET admin = %s 
                WHERE id = %s
            """, (admin, usuario_id))
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()