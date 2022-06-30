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
        
        $.ajax({
            url: SERVICES_URL + API_CLIENT_NAME+'/bookmark',
            type: 'post',
            dataType: 'json',
            headers: { 'Authorization': 'Token ' + AUTH_TOKEN },
            async: false,
            data: {
                id_usuario: USER_ID,
                id_pasta: bookmark.folder,
                nome: bookmark.name,
                indice_documento: DOC_TYPE,
                id_documento: DOC_ID,
                id_consulta: QID
            },
            success: function (res) {
                bookmark.id = res.id_favorito;
                // delay para que o elastic search tenha tempo de atualizar os dados
                setTimeout(function () { update_folder_tree(); }, 1500);
            },
            error: function (res) {
                alert(`Não foi possível salvar o bookmark. Erro: ${res.message}. Tente novamente!`);
            }
        });
    } else {
        // mudando a pasta de local
        $.ajax({
            url: SERVICES_URL + API_CLIENT_NAME+'/bookmark',
            type: 'put',
            dataType: 'json',
            headers: { 'Authorization': 'Token ' + AUTH_TOKEN },
            data: {
                id_favorito: bookmark.id,
                id_pasta: bookmark.folder,
                nome: bookmark.name,
            }, success: function(data) {
                setTimeout(function () { update_folder_tree(); }, 1500);
            }, error: function (data) {
                console.error(data);
            }
        });
    }
}

services.remove_bookmark = function(bookmark_id) {
    
    if (running_in_document_page()) {
        let bookmark_icon = $('#bookmark-icon');
    
        bookmark_icon.removeClass('fas');
        bookmark_icon.addClass('far');

        bookmark.id = null;        
    }

    $.ajax({
        url: SERVICES_URL + API_CLIENT_NAME+'/bookmark',
        type: 'delete',
        dataType: 'json',
        async: false,
        headers: { 'Authorization': 'Token ' + AUTH_TOKEN },
        async: false,
        data: {
            id_favorito: bookmark_id,
        },
        success: function(data) {
            setTimeout(function () { update_folder_tree(); }, 1500);
        },
    });
}

