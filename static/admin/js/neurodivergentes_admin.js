document.addEventListener('DOMContentLoaded', function() {
    // Adiciona cabeçalhos às seções
    const sections = {
        'tab-dados-pessoais': 'Dados Pessoais',
        'tab-localizacao': 'Localização',
        'tab-endereco': 'Endereço',
        'tab-contato': 'Contato',
        'tab-nascimento': 'Nascimento e Primeira Infância',
        'tab-medico': 'Informações Médicas',
        'tab-historico': 'Histórico',
        'tab-relacionamentos': 'Relacionamentos',
        'tab-desenvolvimento': 'Desenvolvimento',
        'tab-percepcao': 'Percepção dos Responsáveis'
    };

    Object.entries(sections).forEach(([className, title]) => {
        const section = document.querySelector(`.${className}`);
        if (section) {
            const header = document.createElement('div');
            header.className = 'tab-header';
            header.textContent = title;
            section.insertBefore(header, section.firstChild);
        }
    });

    // Verifica se jQuery está disponível e carrega as máscaras com segurança
    function initializeMasks() {
        if (typeof jQuery !== 'undefined' && typeof jQuery.fn.mask !== 'undefined') {
            jQuery(function($) {
                // Máscara para celular
                if ($('#id_celular').length) {
                    $('#id_celular').mask('(00) 00000-0000', {
                        onKeyPress: function(phone, e, field, options) {
                            const masks = ['(00) 00000-0000'];
                            const mask = masks[0];
                            $('#id_celular').mask(mask, options);
                        }
                    });
                }
                
                // Máscara para CEP
                if ($('#id_cep').length) {
                    $('#id_cep').mask('00000-000');
                }

                // Máscaras adicionais
                $('[data-mask]').each(function() {
                    $(this).mask($(this).attr('data-mask'));
                });
            });
        }
    }
    
    // Tenta inicializar as máscaras imediatamente
    initializeMasks();
    
    // Tenta novamente após um pequeno atraso para garantir que jQuery.mask esteja carregado
    setTimeout(initializeMasks, 500);

    // CEP auto-complete com tratamento de erro
    const cepInput = document.querySelector('#id_cep');
    if (cepInput) {
        cepInput.addEventListener('blur', function() {
            const cep = this.value.replace(/\D/g, '');
            if (cep.length === 8) {
                fetch(`https://viacep.com.br/ws/${cep}/json/`)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Erro na consulta do CEP');
                        }
                        return response.json();
                    })
                    .then(data => {
                        if (data.erro) {
                            alert('CEP não encontrado. Por favor, verifique o número informado.');
                            return;
                        }
                        
                        // Preenche os campos com os dados do CEP
                        document.querySelector('#id_endereco').value = data.logradouro || '';
                        document.querySelector('#id_bairro').value = data.bairro || '';
                        document.querySelector('#id_cidade').value = data.localidade || '';
                        
                        // Seleciona o estado correto
                        const estadoSelect = document.querySelector('#id_estado');
                        const estadoUF = data.uf.toUpperCase();
                        
                        for (let option of estadoSelect.options) {
                            if (option.value === estadoUF) {
                                option.selected = true;
                                break;
                            }
                        }
                        
                        estadoSelect.dispatchEvent(new Event('change'));
                    })
                    .catch(error => {
                        console.error('Erro ao consultar CEP:', error);
                        alert('Erro ao consultar o CEP. Por favor, tente novamente mais tarde.');
                    });
            }
        });
    }

    // Formatação automática do celular
    const celularInput = document.querySelector('#id_celular');
    if (celularInput) {
        celularInput.addEventListener('input', function() {
            let value = this.value.replace(/\D/g, '');
            if (value.length === 11) {
                this.value = `(${value.substr(0,2)}) ${value.substr(2,5)}-${value.substr(7)}`;
            }
        });
    }

    // Controle de campos dependentes
    function toggleDependentField(triggerField, dependentField) {
        const trigger = document.querySelector(triggerField);
        const dependent = document.querySelector(dependentField);
        
        if (trigger && dependent) {
            const parentDiv = dependent.closest('.form-row');
            
            function updateVisibility() {
                if (trigger.checked || trigger.value === 'True') {
                    parentDiv.classList.remove('hidden');
                } else {
                    parentDiv.classList.add('hidden');
                }
            }
            
            trigger.addEventListener('change', updateVisibility);
            updateVisibility();
        }
    }

    // Configura os campos dependentes
    toggleDependentField('#id_prematuridade', '#id_tempo_prematuridade');
    toggleDependentField('#id_convenio_medico', '#id_nome_convenio');
    toggleDependentField('#id_restricoes_alimentares', '#id_descricao_restricoes');
    toggleDependentField('#id_nao_possui_convenio', '#id_motivo_nao_possui_convenio');


    // Formatação de JSON
    function formatJsonField(fieldId) {
        const field = document.querySelector(fieldId);
        if (field) {
            field.addEventListener('blur', function() {
                try {
                    const obj = JSON.parse(this.value);
                    this.value = JSON.stringify(obj, null, 2);
                } catch (e) {
                    // Mantém o valor original se não for JSON válido
                }
            });
        }
    }

    formatJsonField('#id_medicacoes_list');
    formatJsonField('#id_rotina_text');

    // Preview de imagem
    const fotoInput = document.querySelector('#id_foto_perfil');
    const previewImg = document.querySelector('.field-foto_preview img');
    
    if (fotoInput && previewImg) {
        fotoInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    previewImg.src = e.target.result;
                };
                reader.readAsDataURL(this.files[0]);
            }
        });
    }

    // Validação de campos numéricos
    const numericInputs = document.querySelectorAll('input[type="number"]');
    numericInputs.forEach(input => {
        const min = input.getAttribute('min');
        const max = input.getAttribute('max');
        
        input.addEventListener('input', function() {
            const value = parseInt(this.value);
            if (min && value < parseInt(min)) {
                this.value = min;
            }
            if (max && value > parseInt(max)) {
                this.value = max;
            }
        });
    });
});