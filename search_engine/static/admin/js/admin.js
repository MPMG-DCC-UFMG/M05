( function( factory ) {
	if ( typeof define === "function" && define.amd ) {

		// AMD. Register as an anonymous module.
		define( [ "../widgets/datepicker" ], factory );
	} else {

		// Browser globals
		factory( jQuery.datepicker );
	}
}( function( datepicker ) {

datepicker.regional[ "pt-BR" ] = {
	closeText: "Fechar",
	prevText: "&#x3C;Anterior",
	nextText: "Próximo&#x3E;",
	currentText: "Hoje",
	monthNames: [ "Janeiro","Fevereiro","Março","Abril","Maio","Junho",
	"Julho","Agosto","Setembro","Outubro","Novembro","Dezembro" ],
	monthNamesShort: [ "Jan","Fev","Mar","Abr","Mai","Jun",
	"Jul","Ago","Set","Out","Nov","Dez" ],
	dayNames: [
		"Domingo",
		"Segunda-feira",
		"Terça-feira",
		"Quarta-feira",
		"Quinta-feira",
		"Sexta-feira",
		"Sábado"
	],
	dayNamesShort: [ "Dom","Seg","Ter","Qua","Qui","Sex","Sáb" ],
	dayNamesMin: [ "Dom","Seg","Ter","Qua","Qui","Sex","Sáb" ],
	weekHeader: "Sm",
	dateFormat: "dd/mm/yy",
	firstDay: 0,
	isRTL: false,
	showMonthAfterYear: false,
	yearSuffix: "" };
datepicker.setDefaults( datepicker.regional[ "pt-BR" ] );

return datepicker.regional[ "pt-BR" ];

} ) );

$(function(){
    
    $('.datepicker').datepicker();
	$('[data-toggle="tooltip"]').tooltip({boundary:"viewport"});
	
	$('.results-per-page').change(function(){
		var targetForm = $(this).data('target-form');
		var selectedValue = $(this).val();
		$('#'+targetForm).find('input[name=results_per_page]').val(selectedValue);
		$('#'+targetForm).submit();
	});

	$('.clear-form').click(function(){
		var formObj = $(this).parents('form');
		formObj.find('input,select').each(function(i){
			if($(this).attr('data-no-reset') == undefined){
				if($(this).prop("tagName") == "INPUT")
					$(this).val("")
				else if($(this).prop("tagName") == "SELECT")
					$(this)[0].selectedIndex = 0;
			}
		});
	});

	$('#log-search-table tr').click(function(){
		var id_sessao = $(this).data('id-sessao');
		$('.detalhe-consultas').html('')
		var ajax = $.get('/admin/log_search_detail/?id_sessao='+id_sessao)
		ajax.done(function(response){
			response = response['session_detail'];
			$('.detalhe-id-sessao').html(id_sessao);
			$('.detalhe-nome-usuario').html(response['nome_usuario']);

			var num_consulta = 0;
			for(var id_consulta in response['consultas']){
				// pega o template para consultas e preenche com os dados
				var template_consulta = $($("#detalhe-template-consulta .detalhe-item-consulta").get(0).outerHTML);
				template_consulta.find('.detalhe-id-consulta').html(id_consulta);
				template_consulta.find('.detalhe-texto-consulta').html(response['consultas'][id_consulta]['text_consulta']);
				template_consulta.find('.detalhe-algoritmo').html(response['consultas'][id_consulta]['algoritmo']);

				// o template da consulta já tem uma página de resultados, se precisar de mais páginas, faz um clone
				for(var num_pagina in response['consultas'][id_consulta]['paginas']){
					if(num_pagina == 1){
						var tab = template_consulta.find('.nav-tabs').children().first();
						var tab_content = template_consulta.find('.tab-content').children().first();
					}
					else{
						var tab = template_consulta.find('.nav-tabs').children().first().clone();
						tab.removeClass('active');
						template_consulta.find('.nav-tabs').append(tab);
						
						var tab_content = template_consulta.find('.tab-content').children().first().clone();
						tab_content.removeClass('show active')
						template_consulta.find('.tab-content').append(tab_content)
					}

					// popula a aba com info dos resultados da consulta
					tab.find('.detalhe-numero-pagina').html(num_pagina);
					tab.attr('href', '#c-'+num_consulta+'-p-'+num_pagina)
					tab_content.attr('id', 'c-'+num_consulta+'-p-'+num_pagina)
					tab_content.find('.detalhe-data-hora').html(response['consultas'][id_consulta]['paginas'][num_pagina]['data_criacao']);
					tab_content.find('.detalhe-tempo-resposta').html(response['consultas'][id_consulta]['paginas'][num_pagina]['tempo_resposta_total']);
					tab_content.find('.detalhe-documentos tbody').html('');
					// lista de resultados com info de cliques
					for(var i=0; i<response['consultas'][id_consulta]['paginas'][num_pagina]['documentos'].length; i++){
						var num  = (i+1) + (num_pagina-1) * parseInt(response['consultas'][id_consulta]['resultados_por_pagina']);
						var doc_type = response['consultas'][id_consulta]['paginas'][num_pagina]['tipos'][i];
						var doc_id = response['consultas'][id_consulta]['paginas'][num_pagina]['documentos'][i];
						var clicked = response['consultas'][id_consulta]['paginas'][num_pagina]['cliques'][i];
						var link = '/aduna/document/'+doc_type+'/'+doc_id;
						tab_content.find('.detalhe-documentos tbody').append(
							'<tr><td align="center">'+num+'</td>'+
							'<td>'+doc_type+'</td>'+
							'<td>'+doc_id+'</td>'+
							'<td align="center">'+clicked+'</td>'+
							'<td align="center"><a href="'+link+'" target="blank"><i class="fas fa-external-link-alt"></i></a></td>'+
							'</tr>');
					}


				}
				num_consulta++;
				$('.detalhe-consultas').append(template_consulta);
				$('.detalhe-consultas').append("<br>");
			}
		});
		
		ajax.fail(function(){
			console.log('falha');
		});

		$('#log-search-detail').modal();
	});
});
	
