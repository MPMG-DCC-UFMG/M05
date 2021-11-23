// Contém o código responsável por gerar as visualização das pastas de bookmarks

var active_folder = null;
var folder_to_remove = null;
var MAX_FOLDERS_IN_DROPDOWN = 5;

function update_active_folder(new_active_folder) {
    /** Atualiza a informação de qual pasta está correntemente ativa
     *
     * Argumentos:
     *  -  new_active_folder: ID da nova pasta que será ativa 
     */

    if (active_folder)
        $(`#${active_folder}-folder-name`).removeClass('text-primary')

    active_folder = new_active_folder;

    $(`#${active_folder}-folder-name`).addClass('text-primary')
}

function create_children_from_active_folder() {
    create_children(active_folder)
}

function show_remove_folder_modal() {
    folder_to_remove = this.context

    $('#folderModal').modal('hide')
    $('#removeFolderModal').modal('show')
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

function randomIntFromInterval(min, max) { // min and max included 
    return Math.floor(Math.random() * (max - min + 1) + min)
}

function create_children(parent_id, children_id, folder_name) {
    /* Cria uma subpasta numa pasta pai obtido por meio de seu id `parent_id`

    Argumento:
        - parent_id: ID da pasta pai da subpasta a ser gerada
    */

    // let children_id = services.create_children(parent_id, folder_name)

    let parent_folder = $(`#${parent_id}`);
    let parent_children = $(`#${parent_id}-children`)

    // Objeto onde o menu de contexto aparece, logo após o nome da pasta
    let parent_folder_detail = $(`#${parent_id}-folder-name`)

    if (parent_children.hasClass('d-none'))
        parent_folder_detail.click()

    let parent_depth = parseInt(parent_folder.attr("depth"));

    let new_folder = create_folder(folder_name, children_id, true, parent_depth + 1, []);

    parent_children.append(new_folder);

    
    // fecha o menu de contexto da pasta pai
    parent_folder_detail.popover('hide');

    update_active_folder(children_id)
    enable_edit_mode(children_id)

    attach_context_menu(children_id)
}

function create_children_from_context_menu() {
    $(`#${this.context}-folder-name`).popover('hide');
    services.create_folder(this.context)
}

function create_children_from_active_folder() {
    services.create_folder(active_folder)
}

function enable_edit_mode_from_context_menu() {
    enable_edit_mode(this.context)
}

function remove_folder(decision) {
    $('#removeFolderModal').modal('hide')
    $('#folderModal').modal('show')

    $(`#${folder_to_remove}`).remove()

    services.remove_folder(folder_to_remove, decision)

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

    // html da opção de remover pasta que aparece no menu de contexto de uma página
    let li_remove = create_context_menu_item('fas fa-trash-alt', 'Remover', context, show_remove_folder_modal)
    ul.appendChild(li_remove)

    // melhorias de layout entre as opções do menu de contexto
    li_edit.className = 'mt-2'
    li_remove.className = 'mt-2'

    return ul
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
        text.textContent = input.value
        input.className = disabled_input_classes

        services.rename_folder(folder_id, input.value)
        rename_recently_folder_dropdown_option(folder_id, input.value);

        if (active_folder == folder_id)
            folder_name.className = active_folder_classes

        else
            folder_name.className = unactive_folder_classes
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
        folder_children.className = folder.opened ? 'children' : 'children d-none'
        folder_icon.className = folder.opened ? 'fas fa-folder-open' : 'fas fa-folder'

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

    $('#selectFolder').html(lis);
}

function add_new_folder_to_dropdown(folder_id, name) {
    if ($('#selectFolder > option').length < MAX_FOLDERS_IN_DROPDOWN) {
        let li = `<option id="folder-option-${folder_id}" value="${folder_id}">${name}</option>`;
        $('#selectFolder').append(li);
    }
}

function rename_recently_folder_dropdown_option(folder_id, new_name) {
    $(`#folder-option-${folder_id}`).text(new_name);
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
                            <h5 class="modal-title font-weight-bold" id="removeFolderModalLabel">O que deseja fazer com os favoritos dessa pasta?</h5>
                        </div>
                        <div class="modal-body d-flex justify-content-between">
                            <div class="">
                                <button type="button" class="btn btn-secondary" data-dismiss="modal">Cancelar</button>
                            </div>
                            <div class="">
                                <button type="button" class="btn btn-primary" onclick="remove_folder('keep')">Mover todos para pasta acima</button>
                                <button type="button" class="btn btn-danger" onclick="remove_folder('remove_all')">Excluir todos</button>
                            </div>
                        </div>
                        <!-- <div class="modal-footer d-flex justify-content-between">
                        </div> -->
                    </div>
                </div>
            </div>`
}

function create_folder_modals() {
    let folder_modal_html = get_folder_modal_html(DOC_TITLE)
    let remove_folder_modal_html = get_remove_folder_modal_html()

    let modals = $('.modals')

    // adiciona os modais ao corpo da página
    
    // Se há uma seção para adição de bookmarks, significa que estamos em uma página de 
    // visualização de docuemtnos, então criamos um modal para lidar com as pastas 
    if ($('.bookmark').length > 0)
        modals.append(folder_modal_html)
    
    modals.append(remove_folder_modal_html)
}

$(document).ready(function () {
    create_folder_modals()
    services.get_bookmark_folder_tree()

    // // let tree = services.retrieve_folders()
    // tree = { "name": "Favoritos de Elves", "id": 123, "children": [{ "name": "Processos", "id": 797, "children": [{ "name": "Estaduais", "id": 63, "children": [{ "name": "Minas Gerais", "id": 630, "children": [{ "name": "Municípios", "id": 6340, "children": [] }] }] }, { "name": "Federais", "id": 31, "children": [] }] }, { "name": "Diários", "id": 89, "created_at": "Apr. 2012", "children": [] }] }

    // // Inserindo após converter o json com estrutura de pastas do usuário em HTML
    // $('#bookmark-folder').append(parse_folder_tree(tree))

    // // Habilita o evento de menu de contexto
    // enable_context_menu_event(tree)

    // // define que o pasta raiz é a pasta ativa, por default
    // update_active_folder(tree.id)
});