function update_config_rec_sources() {
    event.preventDefault();

    let rec_size_diario =  $('#rec_size_diario').val();
    if (rec_size_diario.length == 0) {
        alert('A quantidade de recomendações para diário não pode ser vazia.');
        return;
    }

    let rec_size_processo =  $('#rec_size_processo').val();
    if (rec_size_processo.length == 0) {
        alert('A quantidade de recomendações para processos não pode ser vazia.');
        return;
    }
    
    let rec_size_licitacoes =  $('#rec_size_processo').val();
    if (rec_size_licitacoes.length == 0) {
        alert('A quantidade de recomendações para licitações não pode ser vazia.');
        return;
    }

    let rec_diarios =  $('#rec_diarios_active').is(":checked");
    let rec_processo =  $('#rec_processo_active').is(":checked");
    let rec_licitacoes =  $('#rec_licitacoes_active').is(":checked");

    let data = {
        rec_size_diario: parseInt(rec_size_diario),
        rec_diarios_active: rec_diarios,
        rec_size_processo: parseInt(rec_size_processo),
        rec_processo_active: rec_processo,
        rec_size_licitacoes: parseInt(rec_size_licitacoes),
        rec_licitacoes_active: rec_licitacoes
    }

    console.log(data);
}

function update_config_rec_evidences() {
    event.preventDefault();

    let bookmark_amount = parseInt($('#ev_bookmark_amount').val());
    let bookmark_min_sim = parseInt($('#ev_bookmark_min_sim').val());
    let bookmark_top_n = parseInt($('#ev_bookmark_top_n').val());
    let bookmark_active = $('#ev_bookmark_active').is(":checked");
    // 

    let query_amount = parseInt($('#ev_query_amount').val());
    let query_min_sim = parseInt($('#ev_query_min_sim').val());
    let query_top_n = parseInt($('#ev_query_top_n').val());
    let query_active = $('#ev_query_active').is(":checked");
    // 

    let click_amount = parseInt($('#ev_click_amount').val());
    let click_min_sim = parseInt($('#ev_click_min_sim').val());
    let click_top_n = parseInt($('#ev_click_top_n').val());
    let click_active = $('#ev_click_active').is(":checked");

    let bookmark_conf = {
        amount: bookmark_amount,
        min_similarity: bookmark_min_sim,
        top_n_recommendations: bookmark_top_n,
        active: bookmark_active
    }

    let query_conf = {
        amount: query_amount,
        min_similarity: query_min_sim,
        top_n_recommendations: query_top_n,
        active: query_active
    }

    let click_conf = {
        amount: click_amount,
        min_similarity: click_min_sim,
        top_n_recommendations: click_top_n,
        active: click_active
    }

    let conf =  {
        bookmark: bookmark_conf,
        query: query_conf,
        click: click_conf
    }

    console.log(conf);
}

function bind_label_to_range(id) {
    $(`#${id}`).on('input', function() {
        $(`#lbl_${id}`).text(`${this.value}%`);
    });
}

$(document).ready(function() {
    bind_label_to_range('ev_bookmark_min_sim');
    bind_label_to_range('ev_query_min_sim');
    bind_label_to_range('ev_click_min_sim');

});