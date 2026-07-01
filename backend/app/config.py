import os

BASE_DIR  = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA_DIR  = os.path.join(BASE_DIR, 'backend', 'data')
GRAMMAR_DIR = os.path.join(BASE_DIR, 'grammar')

os.makedirs(DATA_DIR, exist_ok=True)