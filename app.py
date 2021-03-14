from flask import Flask, request, render_template, flash, redirect, url_for
from flask_wtf import CSRFProtect
from werkzeug.utils import secure_filename
from os import path, rename, remove
from conexao import Conexao
from forms import Cadastro
from validate_docbr import CPF


app = Flask(__name__)
app.secret_key = 'projeto_rh' #chave secreta para proteger os formularios
csrf = CSRFProtect(app) #variavel que sera implementada nos forms para proteção
UPLOAD_FOLDER = 'C:\Workspace\ControleRH\static\imgs' #caminho onde as imagens serao armazenadas
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

nova_conexao = Conexao() #instancia de conexao com o banco


def salva_imagem(img, cpf): #função responsavel por salvar e renomear a imagem para o numero do cpf(pois é único)
    if img:
        filename = secure_filename(img.filename) #verifica o nome da imagem a ser salva
        img.save(path.join(app.config['UPLOAD_FOLDER'], filename)) #salva a imagem na pasta especificada
        nome_arquivo, extensao = path.splitext(filename) #separa o nome do arquivo e extensão
        rename('C:\Workspace\ControleRH\static\imgs/' + filename,
               'C:\Workspace\ControleRH\static\imgs/' +
               cpf + extensao) #procura a imagem salva na pasta e renoemia ela para o número do cpf
        caminho = 'C:\Workspace\ControleRH\static\imgs\{}'.format(cpf + extensao) #especifica o caminho da imagem
        return caminho #retorna o caminho em que a imagem foi salva para salvar no banco

    else:
        print('Extensão não suportada!')


def valida_tamanho_img(img):
    return path.getsize(img) #mede o tamanho da foto em bytes


@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastro():
    field = Cadastro() #variavel responsável por passar os forms para o template

    if request.method == 'POST' and field.validate(): #se a requiseção for post e os campos estiverem de acordo com a validação ele entra
        verifica_cpf = CPF()  # intancia da biblioteca de validação de cpf
        cpf = request.form['cpf']  # recebe o cpf de acordo com o campo cpf do template
        nome = request.form['nome']  # recebe o nome do formulário
        email = request.form['email']  # recebe o e-mail do formulário
        foto = request.files['foto']  # recebe a foto do template
        data_nascimento = request.form['data_nascimento']  # recebe a data de nascimento do formulário

        if verifica_cpf.validate(cpf) is True:  # validate retorna True se o cpf existir

            if len(nova_conexao.valida_cpf(
                    cpf)) == 0:  # busca no banco se existe algum registro com esse cpf, caso não ele entra

                if foto.filename == '':  # se não for adicionado foto o sistema cadastra
                    str_foto = ''
                    nova_conexao.cadastrar(nome, cpf, email, str_foto,
                                           data_nascimento)  # cadastra uma nova pessoa no banco
                    flash('Cadastro efetuado com sucesso!')  # retorna mensagem de cadastro efetuado
                    return redirect(url_for('listar_pessoas'))  # redireciona para a listaem de pessoas

                else:
                    str_foto = salva_imagem(foto, cpf)  # salva essa imagem e altera o nome para o número do cpf

                    if valida_tamanho_img(str_foto) <= 1000000:  # valida se o tamanho da foto é menor do que 1mb
                        nova_conexao.cadastrar(nome, cpf, email, str_foto,
                                               data_nascimento)  # cadastra uma nova pessoa no banco
                        flash('Cadastro efetuado com sucesso!')  # retorna mensagem de cadastro efetuado
                        return redirect(url_for('listar_pessoas'))  # redireciona para a listaem de pessoas

                    else:  # caso arquivo seja maior que 1 mb retona a mensagem
                        remove(str_foto)
                        flash('Adicione uma foto com tamanho máximo de 1MB!')

            else:  # caso o cpf conste no banco retorna a mensagem
                flash('CPF já cadastrado!')

        else:  # caso cpf não exista retorna a mensagem
            flash('CPF inválido!')

    return render_template('cadastro.html', field=field) #renderiza o template e envia os forms atraves da variavel field


@app.route('/', methods=['GET', 'POST'])
def listar_pessoas():
    pessoas = nova_conexao.listar() #busca todas as pessoas cadastradas no banco

    return render_template('listar.html', pessoas=pessoas) #renderiza o template listar e passa as informações do banco através da variável pessoas


