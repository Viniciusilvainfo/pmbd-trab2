# 🍽️ Sistema Web de Gestão de Pedidos para Restaurante

Dupla **Bruno Nascimento** e **Vinicius Tavares**.

### Descricao
    Trabalho para disciplina de PMBD2
    
* [Enunciado](https://github.com/Chipskein/pmbd-trab2/tree/main/Enunciado.md)
* [TODO](https://github.com/Chipskein/pmbd-trab2/tree/main/TODO.md)

---

## 🔧 Tecnologias Utilizadas

- **Python Flask** – Backend da aplicação.
- **psycopg** – Conector PostgreSQL para Python.
- **PostgreSQL** – Banco de dados com lógica de negócio via funções, stored procedures e triggers.
- **Jinja2** – Templates HTML renderizados no servidor.

---

## 🚀 Como Rodar o Projeto

### 1. Clone o Repositório

```bash
git clone https://github.com/Chipskein/pmbd-trab2.git
cd pmbd-trab2

python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

pip install -r requirements.txt

psql -U seu_usuario -f db/db.sql

flask run
```


Autores

    * [Bruno Nascimento](https://github.com/Chipskein)

    * [Vinicius Tavares](https://github.com/Viniciusilvainfo)

