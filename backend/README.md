## Primeiros Passos

1. Clone do  repositório
2. Entre na pasta do projeto
3. Crie um virtualenv com Python3
  ```
  $ python3 -m venv venv
  ```
4. Ative o virtualenv
   
  ```
  $ . venv/bin/activate
  ```
5. Instale as dependências

  ```
  $ pip install -r requirements.txt
  ```
   
6. Copie o ENV_SAMPLE para um novo arquivo chamado .env que será usado para
armazenar a informações sensivéis da aplicação

7. Execute as migrations
  ```
  $ ./manage.py makemigrations
  $ ./manage.py migrate
  ```
8. Execute a aplicação

  ```
  $ ./manage.py runserver
  ```