@app.route('/deletar/<cpf>', methods=['GET', 'DELETE'])
def deletar(cpf):
    deleta_foto = nova_conexao.valida_cpf(cpf) #recebe as informações da pessoa do banco

    if nova_conexao.deletar(cpf) is True: #remove o cadastro da pessoa e valida se foi removido

        if deleta_foto[0][3] != '': #entra aqui se tiver um caminho de imagem salva
            remove(deleta_foto[0][3]) #remove a foto no caminho
            flash('Cadastro removido com sucesso!') #retorna mensagem de confirmação
            return redirect(url_for('listar_pessoas')) #redireciona para a listagem de pessoas

        else:
            flash('Cadastro removido com sucesso!') #se não tiver foto salva ele apenas retorna a mensagem
            return redirect(url_for('listar_pessoas')) #redireciona para a listagem de pessoas

    else:
        flash('Falha ao tentar remover o cadastro!') #se houver falha retorna a mensagem
        return redirect(url_for('listar_pessoas')) #redireciona para listagem de pessoas


@app.route('/alterar/<cpf>', methods=['GET', 'POST'])
def alterar(cpf):
    field = Cadastro() #variavel que passa o formulario e as validações para o template
    dados = nova_conexao.valida_cpf(cpf) #recebe as informações da pessoa pelo cpf
    id = dados[0][5] #separa o id para poder fazer a alteração no banco

    if dados[0][3] == '': #se a pessoa não tiver foto registrada retorna uma foto padrão
        foto_atual = '/static/imgs/nophoto.png'

    else: #se possuir retorna o caminho da imagem
        nome_arquivo, extensao = path.splitext(dados[0][3])
        foto_atual = '/static/imgs/' + nome_arquivo[36:50] + extensao

    if request.method == 'POST' and field.validate(): #valida os campos e se for metodo post entra aqui
        verifica_cpf = CPF() #função que valida cpf
        cpf = request.form['cpf'] #recebe cpf do template
        nome = request.form['nome'] #recebe nome do template
        email = request.form['email'] #recebe email do template
        foto = request.files['foto'] #recebe foto do template
        data_nascimento = request.form['data_nascimento'] #recebe data de nascimento do template

        if verifica_cpf.validate(cpf) is True: #valida se o cpf é um cpf valido

            if (cpf == dados[0][1]) or (len(nova_conexao.valida_cpf(cpf)) == 0): #valida se o cpf é o mesmo cadasrado ou se não existe no banco

                if (foto.filename == '') and (dados[0][3] != ''): #se o formulario n retornar foto e se tiver uma cadasttrada ele fica co ma atual
                    foto = dados[0][3] #recebe a foto que já esta cadastrada
                    nova_conexao.alterar(nome, cpf, email, foto, data_nascimento, id) #altera os dados no banco
                    flash('Alteração efetuada com sucesso!') #retorna mensagem pro usuário
                    return redirect(url_for('listar_pessoas')) #redireciona para a listagem de pessoas

                else: #se o usuário alterou a foto ele entra aqui

                    if foto.filename == '': #se não tinha foto cadastrada e não cadastrou entra aqui
                        foto = '' #foto continua sem valor no banco
                        nova_conexao.alterar(nome, cpf, email, foto, data_nascimento, id) #altera os dados no banco
                        flash('Alteração efetuada com sucesso!') #retorna mensagem de sucesso
                        return redirect(url_for('listar_pessoas')) #redireciona para a listagem de pessoas

                    else: #se o usuário alterou a imagem e já tinha uma cadastrada entra aqui
                        nome_arquivo, extensao = path.splitext(dados[0][3])
                        rename(dados[0][3], 'C:/Workspace/ControleRH/static/imgs/temp' + extensao)
                        str_foto = salva_imagem(foto, cpf) #salva a foto nova

                        if valida_tamanho_img(str_foto) <= 1000000: #verifica o tamanho da nova foto
                            nova_conexao.alterar(nome, cpf, email, str_foto, data_nascimento, id) #altera os dados no banco
                            remove('C:/Workspace/ControleRH/static/imgs/temp' + extensao)
                            flash('Alteração efetuada com sucesso!') #retorna mensagem de sucesso
                            return redirect(url_for('listar_pessoas'))  #redirecona para a listagem de pessoas

                        else: #se foto tiver mais de 1mb retorna mensagem para o usuário
                            remove(str_foto)
                            rename('C:/Workspace/ControleRH/static/imgs/temp' + extensao,
                                   'C:/Workspace/ControleRH/static/imgs/' + cpf + extensao)
                            flash('Adicione uma foto com tamanho máximo de 1MB!')

            else: #se o cpf já tiver cadastrado retorna mensagem para o usuário
                flash('CPF já cadastrado!')

        else: #se o cpf for inválido retorna mensagem
            flash('CPF inválido!')

    return render_template('alterar.html', field=field, dados=dados, foto_atual=foto_atual) #renderisa o template


if __name__ == '__main__':
    app.run(debug=True)