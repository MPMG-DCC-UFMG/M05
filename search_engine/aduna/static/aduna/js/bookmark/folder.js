// Contém o código responsável por gerar as visualização das pastas de bookmarks
var MAX_FOLDERS_IN_DROPDOWN = 5;

var folder_opened_historic = [];
var active_folder = null;
var folder_to_remove = null;
var move_to_folder = null;
var id_bookmark_to_move = null;
var id_folder_to_move = null;
var folder_tree = {};
var raw_tree = null;
var folders = [];

var folder_blacklist = [];

var bulk = false;
var folders_to_move = [];
var bookmarks_to_move = [];
var folders_to_remove = [];
var bookmarks_to_remove = [];

var bookmark_inside_removed_folder;

function running_in_document_page() {
    if (typeof DOC_ID !== 'undefined')
        return true;
    return false;
}

function show_move_to_modal() {
    id_bookmark_to_move = this.context;
    
    $(`#document-${this.context}`).popover('hide');
    $('#moveBookmarkModal').modal('show');
}

function show_move_folder_modal() {
    bulk = false;

    id_folder_to_move = this.context;
    folder_blacklist = [id_folder_to_move];

    update_folder_move_tree();

    $(`#${this.context}-folder-name`).popover('hide');
    $('#moveFolderModal').modal('show');
}

function remove_bookmark() {
    $(`#document-${this.context}`).popover('hide');
    $(`#document-${this.context}-li`).remove();
    
    let idx = folder_tree[active_folder].favoritos.indexOf(this.context);
    if (idx >= 0) 
        folder_tree[active_folder].favoritos.splice(idx, 1);

    services.remove_bookmark(this.context);
}

function dictify_tree(tree) {
    for (let i = 0; i < tree.subpastas.length; i++)
        dictify_tree(tree.subpastas[i]);
    folder_tree[tree.id] = tree;
}

function update_folder_tree() {
    let tree = services.get_folder_tree();
    dictify_tree(tree);
}

function enable_bookmark_edit_mode() {
    $(`#document-${this.context}`).addClass('d-none');
    $(`#document-${this.context}-input`).removeClass('d-none');
    $(`#document-${this.context}-input`).focus();
    $(`#document-${this.context}`).popover('hide');
}

function document_context_menu(doc_id) {
    // lista base com as opções do menu de contexto de uma pasta
    let ul = document.createElement('UL');

    // melhorando o layout da lista
    ul.style.listStyle = 'none';
    ul.className = 'm-0 p-0';

    // html da opção de criar nova pasta que aparece no menu de contexto de uma página
    let li_new = create_context_menu_item('fas fa-pen', 'Editar', doc_id, enable_bookmark_edit_mode);
    ul.appendChild(li_new);

    let li_move = create_context_menu_item('fas fa-folder', 'Mover para', doc_id, show_move_to_modal);
    ul.appendChild(li_move);

    let li_remove = create_context_menu_item('fas fa-trash-alt', 'Remover', doc_id, remove_bookmark);
    ul.appendChild(li_remove);

    li_move.className = 'mt-2';
    li_remove.className = 'mt-2';

    return ul
}

function get_document_url(bookmark) {
    return `${SERVER_ADDRESS}/aduna/document/${bookmark.indice_documento}/${bookmark.id_documento}`;
}

function attach_document_context_menu(doc_id) {
    $(`#document-${doc_id}`).popover({
        html: true,
        sanitize: false,
        trigger: "manual",
        content: function () {
            // retorna o html do menu de contexto, que será renderizado quando o evento
            // popover('show') estiver ativo
            return document_context_menu(doc_id);
        }
    })
        .on("mouseenter", function () {
            var _this = this;
            $(this).popover("show");
            $(".popover").on("mouseleave", function () {
                $(_this).popover('hide');
            });
        }).on("mouseleave", function () {
            var _this = this;
            if (!$(".popover:hover").length) {
                $(_this).popover("hide");
            }
        });
}

function enable_folder_items_selection() {
    $('#enable-edit-all-folder-wrapper').addClass('d-none');
    $('#edit-all-folder-options-wrapper').removeClass('d-none');

    $('.folder-item-content').removeClass('d-flex')
    $('.folder-item-content').addClass('d-none');

    $('.select-folder-item').removeClass('d-none');
    $('.select-folder-item').addClass('d-flex');
}

function disable_folder_items_selection() {
    $('#edit-all-folder-options-wrapper').addClass('d-none');
    $('#enable-edit-all-folder-wrapper').removeClass('d-none');

    $('.select-folder-item').removeClass('d-flex')
    $('.select-folder-item').addClass('d-none');

    $('.folder-item-content').removeClass('d-none');
    $('.folder-item-content').addClass('d-flex');

    let cb_folders = $('.folder-ckeckbox');
    for (let i = 0; i < cb_folders.length;i++)
        if (cb_folders[i].checked)
            cb_folders[i].checked = false; 

    let cb_bookmarks = $('.bookmark-ckeckbox');
    for (let i = 0; i < cb_bookmarks.length;i++)
        if (cb_bookmarks[i].checked) 
            cb_bookmarks[i].checked = false;
}

