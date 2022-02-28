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

    let rec_diarios =  $('#rec_diarios').is(":checked");
    let rec_processo =  $('#rec_processo').is(":checked");
    let rec_licitacoes =  $('#rec_licitacoes').is(":checked");

    console.log($('#rec_licitacoes').val());

    let data = {
        rec_size_diario: parseInt(rec_size_diario),
        rec_diarios: rec_diarios,
        rec_size_processo: parseInt(rec_size_processo),
        rec_processo: rec_processo,
        rec_size_licitacoes: parseInt(rec_size_licitacoes),
        rec_licitacoes: rec_licitacoes
    }

    console.log(data);
}

function update_config_rec_evidences() {
    console.log('potari');
    event.preventDefault();
}