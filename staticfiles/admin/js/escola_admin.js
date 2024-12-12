document.addEventListener('DOMContentLoaded', function() {
    // Add headers to sections
    const sections = {
        'tab-basic': 'Informações Básicas',
        'tab-contact': 'Contato',
        'tab-address': 'Endereço',
        'tab-operation': 'Funcionamento',
        'tab-resources': 'Recursos e Programas'
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

    // Initialize masks for formatted fields
    if (typeof jQuery !== 'undefined') {
        jQuery(function($) {
            $('[data-mask]').each(function() {
                $(this).mask($(this).attr('data-mask'));
            });
        });
    }

    // CEP auto-complete
    const cepInput = document.querySelector('#id_cep');
    if (cepInput) {
        cepInput.addEventListener('blur', function() {
            const cep = this.value.replace(/\D/g, '');
            if (cep.length === 8) {
                fetch(`https://viacep.com.br/ws/${cep}/json/`)
                    .then(response => response.json())
                    .then(data => {
                        if (!data.erro) {
                            document.querySelector('#id_endereco').value = data.logradouro;
                            document.querySelector('#id_bairro').value = data.bairro;
                            document.querySelector('#id_cidade').value = data.localidade;
                            
                            // Corrigindo a seleção do estado
                            const estadoSelect = document.querySelector('#id_estado');
                            const estadoUF = data.uf.toUpperCase();
                            
                            // Procura a opção correta e a seleciona
                            for (let option of estadoSelect.options) {
                                if (option.value === estadoUF) {
                                    option.selected = true;
                                    break;
                                }
                            }
                            
                            // Dispara um evento de change para atualizar quaisquer listeners
                            estadoSelect.dispatchEvent(new Event('change'));
                        }
                    })
                    .catch(error => console.error('Erro ao consultar CEP:', error));
            }
        });
    }
});