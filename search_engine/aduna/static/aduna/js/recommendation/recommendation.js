var RECOMMENDATION_SERVICES_URL = SERVICES_URL + API_CLIENT_NAME + '/document_recommendation';
var RECOMMENDATIONS;
var ACTIVE_FILTER = 'all';

function get_doc_url(doc_index, doc_id) {
    return `/aduna/documento/${doc_index}/${doc_id}`
}

function titleize(s) {
    s = s.toLowerCase().split(' ');
	for (let i = 0; i < s.length; i++) 
		s[i] = s[i].charAt(0).toUpperCase() + s[i].slice(1);
	return s.join(' ');
}

function update_feedback(recommendation_id, feedback_value) {
    console.log(recommendation_id, feedback_value);

    $.ajax({
        url: RECOMMENDATION_SERVICES_URL,
        type: 'put',
        dataType: 'json',
        data: {
            id_recomendacao: recommendation_id,
            aprovado: feedback_value
        },
        success: function (data) {
        },
        error: function (data) {
            alert('Não foi possível atualizar o feedback da recomendação. Tente novamente!');
        }
    });   
}

function create_reccomendation_line(recommendation) {
    `
    <li class="col-12 border rounded p-3 mt-3">
        <div class="">
            <div class="d-flex justify-content-between align-content-center">
                <a href="">Diário Oficial De Belo Horizonte - 09/12/2021</a>
                <div class="border rounded-pill px-3">
                    <button class="border-0 bg-white" title="Gostei da sugestão">
                        <i class="far fa-thumbs-up"></i>
                    </button>
                    <button class="border-0 bg-white" title="Não gostei da sugestão">
                        <i class="fas fa-thumbs-down"></i>
                    </button>
                </div>
            </div>
            <small class="">Porque você pesquisou por "Dengue"</small>
        </div> 
    </li>
    `

    let li = document.createElement('LI');
    li.className = 'col-12 border rounded p-3 mt-3';

    let div = document.createElement('DIV');

    let content_wrapper = document.createElement('DIV');
    content_wrapper.className = 'd-flex justify-content-between align-content-center';
    
    let link = document.createElement('A');

    link.textContent = titleize(recommendation.titulo_doc_recomendado);
    link.id = `link_rec-${recommendation.id}`;
    link.className = recommendation.data_visualizacao == null ? 'font-weight-bold' : '';
    link.setAttribute('href', get_doc_url(recommendation.indice_doc_recomendado, recommendation.id_doc_recomendado));
    link.setAttribute('target', '_blank');

    let feedback = document.createElement('DIV');
    feedback.id = recommendation.id;
    feedback.className = 'border rounded-pill px-3';
    feedback.value = recommendation.aprovado;

    let btn_positive_feedback = document.createElement('BUTTON');
    btn_positive_feedback.id = `btn-negative-feedback-${recommendation.id}`
    
    btn_positive_feedback.active = false;
    btn_positive_feedback.className = 'border-0 bg-white';

    let btn_negative_feedback = document.createElement('BUTTON');
    btn_negative_feedback.id = `btn-negative-feedback-${recommendation.id}`;
    btn_negative_feedback.active = false;
    btn_negative_feedback.className = 'border-0 bg-white';
    
    positive_feedback_icon = document.createElement('I');
    positive_feedback_icon.id = `positive-feedback-icon-${recommendation.id}`;
    negative_feedback_icon = document.createElement('I');
    negative_feedback_icon.id = `negative-feedback-icon-${recommendation.id}`;

    if (feedback.value == true) {
        positive_feedback_icon.className = 'fas fa-thumbs-up';
        negative_feedback_icon.className = 'far fa-thumbs-down';
    } else if (feedback.value == false) {
        positive_feedback_icon.className = 'far fa-thumbs-up';
        negative_feedback_icon.className = 'fas fa-thumbs-down';
    } else {
        positive_feedback_icon.className = 'far fa-thumbs-up';
        negative_feedback_icon.className = 'far fa-thumbs-down';  
    }
    
    feedback.update_value = function () {
        
        let pos_feedback_icon = $(`#positive-feedback-icon-${feedback.id}`);
        let neg_feedback_icon = $(`#negative-feedback-icon-${feedback.id}`);

        if (btn_positive_feedback.active) {
            feedback.value = true;
            
            pos_feedback_icon.removeClass('far')
            neg_feedback_icon.removeClass('fas')
            
            pos_feedback_icon.addClass('fas')
            neg_feedback_icon.addClass('far')
            
        } else if (btn_negative_feedback.active) {
            feedback.value = false;
            
            pos_feedback_icon.removeClass('fas');
            neg_feedback_icon.removeClass('far');
            
            
            pos_feedback_icon.addClass('far');
            neg_feedback_icon.addClass('fas');
            
        } else {
            feedback.value = null;
            
            pos_feedback_icon.removeClass('fas');
            neg_feedback_icon.removeClass('fas');
            
            pos_feedback_icon.addClass('far');
            neg_feedback_icon.addClass('far');
        }

        for (let i = 0; i< RECOMMENDATIONS.length;i++) {
            if (RECOMMENDATIONS[i].id == feedback.id) {
                RECOMMENDATIONS[i].aprovado = feedback.value;
                break;
            }
        }
        update_feedback(feedback.id, feedback.value);
    }
    
    btn_positive_feedback.appendChild(positive_feedback_icon);
    btn_positive_feedback.onclick = function () {
        if (btn_negative_feedback.active)
        btn_negative_feedback.active = false;
        btn_positive_feedback.active = !btn_positive_feedback.active;
        feedback.update_value();
    }
    
    btn_negative_feedback.appendChild(negative_feedback_icon);
    btn_negative_feedback.onclick = function () {
        if (btn_positive_feedback.active)
        btn_positive_feedback.active = false;
        
        btn_negative_feedback.active = !btn_negative_feedback.active;
        feedback.update_value();
    }
    
    feedback.appendChild(btn_positive_feedback);
    feedback.appendChild(btn_negative_feedback);

    let recommendation_reason = document.createElement('SMALL');

    if (recommendation.evidencia == "bookmark") {
        let doc_link = document.createElement('A');

        doc_link.textContent = titleize(recommendation.evidencia_titulo_doc);
        doc_link.setAttribute('href', get_doc_url(recommendation.evidencia_indice_doc, recommendation.evidencia_id_doc));
        doc_link.setAttribute('target', '_blank');
        
        recommendation_reason.append('Similar ao "');
        recommendation_reason.appendChild(doc_link);
        recommendation_reason.append('" que você favoritou');
    }

    else if (recommendation.evidencia == "query") {
        recommendation_reason.textContent = `Porque você pesquisou por "${titleize(recommendation.evidencia_texto_consulta)}"`;
    }

    else if (recommendation.evidencia == "click") {
        let doc_link = document.createElement('A');

        doc_link.textContent = titleize(recommendation.evidencia_titulo_doc);
        doc_link.setAttribute('href', get_doc_url(recommendation.evidencia_indice_doc, recommendation.evidencia_id_doc));
        doc_link.setAttribute('target', '_blank');
        
        recommendation_reason.append('Similar ao "');
        recommendation_reason.appendChild(doc_link);
        recommendation_reason.append('" que você visitou');
    }

    let date_of_rec = document.createElement('SMALL');
    date_of_rec.textContent = timestamp_converter(recommendation.data_criacao);
    date_of_rec.className = 'small font-italic';
    date_of_rec.style.fontSize = '.75rem';

    let info_wrapper = document.createElement('DIV');
    info_wrapper.className = 'mt-2 d-flex justify-content-between';

    info_wrapper.appendChild(recommendation_reason);
    info_wrapper.appendChild(date_of_rec);

    let mark_as_seen_wrapper = document.createElement('DIV');
    mark_as_seen_wrapper.className = 'd-flex align-items-center border rounded rounded-pill px-2 py-1 d-none';

    let in_mark_as_seen = document.createElement('INPUT');
    in_mark_as_seen.type = 'checkbox';
    in_mark_as_seen.style.cursor = 'pointer';
    in_mark_as_seen.id = `mark_as_seen-${recommendation.id}`;

    let disable_mark_as_seen = function() {
        // Oculta o botão de marcar como visto e faz aparecer os botão de feedback
        mark_as_seen_wrapper.classList.remove('d-flex');
        mark_as_seen_wrapper.classList.add('d-none');
        feedback.classList.remove('d-none');
        link.classList.remove('font-weight-bold');
        mark_recommendation_as_seen(recommendation.id);
    };

    in_mark_as_seen.onchange = disable_mark_as_seen;
    link.onclick = disable_mark_as_seen;

    let label_mark_as_seen = document.createElement('LABEL');
    label_mark_as_seen.textContent = 'Marcar como visto';
    label_mark_as_seen.className = 'small m-0 ml-1';
    label_mark_as_seen.style.cursor = 'pointer';
    label_mark_as_seen.style.userSelect = false;
    label_mark_as_seen.setAttribute('for', `mark_as_seen-${recommendation.id}`);

    mark_as_seen_wrapper.appendChild(in_mark_as_seen);
    mark_as_seen_wrapper.appendChild(label_mark_as_seen);

    let action_wrapper = document.createElement('DIV');

    if (recommendation.data_visualizacao == null) {
        feedback.classList.add('d-none');
        action_wrapper.appendChild(mark_as_seen_wrapper);
        action_wrapper.appendChild(feedback);
    } else  
        action_wrapper.appendChild(feedback);

    content_wrapper.appendChild(link);
    content_wrapper.appendChild(action_wrapper);

    div.appendChild(content_wrapper);
    div.appendChild(info_wrapper);

    li.appendChild(div);

    return li;
}