function create_folder_item(folder) {
    let li = document.createElement('LI');
    li.className = 'mt-1'
    li.style.userSelect = 'none';
    li.id = `folder-${folder.id}-li`;
    li.style.cursor = 'pointer'
    li.title = `Clique para abrir a pasta "${folder.nome}"`;

    let icon = document.createElement('I');
    icon.className = 'fas fa-folder';
    
    let text = document.createElement('SPAN');
    text.textContent = folder.nome;
    text.className = 'mx-2';
    
    let folder_name = document.createElement('P');
    folder_name.id = `folder-${folder.id}-name`;
    folder_name.className = 'p-0 m-0';
    folder_name.appendChild(icon);
    folder_name.appendChild(text); 
    folder_name.style.cursor = 'pointer';
    
    let info = document.createElement('SMALL');
    info.textContent = `${folder.subpastas.length} subpasta(s), ${folder.favoritos.length} documento(s)`;
    
    let detail_wrapper = document.createElement('DIV');
    detail_wrapper.id = `folder-${folder.id}-detail`;
    
    detail_wrapper.className = 'd-flex justify-content-between align-items-center w-100 folder-item-content';

    detail_wrapper.appendChild(folder_name);
    detail_wrapper.appendChild(info);
    detail_wrapper.onclick = () => update_active_folder(`${folder.id}`);

    let checkbox = document.createElement('INPUT');
    checkbox.id = `checkbox-folder-${folder.id}`;
    checkbox.setAttribute('type', 'checkbox');
    checkbox.className = `folder-ckeckbox mr-3 my-0 p-0`;
    checkbox.value = folder.id; 

    let label = document.createElement('LABEL');
    label.className = 'm-0 d-flex justify-content-between align-items-center w-100'
    label.setAttribute('for', `checkbox-folder-${folder.id}`);
    label.style.cursor = 'pointer';

    let label_icon = document.createElement('I');
    label_icon.className = 'fas fa-folder';

    let label_text = document.createElement('SPAN');
    label_text.textContent = folder.nome;
    label_text.className = 'mx-2';

    let label_info = document.createElement('SMALL');
    label_info.textContent = `${folder.subpastas.length} subpasta(s), ${folder.favoritos.length} documento(s)`;

    let label_folder_name = document.createElement('P');
    label_folder_name.className = 'p-0 m-0';
    label_folder_name.appendChild(label_icon);
    label_folder_name.appendChild(label_text);

    label.appendChild(label_folder_name);
    label.appendChild(label_info);

    label.className = 'd-flex justify-content-between align-items-center w-100 m-0';

    let select_wrapper = document.createElement('DIV');
    select_wrapper.appendChild(checkbox)
    select_wrapper.appendChild(label)
    select_wrapper.className = 'align-items-center select-folder-item d-none';

    li.appendChild(select_wrapper);
    li.appendChild(detail_wrapper);

    return li;
}

function create_bookmark_item(bookmark) {
    let li = document.createElement('LI');
    li.className = 'my-1';
    li.id = `document-${bookmark.id}-li`;
    li.style.userSelect = 'none';

    let content_wrapper = document.createElement('DIV');

    let input = document.createElement('INPUT');

    input.setAttribute('type', 'text');
    input.value = bookmark.nome;
    input.id = `document-${bookmark.id}-input`;

    let disabled_input_classes = 'p-0 m-0 border-0 px-2 d-none';
    input.className = disabled_input_classes;

    
    let link = document.createElement('A');
    
    link.id = `document-${bookmark.id}`;
    link.setAttribute('href', get_document_url(bookmark));
    link.setAttribute('target', '_blank');
    
    let icon = document.createElement('I');
    icon.className = 'fas fa-file-alt text-dark';
    
    let text = document.createElement('SPAN');
    text.id = `document-${bookmark.id}-name`;
    text.textContent = bookmark.nome;
    text.className = 'mx-2';
    
    let disable_edit_mode = function () {
        text.textContent = input.value;
        input.className = disabled_input_classes;
        link.className = '';

        $('#inputName').val(input.value);

        services.rename_bookmark(input.value, bookmark.id, active_folder);
    }

    input.addEventListener('keyup', function () {
        // Number 13 is the "Enter" key on the keyboard
        if (event.keyCode === 13) {
            input.blur();
        }
    })

    input.addEventListener('blur', disable_edit_mode);

    link.setAttribute('data-toggle', 'popover');
    link.setAttribute('data-container', 'body');
    link.setAttribute('data-placement', 'right');

    link.appendChild(icon);
    link.appendChild(text);

    content_wrapper.appendChild(input);
    content_wrapper.appendChild(link);
    content_wrapper.className = 'folder-item-content';

    let checkbox = document.createElement('INPUT');
    checkbox.id = `checkbox-bookmark-${bookmark.id}`;
    checkbox.setAttribute('type', 'checkbox');
    checkbox.className = `bookmark-ckeckbox mr-3 my-0 p-0`;
    checkbox.value = bookmark.id;

    let label = document.createElement('LABEL');
    label.className = 'm-0 w-100'
    label.setAttribute('for', `checkbox-bookmark-${bookmark.id}`);
    label.style.cursor = 'pointer';

    let label_text = document.createElement('SPAN');
    label_text.textContent = bookmark.nome;
    label_text.className = 'mx-2';

    let label_icon = document.createElement('I');
    label_icon.className = 'fas fa-file-alt text-dark';

    label.appendChild(label_icon);
    label.appendChild(label_text);
    
    let select_wrapper = document.createElement('DIV');
    select_wrapper.className = 'select-folder-item align-items-center d-none p-0';
    select_wrapper.appendChild(checkbox);
    select_wrapper.appendChild(label);

    li.appendChild(select_wrapper);
    li.appendChild(content_wrapper)

    li.className = 'mt-1 d-flex align-items-center';

    return li;
}

