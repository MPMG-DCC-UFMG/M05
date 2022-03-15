function update_config_rec_sources() {
    event.preventDefault();
    let confs = $('.rec_confs');

    let config = {};
    let config_type;
    
    let amount;
    let active;

    for (let i=0;i<confs.length;i++) {
        config_type = confs[i].getAttribute('config');
        config[config_type] = {};

        amount = parseInt(confs[i].querySelector('.rec_size').value);
        active = confs[i].querySelector('.rec_active').checked;

        if (amount != CONF_REC_SRC[config_type].amount)
            config[config_type]['amount'] = amount;

        if (active != CONF_REC_SRC[config_type].active) 
            config[config_type].active = active;

        if (Object.keys(config[config_type]).length == 0)
            delete config[config_type];
    }

    if (Object.keys(config).length == 0) {
        alert('Nenhuma alteração foi feita nos documentos a serem recomendados!');
        return;
    }

    console.log(config);

    $.ajax({
        url: SERVICES_URL + 'config_recommendation/sources',
        type: 'put',
        dataType: 'json',
        async: false,
        // traditional: true,
        data: config,
        success: function (data) {
            location.reload();
        },
        error: function () {
            console.log('Não foi possível atualizar a configuração!');
        }
    });

}

function update_config_rec_evidences() {
    event.preventDefault();

    let confs = $('.ev_confs');

    let config = {};
    let config_type;
    
    let amount;
    let min_similarity;
    let top_n_recommendations;
    let active;

    for (let i=0;i<confs.length;i++) {
        config_type = confs[i].getAttribute('config');
        config[config_type] = {};

        amount = parseInt(confs[i].querySelector('.ev_amount').value);
        min_similarity = parseInt(confs[i].querySelector('.ev_min_sim').value);
        top_n_recommendations = parseInt(confs[i].querySelector('.ev_top_n').value);
        active = confs[i].querySelector('.ev_active').checked;

        if (amount != CONF_REC_EV[config_type].amount)
            config[config_type]['amount'] = amount;
        
        if (min_similarity != CONF_REC_EV[config_type].min_similarity)
            config[config_type]['min_similarity'] = min_similarity;

        if (top_n_recommendations != CONF_REC_EV[config_type].top_n_recommendations)
            config[config_type]['top_n_recommendations'] = top_n_recommendations;
        
        if (active != CONF_REC_EV[config_type].active)
            config[config_type]['active'] = active;
        
        if (Object.keys(config[config_type]).length == 0)
            delete config[config_type];

    }

    if (Object.keys(config).length == 0) {
        alert('Nenhuma alteração foi feita nas fontes de recomendação!');
        return;
    }
    
    $.ajax({
        url: SERVICES_URL + 'config_recommendation/evidences',
        type: 'put',
        dataType: 'json',
        async: false,
        // traditional: true,
        data: config,
        success: function (data) {
            location.reload();
        },
        error: function () {
            console.log('Não foi possível atualizar a configuração!');
        }
    });
}

function bind_label_to_range(id) {
    $(`#${id}`).on('input', function() {
        $(`#lbl_${id}`).text(`${this.value}%`);
    });
}

function get_confs() {
    CONF_REC_SRC = {};
    $.ajax({
        url: SERVICES_URL + 'config_recommendation/sources',
        type: 'get',
        dataType: 'json',
        // headers: { 'Authorization': 'Token ' + AUTH_TOKEN },
        success: function (data) {
            for (let i=0;i<data.length;i++) {
                CONF_REC_SRC[data[i].es_index_name] = {
                    active: data[i].active,
                    amount: data[i].amount,
                }
            }
        },
        error: function () {
            console.log('Não foi possível obter config. sources!');
        }
    });

    CONF_REC_EV = {};
    $.ajax({
        url: SERVICES_URL + 'config_recommendation/evidences',
        type: 'get',
        dataType: 'json',
        // headers: { 'Authorization': 'Token ' + AUTH_TOKEN },
        success: function (data) {
            for (let i=0;i<data.length;i++) {
                CONF_REC_EV[data[i].evidence_type] = {
                    active: data[i].active,
                    amount: data[i].amount,
                    min_similarity: data[i].min_similarity,
                    top_n_recommendations: data[i].top_n_recommendations
                }
            }
        },
        error: function () {
            console.log('Não foi possível obter config. evidences!');
        }
    });
}

$(document).ready(function() {
    for (let i=0;i<EVIDENCE_TYPES.length;i++)
        bind_label_to_range(`ev_${EVIDENCE_TYPES[i]}_min_sim`);
    
    get_confs();
});