function deactive_filter_btn(btn_ref) {
    btn_ref.classList.remove('bg-primary');
    btn_ref.classList.remove('text-white');
    btn_ref.classList.remove('font-weight-bold');
    btn_ref.classList.add('text-muted');
}

function active_filter_btn(btn_ref) {
    btn_ref.classList.remove('text-muted');
    btn_ref.classList.add('bg-primary');
    btn_ref.classList.add('text-white');
    btn_ref.classList.add('font-weight-bold');
}

function add_filters() {
            // <button class="rounded border rounded-pill text-muted px-2">Tudo</button>
            // <button class="rounded border rounded-pill mx-2 text-muted px-2">Vistos</button>
            // <button class="rounded border rounded-pill bg-primary text-white font-weight-bold px-2">Não vistos</button>

    let filters = document.createElement('DIV');
    filters.id = 'filters';
    filters.className = 'd-flex justify-content-between';
    filters.active = 'all';

    let btn_all = document.createElement('BUTTON');
    btn_all.id = 'filter-all';
    
    let btn_seen = document.createElement('BUTTON');
    btn_seen.id = 'filter-seen';

    let btn_not_seen = document.createElement('BUTTON');
    btn_not_seen.id = 'filter-not-seen';

    btn_all.className = 'rounded border rounded-pill bg-primary text-white font-weight-bold px-2';
    btn_all.textContent = 'Tudo (0)';

    btn_not_seen.className = 'rounded border rounded-pill text-muted px-2 ml-2';
    btn_not_seen.textContent = 'Não visto (0)';

    btn_seen.className = 'rounded border rounded-pill text-muted px-2 ml-2';
    btn_seen.textContent = 'Visto (0)';

    filters.btn_active_ref = btn_all;

    btn_all.onclick = function () {
        if (filters.active == 'all')
            return;
        
        deactive_filter_btn(filters.btn_active_ref);
        active_filter_btn(btn_all);

        filters.active = 'all';
        filters.btn_active_ref = btn_all;
        ACTIVE_FILTER = 'all';

        show_recommendations();
    }

    btn_seen.onclick = function () {
        if (filters.active == 'seen')
            return;

        deactive_filter_btn(filters.btn_active_ref);
        active_filter_btn(btn_seen);

        filters.active = 'seen';
        filters.btn_active_ref = btn_seen;
        ACTIVE_FILTER = 'seen';

        show_recommendations();
    }

    btn_not_seen.onclick = function () {
        if (filters.active == 'not_seen')
            return;

        deactive_filter_btn(filters.btn_active_ref);
        active_filter_btn(btn_not_seen);

        filters.active = 'not_seen';
        filters.btn_active_ref = btn_not_seen;
        ACTIVE_FILTER = 'not_seen';

        show_recommendations();
    }

    filters.appendChild(btn_all);
    filters.appendChild(btn_seen);
    filters.appendChild(btn_not_seen);

    $('#rec-header').append(filters);
}

