"""
Django settings for mpmg project.

Generated by 'django-admin startproject' using Django 3.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'b5=un2ho7+g%ej(kt_eey1$#x9^!!!52szjp1o4qol0j6ly^7='

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'mpmg.services',
    'aduna',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
}

ROOT_URLCONF = 'mpmg.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # 'DIRS': [],
        'DIRS': [os.path.join(BASE_DIR, 'mpmg/admin/templates_admin')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mpmg.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'

# run the command "python manage.py collectstatic" to copy all static files to this folder
STATIC_ROOT = '/home/rafael/UFMG/MPMG/M05/search_engine/assets/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]

# Configure Elasticsearch server
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'localhost:9200'
    },
}

SERVICES_URL = 'http://127.0.0.1:8000/services/'

NER_DIR = '../NER/M02/'


'''
Nome dos índices que serão buscados no ElasticSearch
Eles estão grupados em dois grupos: 
- regular: índices principais
- replica: réplica dos índices principais

A réplica existe para permitir a comparação de diferentes
algoritmos de busca em paralelo.

Os nomes dos índices estão organizados em um dicionário
onde a chave é o nome do índice no ElasticSearch e o 
valor é o nome da classe do Django que encapsula os dados
do índice em questão.
'''
SEARCHABLE_INDICES = {
    'regular': {'diarios': 'Diario', 
                'processos': 'Processo', 
                'licitacoes': 'Licitacao', 
                'diarios_segmentado': 'DiarioSegmentado'
                },
    'replica': {'diarios-replica': 'Diario', 
                'processos-replica': 'Processo', 
                'licitacoes-replica': 'Licitacao', 
                'diarios_segmentado-replica': 'DiarioSegmentado'
                },
}


'''
Nome dos campos no ElasticSearch que serão buscados.
Passe "^NUMERO" logo em seguida do nome para indicar
o peso que aquele campo tem na busca
'''
SEARCHABLE_FIELDS = ['conteudo^1', 'entidade_pessoa^1']


'''
Nome dos campos que devem ser retornados. Repare na diferença
com o parâmetro acima. Aqui listamos todos os campos que devem ser
retornados, alguns não fazem parte da busca, mas contém informações
que precisam ser recuperadas.
'''
RETRIEVABLE_FIELDS = ['fonte', 'titulo', 'conteudo', 'entidade_pessoa', 'entidade_organizacao', 'entidade_municipio', 'entidade_local', 'embedding']


'''
Nome do campo que o ElasticSearch irá parsear para fazer o hightlight
com os termos da busca
'''
HIGHLIGHT_FIELD = 'conteudo'


'''
Número de documentos que serão retornados ao realizar uma busca
'''
NUM_RESULTS_PER_PAGE = 10


'''
Faz o mapeamento entre os tipos de entidades retornados pelo módulo reconhecedor de
entidades para o nome do campos nos índices que armazenam estas entidades.
'''
ENTITY_TYPE_TO_INDEX_FIELD = {
    'PESSOA': 'entidade_pessoa',
    'ORGANIZACAO': 'entidade_organizacao',
    'LOCAL': 'entidade_local', 
    'TEMPO': 'entidade_tempo', 
    'LEGISLACAO': 'entidade_legislacao',
    'JURISPRUDENCIA': 'entidade_jurisprudencia',
    'CPF':'entidade_cpf', 
    'CNPJ':'entidade_cnpj',
    'CEP':'entidade_cep',
    'MUNICIPIO':'entidade_municipio',
    'NUM_LICIT_OU_MODALID':'entidade_processo_licitacao'
}


USE_ENTITIES_IN_SEARCH = False