function back_folder() {
    if (folder_opened_historic.length > 0)
        update_active_folder(folder_opened_historic.pop(), true);
}

function update_gallery() {
    if (running_in_document_page())
        return; 

    let folder_items = $('#folder-items');
    let pasta = folder_tree[active_folder];

    let back_folder_li = '';

    if(folder_opened_historic.length > 0) {
        back_folder_li = `<li class="my-1 d-flex justify-content-between">
            <div class="">
                <p title="Clique para voltar à última pasta vista" class="m-0 p-0" onclick="back_folder()" style="cursor: pointer;"><i class="fas fa-chevron-left"></i> Voltar à pasta anterior</p>
            </div>
            <div class="">
                <div class="" id="enable-edit-all-folder-wrapper">
                    <button class="btn m-0 p-0 border rounded px-2 ml-2" onclick="enable_folder_items_selection()">
                        <i class="fas fa-tasks"></i>
                    </button>
                </div>
                <div id="edit-all-folder-options-wrapper" class="d-none">
                    <button class="btn m-0 p-0" onclick="bulk_move()">
                        <i class="fas fa-arrows-alt"></i> Mover
                    </button>
                    <button class="btn m-0 p-0 ml-2" onclick="bulk_remove()">
                        <i class="fas fa-trash-alt"></i> Remover
                    </button>
                    <button class="btn m-0 p-0 border rounded px-2 ml-2" onclick="disable_folder_items_selection()">
                        <i class="fas fa-times"></i> Cancelar
                    </button>
                </div>
            </div>
        </li>
        <hr/>
        `;
    } else {
        back_folder_li = `<li class="my-1 d-flex justify-content-end">
            <div class="">
                <div class="" id="enable-edit-all-folder-wrapper">
                    <button class="btn m-0 p-0 border rounded px-2 ml-2" onclick="enable_folder_items_selection()">
                        <i class="fas fa-tasks"></i>
                    </button>
                </div>
                <div id="edit-all-folder-options-wrapper" class="d-none">
                    <button class="btn m-0 p-0" onclick="bulk_move()">
                        <i class="fas fa-arrows-alt"></i> Mover
                    </button>
                    <button class="btn m-0 p-0 ml-2" onclick="bulk_remove()">
                        <i class="fas fa-trash-alt"></i> Remover
                    </button>
                    <button class="btn m-0 p-0 border rounded px-2 ml-2" onclick="disable_folder_items_selection()">
                        <i class="fas fa-times"></i> Cancelar
                    </button>
                </div>
            </div>
        </li>
        <hr/>
        `;
    }

    if ((pasta.favoritos.length + pasta.subpastas.length) == 0) {
        folder_items.html(`
            ${back_folder_li}
            <li class="my-1">
                <div class="d-flex justify-content-center text-center">
                    <p class="m-0">Essa pasta está vazia.</p>
                </div>
            </li>
            `);
        return;
    }

    folder_items.html(back_folder_li);

    for (let i=0;i<pasta.subpastas.length;i++) {
        let subpasta = pasta.subpastas[i];
        folder_items.append(create_folder_item(subpasta));
    }


    for (let i=0;i<pasta.favoritos.length;i++) {
        services.get_bookmark(pasta.favoritos[i]).then(response => {
            let bookmark = response;
            folder_items.append(create_bookmark_item(bookmark));
            attach_document_context_menu(bookmark.id);
        });
    }
}

function update_active_folder(new_active_folder, back_folder=false) {

    /** Atualiza a informação de qual pasta está correntemente ativa
     *
     * Argumentos:
     *  -  new_active_folder: ID da nova pasta que será ativa 
     */

    if (active_folder && !back_folder)
        folder_opened_historic.push(active_folder);

    if (active_folder)
        $(`#${active_folder}-folder-name`).removeClass('text-primary');

    active_folder = new_active_folder;

    $(`#${active_folder}-folder-name`).addClass('text-primary');

    update_gallery();
}

function create_children_from_active_folder() {
    create_children(active_folder)
}

function show_remove_folder_modal() {
    bulk = false;

    folder_to_remove = this.context;
    $('#folderModal').modal('hide');
    $('#removeFolderModal').modal('show');
}

