from flask import Flask, render_template
import random
from collections import defaultdict

app = Flask(__name__)

professores = [
    "Prof. Carla", "Prof. Bruno", "Prof. Camila", "Prof. Daniel",
    "Prof. Eduardo", "Prof. Erika", "Prof. Guilherme", "Prof. Helena",
    "Prof. Igor", "Prof. Juliana"
]

disciplinas_por_periodo = {
    1: ["POO Java", "Lógica", "Web I", "Banco I", "Redes I"],
    2: ["Estrutura Dados", "Engenharia Soft I", "Mobile", "Banco II", "Web II"],
    3: ["Engenharia Soft II", "Compiladores", "Sistemas Operacionais", "Gestão TI", "Ética TI"],
    4: ["IA", "Segurança Info", "Projeto Integrador", "Empreendedorismo", "Inovação TI"],
    5: ["TCC", "Lógica Prog II", "Redes II", "Frameworks Web", "DevOps"]
}

def associar_prof_materia():

    prof_materia = []
    codigo_materia = 1

    for periodo in range(1, 6):
        disciplinas = disciplinas_por_periodo[periodo]
        prof_usados = []
        prof_disponiveis = random.sample(professores, len(professores))

        for nome_materia in disciplinas:
            while True:
                prof = prof_disponiveis.pop()
                if prof not in prof_usados:
                    break

            prof_usados.append(prof)
            cod_materia = str(codigo_materia).zfill(2)
            cod_professor = str(professores.index(prof) + 1).zfill(2)
            cod_combinado = f"{periodo}{cod_materia}{cod_professor}"

            prof_materia.append({
                "periodo": periodo,
                "nome_materia": nome_materia,
                "cod_materia": cod_materia,
                "cod_professor": cod_professor,
                "cod_combinado": cod_combinado,
                "professor": prof
            })
            codigo_materia += 1
        
    return prof_materia

def gerar_simulacoes_horarios(prof_materia, qtd_simulacoes=50):
    simulacoes = []

    for i in range(qtd_simulacoes):
        visao_geral = prof_materia 
        linha = [None] * 100  

        for p in range(1, 6):
            horarios_periodo = list(range(20))  
            random.shuffle(horarios_periodo)

            disciplinas = [d for d in visao_geral if d["periodo"] == p]
            prof_por_periodo = {}
            alocacoes_periodo = [None] * 20

            for disc in disciplinas:
                aulas_alocadas = 0
                tentativas = 0

                while aulas_alocadas < 4 and tentativas < 100:
                    idx = horarios_periodo.pop()
                    real_idx = (p - 1) * 20 + idx
                    prof = disc["cod_professor"]

                    if prof_por_periodo.get(prof, 0) >= 2:
                        horarios_periodo.insert(0, idx)
                        tentativas += 1
                        continue

                    if linha[real_idx] is None:
                        linha[real_idx] = disc["cod_combinado"]
                        prof_por_periodo[prof] = prof_por_periodo.get(prof, 0) + 1
                        aulas_alocadas += 1
                    else:
                        tentativas += 1
                        horarios_periodo.insert(0, idx)

            for i in range(20):
                real_idx = (p - 1) * 20 + i
                if linha[real_idx] is None:
                    disc = random.choice(disciplinas)
                    prof = disc["cod_professor"]
                    if prof_por_periodo.get(prof, 0) < 2:
                        linha[real_idx] = disc["cod_combinado"]
                        prof_por_periodo[prof] = prof_por_periodo.get(prof, 0) + 1
                    else:
                        linha[real_idx] = disc["cod_combinado"]

        simulacoes.append(linha)

    return simulacoes


def processar_simulacoes_com_conflitos(simulacoes):
    resultado_processado = []

    for idx, simulacao in enumerate(simulacoes):
        matriz = converter_simulacao_para_matriz(simulacao)
        conflitos = detectar_conflitos_em_matriz(matriz)

        resultado_processado.append({
            "id": idx + 1,
            "matriz": matriz,
            "conflitos": conflitos,  # lista de tuplas (dia, horario)
            "qtd_conflitos": len(conflitos)
        })
    
    # resultado_processado.sort(key=lambda x: x["qtd_conflitos"])

    return resultado_processado


