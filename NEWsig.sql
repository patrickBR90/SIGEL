-- Criação do banco de dados
CREATE DATABASE IF NOT EXISTS sig;
USE sig;

-- Criação da tabela usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- Criação da tabela alunos
CREATE TABLE IF NOT EXISTS alunos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero VARCHAR(20) NOT NULL UNIQUE,
    nome VARCHAR(100) NOT NULL
);

-- Criação da tabela livros
CREATE TABLE IF NOT EXISTS livros (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL
);

-- Criação da tabela emprestimos
CREATE TABLE IF NOT EXISTS emprestimos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    aluno_id INT NOT NULL,
    livro_id INT NOT NULL,
    data_emprestimo DATE NOT NULL,
    data_devolucao DATE NOT NULL,
    FOREIGN KEY (aluno_id) REFERENCES alunos(id) ON DELETE CASCADE,
    FOREIGN KEY (livro_id) REFERENCES livros(id) ON DELETE CASCADE
);

-- Alterações na tabela alunos (adicionando serie e data_cadastro)
ALTER TABLE alunos
ADD COLUMN serie VARCHAR(50),
ADD COLUMN data_cadastro DATE DEFAULT '2025-04-27';

-- Alterações na tabela livros (adicionando autor, data_cadastro e status)
ALTER TABLE livros
ADD COLUMN autor VARCHAR(100),
ADD COLUMN data_cadastro DATE DEFAULT '2025-04-27',
ADD COLUMN status VARCHAR(20) DEFAULT 'Disponível';

-- Inserção de um usuário admin (senha: admin123, hasheada com bcrypt)
-- Nota: O valor da senha hasheada pode variar dependendo da implementação do bcrypt.
-- Substitua o valor abaixo pelo hash gerado pelo seu ambiente.
INSERT INTO usuarios (username, password) VALUES (
    'admin',
    '$2b$12$Kixz7vJ9z7l5Xz7p8vJ9z7u5Xz7p8vJ9z7l5Xz7p8vJ9z7l5Xz7p' -- Substitua pelo hash real da senha 'admin123'
);

-- Exemplo de dados iniciais (opcional, para testes)
INSERT INTO alunos (numero, nome, serie, data_cadastro) VALUES
('001', 'Vinicius Silva', '6º Ano', '2025-04-27');

INSERT INTO livros (titulo, autor, data_cadastro, status) VALUES
('A Arte da Guerra', 'Sun Tzu', '2025-04-27', 'Disponível');

-- Exemplo de empréstimo (opcional, para testes)
INSERT INTO emprestimos (aluno_id, livro_id, data_emprestimo, data_devolucao) VALUES
(1, 1, '2025-04-27', '2025-05-11');

-- Atualizar o status do livro após o empréstimo
UPDATE livros SET status = 'Emprestado' WHERE id = 1;