function update_filters_label() {
    let recommendations_seen = RECOMMENDATIONS.filter(function (rec) {
        return rec.data_visualizacao != null;
    });

    let recommendations_not_seen = RECOMMENDATIONS.filter(function (rec) {
        return rec.data_visualizacao == null;
    });

    $("#filter-all").text(`Tudo (${RECOMMENDATIONS.length})`);
    $("#filter-seen").text(`Visto (${recommendations_seen.length})`);
    $("#filter-not-seen").text(`Não visto (${recommendations_not_seen.length})`);
}

function show_recommendations() {
    let recommendations = [];
    
    if (ACTIVE_FILTER == 'seen')
        recommendations = RECOMMENDATIONS.filter(function (rec) {
            return rec.data_visualizacao != null;
        });
    
    else if (ACTIVE_FILTER == 'not_seen')
        recommendations = RECOMMENDATIONS.filter(function (rec) {
            return rec.data_visualizacao == null;
        });

    else 
        recommendations = RECOMMENDATIONS;
    
    if (recommendations.length == 0)  {
        $('#recommendation-list').html(`
            <li class="border rounded p-3 text-center mt-3 w-100">
                <p class="h6 p-0 m-0">Não há itens a serem apresentados.</p>
            </li>
        `);
        return;
    }

    let rec_lis = [];

    for (let i=0; i< recommendations.length; i++) {
        rec_lis.push(create_reccomendation_line(recommendations[i]));
    }

    $('#recommendation-list').html(rec_lis);
}