def detectar_conflitos_em_matriz(matriz):
    """
    Detecta conflitos reais por horário, considerando que:
    - Cada dia tem 20 células (5 períodos × 4 horários)
    - Cada grupo de 4 células consecutivas forma os horários de 1 período
    - Colunas com professores repetidos (em horários iguais de períodos diferentes) são conflitos
    """
    conflitos = []

    for dia_idx, dia in enumerate(matriz):  # matriz = 5x20
        # Quebrar o dia em 5 períodos de 4 horários
        periodos = [dia[i*4:(i+1)*4] for i in range(5)]  # 5x4

        # Transpor para 4 colunas (cada horário real do dia)
        for col in range(4):  # horários reais do dia
            professores = {}
            for per in range(5):  # 5 períodos
                cod_combinado = periodos[per][col]
                cod_prof = cod_combinado[-2:]

                if cod_prof in professores:
                    # Marca o conflito atual + todos anteriores com mesmo prof
                    conflitos.append((dia_idx, per * 4 + col))
                    conflitos.append((dia_idx, professores[cod_prof]))
                else:
                    professores[cod_prof] = per * 4 + col

    return list(set(conflitos))  # remove duplicatas

def converter_simulacao_para_matriz(simulacao):
    """
    Converte a linha (100 códigos) para uma matriz 5x20.
    Linha = [segunda, terça, quarta, quinta, sexta] → cada um com 20 blocos
    """
    matriz = []
    for dia in range(5):  # Segunda (0) a Sexta (4)
        inicio = dia * 20
        fim = inicio + 20
        matriz.append(simulacao[inicio:fim])
    
    return matriz

def selecionar_pais(ranking):
    """
    Seleciona dois indivíduos:
    - pai1 da metade superior (melhores)
    - pai2 de qualquer posição
    Retorna os 2 vetores (100 posições)
    """
    metade = len(ranking) // 2

    individuo1  = random.choice(ranking[:metade])  # da metade melhor
    individuo2  = random.choice(ranking)           # da matriz toda

    # converter de matriz 5x20 para vetor de 100 posições
    pai1 = [aula for linha in individuo1 ['matriz'] for aula in linha]
    pai2 = [aula for linha in individuo2 ['matriz'] for aula in linha]

    return pai1, pai2, individuo1['id'], individuo2['id']


def cruzamento(pai1, pai2, pc=0.95):
    """
    Realiza cruzamento genético entre dois pais (listas com 100 elementos)
    Retorna dois filhos (listas de 100 elementos cada)
    """
    filhos = [[], []]
    origem_blocos = []  # Lista com 'P1' ou 'P2' para cada bloco de 20

    if random.random() < pc:
        # Número aleatório de cortes entre 1 e 4
        num_cortes = random.randint(1, 4)

        # Gera pontos de corte únicos entre 1 e 4 (depois será * 20)
        pontos_cortes = sorted(random.sample(range(1, 5), num_cortes))
        pontos_cortes = [p * 20 for p in pontos_cortes]

        # Cruzamento com alternância de blocos
        cruza = False
        i = 0
        for corte in pontos_cortes:
            if cruza:
                filhos[0].extend(pai2[i:corte])
                filhos[1].extend(pai1[i:corte])
                origem_blocos.extend(['P2'] * (corte - i))
            else:
                filhos[0].extend(pai1[i:corte])
                filhos[1].extend(pai2[i:corte])
                origem_blocos.extend(['P1'] * (corte - i))
            cruza = not cruza
            i = corte

        # Último pedaço
        if cruza:
            filhos[0].extend(pai2[i:])
            filhos[1].extend(pai1[i:])
            origem_blocos.extend(['P2'] * (100 - i))
        else:
            filhos[0].extend(pai1[i:])
            filhos[1].extend(pai2[i:])
            origem_blocos.extend(['P1'] * (100 - i))
    else:
        # Sem cruzamento: filhos = clones dos pais
        filhos = [pai1[:], pai2[:]]
        origem_blocos = ['P1'] * 100

    return filhos[0], filhos[1], origem_blocos


