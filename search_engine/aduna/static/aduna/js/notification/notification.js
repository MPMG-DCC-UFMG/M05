NOTIFICATION_SERVER_ADDRESS = window.location.origin;
NOTIFICATION_SERVICES_URL = NOTIFICATION_SERVER_ADDRESS + '/services/notification';

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
    li.className = notification.date_visualized == null ? 'font-weight-bold' : ''; 

    let message_wrapper = document.createElement('DIV');
    message_wrapper.className = 'rounded border bg-light p-2'

    let message = document.createElement('P');
    message.className = 'p-0 m-0';

    let content = document.createElement('SPAN');
    content.textContent =  notification.message;

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

    time.textContent = notification.date;

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

        if (notification.date_visualized == null)
            has_new_notifications = true;
    }

    $('#notification-list').empty();
    $('#notification-list').append(notification_lis);

    // habilita o simbolo que tem nova notificação
    if (has_new_notifications) 
        $('#notification-badge').removeClass('d-none');
}

function get_notifications() {
    $.ajax({
        url: NOTIFICATION_SERVICES_URL,
        type: 'get',
        dataType: 'json',
        headers: { 'Authorization': 'Token ' + AUTH_TOKEN },
        data: {
            user_id: USER_ID,
        },
        success: function (notifications) {
            console.log(USER_ID);
            parse_notifications(notifications);
        },
        error: function (data) {
            alert(data);
        }
    });
}

$(document).ready(function () {
    get_notifications();
});