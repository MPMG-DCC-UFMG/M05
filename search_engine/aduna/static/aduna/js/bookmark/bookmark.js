// Contém o código responsável por gerenciar os bookmarks

var bookmark = {};

bookmark.folder = null;
bookmark.id = null;
bookmark.name = DOC_TITLE;

function save_or_update_bookmark_by_dropdown() {
    bookmark.folder = $('.popover select').val();
    bookmark.name = $('.popover #inputName').val();

    $('#inputName').val(bookmark.name);

    update_active_folder(bookmark.folder);

    $('#bookmark-popover').popover('toggle');
    services.create_bookmark();
}


function get_bookmark_html() {
    /** Cria o html que contém o menu de contexto e o icone do bookmark que fica na página
     * 
     */
    let lis = update_recently_folder_dropdown(folders);

    return `<h3 class="h6 font-weight-bold">Editar favorito</h3>
            <div>
                <div class="form-group">
                    <label for="inputName" class="">Nome</label>
                    <div>
                        <input type="texto" class="form-control" id="inputName" placeholder="Nome" value="${bookmark.name}">
                    </div>
                </div>
                <div class="form-group">
                    <label for="selectFolder">Pasta</label>
                    <select class="custom-select" id="selectFolder">
                    ${lis}
                    </select>
                </div>
                <div class="form-group">
                    <button class="btn btn-secondary" data-toggle="modal" data-target="#folderModal">Mais...</button>
                    <button class="btn btn-secondary" onclick="services.remove_bookmark(bookmark.id)">Remover</button>
                    <button class="btn btn-success" onclick="save_or_update_bookmark_by_dropdown()">Salvar</button>
                </div>
            </div>`;
}

function inject_bookmark() {
    // Injeta o HTML do bookmark na página
    $('.bookmark').append(`<div id="bookmark-popover" data-toggle="popover" data-container="body" data-toggle="popover" data-placement="right">
                                <div id="bookmark-toggle-wrapper">
                                </div>
                            </div>`);

    // Cria o evendo que aparece o menu de contexto para edição do bookmark quando 
    // o mouse passa em cima dele
    $('#bookmark-popover').popover({
        html: true,
        sanitize: false,
        trigger: "manual",
        content: function () {
            return get_bookmark_html();
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
        setTimeout(function () {
            if (!$(".popover:hover").length) {
                $(_this).popover("hide");
            }
        }, 300);
    });
}

function create_bookmark_toggle(active) {
    // Cria o icone de bookmark com lógica para manipulá-lo
    let el_bookmark = document.createElement('BUTTON');
    el_bookmark.className = 'btn p-0';
    el_bookmark.active = active;
    el_bookmark.id = 'bookmark-button';

    let icon = document.createElement('I');
    icon.id = 'bookmark-icon';
    icon.className = active ? 'fas fa-star fa-lg' : 'far fa-star fa-lg';

    el_bookmark.appendChild(icon);

    el_bookmark.onclick = function () {
        $('#bookmark-popover').popover('toggle');
        el_bookmark.active = bookmark.id == null ? true : false;

        if (el_bookmark.active)
            services.create_bookmark();
            
        else 
            services.remove_bookmark(bookmark.id);

    }

    return el_bookmark;
}

$(document).ready(function () {
    services.start_bookmark(DOC_TYPE, DOC_ID);
});