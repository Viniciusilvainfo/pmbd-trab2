### Trabalho 2

## 🧾 Projeto: **Sistema Web de Gestão de Pedidos para Restaurante**



### 🔧 Tecnologias Utilizadas:

* **Python Flask**: Backend da aplicação.
* **psycopg**: Integração com PostgreSQL.
* **PostgreSQL**: Banco de dados com lógica em stored procedures, funções e triggers.
* **Jinja2**: Templates HTML dinâmicos.

---

### 🎯 Objetivo:

Construir uma aplicação web para gestão de pedidos de um restaurante, onde o backend serve páginas HTML renderizadas com Jinja2, e toda a lógica de negócios, controle de fluxo e consistência de dados é feita diretamente no banco de dados com funções, stored procedures e triggers.

---

### 🧩 Componentes do Projeto:

#### 1. **Frontend com Jinja2 Templates**

Todas as páginas são renderizadas no servidor:

* `cardapio.html`
* `novo_pedido.html`
* `painel_admin.html`
* `detalhes_pedido.html`

```html
{% for pedido in pedidos %}
  <tr>
    <td>{{ pedido.id }}</td>
    <td>{{ pedido.cliente_nome }}</td>
    <td>{{ pedido.status }}</td>
  </tr>
{% endfor %}
```

---

### 🗃️ Estrutura do Banco de Dados

#### **Tabelas:**

* `usuarios`
* `itens_cardapio`
* `pedidos`
* `itens_pedido`
* `estoque`
* `logs`
* `status_pedido`

---

### ⚙️ Funções e Stored Procedures

#### ✅ `registrar_pedido(cliente_id, itens[])`

Cria um novo pedido com múltiplos itens. Valida estoque e grava o total.

#### ✅ `calcular_total_pedido(pedido_id)`

Retorna a soma do valor dos itens de um pedido.

#### ✅ `listar_pedidos(status TEXT)`

Retorna todos os pedidos com o status informado (ex: ‘em preparo’).

#### ✅ `trocar_status_pedido(pedido_id, novo_status)`

Altera o status de um pedido validando as transições permitidas.

---

### ⚡ Triggers e Funções de Apoio

### 🔹 1. **Trigger: `trg_log_alteracao`**

**Função:** `log_alteracao_pedido()`

* **Objetivo:** Registrar automaticamente qualquer atualização feita na tabela `pedidos`, como mudança de status, alteração no total ou horário de entrega.
* **Por que é útil:** Cria uma trilha de auditoria no sistema sem depender do backend.
* **Onde grava:** Tabela `logs(pedido_id, acao, data_hora)`

📌 *Exemplo de log gerado:*

> Pedido 103 atualizado para “em preparo” em 2025-05-26 14:03:17.

---

### 🔹 2. **Trigger: `trg_validar_estoque`**

**Função:** `validar_estoque()`

* **Objetivo:** Impedir a inserção de um item em um pedido se não houver estoque suficiente.
* **Quando é executada:** Antes de um novo `item_pedido` ser inserido.
* **Comportamento:** Se a quantidade solicitada for maior que o disponível no estoque, lança um erro e cancela a operação.

📌 *Mensagem de erro possível:*

> Estoque insuficiente para o item 45 (Pizza Calabresa).

---

### 🔹 3. **Trigger: `trg_descontar_estoque`**

**Função:** `descontar_estoque()`

* **Objetivo:** Subtrair automaticamente do estoque a quantidade de cada item após ser adicionado a um pedido.
* **Importância:** Garante que o estoque esteja sempre sincronizado com as vendas.
* **Execução:** Após a inserção de cada linha em `itens_pedido`.

🛠️ *Complementar à trigger de validação.* Primeiro valida, depois atualiza.

---

### 🔹 4. **Trigger: `trg_validar_status`**

**Função:** `validar_transicao_status()`

* **Objetivo:** Impedir alterações inválidas no status de pedidos.
* **Regras Exemplo:**

  * Um pedido "entregue" não pode voltar para "em preparo".
  * Um pedido "cancelado" não pode ser reativado.
* **Mensagem de erro:**

  > Não é possível alterar um pedido já entregue.

🔐 *Ajuda a evitar erros humanos ou falhas no frontend.*

---

### 🔹 5. **Trigger: `trg_log_cancelamento`**

**Função:** `log_cancelamento()`

* **Objetivo:** Gravar um log específico sempre que um pedido for cancelado.
* **Execução:** Após a mudança de status para `cancelado`.
* **Comportamento adicional:** Pode ser estendida para notificar a cozinha ou o cliente, via webhook.

📌 *Exemplo de log gerado:*

> Pedido 201 cancelado em 2025-05-26 15:04:20.

---

### 🧪 Fluxo do Sistema:

1. O cliente acessa o sistema via interface web.
2. Escolhe itens do cardápio e registra um novo pedido.
3. O backend chama a **stored procedure** que cria o pedido, valida estoque e atualiza tudo via triggers.
4. Toda alteração em pedidos gera logs e garante consistência via triggers (estoque, status, logs).
5. O administrador visualiza pedidos e atualiza status diretamente, com a lógica de transição controlada por **funções e triggers**.