function attach_context_menu(folder_id) {
    /* Adiciona a função responsável por gerar o menu de contexto a pasta especificado por folder_id
    quando o mouse passe sobre a pasta.

    Arguementos:
        - folder_id: ID da pasta que será linkado o evento de menu de contexto
    
    */ 

    $(`#${folder_id}-folder-name`).popover({
        html: true,
        sanitize: false,
        trigger: "manual",
        content: function () {
            // retorna o html do menu de contexto, que será renderizado quando o evento
            // popover('show') estiver ativo
            return create_context_menu(folder_id);
        }
    })
    .on("mouseenter", function () {
        var _this = this;
        $(this).popover("show");
        $(".popover").on("mouseleave", function () {
            $(_this).popover('hide');
        });
    }).on("mouseleave", function () {
        var _this = this;
        if (!$(".popover:hover").length) {
            $(_this).popover("hide");
        }
    });
}

function enable_edit_mode(context) {
    /* Habilita o modo de edição de uma pasta (permitindo alterar seu nome)

    Argumentos:
        - context: ID da pasta que deverá ser habilitado o modo de edição
    */
    
    $(`#${context}-folder-name`).addClass('d-none');
    $(`#${context}-input`).removeClass('d-none');
    $(`#${context}-input`).focus();
    $(`#${context}-folder-name`).popover('hide');
}

function create_children(parent_id, children_id, folder_name) {
    /* Cria uma subpasta numa pasta pai obtido por meio de seu id `parent_id`

    Argumento:
        - parent_id: ID da pasta pai da subpasta a ser gerada
    */

    // let children_id = services.create_children(parent_id, folder_name)

    let parent_folder = $(`#${parent_id}`);
    let parent_children = $(`#${parent_id}-children`);

    // Objeto onde o menu de contexto aparece, logo após o nome da pasta
    let parent_folder_detail = $(`#${parent_id}-folder-name`);

    if (parent_children.hasClass('d-none'))
        parent_folder_detail.click();

    let parent_depth = parseInt(parent_folder.attr("depth"));

    let new_folder = create_folder(folder_name, children_id, true, parent_depth + 1, []);

    parent_children.append(new_folder);

    
    // fecha o menu de contexto da pasta pai
    parent_folder_detail.popover('hide');

    update_active_folder(children_id);
    enable_edit_mode(children_id);

    attach_context_menu(children_id);

    folders.push({
        data_ultimo_arquivo_adicionado: Date.now(),
        id: children_id,
        nome: folder_name,
    });

    // if (typeof DOC_ID !== 'undefined') {
    //     raw_tree = services.get_folder_tree();
    //     $('#bookmark-move-folder').html(parse_folder_move_tree(raw_tree,'bookmark'));
    //     $('#move-folder').html(parse_folder_move_tree(raw_tree, 'folder'));
    // }
}

function create_children_from_context_menu() {
    $(`#${this.context}-folder-name`).popover('hide');
    services.create_folder(this.context);
}

function create_children_from_active_folder() {
    services.create_folder(active_folder);
}

function enable_edit_mode_from_context_menu() {
    enable_edit_mode(this.context);
}

function update_recently_folders(tree, bookmark_id) {
    console.log(tree);

    for (let i = 0; i < tree.favoritos.length; i++) {
        console.log(bookmark_id, tree.favoritos[i].id);

        if (bookmark_id == tree.favoritos[i].id) 
            bookmark_inside_removed_folder = true;
    }
    
    for (let i = 0; i < tree.subpastas.length; i++)
        update_recently_folders(tree.subpastas[i], bookmark_id);

    let idx = folders.findIndex(pasta => pasta.id === tree.id);
    if (idx >= 0)
        folders.splice(idx, 1);

}

function remove_folder() {
    $('#removeFolderModal').modal('hide');
    $('#folderModal').modal('show');
    
    $(`#${folder_to_remove}`).remove();

    let pasta_pai = folder_tree[folder_to_remove].pasta_pai;
    if (pasta_pai) {
        let idx = folder_tree[pasta_pai].subpastas.findIndex(pasta => pasta.id === folder_to_remove);
        if (idx >= 0)
            folder_tree[pasta_pai].subpastas.splice(idx, 1);
    }

    if (running_in_document_page()) {
        bookmark_inside_removed_folder = false;
        
        update_recently_folders(folder_tree[folder_to_remove], bookmark.id);

        if (bookmark_inside_removed_folder) {
            let bookmark_icon = $('#bookmark-icon');
    
            bookmark_icon.removeClass('fas');
            bookmark_icon.addClass('far');
    
            bookmark.id = null;    
        }
    }

    update_active_folder(pasta_pai);
    services.remove_folder(folder_to_remove)

    let idx = folder_opened_historic.indexOf(folder_to_remove);
    while (idx >= 0) {
        folder_opened_historic.splice(idx, 1);
        idx = folder_opened_historic.indexOf(folder_to_remove);
    }

    // TODO: desabilitar todos os listeners da pasta excluída
}

