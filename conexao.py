import psycopg2


class Conexao:

    #caminho do banco e acesso
    def __init__(self):
        try:
            self.conexao = psycopg2.connect(user='postgres', password='',
                                            host='127.0.0.1', port='5432',
                                            database='rh')
            self.conexao.autocommit = True
            self.cursor = self.conexao.cursor()

        except Exception as e:
            print('Falha ao conectar!')

    #função responsável por cadastrar pessoas
    def cadastrar(self, nome, cpf, email, foto, data_nascimento):
        try:
            self.cursor.execute("Insert into pessoas (nome, cpf, email, foto, data_nascimento) "
                                "values ('{}', '{}', '{}', '{}', '{}');"
                                .format(nome, cpf, email, foto, data_nascimento))

        except Exception as e:
            print('Falha ao cadastrar!')

    #valida se o cpf é único
    def valida_cpf(self, cpf):
        try:
            aux = self.cursor.execute("select * from pessoas where cpf = '{}'".format(cpf))
            aux = self.cursor.fetchall()
            return aux

        except Exception as e:
            print('Falha ao conectar!')

    #busca todos os registros no banco
    def listar(self):
        try:
            aux = self.cursor.execute("select * from pessoas")
            aux = self.cursor.fetchall()
            return aux

        except Exception as e:
            print('Falha ao conectar!')

    #deleta dados do banco
    def deletar(self, cpf):
        try:
            self.cursor.execute("Delete from pessoas where cpf = '{}'".format(cpf))
            return True

        except Exception as e:
            print('Falha ao conectar!')

    #altera os dados da pessoa
    def alterar(self, nome, cpf, email, foto, data_nascimento, id):
        try:
            self.cursor.execute("update pessoas set nome= '{}', cpf= '{}', email= '{}', foto= '{}',"
                                "data_nascimento= '{}' where id= '{}';"
                                .format(nome, cpf, email, foto, data_nascimento, id))
            return True

        except Exception as e:
            print('Erro ao alterar!')
            print(e)
