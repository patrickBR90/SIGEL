from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import mysql.connector
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import bcrypt

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_muito_segura'

# Carregar variáveis de ambiente
load_dotenv()

# Configuração do MySQL
db_config = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DATABASE')
}

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Classe para representar o usuário
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

# Carregar usuário para Flask-Login
@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    conn.close()
    if user_data:
        return User(user_data['id'], user_data['username'])
    return None

def get_db_connection():
    return mysql.connector.connect(**db_config)

# Página de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE username = %s", (username,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data['password'].encode('utf-8')):
            user = User(user_data['id'], user_data['username'])
            login_user(user)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Usuário ou senha inválidos.', 'danger')
    
    return render_template('login.html')

# Página de logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu do sistema.', 'success')
    return redirect(url_for('login'))

# Página inicial
@app.route('/')
@login_required
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Contar total de livros
    cursor.execute("SELECT COUNT(*) AS total FROM livros")
    total_livros = cursor.fetchone()['total']
    
    # Contar total de alunos
    cursor.execute("SELECT COUNT(*) AS total FROM alunos")
    total_alunos = cursor.fetchone()['total']
    
    # Contar total de empréstimos ativos
    cursor.execute("SELECT COUNT(*) AS total FROM emprestimos")
    total_emprestimos = cursor.fetchone()['total']
    
    # Contar empréstimos prestes a vencer e atrasados
    hoje = datetime.now().date()
    prestes_a_vencer_limite = hoje + timedelta(days=3)
    
    cursor.execute("SELECT COUNT(*) AS total FROM emprestimos WHERE data_devolucao <= %s AND data_devolucao >= %s",
                   (prestes_a_vencer_limite, hoje))
    prestes_a_vencer = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) AS total FROM emprestimos WHERE data_devolucao < %s", (hoje,))
    atrasados = cursor.fetchone()['total']
    
    cursor.close()
    conn.close()
    
    return render_template('index.html', total_livros=total_livros, total_alunos=total_alunos,
                          total_emprestimos=total_emprestimos, prestes_a_vencer=prestes_a_vencer, atrasados=atrasados)

# Gerenciamento de Alunos
@app.route('/alunos', methods=['GET', 'POST'])
@login_required
def alunos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        numero = request.form['numero']
        nome = request.form['nome']
        serie = request.form.get('serie', '')
        data_cadastro = datetime.now().strftime('%Y-%m-%d')
        
        try:
            cursor.execute("INSERT INTO alunos (numero, nome, serie, data_cadastro) VALUES (%s, %s, %s, %s)", 
                          (numero, nome, serie, data_cadastro))
            conn.commit()
            flash('Aluno cadastrado com sucesso!', 'success')
        except mysql.connector.Error as err:
            flash(f'Erro: {err}', 'danger')
        
    cursor.execute("SELECT * FROM alunos")
    alunos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('alunos.html', alunos=alunos)

