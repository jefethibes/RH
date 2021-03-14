from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, validators
from wtforms.fields.html5 import EmailField, DateField


class Cadastro(FlaskForm): #cria e valida o formulario pessoas
    nome = StringField('Nome:', [validators.length(min=1, max=150, message='Nome inválido!')])
    cpf = StringField('CPF:', [validators.length(min=14, max=14, message='CPF inválido!')])
    email = EmailField('E-mail:', [validators.length(min=10, max=400, message='E-mail inválido!')])
    foto = FileField('Upload Foto:', validators=[FileAllowed(['png', 'jpg', 'jpeg', 'bmp'], 'Não é uma extensão válida!')])
    data_nascimento = DateField('Data nascimento:', [validators.data_required('Não é uma data válida!')])
