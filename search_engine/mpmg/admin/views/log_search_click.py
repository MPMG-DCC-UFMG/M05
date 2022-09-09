from django.contrib import admin
from django.shortcuts import render
from mpmg.services.models import LogSearchClick

class LogSearchClickView(admin.AdminSite):

    def __init__(self):
        self.results_per_page = 10
        super(LogSearchClickView, self).__init__()
    
    def view_log_click(self, request):
        results_per_page = int(request.GET.get('results_per_page', self.results_per_page))
        id_documento = request.GET.get('id_documento', '')
        tipo_documento = request.GET.get('tipo_documento', '')
        id_consulta = request.GET.get('id_consulta', '')
        start_date = request.GET.get('start_date', '')
        end_date = request.GET.get('end_date', '')
        pagina_op = request.GET.get('pagina_op')
        pagina = request.GET.get('pagina', '')
        posicao_op = request.GET.get('posicao_op')
        posicao = request.GET.get('posicao', '')
        page = int(request.GET.get('page', 1))
        self.results_per_page = results_per_page

        LogSearchClick.results_per_page = self.results_per_page
        total_records, log_clicks_list = LogSearchClick.get_list_filtered(
            api_client_name=request.user.api_client_name,
            id_documento=id_documento,
            tipo_documento=tipo_documento,
            id_consulta=id_consulta,
            start_date=start_date,
            end_date=end_date,
            pagina_op=pagina_op,
            pagina=pagina,
            posicao_op=posicao_op,
            posicao=posicao,
            page=page,
            sort={'data_criacao':{'order':'desc'}}
        )

        total_pages = (total_records // self.results_per_page) + 1

        url_params = "&id_documento=%s&tipoo_documento=%s&id_consulta=%s"\
                     "&start_date=%s&end_date=%s&pagina_op=%s&pagina=%s"\
                     "&posicao_op=%s&posicao=%s"\
                     % (id_documento, tipo_documento, id_consulta,\
                        start_date, end_date, pagina_op, pagina,\
                        posicao_op, posicao)

        context = dict(
            self.each_context(request), # admin template variables.
            id_documento=id_documento,
            tipo_documento=tipo_documento,
            id_consulta=id_consulta,
            start_date=start_date,
            end_date=end_date,
            pagina_op=pagina_op,
            pagina=pagina,
            posicao_op=posicao_op,
            posicao=posicao,
            result_list=log_clicks_list,
            page=page,
            total_records=total_records,
            results_per_page=self.results_per_page,
            total_pages=total_pages,
            pagination_items=range(min(9, total_pages)),
            url_params=url_params,
        )
        
        return render(request, 'admin/log_search_click.html', context)
