function send_change_request(conf_type, data) {
    $.ajax({
        url: SERVICES_URL + `config_recommendation/${conf_type}`,
        type: 'put',
        dataType: 'json',
        async: false,
        data: data,
        success: function (data) {
        },
        error: function (data) {
            console.error(data);
        }
    });    
}

function update_config_rec_sources() {
    event.preventDefault();

    let confs = $('.rec_confs');

    let config;
    let data_changed;
    let config_type;
    let config_id;
    
    let amount;
    let active;

    let wait_for_changes = false;

    for (let i=0;i<confs.length;i++) {
        config_type = confs[i].getAttribute('config');
        config_id = confs[i].getAttribute('index_id');

        amount = parseInt(confs[i].querySelector('.rec_size').value);
        active = confs[i].querySelector('.rec_active').checked;

        config = CONF_REC_SRC.filter(function(item) { return item.nome_indice == config_type;})[0];
        data_changed = {};

        if (amount != config.quantidade)
            data_changed.quantidade = amount;

        if (active != config.ativo)
            data_changed.ativo = active;

        if (Object.keys(data_changed).length > 0) {
            data_changed.id_conf_fonte = config_id;
            wait_for_changes = true;

            send_change_request('sources', data_changed);
        }
    }

    if (wait_for_changes){
        setTimeout(function () {
            location.reload();
        }, 750);
    }
}

function update_config_rec_evidences() {
    event.preventDefault();

    let confs = $('.ev_confs');

    let config;
    let data_changed;
    let config_type;
    
    let amount;
    let min_similarity;
    let top_n_recommendations;
    let active;

    let wait_for_changes = false;

    for (let i=0;i<confs.length;i++) {
        config_type = confs[i].getAttribute('config');

        amount = parseInt(confs[i].querySelector('.ev_amount').value);
        min_similarity = parseInt(confs[i].querySelector('.ev_min_sim').value);
        top_n_recommendations = parseInt(confs[i].querySelector('.ev_top_n').value);
        active = confs[i].querySelector('.ev_active').checked;
        
        config = CONF_REC_EV.filter(function (item) { return item.id == config_type })[0];
        data_changed = {};

        if (amount != config.quantidade)
            data_changed.quantidade = amount;

        if (min_similarity != config.similaridade_minima)
            data_changed.similaridade_minima = min_similarity;

        if (top_n_recommendations != config.top_n_recomendacoes)
            data_changed.top_n_recomendacoes = top_n_recommendations;
            
        if (active != config.ativo)
            data_changed.ativo = active;

        
        if (Object.keys(data_changed).length > 0) {
            data_changed.id_conf_evidencia = config_type;
            wait_for_changes = true;

            send_change_request('evidences', data_changed);
        }
    }

    if (wait_for_changes) {
        setTimeout(function () {
            location.reload();
        }, 950);
    }

   
}

function bind_label_to_range(id) {
    $(`#${id}`).on('input', function() {
        $(`#lbl_${id}`).text(`${this.value}%`);
    });
}

$(document).ready(function() {
    for (let i=0;i<EVIDENCE_TYPES.length;i++)
        bind_label_to_range(`ev_${EVIDENCE_TYPES[i]}_min_sim`);
});