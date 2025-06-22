from psycopg2.extensions import connection

class CardapioDAO:

    def __init__(self,db:connection):
        self.db = db

    def get_all(self,limit:int = 10, offset:int = 0):
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT 
                ic.id,
                ic.nome, 
                ic.descricao, 
                ic.preco,
                ARRAY_AGG(e.ingrediente) AS ingredientes
            FROM item_cardapio ic
            INNER JOIN estoque e ON ic.id = e.item_cardapio_id
            WHERE 
                ic.disponivel = TRUE
            GROUP BY ic.id
            LIMIT %s OFFSET %s
        """, (limit, offset))
        rows = cursor.fetchall()
        cursor.close()
        
        cardapio = []
        for row in rows:
            item = {
                "id": row[0],
                "nome": row[1],
                "descricao": row[2],
                "preco": row[3],
                "ingredientes": row[4],
            }
            cardapio.append(item)

        return cardapio
    
    def count_all(self)->int:
        cursor = self.db.cursor()
        cursor.execute("SELECT COUNT(*) FROM item_cardapio WHERE disponivel = TRUE")
        row = cursor.fetchone()
        return row[0] if row else 0
    
        

    