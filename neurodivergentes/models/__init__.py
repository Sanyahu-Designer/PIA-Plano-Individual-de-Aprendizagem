from .base import Neurodivergente
from .grupo_familiar import GrupoFamiliar
# Histórico escolar removido - não é mais necessário, SeriesCursadas
from .neurodivergencias import (
    Neurodivergencia, CondicaoNeurodivergente,
    CategoriaNeurodivergente, DiagnosticoNeurodivergente
)
from .anamnese import Anamnese, Medicacao, RotinaAtividade
from .pdi import PDI, PlanoEducacional, AdaptacaoCurricular
from .evolucao import RegistroEvolucao
from .pei import Monitoramento, MonitoramentoMeta
from .parecer import ParecerAvaliativo
from .meta_habilidade import MetaHabilidade, PDIMetaHabilidade
from escola.models import ModalidadeEnsino, ProgramaEducacional, Recurso, Escola

__all__ = [
    'Neurodivergente',
    'GrupoFamiliar',
    'Neurodivergencia',
    'CondicaoNeurodivergente',
    'CategoriaNeurodivergente',
    'DiagnosticoNeurodivergente',
    'Anamnese',
    'Medicacao',
    'RotinaAtividade',
    'PDI',
    'PlanoEducacional',
    'AdaptacaoCurricular',
    'RegistroEvolucao',
    'Monitoramento',
    'MonitoramentoMeta',
    'ParecerAvaliativo',
    'MetaHabilidade',
    'PDIMetaHabilidade',
    'ModalidadeEnsino',
    'ProgramaEducacional', 
    'Recurso',
    'Escola'
]