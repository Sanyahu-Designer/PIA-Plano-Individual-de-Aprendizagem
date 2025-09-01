#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pia_config.settings')
django.setup()

from neurodivergentes.models import Neurodivergente, GrupoFamiliar
from django.db import transaction
import logging

# Configurar logging detalhado
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_save_neurodivergente():
    """Testa salvamento básico sem Grupo Familiar"""
    print("=== TESTE 1: Salvamento básico ===")
    try:
        with transaction.atomic():
            neuro = Neurodivergente(
                primeiro_nome="Teste",
                ultimo_nome="Debug",
                data_nascimento="2010-01-01",
                genero="M",
                cpf="123.456.789-00"
            )
            print("Antes do save()...")
            neuro.save()
            print(f"✅ Salvamento básico OK - ID: {neuro.id}")
            return neuro
    except Exception as e:
        print(f"❌ Erro no salvamento básico: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_save_with_grupo_familiar(neurodivergente):
    """Testa salvamento com Grupo Familiar"""
    print("\n=== TESTE 2: Salvamento com Grupo Familiar ===")
    try:
        with transaction.atomic():
            grupo = GrupoFamiliar(
                neurodivergente=neurodivergente,
                primeiro_nome="Maria",
                ultimo_nome="Teste",
                vinculo="pai_mae"
            )
            print("Antes do save() do Grupo Familiar...")
            grupo.save()
            print(f"✅ Grupo Familiar salvo OK - ID: {grupo.id}")
            return grupo
    except Exception as e:
        print(f"❌ Erro no Grupo Familiar: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_admin_save():
    """Simula salvamento via admin"""
    print("\n=== TESTE 3: Simulação Admin Save ===")
    try:
        from neurodivergentes.admin import NeurodivergenciaAdmin
        from django.contrib.admin.sites import site
        
        # Criar dados de teste
        data = {
            'primeiro_nome': 'Admin',
            'ultimo_nome': 'Teste',
            'data_nascimento': '2010-01-01',
            'genero': 'F',
            'cpf': '987.654.321-00',
            'grupo_familiar-TOTAL_FORMS': '1',
            'grupo_familiar-INITIAL_FORMS': '0',
            'grupo_familiar-MIN_NUM_FORMS': '0',
            'grupo_familiar-MAX_NUM_FORMS': '1000',
            'grupo_familiar-0-primeiro_nome': 'João',
            'grupo_familiar-0-ultimo_nome': 'Silva',
            'grupo_familiar-0-vinculo': 'pai_mae',
        }
        
        print("Dados preparados para admin...")
        print("⚠️  Teste admin requer request object - pulando")
        
    except Exception as e:
        print(f"❌ Erro no teste admin: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔍 INICIANDO DEBUG DO SALVAMENTO")
    print("=" * 50)
    
    # Teste 1: Salvamento básico
    neuro = test_save_neurodivergente()
    
    # Teste 2: Com Grupo Familiar
    if neuro:
        grupo = test_save_with_grupo_familiar(neuro)
    
    # Teste 3: Admin
    test_admin_save()
    
    print("\n" + "=" * 50)
    print("🏁 DEBUG CONCLUÍDO")
