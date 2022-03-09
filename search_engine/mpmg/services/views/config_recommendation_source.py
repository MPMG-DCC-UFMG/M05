from os import stat
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from mpmg.services.models import ConfigRecommendationSource

from ..docstring_schema import AutoDocstringSchema

class ConfigRecommendationSourceView(APIView):
    # schema = AutoDocstringSchema()

    def get(self, request):
        source_id = request.GET.get('source_id')
        index_name = request.GET.get('index_name')

        conf_rec_source = ConfigRecommendationSource()

        if source_id or index_name:
            source, msg_error = conf_rec_source.get(source_id, index_name)

            if source is None:
                return Response({'message': msg_error}, status=status.HTTP_404_NOT_FOUND)

            return Response(source, status=status.HTTP_200_OK)

        active = request.GET.get('active')
        if active is not None:
            if active == 'false':
                active = False
        
            elif active == 'true':
                active = True
        
            else:
                active = False

        
        sources, _ = conf_rec_source.get(active=active)
        return Response(sources, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.POST if len(request.POST) > 0 else request.data

        try:
            source_repr = dict(
                ui_name = data['ui_name'],
                es_index_name = data['es_index_name'],
                amount = data['amount'],
                active = data['active'],
            )
        except:
            return Response({'message': 'Informe todos os campos corretamente!'}, status=status.HTTP_400_BAD_REQUEST)

        conf_rec_source = ConfigRecommendationSource()
        source_id, msg_error = conf_rec_source.save(source_repr)

        if source_id:
            return Response({'source_id': source_id}, status=status.HTTP_201_CREATED)

        return Response({'message': msg_error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

    def put(self, request):
        data = request.data
        if type(data) is not dict:
            data = data.dict()
        
        conf_rec_source = ConfigRecommendationSource()

        error = dict()
        all_successfull = True
        for index_name in data:
            config = data[index_name]
            success, msg_error = conf_rec_source.update(config, index_name=index_name)

            if not success:
                all_successfull = False

            error[index_name] = {
                'success': success,
                'message': msg_error 
            }

        if all_successfull:
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(error, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request):
        data = request.data
        if type(data) is not dict:
            data = data.dict()

        source_id = data.get('source_id')
        index_name = data.get('index_name')

        conf_rec_source = ConfigRecommendationSource()

        if source_id or index_name:
            source, msg_error = conf_rec_source.get(source_id, index_name)
            if source is None:
                return Response({'message': 'Item não encontrado para ser removido!'}, status=status.HTTP_404_NOT_FOUND)

            success, msg_error = conf_rec_source.delete(source_id, index_name)
            if success:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'message': msg_error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'É necessário informar "source_id" ou "index_name"!'}, status=status.HTTP_400_BAD_REQUEST)