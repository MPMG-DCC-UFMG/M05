
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from mpmg.services.models import ConfigRecommendationEvidence

from ..docstring_schema import AutoDocstringSchema

class ConfigRecommendationEvidenceView(APIView):
    # schema = AutoDocstringSchema()

    def get(self, request):
        evidence_id = request.GET.get('evidence_id')
        evidence_type = request.GET.get('evidence_type')

        conf_rec_ev = ConfigRecommendationEvidence()

        if evidence_id or evidence_type:
            evidence, msg_error = conf_rec_ev.get(evidence_id, evidence_type)
            if evidence is None:
                return Response({'message': msg_error}, status=status.HTTP_404_NOT_FOUND)
            
            return Response(evidence, status=status.HTTP_200_OK)
        
        active = request.GET.get('active')
        if active is not None:
            if active == 'false':
                active = False
        
            elif active == 'true':
                active = True
        
            else:
                active = False
        
        evidences, _ = conf_rec_ev.get(active=active)

        return Response(evidences, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.POST if len(request.POST) > 0 else request.data
        
        try:
            ev_repr = dict(
                ui_name = data['ui_name'],
                evidence_type = data['evidence_type'],
                es_index_name = data['es_index_name'],
                amount = data['amount'],
                min_similarity = data['min_similarity'],
                top_n_recommendations = data['top_n_recommendations'],
                active = data['active'],
            )
        except:
            return Response({'message': 'Informe todos os campos corretamente!'}, status=status.HTTP_400_BAD_REQUEST)

        
        conf_rec_ev = ConfigRecommendationEvidence()
        evidence_id, msg_error = conf_rec_ev.save(ev_repr)

        if evidence_id:
            return Response({'evidence_id': evidence_id}, status=status.HTTP_201_CREATED)

        return Response({'message': msg_error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def put(self, request):
        data = request.data
        if type(data) is not dict:
            data = data.dict()
        
        conf_rec_ev = ConfigRecommendationEvidence()

        error = dict()
        all_successfull = True
        for evidence_type in data:
            config = data[evidence_type]
            success, msg_error = conf_rec_ev.update(config, evidence_type=evidence_type)

            if not success:
                all_successfull = False 

            error[evidence_type] = {
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

        evidence_id = data.get('evidence_id')
        evidence_type = data.get('evidence_type')

        conf_rec_ev = ConfigRecommendationEvidence()
        if evidence_id or evidence_type:
            evidence, msg_error = conf_rec_ev.get(evidence_id, evidence_type)
            if evidence is None:
                return Response({'message': 'Item não encontrado para ser removido!'}, status=status.HTTP_404_NOT_FOUND)

            success, msg_error = conf_rec_ev.delete(evidence_id, evidence_type)
            if success:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'message': msg_error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'É necessário informar "evidence_id" ou "evidence_type"!'}, status=status.HTTP_400_BAD_REQUEST)