function get_algo_options(prefix){
	console.log(prefix);
	console.log('#' + prefix + '-algorithm');
	var selected_algo = $('#' + prefix + '-algorithm').val().toLowerCase();
	$( '#' + prefix + '-algorithm' ).children('option').each(function( index ) {
		var algo = $( this ).val().toLowerCase();
		var elements_by_class = $('.' + algo);
		$.each(elements_by_class, function() {
			var cur_id = $( this ).attr('id');
			if (algo == selected_algo) { // Mostrar opções
				$('#' + cur_id).show();
				$('#' + cur_id)[0].disabled = false;
				$( "label[for='" + cur_id + "']").show();
				if (($('#' + prefix + '-normalization_' + algo).val()) == 'no') {
					$('#' + prefix + '-normalization_parameter_' + algo)[0].disabled = true;
					$('#' + prefix + '-normalization_parameter_' + algo).hide();
					$("label[for='" + prefix + "-normalization_parameter_" + algo + "']").hide();
				}
			}
			else { // Esconder opções
				$('#' + cur_id)[0].disabled = true;
				$('#' + cur_id).hide();
				$( "label[for='" + cur_id + "']").hide();
				
			}
		});
	});
};

$(function(){
	$('[id$=-algorithm], [id$=-normalization_ib], [id$=-normalization_dfr]').change(function(event){
		var prefix = event.target.id.split('-')[0]
		console.log(prefix)
		get_algo_options(prefix);
	});
});

$(document).ready(function() {
	$("#regular_btn").click(function(event) {
	  $("#regular_form").toggle();
	  if($("#replica_form").is(":visible")){
		$("#replica_form").toggle();	
	  }
	  var prefix = event.target.id.split('_')[0];
	  get_algo_options('id_' + prefix);
	});
});

$(document).ready(function() {
	$("#replica_btn").click(function(event) {
	  $("#replica_form").toggle();
	  if($("#regular_form").is(":visible")){
	    $("#regular_form").toggle();	
	  }
	  var prefix = event.target.id.split('_')[0]
	  get_algo_options('id_' + prefix);
	});
});