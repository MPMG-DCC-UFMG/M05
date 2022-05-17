function log_search_click(link){
    // var query = $('#results-container').data('executed-query');
    $.ajax({
        async: false,
        url: SERVICES_URL+'log_search_click',
        type: 'post',
        dataType: 'json',
        headers:{'Authorization': 'Token ' + AUTH_TOKEN},
        data:{
            id_usuario: USER_ID,
            posicao: $(link).data('rank-number'),
            id_documento: $(link).data('item-id'),
            tipo_documento: $(link).data('item-type'),
            qid: QID,
            pagina: PAGE,
        }
    });
}

function log_suggestion_click(item){
    $.ajax({
        url: SERVICES_URL+'log_query_suggestion_click',
        type: 'post',
        dataType: 'json',
        headers:{'Authorization': 'Token ' + AUTH_TOKEN},
        data:{
            posicao_ranking: item['posicao_ranking'],
            suggestion: item['value'],
        }
    });
}

$(function(){
    $("#query").autocomplete({
        source: function(request, response){
            var ajax = $.ajax({
                url: SERVICES_URL+'query_suggestion',
                type: 'get',
                dataType: 'json',
                headers:{'Authorization': 'Token ' + AUTH_TOKEN},
                data:{
                    consulta: request.term
                }
            });

            ajax.done(function(data){
                suggestions = data['suggestions'];
                response(suggestions);
            });

        },
        select: function(event, ui) {
            log_suggestion_click(ui['item']);
        }
    });

    $('#results-container .result-link').on('mousedown', function(e1){
        $('#results-container .result-link').one('mouseup', function(e2){
          if (e1.which == 2 && e1.target == e2.target) { // consider only the middle button click
            log_search_click(e2.target);
          }
        });
      });

    $('#results-container .result-link').click(function(e){
        // e.preventDefault();
        log_search_click(e.target);
    });

    $('#filter_instances').multiselect({
        includeSelectAllOption: true,
        enableFiltering: true,
        selectAllText: 'Selecionar todas',
        nonSelectedText: 'Nada selecionado',
        filterPlaceholder: 'Procurar',
        buttonClass: 'btn btn-outline-secondary',
        buttonWidth: '100%',
    });

    $('#filter_doc_types').multiselect({
        includeSelectAllOption: true,
        enableFiltering: true,
        selectAllText: 'Selecionar todos',
        nonSelectedText: 'Nada selecionado',
        filterPlaceholder: 'Procurar',
        buttonClass: 'btn btn-outline-secondary',
        buttonWidth: '100%',
    });

    $('#filter_entidade_pessoa, #filter_entidade_municipio, #filter_entidade_organizacao, #filter_entidade_local').multiselect({
        includeSelectAllOption: true,
        enableFiltering: true,
        selectAllText: 'Selecionar todos',
        nonSelectedText: 'Nada selecionado',
        filterPlaceholder: 'Procurar',
        buttonClass: 'btn btn-outline-secondary',
        buttonWidth: '100%',
    });

    $("#filter_start_date_display").datepicker({
        changeMonth: true,
        changeYear: true,
        dateFormat: 'dd/mm/yy',
        altField: "#filter_start_date",
        altFormat: "yy-mm-dd"
    });

    $("#filter_end_date_display").datepicker({
        changeMonth: true,
        changeYear: true,
        dateFormat: 'dd/mm/yy',
        altField: "#filter_end_date",
        altFormat: "yy-mm-dd"
    });
});



menu = $('.searchbar.navbar');
menuPosition = menu.offset().top;
searchBody = $('.searchresult-container')
bodyPosition = searchBody.offset().top;
$(window).bind('scroll', function() {
    
    var position = $(window).scrollTop() - menuPosition;
    if(position >= 50){
        if(!menu.hasClass('fixed-top')){
            searchBody.css('margin-top', '97px');
            menu.addClass('fixed-top');
            
            menu.css('top', '-57px');
            menu.animate({top: 0}, 500);
        }
    }
    else{
        menu.removeClass('fixed-top');
        searchBody.css('margin-top', 0);
    }
    
});

$(document).ready(function() {
    menu.removeClass('fixed-top');
    $("body").tooltip({ selector: '[data-toggle=tooltip]' });
});

function pad_time(time) {
    return time >= 10 ? time : '0' + time;
}

function timestamp_converter(timestamp) {
    let date = new Date(timestamp);

    let days = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];
    let months = ['Jan', 'Fev', 'Mar', 'Abr', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];

    let cur_date = new Date();

    let year = cur_date.getFullYear() != date.getFullYear() ? date.getFullYear() : '';

    return `${days[date.getDay()]}, ${pad_time(date.getDate())} de ${months[date.getMonth()]} ${year} - ${pad_time(date.getHours())}h${pad_time(date.getMinutes())}`;
}