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
    return render_template('index.html')

# Gerenciamento de Alunos
@app.route('/alunos', methods=['GET', 'POST'])
@login_required
def alunos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        numero = request.form['numero']
        nome = request.form['nome']
        
        try:
            cursor.execute("INSERT INTO alunos (numero, nome) VALUES (%s, %s)", (numero, nome))
            conn.commit()
            flash('Aluno cadastrado com sucesso!', 'success')
        except mysql.connector.Error as err:
            flash(f'Erro: {err}', 'danger')
        
    cursor.execute("SELECT * FROM alunos")
    alunos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('alunos.html', alunos=alunos)

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
        
        try:
            cursor.execute("INSERT INTO livros (titulo) VALUES (%s)", (titulo,))
            conn.commit()
            flash('Livro cadastrado com sucesso!', 'success')
        except mysql.connector.Error as err:
            flash(f'Erro: {err}', 'danger')
        
    cursor.execute("SELECT * FROM livros")
    livros = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('livros.html', livros=livros)

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
        
        try:
            cursor.execute(
                "INSERT INTO emprestimos (aluno_id, livro_id, data_emprestimo, data_devolucao) VALUES (%s, %s, %s, %s)",
                (aluno_id, livro_id, data_emprestimo, data_devolucao)
            )
            conn.commit()
            flash('Empréstimo registrado com sucesso!', 'success')
        except mysql.connector.Error as err:
            flash(f'Erro: {err}', 'danger')
        
    cursor.execute("SELECT e.id, a.nome, a.numero, l.titulo, e.data_emprestimo, e.data_devolucao "
                   "FROM emprestimos e JOIN alunos a ON e.aluno_id = a.id JOIN livros l ON e.livro_id = l.id")
    emprestimos = cursor.fetchall()
    
    cursor.execute("SELECT * FROM alunos")
    alunos = cursor.fetchall()
    cursor.execute("SELECT * FROM livros")
    livros = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('emprestimos.html', emprestimos=emprestimos, alunos=alunos, livros=livros)

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

# Rota para criar um usuário inicial (opcional, para testes)
@app.route('/setup')
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