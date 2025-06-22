DROP DATABASE IF EXISTS resturante_abc123;

CREATE DATABASE resturante_abc123;

\c resturante_abc123

CREATE TABLE usuario(
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    admin BOOLEAN NOT NULL DEFAULT FALSE
);

INSERT INTO usuario (nome, email, senha,admin) VALUES
    --senha admin
    ('Administrador', 'admin@gmail.com', 'scrypt:32768:8:1$czMHicXAtEJz2SwF$d424e80cabda0c7ac989ad2a8bc11a9d85cadd8035328e75592371b9b364abcb9c34a8c91ac9e6beea57b6826a28927ae9bd6583d4a29f43c918500ab1243e8a',true),
    --senha admin
    ('Usuário', 'usuario@gmail.com', 'scrypt:32768:8:1$czMHicXAtEJz2SwF$d424e80cabda0c7ac989ad2a8bc11a9d85cadd8035328e75592371b9b364abcb9c34a8c91ac9e6beea57b6826a28927ae9bd6583d4a29f43c918500ab1243e8a',false)
;


CREATE TABLE status_pedido(
    id SERIAL PRIMARY KEY,
    descricao VARCHAR(50) NOT NULL UNIQUE
);

INSERT INTO status_pedido (descricao) VALUES
    ('pendente'),
    ('em preparacao'),
    ('pronto'),
    ('entregue'),
    ('cancelado')
;

CREATE TABLE item_cardapio(
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    preco DECIMAL(10, 2) NOT NULL,
    disponivel BOOLEAN NOT NULL DEFAULT TRUE
);

INSERT INTO item_cardapio (nome, descricao, preco) VALUES
    ('Pizza Margherita', 'Pizza clássica com molho de tomate, mussarela e manjericão.', 29.90),
    ('Hambúrguer Clássico', 'Hambúrguer suculento com queijo, alface, tomate e maionese.', 19.90),
    ('Salada Caesar', 'Salada fresca com alface romana, croutons e molho Caesar.', 15.90),
    ('Espaguete à Carbonara', 'Espaguete com molho cremoso de ovos, queijo parmesão e pancetta.', 24.90),
    ('Tiramisu', 'Sobremesa italiana com camadas de café e mascarpone.', 12.90)
;

CREATE TABLE estoque(
    id SERIAL PRIMARY KEY,
    ingrediente VARCHAR(100) NOT NULL,
    item_cardapio_id INTEGER NOT NULL REFERENCES item_cardapio(id) ON DELETE CASCADE,
    quantidade INTEGER NOT NULL DEFAULT 0
);

INSERT INTO estoque (ingrediente, item_cardapio_id, quantidade) VALUES
    ('Mussarela', 1, 50),
    ('Molho de Tomate', 1, 30),
    ('Manjericão', 1, 20),
    ('Pão de Hambúrguer', 2, 40),
    ('Carne Moída', 2, 30),
    ('Alface', 2, 25),
    ('Tomate', 2, 25),
    ('Queijo Parmesão', 3, 15),
    ('Croutons', 3, 10),
    ('Espaguete', 4, 20),
    ('Ovos', 4, 30),
    ('Pancetta', 4, 15),
    ('Café', 5, 10),
    ('Mascarpone', 5, 10)
;

CREATE TABLE pedido(
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuario(id) ON DELETE SET NULL,
    status_id INTEGER NOT NULL REFERENCES status_pedido(id) ON DELETE SET NULL,
    data_hora TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total DECIMAL(10, 2) NOT NULL DEFAULT 0.00
);

CREATE TABLE pedido_item(
    id SERIAL PRIMARY KEY,
    pedido_id INTEGER NOT NULL REFERENCES pedido(id) ON DELETE CASCADE,
    item_cardapio_id INTEGER NOT NULL REFERENCES item_cardapio(id) ON DELETE CASCADE
);

