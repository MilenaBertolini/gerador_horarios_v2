import random

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
    
    # Contador de matérias por professor para distribuição igualitária
    contador_materias_prof = {prof: 0 for prof in professores}
    
    # Total de matérias: 5 períodos × 5 matérias = 25 matérias
    # 10 professores, então idealmente cada professor deveria ter 2-3 matérias
    
    for periodo in range(1, 6):
        disciplinas = disciplinas_por_periodo[periodo]
        prof_usados_periodo = []  # Professores já usados neste período
        
        for nome_materia in disciplinas:
            # Lista de professores disponíveis (não usados neste período)
            profs_disponiveis = [p for p in professores if p not in prof_usados_periodo]
            
            # Entre os disponíveis, prioriza quem tem menos matérias atribuídas
            profs_disponiveis.sort(key=lambda p: contador_materias_prof[p])
            
            # Pega o professor com menos matérias (ou aleatório entre os que têm menos)
            min_materias = contador_materias_prof[profs_disponiveis[0]]
            profs_com_menos_materias = [p for p in profs_disponiveis 
                                      if contador_materias_prof[p] == min_materias]
            
            prof_escolhido = random.choice(profs_com_menos_materias)
            
            # Atualiza contadores e listas
            prof_usados_periodo.append(prof_escolhido)
            contador_materias_prof[prof_escolhido] += 1
            
            # Gera códigos
            cod_materia = str(codigo_materia).zfill(2)
            cod_professor = str(professores.index(prof_escolhido) + 1).zfill(2)
            cod_combinado = f"{periodo}{cod_materia}{cod_professor}"

            prof_materia.append({
                "periodo": periodo,
                "nome_materia": nome_materia,
                "cod_materia": cod_materia,
                "cod_professor": cod_professor,
                "cod_combinado": cod_combinado,
                "professor": prof_escolhido
            })
            codigo_materia += 1
        
    # Debug: mostra a distribuição final
    print("📊 Distribuição de matérias por professor:")
    for prof in professores:
        materias_prof = [item for item in prof_materia if item["professor"] == prof]
        print(f"{prof}: {len(materias_prof)} matérias - {[m['nome_materia'] for m in materias_prof]}")
    
    return prof_materia

if __name__ == "__main__":
    print("Testando a distribuição igualitária de matérias...\n")
    resultado = associar_prof_materia()
    
    print(f"\nTotal de matérias distribuídas: {len(resultado)}")
    print("✅ Teste concluído!")
