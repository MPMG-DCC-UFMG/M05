function update_config_rec_sources() {
    event.preventDefault();
    let confs = $('.rec_confs');

    let config = {};
    let config_type;
    
    for (let i=0;i<confs.length;i++) {
        config_type = confs[i].getAttribute('config');

        config[config_type] = {
            amount: parseInt(confs[i].querySelector('.rec_size').value),
            active: confs[i].querySelector('.rec_active').checked
        }
    }

    console.log(config);

}

function update_config_rec_evidences() {
    event.preventDefault();

    let confs = $('.ev_confs');

    let config = {};
    let config_type;
    
    for (let i=0;i<confs.length;i++) {
        config_type = confs[i].getAttribute('config');

        config[config_type] = {
            amount: parseInt(confs[i].querySelector('.ev_amount').value),
            min_similarity: parseInt(confs[i].querySelector('.ev_min_sim').value),
            top_n_recommendations: parseInt(confs[i].querySelector('.ev_top_n').value),
            active: confs[i].querySelector('.ev_active').checked
        }
    }

    console.log(config);
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