def mutacao(filhos, pm=0.3):
    """
    Aplica mutação nos filhos com base na probabilidade `pm`.
    Cada filho sofre 4 trocas por período (20 genes).
    """
    trocas = [set(), set()]

    if random.random() < pm:
        for k in range(2):  # para os dois filhos
            for bloco in range(0, 100, 20):  # blocos de 20 (períodos)
                for _ in range(4):  # 4 trocas por bloco
                    p1 = random.randint(bloco, bloco + 19)
                    p2 = random.randint(bloco, bloco + 19)
                    filhos[k][p1], filhos[k][p2] = filhos[k][p2], filhos[k][p1]
                    trocas[k].update([p1, p2])
    # else: não faz nada, filhos continuam iguais

    return filhos, trocas


def evoluir(pop_inicial, max_gen=100, pc=0.95, pm=0.3):
    """
    Executa o ciclo completo do AG até encontrar o melhor indivíduo possível.
    - pop_inicial: lista de listas (100 genes por indivíduo)
    """
    pop = pop_inicial[:]  # população atual
    melhor_global = None
    melhor_nota = float('inf')
    melhor_geracao = 0

    for gen in range(max_gen):
        # Avaliação e ordenação
        pop_avaliada = processar_simulacoes_com_conflitos(pop)
        pop_ordenada = sorted(pop_avaliada, key=lambda x: x["qtd_conflitos"])

        # Atualiza melhor global
        if pop_ordenada[0]["qtd_conflitos"] < melhor_nota:
            melhor_global = pop_ordenada[0]
            melhor_nota = melhor_global["qtd_conflitos"]
            melhor_geracao = gen

        print(f"[G{gen:03d}] Melhor: {pop_ordenada[0]['qtd_conflitos']} | Pior: {pop_ordenada[-1]['qtd_conflitos']}")

        # Gerar nova população por filhos
        nova_pop = []
        while len(nova_pop) < len(pop):
            # Seleção
            pai1, pai2, *_ = selecionar_pais(pop_ordenada)

            # Cruzamento
            filho1, filho2, _ = cruzamento(pai1, pai2, pc)

            # Mutação
            [filho1, filho2], _ = mutacao([filho1, filho2], pm)

            nova_pop.extend([filho1, filho2])

        pop = nova_pop[:len(pop)]  # garante tamanho fixo

    print(f"\n🏆 Melhor de todas as gerações: {melhor_nota} conflitos (Geração {melhor_geracao})")
    melhor_global["simulacao"] = [aula for linha in melhor_global["matriz"] for aula in linha]
    print(melhor_global)
    return melhor_global

@app.route('/')
def index():
    relacao_prof_materia = associar_prof_materia()
    simulacoes_horarios = gerar_simulacoes_horarios(prof_materia=relacao_prof_materia)
    conflitos_por_simulacao = processar_simulacoes_com_conflitos(simulacoes_horarios)
    ranking = sorted(conflitos_por_simulacao, key=lambda x: x["qtd_conflitos"])
    pai1, pai2, linha_pai1, linha_pai2 = selecionar_pais(ranking=ranking)
    filho1, filho2, blocos_origem = cruzamento(pai1, pai2, pc=0.97)
    filhos_mutados, trocas = mutacao([filho1[:], filho2[:]], pm=0.3)
    melhor = evoluir(simulacoes_horarios, max_gen=100)

    return render_template(
        'index.html', 
        prof_materia = relacao_prof_materia,
        simulacoes = simulacoes_horarios,
        conflitos_simulacoes = conflitos_por_simulacao,
        ranking = ranking,
        linha_pai1 = pai1,
        linha_pai2 = pai2,
        num_linha_pai1 = linha_pai1,
        num_linha_pai2 = linha_pai2,
        filho1 = filho1,
        filho2 = filho2,
        blocos_origem = blocos_origem,
        filho1_mutado=filhos_mutados[0],
        filho2_mutado=filhos_mutados[1],
        trocas_filho1=trocas[0],
        trocas_filho2=trocas[1],
        melhor = melhor
    )


if __name__ == '__main__':
    app.run(debug=True)