function create_context_menu_item(icon, name, context, event = null) {
    /* Cria o html de um item no menu de contexto de uma pasta.
    
    Argumentos: 
        - icon: O ícone do item no menu de contexto
        - name: O nome do item no menu de contexto
        - context: ID da pasta onde o menu de contexto está sendo exibido
        - event: Função a ser chamada quando houver um clique neste item no menu de contexto
    
    Retorno:
        Retorna o HTML de uma opção no menu de contexto que aparece sobre uma pasta.

    */

    let li = document.createElement('LI')
    li.style.cursor = 'pointer'
    li.context = context

    let li_icon = document.createElement('I')
    li_icon.className = icon

    let li_text = document.createElement('STRONG')
    li_text.textContent = name
    li_text.className = 'ml-2'

    li.appendChild(li_icon)
    li.appendChild(li_text)

    li.onclick = event

    return li;
}

function create_context_menu(context) {
    /* Método responsável por criar o HTML para o menu de contexto de uma pasta (aquele que ao passar o mouse 
        sob uma pasta e ele aparece)
    Argumentos:
        context: ID da pasta que o menu de contexto será criado

    Retorno:
        Retorna o HTML de uma lista das opções disponíveis para o menu de contexto que aparece sob uma pasta

    */

    // lista base com as opções do menu de contexto de uma pasta
    let ul = document.createElement('UL');
    
    // melhorando o layout da lista
    ul.style.listStyle = 'none'
    ul.className = 'm-0 p-0'
    
    // html da opção de criar nova pasta que aparece no menu de contexto de uma página
    let li_new = create_context_menu_item('fas fa-plus', 'Nova pasta', context, create_children_from_context_menu)
    ul.appendChild(li_new)
        
    // obtendo a identação da pasta que o menu de contexto está aparecendo
    let depth = parseInt($(`#${context}`).attr("depth"));

    // trata-se da pasta base, que só pode criar novas pastas a partir dela
    if (depth == 0)
        return ul

    // html da opção de editar o nome da pasta que aparece no menu de contexto de uma página
    let li_edit = create_context_menu_item('fas fa-pen', 'Editar', context, enable_edit_mode_from_context_menu)
    ul.appendChild(li_edit)

    if (!running_in_document_page()) {
        let li_move = create_context_menu_item('fas fa-folder', 'Mover para', context, show_move_folder_modal);
        ul.appendChild(li_move);
        li_move.className = 'mt-2'
    }

    // html da opção de remover pasta que aparece no menu de contexto de uma página
    let li_remove = create_context_menu_item('fas fa-trash-alt', 'Remover', context, show_remove_folder_modal)
    ul.appendChild(li_remove)

    // melhorias de layout entre as opções do menu de contexto
    li_edit.className = 'mt-2'
    li_remove.className = 'mt-2'

    return ul
}

function update_folder_to_move(folder_id, context) {
    if (move_to_folder)
        $(`#${move_to_folder}-${context}-move-to-name`).removeClass('text-primary');
    move_to_folder = folder_id;
    $(`#${move_to_folder}-${context}-move-to-name`).addClass('text-primary');
}

function create_simple_folder(name, folder_id, opened, depth, context, children = []) {
    let folder = document.createElement('DIV')

    folder.id = `move-to-${folder_id}`
    folder.name = name

    folder.depth = depth
    folder.opened = opened
    folder.className = 'folder d-flex mt-2'
    folder.style.userSelect = 'none';
    folder.setAttribute('depth', depth)

    // Criação da seção responsável por realizar a identação da pasta de acordo com sua pasta pai
    let folder_wrapper = document.createElement('DIV')

    // Identa a pasta de acordo com a pasta pai
    // A pasta filho terá margin esquerda maior que a da pai caso não seja a pasta raiz (profundidade 0)
    folder_wrapper.className = depth > 0 ? 'ml-4' : 'ml-0'

    // Seção que possui as informações básicas da pasta.
    let folder_info = document.createElement('DIV')
    folder_info.className = 'folder-info d-flex align-items-center'
    folder_info.style.cursor = 'pointer'

    // ícone da pasta que varia se ela deverá estar aberta (mostrando subpastas) ou não
    let folder_icon = document.createElement('I')
    folder_icon.className = folder.opened ? 'fas fa-folder-open' : 'fas fa-folder'

    // Cria o nome da pasta
    let folder_name = document.createElement('P')
    folder_name.id = `${folder_id}-${context}-move-to-name`

    folder_name.className = 'my-0 ml-2'

    // adicionando o ícone na pasta
    folder_name.appendChild(folder_icon)

    // Cria o texto com o nome da pasta
    let text = document.createElement('STRONG');
    text.textContent = name;
    text.className = 'mx-2';

    // adicionando o nome da pasta 
    folder_name.appendChild(text);

    // Cria a seção de subpastas dessa pasta
    let folder_children = document.createElement('DIV');
    folder_children.id = `${folder_id}-${context}-move-to-children`;

    // Se a pasta está aberta, devemos mostrar suas subpastas. A presença ou ausência da classe
    // `d-none` define se as subpastas são ou não mostradas
    folder_children.className = folder.opened ? 'children' : 'children d-none';

    // Adicionamos todas subpastas dessa pasta na sua devida seção
    for (let i = 0; i < children.length; i++)
        folder_children.appendChild(children[i]);

    // Criação de seção apenas para manter o layout correto 
    let input_detail_wrapper = document.createElement('DIV');

    // Adiciona do elemento input de texto (que aparece quando o modo edição está ativado) e do 
    // de nome da pasta
    input_detail_wrapper.appendChild(folder_name);

    // Inserção da seção para corrigir layout, que também possui o nome da pasta e o input de texto 
    // do modo edição na seção superior
    folder_info.appendChild(input_detail_wrapper);

    // inserção da seção de informações da pasta e da de subpasta na seção superior
    folder_wrapper.appendChild(folder_info);
    folder_wrapper.appendChild(folder_children);

    // Finalmente, adicionamos a seção com o conteúdo da pasta na seção raiz
    folder.appendChild(folder_wrapper);

    // Criação de um listener que fecha ou abre a pasta, mostrando suas subpastas
    folder_name.onclick = () => update_folder_to_move(folder_id, context);
    
    return folder;
}

