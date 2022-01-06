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
                user_id: USER_ID,
                folder_id: bookmark.folder,
                name: bookmark.name,
                doc_index: DOC_TYPE,
                doc_id: DOC_ID,
                query_id: QID
            },
            success: function (res) {
                bookmark.id = res.bookmark_id;
            },
            error: function (res) {
                console.log(res); //`Não foi possível salvar o bookmark. Erro: ${res.message}. Tente novamente!`);
            }
        });
    } else {
        // mudando a pasta de local
        $.ajax({
            url: SERVICES_URL + 'bookmark',
            type: 'put',
            dataType: 'json',
            headers: { 'Authorization': 'Token ' + AUTH_TOKEN },
            data: {
                folder_id: bookmark.folder,
                name: bookmark.name,
                bookmark_id: bookmark.id,
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
            bookmark_id: bookmark_id,
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
            user_id: USER_ID,
            doc_index: index,
            doc_id: item_id,
        },
        success: function (data) {
            bookmark.id = data.id;
            bookmark.folder = data.id_folder;
            bookmark.name = data.nome;
            
            inject_bookmark();
            $('#bookmark-toggle-wrapper').append(create_bookmark_toggle(true));
            
            $('#inputName').val(bookmark.name);
        },
        error: function () {
            inject_bookmark();
            $('#bookmark-toggle-wrapper').append(create_bookmark_toggle(false))
        }
    });
}

services.get_bookmark = function (bookmark_id) {
    return $.ajax({
        url: SERVICES_URL + 'bookmark',
        type: 'get',
        dataType: 'json',
        data: {
            bookmark_id: bookmark_id,
        },
        // async: false,
        headers: { 'Authorization': 'Token ' + AUTH_TOKEN },
    });
}

services.move_bookmark = function () {
    if (!move_to_folder) {
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

    folder_tree[move_to_folder].arquivos.push(id_bookmark_to_move);

    update_gallery();

    $.ajax({
        url: SERVICES_URL + 'bookmark',
        type: 'put',
        dataType: 'json',
        headers: { 'Authorization': 'Token ' + AUTH_TOKEN },
        data: {
            name: doc_name,
            folder_id: move_to_folder,
            bookmark_id: id_bookmark_to_move,
        }
    });
}

services.rename_bookmark = function (new_name, bookmark_id, folder_id) {
    $.ajax({
        url: SERVICES_URL + 'bookmark',
        type: 'put',
        dataType: 'json',
        headers: { 'Authorization': 'Token ' + AUTH_TOKEN },
        data: {
            name: new_name,
            folder_id: folder_id,
            bookmark_id: bookmark_id,
        }
    });
}


services.rename_folder = function(folder_id, new_name) {
    $.ajax({
        url: SERVICES_URL + 'bookmark_folder',
        type: 'put',
        dataType: 'json',
        headers: { 'Authorization': 'Token ' + AUTH_TOKEN },
        data: {
            folder_id: folder_id,
            name: new_name,
        }
    });
}

services.remove_folder = function(folder_id) {
    $.ajax({
        url: SERVICES_URL + 'bookmark_folder',
        type: 'delete',
        dataType: 'json',
        headers: { 'Authorization': 'Token ' + AUTH_TOKEN },
        data: {
            folder_id: folder_id,
        }
    });
}

services.create_folder = function(parent_id) {
    let folder_name = 'Nova pasta';
    
    let ajax = $.ajax({
        url: SERVICES_URL + 'bookmark_folder',
        type: 'post',
        dataType: 'json',
        headers: { 'Authorization': 'Token ' + AUTH_TOKEN },
        data: {
            user_id: USER_ID,
            parent_folder_id: parent_id,
            name: folder_name,
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
        url: SERVICES_URL + 'bookmark_folder',
        type: 'get',
        dataType: 'json',
        data: {
            user_id: USER_ID
        },
        headers: { 'Authorization': 'Token ' + AUTH_TOKEN },
    });

    ajax.done(function (tree) {
        // Inserindo após converter o json com estrutura de pastas do usuário em HTML
        $('#bookmark-folder').append(parse_folder_tree(tree));
        $('#bookmark-move-folder').html(parse_folder_move_tree(tree,'bookmark'));
        $('#move-folder').html(parse_folder_move_tree(tree, 'folder'));

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

services.move_folder = function () {
    if (id_folder_to_move == move_to_folder) {
        // TODO: Não deixar também mover para nenhuma subpasta
        alert('Você não pode mover uma pasta para ela mesma!');
    }
    console.log(id_folder_to_move, move_to_folder)

    $('#moveFolderModal').modal('hide');
    $.ajax({
        url: SERVICES_URL + 'bookmark_folder',
        type: 'put',
        dataType: 'json',
        headers: { 'Authorization': 'Token ' + AUTH_TOKEN },
        data: {
            folder_id: id_folder_to_move,
            parent_folder_id: move_to_folder,
        },
        success: function () {
            location.reload();
        },
        error: function (res) {
            alert(res.message)
        }
    });
    
    // console.log(id_folder_to_move, move_to_folder);
}