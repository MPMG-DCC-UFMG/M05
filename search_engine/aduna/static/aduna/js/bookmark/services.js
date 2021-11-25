// Implementa a integração com o servidor

var services = {}

services.create_bookmark = function() {
    let last_selected_folder = $('#selectFolder').val();

    $(`#folder-option-${last_selected_folder}`).removeAttr('selected');
    $(`#folder-option-${bookmark.folder}`).attr("selected", "selected");

    if (bookmark.id == null) {
        let bookmark_icon = $('#bookmark-icon');
    
        bookmark_icon.removeClass('far');
        bookmark_icon.addClass('fas');
        
        let ajax = $.ajax({
            url: SERVICES_URL + 'bookmark',
            type: 'post',
            dataType: 'json',
            headers: { 'Authorization': 'Token ' + AUTH_TOKEN },
            data: {
                id_folder: bookmark.folder,
                nome: bookmark.name,
                index: DOC_TYPE,
                item_id: DOC_ID,
                consulta: QUERY
            }
        });
    
        ajax.done(function (data) {
            if (data.success)
                bookmark.id = data.id_bookmark;
            
            else 
                alert('Não foi possível salvar o bookmark. Tente novamente!');
    
        });
    } else {
        // mudando a pasta de local
        $.ajax({
            url: SERVICES_URL + 'bookmark',
            type: 'put',
            dataType: 'json',
            headers: { 'Authorization': 'Token ' + AUTH_TOKEN },
            data: {
                novo_nome: bookmark.name,
                id_pasta_destino: bookmark.folder,
                id_bookmark: bookmark.id,
            }
        });
    }
}

services.remove_bookmark = function(bookmark_id) {
    let bookmark_icon = $('#bookmark-icon');

    bookmark_icon.removeClass('fas');
    bookmark_icon.addClass('far');

    // bookmark.id = null;
    // bookmark.folder = null;

    $.ajax({
        url: SERVICES_URL + 'bookmark',
        type: 'delete',
        dataType: 'json',
        headers: { 'Authorization': 'Token ' + AUTH_TOKEN },
        data: {
            id_bookmark: bookmark_id,
        }
    });
}

services.start_bookmark = function(index, item_id) {
    $.ajax({
        url: SERVICES_URL + 'bookmark',
        type: 'get',
        dataType: 'json',
        headers: { 'Authorization': 'Token ' + AUTH_TOKEN },
        data: {
            index: index,
            item_id: item_id,
        },
        success: function (res) {
            bookmark.id = res.bookmark.id;
            bookmark.folder = res.bookmark.id_folder;
            bookmark.name = res.bookmark.nome;

            inject_bookmark();
            $('#bookmark-toggle-wrapper').append(create_bookmark_toggle(true));
        },
        error: function () {
            inject_bookmark();
            $('#bookmark-toggle-wrapper').append(create_bookmark_toggle(false))
        }
    });
}

services.get_bookmark = function (id_bookmark) {
    return $.ajax({
        url: SERVICES_URL + 'bookmark',
        type: 'get',
        dataType: 'json',
        data: {
            id_bookmark: id_bookmark,
        },
        // async: false,
        headers: { 'Authorization': 'Token ' + AUTH_TOKEN },
    });
}

services.move_bookmark = function () {
    if (!folder_to_move_bookmark) {
        alert('Escolha a nova pasta do favorito!');
        return;
    }
    
    if (!id_bookmark_to_move) {
        alert('Escolha o favorito a ser movido!');
        return;
    }
    
    $('#moveBookmarkModal').modal('hide');
    let doc_name = $(`#document-${id_bookmark_to_move}-name`).text();

    let idx = folder_tree[active_folder].arquivos.indexOf(id_bookmark_to_move);
    if (idx >= 0)
        folder_tree[active_folder].arquivos.splice(idx, 1);

    folder_tree[folder_to_move_bookmark].arquivos.push(id_bookmark_to_move);

    update_gallery();

    $.ajax({
        url: SERVICES_URL + 'bookmark',
        type: 'put',
        dataType: 'json',
        headers: { 'Authorization': 'Token ' + AUTH_TOKEN },
        data: {
            novo_nome: doc_name,
            id_pasta_destino: folder_to_move_bookmark,
            id_bookmark: id_bookmark_to_move,
        }
    });
}

services.rename_bookmark = function (new_name, id_bookmark, id_folder) {
    $.ajax({
        url: SERVICES_URL + 'bookmark',
        type: 'put',
        dataType: 'json',
        headers: { 'Authorization': 'Token ' + AUTH_TOKEN },
        data: {
            novo_nome: new_name,
            id_pasta_destino: id_folder,
            id_bookmark: id_bookmark,
        }
    });
}


services.rename_folder = function(folder_id, new_name) {
    $.ajax({
        url: SERVICES_URL + 'bookmark/folder',
        type: 'put',
        dataType: 'json',
        headers: { 'Authorization': 'Token ' + AUTH_TOKEN },
        data: {
            folder_id: folder_id,
            nome: new_name,
        }
    });
}

services.remove_folder = function(folder_id, remove_or_move_itens_inside_folder_to_parent_decision) {
    $.ajax({
        url: SERVICES_URL + 'bookmark/folder',
        type: 'delete',
        dataType: 'json',
        headers: { 'Authorization': 'Token ' + AUTH_TOKEN },
        data: {
            folder_id: folder_id,
            decision: remove_or_move_itens_inside_folder_to_parent_decision,
        }
    });
}

services.create_folder = function(parent_id) {
    let folder_name = 'Nova pasta';
    
    let ajax = $.ajax({
        url: SERVICES_URL + 'bookmark/folder',
        type: 'post',
        dataType: 'json',
        headers: { 'Authorization': 'Token ' + AUTH_TOKEN },
        data: {
            pasta_pai: parent_id,
            nome: folder_name,
        }
    });

    ajax.done(function (data) {
        
        folder_tree[data.folder_id] = {
            id: data.folder_id,
            pasta_pai: parent_id,
            nome: folder_name,
            subpastas: [],
            arquivos: [],
        }

        folder_tree[parent_id].subpastas.push(folder_tree[data.folder_id]);
        
        create_children(parent_id, data.folder_id, folder_name);
    });
}

services.get_bookmark_folder_tree = function() {
    let ajax = $.ajax({
        url: SERVICES_URL + 'bookmark/folder',
        type: 'get',
        dataType: 'json',
        headers: { 'Authorization': 'Token ' + AUTH_TOKEN },
    });

    ajax.done(function (tree) {
        // Inserindo após converter o json com estrutura de pastas do usuário em HTML
        $('#bookmark-folder').append(parse_folder_tree(tree));
        $('#bookmark-move-folder').html(parse_folder_move_tree(tree));
        // Habilita o evento de menu de contexto
        enable_context_menu_event(tree);

        dictify_tree(tree);

        if (typeof DOC_ID !== 'undefined')
            listify_tree(tree, folders);

        // // define que o pasta raiz é a pasta ativa, por default
        // active_folder = tree.id;

        update_active_folder(tree.id) ;
    });
}