function create_folder(name, folder_id, opened, depth, children = []) {
    /* Cria a seguinte estrutura HTML representando uma pasta:

    <div id="[id da pasta]" class="folder d-flex mt-2" depth="[nivel identação da pasta]" style="user-select: none;">
        <div class="ml-4">
            <div class="folder-info d-flex align-items-center" data-toggle="popover" data-container="body" data-placement="right" style="cursor: pointer;">
                // seção necessária para deixar o layout correto
                <div>
                    <input type="text" id="<id_da_past>-input" class="p-0 m-0 border-0 bg-light px-2 font-weight-bold d-none">
                    <p id="[id da pasta]-folder-name" class="my-0 ml-2" data-original-title="" title="">
                        <i class="fas fa-folder[+"-open" se pasta aberta]>"></i>
                        <strong class="mx-2">[nome da pasta]</strong>
                    </p>
                </div>
            </div>
            <div id="[id da pasta]-children" class="children">
            // outras estruturas iguais a essa para as subpastas dessa pasta
            </div>
        </div>
    </div>

    Argumentos:
        - name: Nome da pasta
        - folder_id: ID da pasta
        - opened: Se devemos mostrar as subpastas dessa pasta
        - depth: Determina a profundidade que a pasta está em relação a pasta base/raiz
        - children: Lista de subpastas dessa pasta que será criada

    Retorno:
        Retorna o HTML de uma pasta com tratamento de alguns eventos que ocorrem nela.

    */

    // Cria a seção base com alguns de seus atributos
    let folder = document.createElement('DIV')

    folder.id = folder_id
    folder.name = name

    folder.depth = depth
    folder.opened = opened
    folder.className = 'folder d-flex mt-2'
    folder.style.userSelect = 'none';
    folder.setAttribute('depth', depth)

    // Criação da seção responsável por realizar a identação da pasta de acordo com sua pasta pai
    let folder_wrapper = document.createElement('DIV')

    // Identa a pasta de acordo com a pasta pai
    // A pasta filho terá margin esquerda maior que a da pai caso não seja a pasta raiz (profundidade 0)
    folder_wrapper.className = depth > 0 ? 'ml-4' : 'ml-0'

    // Seção que possui as informações básicas da pasta.
    let folder_info = document.createElement('DIV')
    folder_info.className = 'folder-info d-flex align-items-center'
    folder_info.style.cursor = 'pointer'

    // ícone da pasta que varia se ela deverá estar aberta (mostrando subpastas) ou não
    let folder_icon = document.createElement('I')
    folder_icon.className = folder.opened ? 'fas fa-folder-open' : 'fas fa-folder'

    // Cria o nome da pasta
    let folder_name = document.createElement('P')
    folder_name.id = `${folder_id}-folder-name`

    let unactive_folder_classes = 'my-0 ml-2'
    let active_folder_classes = 'my-0 ml-2 text-primary'

    folder_name.className = unactive_folder_classes

    // adicionando o ícone na pasta
    folder_name.appendChild(folder_icon)

    // Cria o texto com o nome da pasta
    let text = document.createElement('STRONG')
    text.textContent = name
    text.className = 'mx-2'

    // adicionando o nome da pasta 
    folder_name.appendChild(text)

    // cria um input de texto que se tornará visível quando a pasta estiver no modo de edição
    let input = document.createElement('INPUT')
    input.setAttribute('type', 'text')
    input.value = name
    input.id = `${folder_id}-input`

    let disabled_input_classes = 'p-0 m-0 border-0 bg-light px-2 font-weight-bold d-none'
    input.className = disabled_input_classes

    // disabilita o modo de edição da pasta ao esconder o input de texto
    let disable_edit_mode = function () {
        text.textContent = input.value;
        input.className = disabled_input_classes;

        services.rename_folder(folder_id, input.value);

        if (!running_in_document_page()) {
            raw_tree = services.get_folder_tree();
            $('#move-folder').html(parse_folder_move_tree(raw_tree, 'folder'));
            folder_blacklist = [];
            $('#bookmark-move-folder').html(parse_folder_move_tree(raw_tree,'bookmark'));
        }

        let idx = folders.findIndex(pasta => pasta.id === folder_id);
        if (idx >= 0) {
            folders[idx].nome = input.value;
        }
        
        folder_tree[folder_id].nome = input.value;

        if (active_folder == folder_id)
            folder_name.className = active_folder_classes;

        else
            folder_name.className = unactive_folder_classes;
    }

    // Quando clicamos ENTER dentro do input de texto quando a pasta está sendo editada,
    // o modo de edição deve ser desabilidata
    input.addEventListener('keyup', function () {
        // Number 13 is the "Enter" key on the keyboard
        if (event.keyCode === 13) {
            input.blur()
        }
    })

    // Também quando clicamos o input de texto que aparece no modo de edição sai do foco, 
    // é sinal que o modo de edição deve ser desabilitado
    input.addEventListener('blur', disable_edit_mode)

    // Cria a seção de subpastas dessa pasta
    let folder_children = document.createElement('DIV')
    folder_children.id = `${folder_id}-children`

    // Se a pasta está aberta, devemos mostrar suas subpastas. A presença ou ausência da classe
    // `d-none` define se as subpastas são ou não mostradas
    folder_children.className = folder.opened ? 'children' : 'children d-none'

    // Adicionamos todas subpastas dessa pasta na sua devida seção
    for (let i = 0; i < children.length; i++)
        folder_children.appendChild(children[i])

    // Criação de seção apenas para manter o layout correto 
    let input_detail_wrapper = document.createElement('DIV')

    // Adiciona do elemento input de texto (que aparece quando o modo edição está ativado) e do 
    // de nome da pasta
    input_detail_wrapper.appendChild(input)
    input_detail_wrapper.appendChild(folder_name)

    // Inserção da seção para corrigir layout, que também possui o nome da pasta e o input de texto 
    // do modo edição na seção superior
    folder_info.appendChild(input_detail_wrapper)

    // inserção da seção de informações da pasta e da de subpasta na seção superior
    folder_wrapper.appendChild(folder_info)
    folder_wrapper.appendChild(folder_children)

    // Finalmente, adicionamos a seção com o conteúdo da pasta na seção raiz
    folder.appendChild(folder_wrapper)

    // Criação de um listener que fecha ou abre a pasta, mostrando suas subpastas
    folder_name.onclick = function () {
        folder.opened = !folder.opened;

        if (running_in_document_page()) {
            folder_children.className = folder.opened ? 'children' : 'children d-none'
            folder_icon.className = folder.opened ? 'fas fa-folder-open' : 'fas fa-folder'
        }

        update_active_folder(folder_id)
    }

    // Definição de atributos para o funcionamento do popover (menus de contexto que aparecem ao 
    // passar o mouse em cima da pasta)
    folder_info.setAttribute('data-toggle', 'popover')
    folder_info.setAttribute('data-container', 'body')
    folder_info.setAttribute('data-placement', 'right')

    return folder;
}

