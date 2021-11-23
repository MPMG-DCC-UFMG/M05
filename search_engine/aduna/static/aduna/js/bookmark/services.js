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
                nome: DOC_TITLE,
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

    bookmark.id = null;
    bookmark.folder = null;

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
            $('#bookmark-toggle-wrapper').append(create_bookmark_toggle(true))
        },
        error: function () {
            $('#bookmark-toggle-wrapper').append(create_bookmark_toggle(false))
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
        create_children(parent_id, data.folder_id, folder_name);
        add_new_folder_to_dropdown(data.folder_id, folder_name);
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
        $('#bookmark-folder').append(parse_folder_tree(tree))

        // Habilita o evento de menu de contexto
        enable_context_menu_event(tree)

        // define que o pasta raiz é a pasta ativa, por default
        update_active_folder(tree.id)    

        let folders = [];
        listify_tree(tree, folders);
        
        update_recently_folder_dropdown(folders);
    });
}