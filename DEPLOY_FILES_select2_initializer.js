/**
 * Script para inicialização padronizada dos menus suspensos (Select2)
 * Este arquivo centraliza a configuração do Select2 para garantir consistência
 * em todas as páginas de edição do sistema.
 */

(function($) {
  $(document).ready(function() {
    // Função para inicializar o Select2 com configurações padrão
    function initializeSelect2() {
      // Verificar se o Select2 já foi inicializado por outra instância
      if (window.select2AlreadyInitialized) {
        console.log("Select2 já foi inicializado em outra parte do código. Ignorando inicialização global.");
        return;
      }
      
      console.log("Inicializando Select2...");
      
      // Aplicar Select2 a todos os selects que ainda não foram inicializados
      $('select').not('.select2-hidden-accessible').each(function() {
        var $this = $(this);
        
        // Obter o placeholder do atributo data-placeholder ou do texto da opção vazia
        var placeholder = $this.attr('data-placeholder') || 
                         ($this.find('option[value=""]').length ? $this.find('option[value=""]').text() : 'Selecione uma opção');
        
        // Configurar o Select2 com as opções padrão
        $this.select2({
          language: {
            noResults: function() {
              return "Nenhum resultado encontrado";
            },
            searching: function() {
              return "Buscando...";
            }
          },
          placeholder: placeholder,
          allowClear: false,
          minimumResultsForSearch: 0, // Sempre mostrar a caixa de pesquisa
          width: '100%'
        });
      });
      
      // Ocultar botões de relacionamento
      $('.related-widget-wrapper-link, .related-lookup, a[data-href-template]').hide();
      
      // Adicionar classe is-filled para campos com valor
      $('select').each(function() {
        if ($(this).val() !== '' && $(this).val() !== null) {
          $(this).parent().addClass('is-filled');
        }
      });
      
      // Marcar como inicializado para evitar duplicação
      window.select2AlreadyInitialized = true;
      
      console.log("Select2 inicializado com sucesso!");
    }
    
    // Inicializar Select2 após um pequeno atraso para garantir que todos os elementos estejam carregados
    setTimeout(function() {
      initializeSelect2();
    }, 100);
  });
})(jQuery);