function mark_recommendation_as_seen(recommendation_id) {
    for (let i = 0; i< RECOMMENDATIONS.length;i++) {
        if (RECOMMENDATIONS[i].id == recommendation_id) {
            if (RECOMMENDATIONS[i].data_visualizacao)
                return;

            RECOMMENDATIONS[i].data_visualizacao = Date.now();
            update_filters_label();
            show_recommendations();
            break;
        }
    }

    $.ajax({
        url: RECOMMENDATION_SERVICES_URL,
        type: 'put',
        dataType: 'json',
        data: {
            id_recomendacao: recommendation_id,
            visualizado: true
        },
        success: function (data) {
            // console.log('tudo ok');
        },
        error: function (data) {
            console.error(data)
            // alert('Não foi possível atualizar o status da recomendação. Tente novamente!');
        }
    });   
}

function get_recommendations() {
    let data = {
        id_usuario: USER_ID
    }

    if (NOTIFICATION_ID.length > 0)
        data.id_notificacao = NOTIFICATION_ID;
     
    $.ajax({
        url: RECOMMENDATION_SERVICES_URL,
        type: 'get',
        dataType: 'json',
        data: data,
        success: function (recommendations) {
            RECOMMENDATIONS = recommendations;
            show_recommendations('Sem recomendações!');
            update_filters_label();
        },
        error: function (data) {
            alert('Não foi possível obter recomendações!');
        }
    });
}

$(document).ready(function () {
    $('body').removeClass('view-as-page');
    add_filters();
    get_recommendations();
});
