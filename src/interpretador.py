import json
import math
import networkx as nx
import matplotlib.pyplot as plt

def visualizar_grafo(G):
    print("Preparando visualização...")
    
    # 1. Extrair as coordenadas para o formato que o Matplotlib entende.
    # O NetworkX exige um dicionário no formato: {id_do_no: (x, y)}
    posicoes = {}
    for id_no, dados in G.nodes(data=True):
        posicoes[id_no] = (dados['x'], dados['y'])

    # 2. Configurar o tamanho da janela de exibição
    plt.figure(figsize=(12, 8))
    plt.title("Grafo da Planta Baixa (Nós e Arestas)", fontsize=14)

    # 3. Desenhar o grafo
    # Ajustamos os parâmetros visuais para ficar fácil de debugar
    nx.draw(
        G, 
        pos=posicoes,          # Trava os nós nas posições reais
        node_size=15,          # Tamanho da "bolinha" (vértice).
        node_color="red",      # Vértices em vermelho
        edge_color="blue",     # Paredes em azul
        width=1.5,             # Espessura das paredes
        with_labels=False      # Se True, imprime o ID do nó
    )

    # 4. Ajustar proporção dos eixos para 1:1
    # Isso impede que a planta fique esticada se a janela for retangular
    plt.axis('equal') 
    
    # 5. Exibir a janela na tela
    print("Abrindo janela de visualização. Feche a janela para encerrar o script.")
    plt.show()

def calcular_distancia(p1, p2):
    """Calcula a distância euclidiana entre dois pontos 2D."""
    return math.sqrt((p1['x'] - p2['x'])**2 + (p1['y'] - p2['y'])**2)

def encontrar_ou_criar_no(grafo, ponto, tolerancia=0.05):
    """
    Busca se já existe um nó no grafo muito próximo ao ponto atual.
    Tolerância de 0.05 significa 5 centímetros (já que nossa unidade é metro).
    """
    # Itera pelos nós já existentes no grafo
    for no_existente, dados in grafo.nodes(data=True):
        # O NetworkX permite guardar dados dentro do nó. Vamos guardar as coordenadas 'x' e 'y'.
        coord_existente = {'x': dados['x'], 'y': dados['y']}
        
        if calcular_distancia(ponto, coord_existente) <= tolerancia:
            # Encontrou um nó próximo! Retorna o ID desse nó existente (faz o snapping)
            return no_existente
            
    # Se não encontrou nenhum próximo, cria um novo nó.
    # Usaremos o tamanho do grafo atual como ID (0, 1, 2, 3...)
    novo_id = len(grafo.nodes)
    # Adiciona o nó no grafo guardando suas coordenadas reais
    grafo.add_node(novo_id, x=ponto['x'], y=ponto['y'])
    
    return novo_id

def construir_grafo_das_paredes(caminho_json):
    # Inicializa um grafo não-direcionado
    G = nx.Graph()
    
    # Carrega os dados que extraímos do DXF
    try:
        with open(caminho_json, 'r', encoding='utf-8') as f:
            linhas = json.load(f)
    except FileNotFoundError:
        print("Arquivo JSON não encontrado.")
        return G

    print(f"Lendo {len(linhas)} linhas para construir o grafo...")

    # Itera sobre as linhas extraídas
    for linha in linhas:
        p_inicio = linha['inicio']
        p_fim = linha['fim']
        
        # Ignorar linhas de tamanho zero (sujeira de CAD)
        if calcular_distancia(p_inicio, p_fim) < 0.01:
            continue
            
        # Pega o ID do nó (criando um novo ou aproveitando um próximo)
        id_inicio = encontrar_ou_criar_no(G, p_inicio)
        id_fim = encontrar_ou_criar_no(G, p_fim)
        
        # Evita criar arestas que conectam um nó a ele mesmo (loops)
        if id_inicio != id_fim:
            # Adiciona a aresta. Podemos guardar o tipo de camada como atributo!
            G.add_edge(id_inicio, id_fim, camada=linha['camada'])
            
    print(f"Grafo construído com sucesso!")
    print(f"Total de Nós (Vértices): {G.number_of_nodes()}")
    print(f"Total de Arestas (Paredes): {G.number_of_edges()}")
    
    return G

if __name__ == "__main__":
    # Testando a função com o arquivo gerado anteriormente
    grafo_planta = construir_grafo_das_paredes("planta_estrutural.json")

    # 2. Chama a função de desenho passando o grafo recém-criado
    if grafo_planta.number_of_nodes() > 0:
        visualizar_grafo(grafo_planta)