function parse_folder_tree(tree, depth = 0) {
    /** Transforma o JSON com árvore de pastas em HTML
     * 
     * Argumentos:
     *  - tree: JSON com a árvore de pastas. Possui a seguinte estrutura
     *      {
     *          nome:
     *          id
     *          
     *       }
     * 
     * Retorno:
     *  Retorna o HTML representando a árvore de pastas do JSON passado
     */
    let subpastas_processadas = []

    for (let i = 0; i < tree.subpastas.length; i++)
        subpastas_processadas.push(parse_folder_tree(tree.subpastas[i], depth + 1))


    return create_folder(tree.nome, tree.id, true, depth, subpastas_processadas)
}

function parse_folder_move_tree(tree, context, depth = 0) {
    let subpastas_processadas = [];
    
    for (let i = 0; i < tree.subpastas.length; i++)
        if (!folder_blacklist.includes(tree.subpastas[i].id))
            subpastas_processadas.push(parse_folder_move_tree(tree.subpastas[i], context, depth + 1));

    return create_simple_folder(tree.nome, tree.id, true, depth, context, subpastas_processadas);
}

function update_folder_move_tree() {
    $('#move-folder').html(parse_folder_move_tree(raw_tree, 'folder'));
}

function folder_comparator(a, b) {
    return b.data_ultimo_arquivo_adicionado - a.data_ultimo_arquivo_adicionado;
}

function update_recently_folder_dropdown(folders) {
    let lis = [];
    folders.sort(folder_comparator);
    for (let i = 0; i < Math.min(folders.length, MAX_FOLDERS_IN_DROPDOWN);i++) {
        folder = folders[i];
        lis.push(`<option id="folder-option-${folder.id}" value="${folder.id}">${folder.nome}</option>`)
    }

    return lis;
    // $('#selectFolder').html(lis);
}

function bulk_move() {
    bulk = true;

    let cb_folders = $('.folder-ckeckbox');
    for (let i = 0; i < cb_folders.length;i++)
        if (cb_folders[i].checked) 
            folders_to_move.push(cb_folders[i].value);

    let cb_bookmarks = $('.bookmark-ckeckbox');
    for (let i = 0; i < cb_bookmarks.length;i++)
        if (cb_bookmarks[i].checked) 
            bookmarks_to_move.push(cb_bookmarks[i].value);

    folder_blacklist = folders_to_move;
    update_folder_move_tree();
    
    $('#moveFolderModal').modal('show');

}

