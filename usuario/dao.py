from psycopg2.extensions import connection

class UsuarioDAO:

    def __init__(self,db:connection):
        self.db = db

    
    def getOne(self, where: dict) -> dict | None:
        cursor = self.db.cursor()
        query = "SELECT id, nome, email,senha,admin FROM usuario "
        
        values = []
        if where:
            conditions = [f"{key} = %s" for key in where]
            query += " WHERE " + " AND ".join(conditions)
            values = list(where.values())

        query += ";"

        cursor.execute(query, tuple(values))
        row = cursor.fetchone()
        cursor.close()

        if row is None:
            return None
        
        usuario = {
            'id': row[0],
            'nome': row[1],
            'email': row[2],
            'senha': row[3],
            'admin': row[4]
        }
        
        return usuario

    def save(self, usuario: dict) -> dict:
        try:
            cursor = self.db.cursor()
            if 'id' in usuario and usuario['id'] is not None:
                cursor.execute("""
                    UPDATE usuario 
                    SET nome = %s, email = %s, senha = %s, admin = %s 
                    WHERE id = %s;
                """, (usuario['nome'], usuario['email'], usuario['senha'], usuario['admin'], usuario['id']))
            else:
                cursor.execute("""
                    INSERT INTO usuario (nome, email, senha, admin) 
                        VALUES (%s, %s, %s, %s)
                    RETURNING id;
                """, (usuario['nome'], usuario['email'], usuario['senha'], usuario['admin']))
                row = cursor.fetchone()
                usuario['id'] = row[0] if row else None
            
            self.db.commit()
            return usuario
        
        except Exception as e:
            self.db.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()