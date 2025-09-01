from django.db import models
from django.core.validators import RegexValidator
from django.utils.html import mark_safe
from django.core.exceptions import ValidationError
from datetime import date

def validate_future_date(value):
    if value > date.today():
        raise ValidationError('A data não pode ser no futuro.')

class Neurodivergente(models.Model):
    GENDER_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
    ]
    
    ESTADOS_CHOICES = [
        ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'),
        ('AM', 'Amazonas'), ('BA', 'Bahia'), ('CE', 'Ceará'),
        ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'),
        ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MT', 'Mato Grosso'),
        ('MS', 'Mato Grosso do Sul'), ('MG', 'Minas Gerais'),
        ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'),
        ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'),
        ('RN', 'Rio Grande do Norte'), ('RS', 'Rio Grande do Sul'),
        ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'),
        ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins'),
    ]

    # Dados Pessoais
    primeiro_nome = models.CharField('Primeiro Nome', max_length=50)
    ultimo_nome = models.CharField('Último Nome', max_length=50)
    data_nascimento = models.DateField(
        'Data de Nascimento',
        validators=[validate_future_date]
    )
    genero = models.CharField('Gênero', max_length=1, choices=GENDER_CHOICES)
    cpf = models.CharField(
        'CPF',
        max_length=14,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
                message='CPF inválido. Use o formato XXX.XXX.XXX-XX'
            )
        ]
    )
    rg = models.CharField('RG', max_length=20, blank=True, null=True)

    # NOVOS CAMPOS OPCIONAIS
    NACIONALIDADE_CHOICES = [
        ('brasileira', 'Brasileira'),
        ('estrangeira', 'Estrangeira'),
    ]
    COR_PELE_CHOICES = [
        ('branca', 'Branca'),
        ('preta', 'Preta'),
        ('parda', 'Parda'),
        ('amarela', 'Amarela'),
        ('indigena', 'Indígena'),
    ]
    TIPO_SANGUINEO_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]
    nacionalidade = models.CharField('Nacionalidade', max_length=20, choices=NACIONALIDADE_CHOICES, blank=True, help_text="Selecione se é brasileira ou estrangeira")
    naturalidade = models.CharField('Naturalidade', max_length=100, blank=True, null=True, help_text="Cidade e estado de nascimento (ex: São Paulo - SP)")
    pais_origem = models.CharField('País de Origem', max_length=50, blank=True, help_text="Informe o país de origem caso seja estrangeiro")
    cor_pele = models.CharField('Cor da Pele', max_length=10, choices=COR_PELE_CHOICES, blank=True, help_text="Selecione a cor da pele conforme autodeclaração")
    tipo_sanguineo = models.CharField('Tipo Sanguíneo', max_length=3, choices=TIPO_SANGUINEO_CHOICES, blank=True, help_text="Selecione o tipo sanguíneo se conhecido")
    
    # Localização
    estado_nascimento = models.CharField(
        'Estado de Nascimento',
        max_length=2,
        choices=ESTADOS_CHOICES,
        blank=True
    )
    cidade_nascimento = models.CharField('Cidade de Nascimento', max_length=100, blank=True)
    
    # Endereço
    cep = models.CharField(
        'CEP',
        max_length=9,
        validators=[
            RegexValidator(
                regex=r'^\d{5}-\d{3}$',
                message='CEP inválido. Use o formato XXXXX-XXX'
            )
        ]
    )
    endereco = models.CharField('Endereço', max_length=255)
    numero = models.CharField('Número', max_length=10)
    complemento = models.CharField(
        'Complemento',
        max_length=100,
        blank=True,
        null=True
    )
    bairro = models.CharField('Bairro', max_length=100)
    cidade = models.CharField('Cidade', max_length=100)
    estado = models.CharField('Estado', max_length=2, choices=ESTADOS_CHOICES)
    
    # Contato
    celular = models.CharField(
        'Celular/WhatsApp',
        max_length=15,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\(\d{2}\) \d{5}-\d{4}$',
                message='Formato inválido. Use (XX) XXXXX-XXXX'
            )
        ]
    )
    email = models.EmailField('E-mail', blank=True, null=True)
    
    # Foto
    foto_perfil = models.ImageField(
        'Foto de Perfil',
        upload_to='neurodivergentes/fotos/',
        blank=True,
        null=True
    )
    
    # Escola e Ano Escolar
    escola = models.ForeignKey(
        'escola.Escola',
        verbose_name='Escola',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alunos'
    )
    
    SERIES_CHOICES = [
        ('', '---------'),
        ('EDUCAÇÃO INFANTIL', (
            ('bercario1', 'Berçário I'),
            ('bercario2', 'Berçário II'),
            ('maternal1', 'Maternal I'),
            ('maternal2', 'Maternal II'),
            ('jardim', 'Jardim'),
            ('pre1', 'Pré I'),
            ('pre2', 'Pré II'),
        )),
        ('ENSINO FUNDAMENTAL I', (
            ('1ano', '1º Ano'),
            ('2ano', '2º Ano'),
            ('3ano', '3º Ano'),
            ('4ano', '4º Ano'),
            ('5ano', '5º Ano'),
        )),
        ('ENSINO FUNDAMENTAL II', (
            ('6ano', '6º Ano'),
            ('7ano', '7º Ano'),
            ('8ano', '8º Ano'),
            ('9ano', '9º Ano'),
        )),
    ]
    
    ano_escolar = models.CharField(
        'Ano Escolar',
        max_length=50,
        choices=[item for group in SERIES_CHOICES[1:] for item in group[1]],
        blank=True,
        null=True
    )
    ativo = models.BooleanField('Ativo', default=True)
    motivo_inatividade = models.TextField(
        'Motivo da Inatividade',
        blank=True,
        null=True,
        help_text='Descreva o motivo da inatividade (ex: transferência de cidade, mudança de escola, etc.)'
    )
    
    # Campos de controle
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Aluno/Paciente'
        verbose_name_plural = 'Alunos/Pacientes'
        ordering = ['primeiro_nome', 'ultimo_nome']
        
    def __str__(self):
        return f"{self.primeiro_nome} {self.ultimo_nome}"

    @property
    def nome_completo(self):
        return f"{self.primeiro_nome} {self.ultimo_nome}"
    
    def foto_preview(self):
        if self.foto_perfil:
            return mark_safe(
                f'<img src="{self.foto_perfil.url}" width="150" alt="Foto de perfil" />'
            )
        return "Sem foto"
    foto_preview.short_description = 'Visualização da Foto'
    
    def idade(self):
        hoje = date.today()
        return hoje.year - self.data_nascimento.year - (
            (hoje.month, hoje.day) < 
            (self.data_nascimento.month, self.data_nascimento.day)
        )
    idade.short_description = 'Idade'

    def clean(self):
        super().clean()
        
        # Não formata o CEP aqui pois já é formatado no formulário
        # para evitar conflito de formatação dupla
        
        # Formata o celular apenas se não estiver formatado
        if self.celular and not self.celular.startswith('('):
            celular = ''.join(filter(str.isdigit, self.celular))
            if len(celular) == 11:
                self.celular = f'({celular[:2]}) {celular[2:7]}-{celular[7:]}'