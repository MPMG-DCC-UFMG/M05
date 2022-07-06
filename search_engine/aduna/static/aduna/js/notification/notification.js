NOTIFICATION_SERVER_ADDRESS = window.location.origin;
NOTIFICATION_SERVICE_URL = SERVICES_URL+API_CLIENT_NAME+'/notification';

function get_notification_url(notification_id) {
    return NOTIFICATION_SERVER_ADDRESS + `/aduna/recomendacoes?notification_id=${notification_id}`;
}

function notification2html(notification) {
    // `<li class="font-weight-bold">
    //     <div class="rounded border bg-light p-2">
    //         <p class="p-0 m-0">Descobrimos novos documentos que podem te interessar! <a href="recomendacoes/documentos">Visualizar</a>.</p>
    //     </div>
    //     <div class="d-flex justify-content-end pr-1 mt-1">
    //         <span class="small">08/12/2021 às 12:37</span>
    //     </div>
    // </li>`

    let li = document.createElement('LI');
    li.className = notification.data_visualizacao == null ? 'font-weight-bold' : ''; 

    let message_wrapper = document.createElement('DIV');
    message_wrapper.className = 'rounded border bg-light p-2'

    let message = document.createElement('P');
    message.className = 'p-0 m-0';

    let content = document.createElement('SPAN');
    content.textContent =  notification.texto;

    let url = document.createElement('A');
    url.setAttribute('href', get_notification_url(notification.id));
    url.textContent = 'Visualizar';

    message.appendChild(content);
    // message.appendChild(url);

    message_wrapper.appendChild(message);
    message_wrapper.appendChild(url);

    let time_wrapper = document.createElement('DIV');
    time_wrapper.className = 'd-flex justify-content-end pr-1 mt-1 mb-1 font-italic';

    let time = document.createElement('SPAN');
    time.className = 'small';

    time.textContent = timestamp_converter(notification.data_criacao);

    time_wrapper.appendChild(time);

    li.appendChild(message_wrapper);
    li.appendChild(time_wrapper);

    return li;

}

function parse_notifications(notifications) {
    let has_new_notifications = false;

    let notification_lis = [];
    for (let idx in notifications) {
        let notification = notifications[idx];

        notification_lis.push(notification2html(notification));

        if (notification.data_visualizacao == null)
            has_new_notifications = true;
    }

    if (notification_lis.length == 0) {
        notification_lis.push(`
        <li>
            <p class="m-0 p-0 text-center">Sem notificações.</p>
        </li>
        `)
    }

    $('#notification-list').empty();
    $('#notification-list').append(notification_lis);

    // habilita o simbolo que tem nova notificação
    if (has_new_notifications) 
        $('#notification-badge').removeClass('d-none');
}

function get_notifications() {
    $.ajax({
        url: NOTIFICATION_SERVICE_URL,
        type: 'get',
        dataType: 'json',
        headers: { 'Authorization': 'Token ' + AUTH_TOKEN },
        data: {
            id_usuario: USER_ID,
        },
        success: function (notifications) {
            parse_notifications(notifications);
        },
        error: function (data) {
            alert('Não foi possível obter novas notificações!');
        }
    });
}

$(document).ready(function () {
    get_notifications();
});