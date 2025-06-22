from psycopg2.extensions import connection

class PedidoDAO:

    def __init__(self,db:connection):
        self.db = db

    def countByUser(self, user_id: int) -> int:
        cursor = self.db.cursor()
        cursor.execute("""SELECT COUNT(*) FROM pedido WHERE usuario_id = %s;""", (user_id,))
        count = cursor.fetchone()[0]
        cursor.close()
        return count

    def getManyByUser(self, user_id: int,limit:int=10,offset:int=0) -> list[dict]:
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT
                p.id,
                u.nome AS cliente_nome,
                p.usuario_id,
                p.status_id,
                p.total,
                sp.descricao AS status
            FROM pedido p 
            INNER JOIN status_pedido sp ON p.status_id = sp.id
            INNER JOIN usuario u ON p.usuario_id = u.id
            WHERE 
                p.usuario_id = %s
            ORDER BY p.id DESC
            LIMIT %s OFFSET %s
            ;
        """, (user_id,limit, offset))
        rows = cursor.fetchall()
        cursor.close()
        pedidos = []
        for row in rows:
            pedido = {
                'id': row[0],
                'cliente_nome': row[1],
                'usuario_id': row[2],
                'status_id': row[3],
                'total': row[4],
                'status': row[5],
                'items': self.getItemsFromPedido(row[0])
            }
            pedidos.append(pedido)
        return pedidos

    def getOne(self, pedido_id: int) -> dict | None:
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT
                p.id,
                u.nome AS cliente_nome,
                p.usuario_id,
                p.status_id,
                p.total,
                sp.descricao AS status
            FROM pedido p 
            INNER JOIN status_pedido sp ON p.status_id = sp.id
            INNER JOIN usuario u ON p.usuario_id = u.id
            WHERE 
                p.id = %s
            ;
        """, (pedido_id,))
        row = cursor.fetchone()
        cursor.close()
        if row is None:
            return None
        pedido = {
            'id': row[0],
            'cliente_nome': row[1],
            'usuario_id': row[2],
            'status_id': row[3],
            'total': row[4],
            'status': row[5],
            'items': self.getItemsFromPedido(pedido_id)
        }
        return pedido
    
    def getItemsFromPedido(self, pedido_id: int)-> list[dict]:
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT
                ic.id,
                ic.nome,
                ic.descricao,
                ic.preco,
                ic.disponivel,
                string_agg(distinct e.ingrediente,',') as ingredientes
            FROM pedido_item pi
            INNER JOIN item_cardapio ic ON pi.item_cardapio_id = ic.id
            inner join estoque e on e.item_cardapio_id = ic.id
            WHERE 
                pi.pedido_id = %s
            group by ic.id
            ;
        """, (pedido_id,))
        rows = cursor.fetchall()
        cursor.close()
        items = []
        for row in rows:
            item = {
                'id': row[0],
                'nome': row[1],
                'descricao': row[2],
                'preco': row[3],
                'disponivel': row[4],
                'ingredientes': row[5]
            }
            items.append(item)
        return items
    
    def getIngrendientsFromPedido(self, pedido_id: int) -> list[dict]:
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT
                e.ingrediente
            FROM pedido_item pi
            INNER JOIN item_cardapio ic ON pi.item_cardapio_id = ic.id
            INNER JOIN estoque e ON ic.id = e.item_cardapio_id
            WHERE 
                pi.pedido_id = %s
            ;
        """, (pedido_id,))
        rows = cursor.fetchall()
        cursor.close()
        ingredientes = []
        for row in rows:
            ingrediente = {
                'id': row[0],
                'nome': row[1],
                'descricao': row[2]
            }
            ingredientes.append(ingrediente)
        return ingredientes

    def checkIfItemsExist(self, items: list[int]) -> bool:
        if not items:
            return False
        cursor = self.db.cursor()
        cursor.execute("""SELECT COUNT(*) FROM item_cardapio WHERE id = ANY(%s) and disponivel is true;""", (items,))
        count = cursor.fetchone()[0]
        cursor.close()
        return count == len(items)

    def getAllStatusPedido(self) -> list[dict]:
        cursor = self.db.cursor()
        cursor.execute("SELECT id, descricao FROM status_pedido;")
        rows = cursor.fetchall()
        cursor.close()
        status_list = []
        for row in rows:
            status = {
                'id': row[0],
                'descricao': row[1]
            }
            status_list.append(status)
        return status_list

    def updateStatus(self, pedido_id: int, status_id: int) -> bool:
        try:
            cursor = self.db.cursor()
            cursor.execute("CALL trocar_status_pedido(%s, %s);", (pedido_id, status_id))
            self.db.commit()
            cursor.close()
            return True
        except Exception as e:
            self.db.rollback()
            print("Erro ao atualizar status:", e)
            return False

    def save(self, usuario_id: int, items_id: list[int]) -> int:
        try:
            if not items_id:
                return 0
            query = "SELECT registrar_pedido(%s, %s);"
            cursor = self.db.cursor()
            cursor.execute(query, (usuario_id, items_id))
            pedido_id = cursor.fetchone()[0]
            self.db.commit()
            return pedido_id
        
        except Exception as e:
            self.db.rollback()
            raise e
        
        finally:
            if cursor:
                cursor.close()

        
            

        
        