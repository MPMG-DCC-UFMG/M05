function update_cities_select_options(data) {
    let filter_cities = $('#filter_city');
    
    filter_cities.empty();

    let options = ['<option value="" selected disabled>Selecionar</option>']
    let city;

    console.log(data);

    for (let i=0;i<data.length;i++) {
        city = data[i];
        options.push(`<option value="${city.nome_cidade}">${city.nome_cidade}</option>`);
    } 

    filter_cities.html(options.join(''));

    filter_cities.multiselect('rebuild');
}

function update_available_cities(state_id) {
    let cities_api = SERVICES_URL + `cities?filtro_sigla_estado=${state_id}`
    
    $.ajax({
        url: cities_api,
        type: 'get',
        dataType: 'json',
        headers: { 'Authorization': 'Token ' + AUTH_TOKEN },
        data: {
            id_usuario: USER_ID,
        },
        success: function (data) {
            update_cities_select_options(data);
            $('#filter_city_wrapper').removeClass('d-none');
        },
        error: function (data) {
            alert(`Não foi possível obter as cidades para o estado ${state_id}!`);
        }
    });   
}

$(document).ready(function () {
    $('#filter_state').on('change', function () {
        $('#filter_city_wrapper').addClass('d-none');

        update_available_cities(this.value);
    });
});