CREATE TABLE log(
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuario(id) ON DELETE SET NULL,
    pedido_id INTEGER REFERENCES pedido(id) ON DELETE SET NULL,
    acao VARCHAR(255) NOT NULL,
    data_hora TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Funções e procedimentos

CREATE OR REPLACE FUNCTION registrar_pedido(cliente_id INTEGER, itens INTEGER[]) RETURNS INTEGER 
LANGUAGE plpgsql AS $$
DECLARE
    pedido_id INTEGER;
    item_id INTEGER;
BEGIN
    IF cliente_id IS NULL THEN
        RAISE EXCEPTION 'ID do cliente não pode ser nulo';
    END IF;

    INSERT INTO pedido (usuario_id, status_id) VALUES (cliente_id, 1) RETURNING id INTO pedido_id;

    IF itens IS NULL OR array_length(itens, 1) is NULL THEN
        RAISE EXCEPTION 'Lista de itens não pode ser nula ou vazia';
    END IF;

    FOREACH item_id IN ARRAY itens LOOP
        INSERT INTO pedido_item (pedido_id, item_cardapio_id) VALUES (pedido_id, item_id);
    END LOOP;

    UPDATE pedido SET total = calcular_total_pedido(pedido_id) WHERE id = pedido_id;

    RETURN pedido_id;
END;
$$;


CREATE OR REPLACE FUNCTION calcular_total_pedido(p_pedido_id INTEGER) RETURNS DECIMAL
LANGUAGE plpgsql AS $$
DECLARE
    total DECIMAL(10, 2);
BEGIN
    SELECT 
        SUM(ic.preco) INTO total
    FROM item_cardapio ic
    INNER JOIN pedido_item pi ON ic.id = pi.item_cardapio_id
    WHERE 
        pi.pedido_id = p_pedido_id and
        ic.disponivel = TRUE
    ;
    RETURN COALESCE(total, 0);
END;
$$;

CREATE OR REPLACE FUNCTION listar_pedidos(status TEXT)
RETURNS TABLE (
    id INTEGER,
    usuario_id INTEGER,
    status_descricao VARCHAR(50),
    data_hora TIMESTAMP,
    total DECIMAL(10, 2)
)
LANGUAGE plpgsql AS $$
BEGIN
    IF status IS NULL THEN
        RAISE EXCEPTION 'Status não pode ser nulo';
    END IF;

    RETURN QUERY
    SELECT 
        p.id,
        p.usuario_id,
        sp.descricao AS status_descricao,
        p.data_hora,
        calcular_total_pedido(p.id) AS total
    FROM pedido p
    INNER JOIN status_pedido sp ON p.status_id = sp.id
    WHERE 
        sp.descricao = status
    ORDER BY p.data_hora DESC
    ;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Nenhum pedido encontrado com o status: %', status;
    END IF;
END;
$$;

CREATE OR REPLACE PROCEDURE trocar_status_pedido(pedido_id INTEGER, novo_status_id INTEGER)
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE pedido SET status_id = novo_status_id WHERE id = pedido_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Pedido não encontrado com o ID: %', pedido_id;
    END IF;
END;
$$;


-- Triggers

CREATE OR REPLACE FUNCTION trg_log_alteracao_pedido() RETURNS TRIGGER 
LANGUAGE plpgsql AS $$
DECLARE
    alteracoes TEXT := '';
    old_status_desc TEXT;
    new_status_desc TEXT;
BEGIN
    SELECT descricao INTO old_status_desc FROM status_pedido WHERE id = OLD.status_id;
    
    SELECT descricao INTO new_status_desc FROM status_pedido WHERE id = NEW.status_id;

    IF NEW.status_id IS DISTINCT FROM OLD.status_id THEN
        alteracoes := alteracoes || 'Status alterado de "' || old_status_desc || '" para "' || new_status_desc || '". ';
    END IF;

    IF NEW.total IS DISTINCT FROM OLD.total THEN
        alteracoes := alteracoes || 'Total alterado de ' || OLD.total || ' para ' || NEW.total || '. ';
    END IF;

    IF NEW.data_hora IS DISTINCT FROM OLD.data_hora THEN
        alteracoes := alteracoes || 'Horário de entrega alterado de "' || OLD.data_hora || '" para "' || NEW.data_hora || '". ';
    END IF;

    IF alteracoes <> '' THEN
        INSERT INTO log (pedido_id, acao, data_hora)
        VALUES (NEW.id, alteracoes, CURRENT_TIMESTAMP);
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trigger_log_alteracao_pedido
AFTER UPDATE ON pedido
FOR EACH ROW
EXECUTE FUNCTION trg_log_alteracao_pedido();



CREATE OR REPLACE FUNCTION trg_validar_estoque() RETURNS TRIGGER 
LANGUAGE plpgsql AS $$
DECLARE
    ingrediente_reg RECORD;
    total_pedidos INTEGER;
BEGIN
    
    SELECT COUNT(*) INTO total_pedidos
    FROM pedido_item
    WHERE pedido_id = NEW.pedido_id
      AND item_cardapio_id = NEW.item_cardapio_id;

    FOR ingrediente_reg IN
        SELECT ingrediente, quantidade
        FROM estoque
        WHERE item_cardapio_id = NEW.item_cardapio_id
    LOOP
        IF ingrediente_reg.quantidade < (total_pedidos + 1) THEN
            RAISE EXCEPTION 'Estoque insuficiente para ingrediente "%": disponível %, necessário %',
                ingrediente_reg.ingrediente, ingrediente_reg.quantidade, total_pedidos + 1;
        END IF;
    END LOOP;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trigger_validar_estoque
BEFORE INSERT ON pedido_item
FOR EACH ROW
EXECUTE FUNCTION trg_validar_estoque();




CREATE OR REPLACE FUNCTION trg_descontar_estoque() RETURNS TRIGGER
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE estoque SET quantidade = quantidade - 1 WHERE item_cardapio_id = NEW.item_cardapio_id;
    RETURN NEW;
END;

$$;

CREATE TRIGGER trigger_descontar_estoque
AFTER INSERT ON pedido_item
FOR EACH ROW
EXECUTE FUNCTION trg_descontar_estoque();








CREATE OR REPLACE FUNCTION trg_validar_status() RETURNS TRIGGER
LANGUAGE plpgsql AS $$
DECLARE
    status_anterior TEXT;
BEGIN
    IF NEW.status_id IS NULL THEN
        RAISE EXCEPTION 'Status não pode ser nulo';
    END IF;

    SELECT descricao INTO status_anterior FROM status_pedido WHERE id = OLD.status_id;

    IF status_anterior = 'cancelado' THEN
        RAISE EXCEPTION 'Não é permitido alterar um pedido com status "cancelado"';
    ELSIF status_anterior = 'entregue' THEN
        RAISE EXCEPTION 'Não é permitido alterar um pedido com status "entregue"';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trigger_validar_status
BEFORE UPDATE ON pedido
FOR EACH ROW
EXECUTE FUNCTION trg_validar_status();







CREATE OR REPLACE FUNCTION trg_log_cancelamento() RETURNS TRIGGER
LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.status_id = (SELECT id FROM status_pedido WHERE descricao = 'cancelado') THEN
        INSERT INTO log (usuario_id,pedido_id, acao) 
        VALUES (NEW.usuario_id,NEW.id,'Pedido cancelado: ' || NEW.id || ' - ' || NEW.data_hora);
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trigger_log_cancelamento
AFTER UPDATE ON pedido
FOR EACH ROW
WHEN (OLD.status_id IS DISTINCT FROM NEW.status_id)
EXECUTE FUNCTION trg_log_cancelamento();

