RECOMMENDATION_SERVICE_URL = window.location.origin;
RECOMMENDATION_SERVICES_URL = RECOMMENDATION_SERVICE_URL + '/services/document_recommendation';

function get_doc_url(doc_index, doc_id) {
    return `/aduna/document/${doc_index}/${doc_id}`
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
            recommendation_id: recommendation_id,
            accepted: feedback_value
        },
        headers: { 'Authorization': 'Token ' + AUTH_TOKEN },
        success: function (data) {
            console.log('tudo ok');
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

    link.textContent = titleize(recommendation.recommended_doc_title);
    link.setAttribute('href', get_doc_url(recommendation.recommended_doc_index, recommendation.recommended_doc_id));
    link.setAttribute('target', '_blank');

    let feedback = document.createElement('DIV');
    feedback.id = recommendation.id;
    feedback.className = 'border rounded-pill px-3';
    feedback.value = recommendation.accepted;

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

    let recommendation_reason = document.createElement('SMALL');

    if (recommendation.matched_from == "BOOKMARK") {
        let doc_link = document.createElement('A');

        doc_link.textContent = titleize(recommendation.evidence_doc_title);
        doc_link.setAttribute('href', get_doc_url(recommendation.evidence_doc_index, recommendation.evidence_doc_id));
        doc_link.setAttribute('target', '_blank');
        
        recommendation_reason.append('Similar ao "');
        recommendation_reason.appendChild(doc_link);
        recommendation_reason.append('" que você favoritou');
    }

    else if (recommendation.matched_from == "QUERY") {
        recommendation_reason.textContent = `Porque você pesquisou por "${titleize(recommendation.evidence_query_text)}"`;
    }

    // recommendation_reason.textContent = recommendation.reason;

    feedback.appendChild(btn_positive_feedback);
    feedback.appendChild(btn_negative_feedback);

    content_wrapper.appendChild(link);
    content_wrapper.appendChild(feedback);

    div.appendChild(content_wrapper);
    div.appendChild(recommendation_reason);

    li.appendChild(div);

    return li;
}

function show_recommendations(recommendations) {
    let rec_lis = [];

    for (let i=0; i< recommendations.length; i++) {
        rec_lis.push(create_reccomendation_line(recommendations[i]));
    }

    $('#recommendation-list').html(rec_lis);
}

function get_recommendations() {
    let data = {
        user_id: USER_ID
    }

    if (NOTIFICATION_ID.length > 0)
        data.notification_id = NOTIFICATION_ID;
     
    $.ajax({
        url: RECOMMENDATION_SERVICES_URL,
        type: 'get',
        dataType: 'json',
        data: data,
        headers: { 'Authorization': 'Token ' + AUTH_TOKEN },
        success: function (recommendations) {
            show_recommendations(recommendations);
        },
        error: function (data) {
            alert('Não foi possível obter recomendações!');
        }
    });
}

$(document).ready(function () {
    $('body').removeClass('view-as-page');

    get_recommendations();
});