services.start_bookmark = function(index, item_id) {
    $.ajax({
        url: SERVICES_URL + API_CLIENT_NAME+'/bookmark',
        type: 'get',
        dataType: 'json',
        headers: { 'Authorization': 'Token ' + AUTH_TOKEN },
        data: {
            id_usuario: USER_ID,
            indice_documento: index,
            id_documento: item_id,
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
        url: SERVICES_URL + API_CLIENT_NAME+'/bookmark',
        type: 'get',
        dataType: 'json',
        data: {
            id_favorito: bookmark_id,
        },
        headers: { 'Authorization': 'Token ' + AUTH_TOKEN },
        error: function (res) {
            console.error(res.message);
        }
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
    
    if (!bulk)
        $('#moveBookmarkModal').modal('hide');
    
    let doc_name = $(`#document-${id_bookmark_to_move}-name`).text();

    let idx = folder_tree[active_folder].favoritos.findIndex(bookmark => bookmark.id === id_bookmark_to_move);

    if (idx >= 0) {
        let bookmark_moved = folder_tree[active_folder].favoritos[idx];
        bookmark_moved.id_pasta = move_to_folder

        folder_tree[active_folder].favoritos.splice(idx, 1);        
        folder_tree[move_to_folder].favoritos.push(bookmark_moved);
    }


    if (!bulk) 
        update_gallery();

    $.ajax({
        url: SERVICES_URL + API_CLIENT_NAME+'/bookmark',
        type: 'put',
        dataType: 'json',
        async: false,
        headers: { 'Authorization': 'Token ' + AUTH_TOKEN },
        data: {
            nome: doc_name,
            id_pasta: move_to_folder,
            id_favorito: id_bookmark_to_move,
        },
        error: function (res) {
            console.error(res.message);
        }
    });
}

services.rename_bookmark = function (new_name, bookmark_id, folder_id) {
    $.ajax({
        url: SERVICES_URL + API_CLIENT_NAME+'/bookmark',
        type: 'put',
        dataType: 'json',
        headers: { 'Authorization': 'Token ' + AUTH_TOKEN },
        data: {
            nome: new_name,
            id_pasta: folder_id,
            id_favorito: bookmark_id,
        }
    });
}


services.rename_folder = function(folder_id, new_name) {
    let data = {
        id_pasta: folder_id,
        nome: new_name,
    };
    

    $.ajax({
        url: SERVICES_URL + API_CLIENT_NAME+'/bookmark_folder',
        type: 'put',
        dataType: 'json',
        headers: { 'Authorization': 'Token ' + AUTH_TOKEN },
        data: data,
        async: false
    });
}

services.remove_folder = function(folder_id) {
    console.log(`Removendo ${folder_id}`);
    
    $.ajax({
        url: SERVICES_URL + API_CLIENT_NAME+'/bookmark_folder',
        type: 'delete',
        dataType: 'json',
        async: false,
        headers: { 'Authorization': 'Token ' + AUTH_TOKEN },
        data: {
            id_pasta: folder_id,
        }
    });
}

services.create_folder = function(parent_id) {
    let folder_name = 'Nova pasta';
    
    let ajax = $.ajax({
        url: SERVICES_URL + API_CLIENT_NAME+'/bookmark_folder',
        type: 'post',
        dataType: 'json',
        headers: { 'Authorization': 'Token ' + AUTH_TOKEN },
        data: {
            id_usuario: USER_ID,
            id_pasta_pai: parent_id,
            nome: folder_name,
        },
        success: function(data) {
            folder_tree[data.id_pasta] = {
                id: data.id_pasta,
                pasta_pai: parent_id,
                nome: folder_name,
                subpastas: [],
                favoritos: [],
            }
        
            folder_tree[parent_id].subpastas.push(folder_tree[data.id_pasta]);
            
            create_children(parent_id, data.id_pasta, folder_name);
        }
    });

}

services.get_folder_tree = function()  {
    let tree;
    $.ajax({
        url: SERVICES_URL + API_CLIENT_NAME+'/bookmark_folder',
        type: 'get',
        dataType: 'json',
        async: false,
        data: {
            id_usuario: USER_ID
        },
        headers: { 'Authorization': 'Token ' + AUTH_TOKEN },
        success: function (data) {
            tree = data;
        }
    });

    return tree;
}

services.get_bookmark_folder_tree = function() {
    tree = services.get_folder_tree();
    raw_tree = tree;

    // Inserindo após converter o json com estrutura de pastas do usuário em HTML
    $('#bookmark-folder').append(parse_folder_tree(tree));
    $('#bookmark-move-folder').html(parse_folder_move_tree(tree,'bookmark'));
    // $('#move-folder').html(parse_folder_move_tree(tree, 'folder'));

    // Habilita o evento de menu de contexto
    enable_context_menu_event(tree);

    dictify_tree(tree);

    if (running_in_document_page())
        listify_tree(tree, folders);

    // // define que o pasta raiz é a pasta ativa, por default
    // active_folder = tree.id;

    update_active_folder(tree.id) ;
}

services.move_folder = function () {
    if (move_to_folder == null) {
        alert('Escolha uma pasta de destino!');
        return;
    }

    if (bulk) {
        for (let i = 0; i < bookmarks_to_move.length;i++) {
            id_bookmark_to_move = bookmarks_to_move[i];
            services.move_bookmark();
        }

        for (let i = 0; i < folders_to_move.length;i++) {
            $.ajax({
                url: SERVICES_URL + API_CLIENT_NAME+'/bookmark_folder',
                type: 'put',
                dataType: 'json',
                headers: { 'Authorization': 'Token ' + AUTH_TOKEN },
                async: false,
                data: {
                    id_pasta: folders_to_move[i],
                    id_pasta_pai: move_to_folder,
                }
            });
        }

        // delay para que o elastic search tenha tempo de atualizar o índice
        setTimeout(function () { location.reload()}, 1000);

        return;
    }

    $('#moveFolderModal').modal('hide');
    
    if (id_folder_to_move == move_to_folder) {
        alert('Você não pode mover uma pasta para ela mesma!');
        return;
    }


    $.ajax({
        url: SERVICES_URL + API_CLIENT_NAME+'/bookmark_folder',
        type: 'put',
        dataType: 'json',
        headers: { 'Authorization': 'Token ' + AUTH_TOKEN },
        data: {
            id_pasta: id_folder_to_move,
            id_pasta_pai: move_to_folder,
        },
        success: function () {
            folder_blacklist = [];
            location.reload();
        }
    });
    
}