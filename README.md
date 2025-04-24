SIGEL: Sistema Integrado de Gerenciamento de Empréstimos de Livros para Bibliotecas Escolares

Projeto Integrador em Computação Univesp


instalação do software:


instale: python , MySQL.


configure o MySQL com MySQL workbench e abra o arquivo “NEWsgi.sql”


Abra o CMD e:

mkdir SIGEL

cd SIGEL

python -m venv venv


no desktop: faça o download do repositório e coloque os arquivos na raiz do diretório( /SIGEL)


crie um arquivo de texto chamado .env

e coloque:
MYSQL_HOST=localhost

MYSQL_USER=YYYY

MYSQL_PASSWORD=XXXX

MYSQL_DATABASE=sig



Y= usuario do MySQL admin
X=Senha do MySQL admin


no CMD:
cd SIGEL

.venv\Scripts\activate


python app.py



e acesse a página em um navegador web: http://127.0.0.1:5000/setup

Utilize: admin/admin123 para o login inicial.



