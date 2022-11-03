var isTabActive = true;

window.onfocus = function(){ 
    isTabActive = true; 
}; 

window.onblur = function(){ 
    isTabActive = false; 
};

function get_cluster_info(){
    // console.log(!document.hidden)
    if(!document.hidden){ //(isTabActive) { // só faz se a janela estiver ativa
        var ajax = $.get(SERVICES_URL+'monitoring/cluster')
            ajax.done(function(response){
                $('#cpu_percent').html(response['cpu_percent']+'%');
                var mem_percent = ((response['jvm_heap_used'] / response['jvm_heap_size']) * 100).toFixed(2);
                $('#mem_percent').html(mem_percent+'%');

                //atualiza os gráficos
                grafico_uso_processador.data['datasets'][0]["data"].shift();
                grafico_uso_processador.data['datasets'][0]["data"].push(response['cpu_percent']);
                grafico_uso_memoria.data['datasets'][0]["data"].shift();
                grafico_uso_memoria.data['datasets'][0]["data"].push(mem_percent);
                grafico_uso_processador.update();
                grafico_uso_memoria.update();
            });
    }
}

var grafico_uso_processador;
var grafico_uso_memoria;

$(function(){
    var uso_processador_ctx = $("#grafico-uso-processador").get(0).getContext("2d");
    var uso_processador_config = {
        type: 'line',
        data: {
            datasets: [
                {label: 'Processador',
                data: [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                borderColor: '#f4a261',},
            ],
            labels: [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            legend: false,
            elements: {
                point: {
                    radius: 0,
                    backgroundColor: "#000"
                },
                line: {
                    tension: 0
                }
            },
            scales: {
                yAxes: [{
                    ticks: {
                        min: 0,
                        max: 100
                    }
                }],
                xAxes: [{
                    ticks: {
                        display: false
                    }
                }]
            },
        }
    }
    grafico_uso_processador = new Chart(uso_processador_ctx, uso_processador_config);


    var uso_memoria_ctx = $("#grafico-uso-memoria").get(0).getContext("2d");
    var uso_memoria_config = {
        type: 'line',
        data: {
            datasets: [
                {label: 'Memória',
                data: [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                borderColor: '#2a9d8f',},
            ],
            labels: [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            legend: false,
            elements: {
                point: {
                    radius: 0,
                    backgroundColor: "#000"
                },
                line: {
                    tension: 0
                }
            },
            scales: {
                yAxes: [{
                    ticks: {
                        min: 0,
                        max: 100
                    }
                }],
                xAxes: [{
                    ticks: {
                        display: false
                    }
                }]
            },
        },
    }
    grafico_uso_memoria = new Chart(uso_memoria_ctx, uso_memoria_config);



    //solicita informação sobre o cluster a cada 2s
    setInterval(get_cluster_info, 2000);

    var qtdes_ctx = $("#grafico-pizza-qtdes-indices").get(0).getContext("2d");
    var qtdes_config = {
        type: 'pie',
        data: {
            datasets: [{
                data: indices_amounts['data'],
                backgroundColor: indices_amounts['colors'],
            }],
            labels: indices_amounts['labels']
        },
        options: {
            legend:{
                position: 'left',
            },
            responsive: true
        }
    };
    var grafico_qtdes_indices = new Chart(qtdes_ctx, qtdes_config);


    var num_buscas_ctx = $("#grafico-num-buscas-dia").get(0).getContext("2d");
    var num_buscas_config = {
        type: 'bar',
        data: {
            datasets: [
                {label: 'Total',
                data: total_searches_per_day['data'],
                backgroundColor: '#36a2eb',},

                {label: 'Sem cliques',
                data: no_clicks_per_day['data'],
                backgroundColor: '#ffcd56',},

                {label: 'Sem resultados',
                data: no_results_per_day['data'],
                backgroundColor: '#ff9f40'},

            ],
            labels: total_searches_per_day['labels']
        },
        options: {
            legend: {}
        }
    }
    var grafico_num_buscas_dia = new Chart(num_buscas_ctx, num_buscas_config);


    var response_time_ctx = $("#grafico-tempo-resposta").get(0).getContext("2d");
    var response_time_config = {
        type: 'line',
        data: {
            datasets: [
                {label: 'Tempo de resposta',
                data: response_time_per_day['data'],
                borderColor: '#6ac472',
                backgroundColor: '#b2e1b6',},
            ],
            labels: response_time_per_day['labels']
        },
        options: {
            legend: false,
            elements: {
                point: {
                    radius: 3,
                    backgroundColor: "#000"
                },
                line: {
                    tension: 0
                }
            },
        }
    }
    var chart_response_time = new Chart(response_time_ctx, response_time_config);


    var no_clicks_ctx = $("#grafico-consultas-sem-clique").get(0).getContext("2d");
    var no_clicks_config = {
        type: 'bar',
        data: {
            datasets: [{
                data: porc_no_clicks_per_day['data'],
                backgroundColor: '#ffcd56',

            }],
            labels: porc_no_clicks_per_day['labels']
        },
        options: {
            legend: false,
            scales: {
                yAxes: [{
                    ticks: {
                        min: 0,
                        max: 100
                    }
                }]
            },
        }
    }
    var grafico_sem_cliques_dia = new Chart(no_clicks_ctx, no_clicks_config);


    var no_results_ctx = $("#grafico-consultas-sem-resultado").get(0).getContext("2d");
    var no_results_config = {
        type: 'bar',
        data: {
            datasets: [{
                data: porc_no_results_per_day['data'],
                backgroundColor: '#ff9f40',

            }],
            labels: porc_no_results_per_day['labels']
        },
        options: {
            legend: false,
            scales: {
                yAxes: [{
                    ticks: {
                        min: 0,
                        max: 100
                    }
                }]
            },
        }
    }
    var grafico_sem_resultados_dia = new Chart(no_results_ctx, no_results_config);


    var posicao_clique_ctx = $("#grafico-posicao-clique").get(0).getContext("2d");
    var posicao_clique_config = {
        type: 'bar',
        data: {
            datasets: [{
                data: avg_click_position_per_day['data'],
                backgroundColor: '#114b5f',

            }],
            labels: avg_click_position_per_day['labels']
        },
        options: {
            legend: false,
            scales: {
                yAxes: [{
                  scaleLabel: {
                    display: true,
                    labelString: 'Posição no ranking'
                  }
                }]
            }
        }
    }
    var grafico_posicao_clique = new Chart(posicao_clique_ctx, posicao_clique_config);

    
    var tempo_clique_ctx = $("#grafico-tempo-ate-clique").get(0).getContext("2d");
    var tempo_clique_config = {
        type: 'bar',
        data: {
            datasets: [{
                data: time_to_first_click_per_day['data'],
                backgroundColor: '#faa613',

            }],
            labels: time_to_first_click_per_day['labels']
        },
        options: {
            legend: false,
            scales: {
                yAxes: [{
                  scaleLabel: {
                    display: true,
                    labelString: 'Tempo em segundos'
                  }
                }]
            }
        }
    }
    var grafico_tempo_clique = new Chart(tempo_clique_ctx, tempo_clique_config);


    var cliques_por_consulta_ctx = $("#grafico-cliques-por-consulta").get(0).getContext("2d");
    var cliques_por_consulta_config = {
        type: 'bar',
        data: {
            datasets: [{
                data: avg_clicks_per_query_per_day['data'],
                backgroundColor: '#688e26',

            }],
            labels: avg_clicks_per_query_per_day['labels']
        },
        options: {
            legend: false,
            scales: {
                yAxes: [{
                  scaleLabel: {
                    display: true,
                    labelString: 'Média de cliques'
                  }
                }]
            }
        }
    }
    var grafico_cliques_por_consulta = new Chart(cliques_por_consulta_ctx, cliques_por_consulta_config);


    var duracao_sessao_ctx = $("#grafico-duracao-sessao").get(0).getContext("2d");
    var duracao_sessao_config = {
        type: 'bar',
        data: {
            datasets: [{
                data: avg_session_duration_per_day['data'],
                backgroundColor: '#f44708',

            }],
            labels: avg_session_duration_per_day['labels']
        },
        options: {
            legend: false,
            scales: {
                yAxes: [{
                  scaleLabel: {
                    display: true,
                    labelString: 'Duração em segundos'
                  }
                }]
            }
        }
    }
    var grafico_duracao_sessao = new Chart(duracao_sessao_ctx, duracao_sessao_config);
    
});