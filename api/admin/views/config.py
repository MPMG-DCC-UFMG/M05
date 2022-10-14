from django.contrib import admin
from django.urls import reverse
from django.shortcuts import render, redirect
from admin.forms import ConfigForm
from services.elastic import Elastic

class ConfigView(admin.AdminSite):

    def __init__(self):
        super(ConfigView, self).__init__()
        self.es = Elastic()

    def get_default_options(self, group='regular'):
        sim_settings = self.es.get_cur_algo(group=group) #TODO: acertar isso para obter da interface
        current_num_repl = self.es.get_cur_replicas()
        max_result_window = self.es.get_max_result_window()
        algo = sim_settings['type']
        initial = {'algorithm': algo, 
                   'num_repl': current_num_repl,
                   'max_result_window': max_result_window,}

        # Settings específicos por algoritmo
        if algo == 'BM25':
            initial['k1'] = sim_settings['k1']
            initial['b'] = sim_settings['b']
            initial['discount_overlaps'] = sim_settings['discount_overlaps']
        elif algo == 'DFR':
            initial['basic_model'] = sim_settings['basic_model']
            initial['after_effect'] = sim_settings['after_effect']
            normalization = sim_settings['normalization']
            initial['normalization_dfr'] = normalization
            # O nome do parâmetro muda a depender da normalização, assim conseguimos pegar independente do nome
            # Só o parâmetro de normalização é representado com dict
            if normalization != 'no':
                normalization_parameter = [x for x in sim_settings.values() if type(x) == dict][0] 
                initial['normalization_parameter_dfr'] = list(normalization_parameter.values())[0] 
        elif algo == 'DFI':
            initial['independence_measure'] = sim_settings['independence_measure']
        elif algo == 'IB':
            initial['distribution'] = sim_settings['distribution']
            initial['lambda_ib'] = sim_settings['lambda']
            normalization = sim_settings['normalization']
            initial['normalization_ib'] = normalization
            # O nome do parâmetro muda a depender da normalização, assim conseguimos pegar independente do nome
            # Só o parâmetro de normalização é representado com dict
            if normalization != 'no':
                normalization_parameter = [x for x in sim_settings.values() if type(x) == dict][0] 
                initial['normalization_parameter_ib'] = list(normalization_parameter.values())[0] 
        elif algo == 'LMDirichlet':
            initial['mu'] = sim_settings['mu']
        elif algo == 'LMJelinek':
            initial['lambda_jelinek'] = sim_settings['lambda']

        return initial

    def view_config(self, request):
        initial_regular = self.get_default_options(group='regular')
        initial_replica = self.get_default_options(group='replica')

        form_regular = ConfigForm(initial=initial_regular, prefix='regular')
        form_replica = ConfigForm(initial=initial_replica, prefix='replica')

        context = dict(
            self.each_context(request), # Include common variables for rendering the admin template.
            form_regular = form_regular,
            form_replica = form_replica,
        )
        
        return render(request, 'admin/config.html', context)

    def view_save_config(self, request):
        # Remove prefix (regular/replica) from the request 
        params_dict = {}
        for k, v in request.POST.dict().items():
            if (k.find('regular') != -1 or k.find('replica') != -1):
                params_dict[k.split('-')[1]] = v
            else:
                params_dict[k] = v

        num_repl = params_dict['num_repl']
        max_result_window = params_dict['max_result_window']
        
        self.es.set_cur_algo(**params_dict)
        self.es.set_cur_replicas(num_repl)
        self.es.set_max_result_window(max_result_window)
        context = dict(
            self.each_context(request), # Include common variables for rendering the admin template.
        )
        
        return redirect(reverse('admin:config'))