function bulk_remove() {
    bulk = true;

    let cb_bookmarks = $('.bookmark-ckeckbox');
    for (let i = 0; i < cb_bookmarks.length;i++) 
        if (cb_bookmarks[i].checked) 
            services.remove_bookmark(cb_bookmarks[i].value);

    let cb_folders = $('.folder-ckeckbox');
    for (let i = 0; i < cb_folders.length;i++)
        if (cb_folders[i].checked)
            services.remove_folder(cb_folders[i].value);

    location.reload();
}

function listify_tree(tree, list) {
    for (let i = 0; i < tree.subpastas.length; i++)
        listify_tree(tree.subpastas[i], list);
    
    if (tree.data_ultimo_arquivo_adicionado == null)
        tree.data_ultimo_arquivo_adicionado = 0;
    
    list.push(tree);
}

function enable_context_menu_event(tree) {
    attach_context_menu(tree.id)
    for (let i = 0; i < tree.subpastas.length; i++)
        enable_context_menu_event(tree.subpastas[i])
}

function save_or_update_bookmark_by_detailed_folder() {
    $('#folderModal').modal('hide');
    bookmark.folder = active_folder;
    bookmark.name = $('#inputName').val();
    services.create_bookmark();
}

function get_folder_modal_html(doc_title) {
    return `<div class="modal fade" id="folderModal" tabindex="-1" aria-labelledby="folderModalLabel" aria-hidden="true">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title font-weight-bold" id="folderModalLabel">Editar favorito</h5>
                            <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                                <span aria-hidden="true">&times;</span>
                            </button>
                        </div>
                        <div class="modal-body">
                            <div class="form-group">
                                <label for="inputName" class="">Nome</label>
                                <div>
                                    <input type="texto" class="form-control" id="inputName" placeholder="Nome" value="${doc_title}">
                                </div>
                            </div>
                            <label for="">Pasta</label>
                            <div class="bg-light rounded border px-3 pt-1 pb-3 font-weight-bold" id="bookmark-folder" style="min-height: 180px;">
                            </div>
                        </div>
                        <div class="modal-footer d-flex justify-content-between">
                            <div class="">
                                <button type="button" class="btn btn-secondary" onclick="create_children_from_active_folder()">Nova pasta</button>
                            </div>
                            <div class="">
                                <button type="button" class="btn btn-secondary" data-dismiss="modal">Cancelar</button>
                                <button type="button" class="btn btn-primary" onclick="save_or_update_bookmark_by_detailed_folder()">Salvar</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>`
}

function get_remove_folder_modal_html() {
    return `<div class="modal fade" id="removeFolderModal" tabindex="-1" aria-labelledby="removeFolderModalLabel" aria-hidden="true">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title font-weight-bold" id="removeFolderModalLabel">Tem certeza que deseja deseja excluir a pasta com todo seu conteúdo?</h5>
                        </div>
                        <div class="modal-body d-flex justify-content-between">
                            <div class="">
                                <button type="button" class="btn btn-secondary" data-dismiss="modal">Cancelar</button>
                            </div>
                            <div class="">
                                <button type="button" class="btn btn-danger" onclick="remove_folder()">Excluir</button>
                            </div>
                        </div>
                        <!-- <div class="modal-footer d-flex justify-content-between">
                        </div> -->
                    </div>
                </div>
            </div>`
}

function create_folder_modals() {
    // adiciona os modais ao corpo da página
    let remove_folder_modal_html = get_remove_folder_modal_html();
    let modals = $('.modals');
    
    // Se há uma seção para adição de bookmarks, significa que estamos em uma página de 
    // visualização de docuemtnos, então criamos um modal para lidar com as pastas 
    if ($('.bookmark').length > 0) {
        let folder_modal_html = get_folder_modal_html(bookmark.name);
        modals.append(folder_modal_html);
    }
    
    modals.append(remove_folder_modal_html);
}

$(document).ready(function () {
    services.get_bookmark_folder_tree()
    create_folder_modals()

    // // let tree = services.retrieve_folders()
    // tree = { "name": "Favoritos de Elves", "id": 123, "children": [{ "name": "Processos", "id": 797, "children": [{ "name": "Estaduais", "id": 63, "children": [{ "name": "Minas Gerais", "id": 630, "children": [{ "name": "Municípios", "id": 6340, "children": [] }] }] }, { "name": "Federais", "id": 31, "children": [] }] }, { "name": "Diários", "id": 89, "created_at": "Apr. 2012", "children": [] }] }

    // Inserindo após converter o json com estrutura de pastas do usuário em HTML
    $('#bookmark-folder').append(parse_folder_tree(tree))

    // Habilita o evento de menu de contexto
    enable_context_menu_event(tree)

    // define que o pasta raiz é a pasta ativa, por default
    update_active_folder(tree.id)
});