@app.route('/alunos/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_aluno(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        numero = request.form['numero']
        nome = request.form['nome']
        serie = request.form.get('serie', '')
        
        try:
            cursor.execute("UPDATE alunos SET numero = %s, nome = %s, serie = %s WHERE id = %s",
                          (numero, nome, serie, id))
            conn.commit()
            flash('Aluno atualizado com sucesso!', 'success')
            return redirect(url_for('alunos'))
        except mysql.connector.Error as err:
            flash(f'Erro: {err}', 'danger')
    
    cursor.execute("SELECT * FROM alunos WHERE id = %s", (id,))
    aluno = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not aluno:
        flash('Aluno não encontrado.', 'danger')
        return redirect(url_for('alunos'))
    
    return render_template('alunos.html', alunos=[], edit_aluno=aluno)

@app.route('/alunos/delete/<int:id>')
@login_required
def delete_aluno(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM alunos WHERE id = %s", (id,))
        conn.commit()
        flash('Aluno excluído com sucesso!', 'success')
    except mysql.connector.Error as err:
        flash(f'Erro: {err}', 'danger')
    cursor.close()
    conn.close()
    return redirect(url_for('alunos'))

# Gerenciamento de Livros
@app.route('/livros', methods=['GET', 'POST'])
@login_required
def livros():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        titulo = request.form['titulo']
        autor = request.form.get('autor', '')
        data_cadastro = datetime.now().strftime('%Y-%m-%d')
        status = 'Disponível'
        
        try:
            cursor.executeeuro("INSERT INTO livros (titulo, autor, data_cadastro, status) VALUES (%s, %s, %s, %s)", 
                          (titulo, autor, data_cadastro, status))
            conn.commit()
            flash('Livro cadastrado com sucesso!', 'success')
        except mysql.connector.Error as err:
            flash(f'Erro: {err}', 'danger')
        
    cursor.execute("SELECT * FROM livros")
    livros = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('livros.html', livros=livros)

@app.route('/livros/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_livro(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        titulo = request.form['titulo']
        autor = request.form.get('autor', '')
        
        try:
            cursor.execute("UPDATE livros SET titulo = %s, autor = %s WHERE id = %s",
                          (titulo, autor, id))
            conn.commit()
            flash('Livro atualizado com sucesso!', 'success')
            return redirect(url_for('livros'))
        except mysql.connector.Error as err:
            flash(f'Erro: {err}', 'danger')
    
    cursor.execute("SELECT * FROM livros WHERE id = %s", (id,))
    livro = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not livro:
        flash('Livro não encontrado.', 'danger')
        return redirect(url_for('livros'))
    
    return render_template('livros.html', livros=[], edit_livro=livro)

@app.route('/livros/delete/<int:id>')
@login_required
def delete_livro(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM livros WHERE id = %s", (id,))
        conn.commit()
        flash('Livro excluído com sucesso!', 'success')
    except mysql.connector.Error as err:
        flash(f'Erro: {err}', 'danger')
    cursor.close()
    conn.close()
    return redirect(url_for('livros'))

# Gerenciamento de Empréstimos
@app.route('/emprestimos', methods=['GET', 'POST'])
@login_required
def emprestimos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        aluno_id = request.form['aluno_id']
        livro_id = request.form['livro_id']
        data_devolucao = request.form['data_devolucao']
        data_emprestimo = datetime.now().strftime('%Y-%m-%d')
        
        # Verificar se o livro está disponível
        cursor.execute("SELECT status FROM livros WHERE id = %s", (livro_id,))
        livro = cursor.fetchone()
        
        if not livro:
            flash('Livro não encontrado.', 'danger')
        elif livro['status'] != 'Disponível':
            flash('Este livro já está emprestado. Aguarde a devolução para emprestá-lo novamente.', 'danger')
        else:
            try:
                cursor.execute(
                    "INSERT INTO emprestimos (aluno_id, livro_id, data_emprestimo, data_devolucao) VALUES (%s, %s, %s, %s)",
                    (aluno_id, livro_id, data_emprestimo, data_devolucao)
                )
                cursor.execute("UPDATE livros SET status = 'Emprestado' WHERE id = %s", (livro_id,))
                conn.commit()
                flash('Empréstimo registrado com sucesso!', 'success')
            except mysql.connector.Error as err:
                flash(f'Erro: {err}', 'danger')
        
    cursor.execute("SELECT e.id, a.nome, a.numero, a.serie, l.titulo, e.data_emprestimo, e.data_devolucao "
                   "FROM emprestimos e JOIN alunos a ON e.aluno_id = a.id JOIN livros l ON e.livro_id = l.id")
    emprestimos = cursor.fetchall()
    
    cursor.execute("SELECT * FROM alunos")
    alunos = cursor.fetchall()
    # Carregar apenas livros disponíveis para o formulário
    cursor.execute("SELECT * FROM livros WHERE status = 'Disponível'")
    livros = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('emprestimos.html', emprestimos=emprestimos, alunos=alunos, livros=livros)

@app.route('/emprestimos/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_emprestimo(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        aluno_id = request.form['aluno_id']
        livro_id = request.form['livro_id']
        data_devolucao = request.form['data_devolucao']
        
        # Verificar o status do livro
        cursor.execute("SELECT status FROM livros WHERE id = %s", (livro_id,))
        livro = cursor.fetchone()
        
        if not livro:
            flash('Livro não encontrado.', 'danger')
        elif livro['status'] != 'Disponível':
            # Verificar se o livro já está associado a este empréstimo
            cursor.execute("SELECT livro_id FROM emprestimos WHERE id = %s", (id,))
            current_livro = cursor.fetchone()
            if current_livro['livro_id'] != int(livro_id):
                flash('Este livro já está emprestado. Escolha outro livro ou edite o empréstimo existente.', 'danger')
                cursor.close()
                conn.close()
                return redirect(url_for('edit_emprestimo', id=id))
        
        try:
            # Atualizar o empréstimo
            cursor.execute("UPDATE emprestimos SET aluno_id = %s, livro_id = %s, data_devolucao = %s WHERE id = %s",
                          (aluno_id, livro_id, data_devolucao, id))
            # Atualizar o status do livro (se o livro foi alterado)
            cursor.execute("UPDATE livros SET status = 'Disponível' WHERE id = %s", (current_livro['livro_id'],))
            cursor.execute("UPDATE livros SET status = 'Emprestado' WHERE id = %s", (livro_id,))
            conn.commit()
            flash('Empréstimo atualizado com sucesso!', 'success')
            return redirect(url_for('emprestimos'))
        except mysql.connector.Error as err:
            flash(f'Erro: {err}', 'danger')
    
    cursor.execute("SELECT e.id, a.id as aluno_id, a.nome, a.numero, a.serie, l.id as livro_id, l.titulo, e.data_emprestimo, e.data_devolucao "
                   "FROM emprestimos e JOIN alunos a ON e.aluno_id = a.id JOIN livros l ON e.livro_id = l.id WHERE e.id = %s", (id,))
    emprestimo = cursor.fetchone()
    
    cursor.execute("SELECT * FROM alunos")
    alunos = cursor.fetchall()
    cursor.execute("SELECT * FROM livros WHERE status = 'Disponível' OR id = %s", (emprestimo['livro_id'],))
    livros = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    if not emprestimo:
        flash('Empréstimo não encontrado.', 'danger')
        return redirect(url_for('emprestimos'))
    
    return render_template('emprestimos.html', emprestimos=[], edit_emprestimo=emprestimo, alunos=alunos, livros=livros)

@app.route('/emprestimos/devolver/<int:id>')
@login_required
def devolver_emprestimo(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Obter o livro associado ao empréstimo
        cursor.execute("SELECT livro_id FROM emprestimos WHERE id = %s", (id,))
        livro = cursor.fetchone()
        if livro:
            livro_id = livro[0]
            # Atualizar o status do livro para Disponível
            cursor.execute("UPDATE livros SET status = 'Disponível' WHERE id = %s", (livro_id,))
        # Remover o empréstimo
        cursor.execute("DELETE FROM emprestimos WHERE id = %s", (id,))
        conn.commit()
        flash('Livro devolvido com sucesso!', 'success')
    except mysql.connector.Error as err:
        flash(f'Erro: {err}', 'danger')
    cursor.close()
    conn.close()
    return redirect(url_for('emprestimos_ativos'))

@app.route('/emprestimos/delete/<int:id>')
@login_required
def delete_emprestimo(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM emprestimos WHERE id = %s", (id,))
        conn.commit()
        flash('Empréstimo excluído com sucesso!', 'success')
    except mysql.connector.Error as err:
        flash(f'Erro: {err}', 'danger')
    cursor.close()
    conn.close()
    return redirect(url_for('emprestimos'))

# Empréstimos Ativos
@app.route('/emprestimos_ativos')
@login_required
def emprestimos_ativos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Carregar todos os empréstimos ativos
    cursor.execute("SELECT e.id, a.nome, a.numero, a.serie, l.titulo, e.data_emprestimo, e.data_devolucao "
                   "FROM emprestimos e JOIN alunos a ON e.aluno_id = a.id JOIN livros l ON e.livro_id = l.id")
    emprestimos = cursor.fetchall()
    
    # Calcular total, prestes a vencer e atrasados
    hoje = datetime.now().date()
    prestes_a_vencer_limite = hoje + timedelta(days=3)
    
    total_emprestimos = len(emprestimos)
    prestes_a_vencer = 0
    atrasados = 0
    
    # Adicionar flags para cada empréstimo
    for emprestimo in emprestimos:
        data_devolucao = emprestimo['data_devolucao']  # Já é um objeto datetime.date
        emprestimo['atrasado'] = data_devolucao < hoje
        emprestimo['prestes_a_vencer'] = hoje <= data_devolucao <= prestes_a_vencer_limite and not emprestimo['atrasado']
        
        if emprestimo['atrasado']:
            atrasados += 1
        elif emprestimo['prestes_a_vencer']:
            prestes_a_vencer += 1
    
    cursor.close()
    conn.close()
    return render_template('emprestimos_ativos.html', emprestimos=emprestimos, total_emprestimos=total_emprestimos,
                          prestes_a_vencer=prestes_a_vencer, atrasados=atrasados)
def setup():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Criar um usuário admin com senha hasheada
    username = 'admin'
    password = 'admin123'  # Senha inicial
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    try:
        cursor.execute("INSERT INTO usuarios (username, password) VALUES (%s, %s)", (username, hashed_password))
        conn.commit()
        flash('Usuário admin criado com sucesso! Use: admin / admin123', 'success')
    except mysql.connector.Error as err:
        flash(f'Erro: {err}', 'danger')
    
    cursor.close()
    conn.close()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
