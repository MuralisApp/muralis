import ezdxf
import sys
import json

UNIDADES_DXF = {
    0: "Sem unidade", 1: "Polegadas", 2: "Pés", 3: "Milhas", 
    4: "Milímetros", 5: "Centímetros", 6: "Metros", 
}

# Aqui nós definimos o que nos interessa. 
# Adicionei a camada '0' porque muitos projetistas desenham portas/janelas nela por preguiça.
CAMADAS_ALVO = ['A-WALL', 'I-WALL', '0'] 

def extrair_dxf_para_json(caminho_arquivo, caminho_saida_json):
    try:
        documento = ezdxf.readfile(caminho_arquivo)
        msp = documento.modelspace()
        
        codigo_unidade = documento.header.get('$INSUNITS', 0)
        unidade_nome = UNIDADES_DXF.get(codigo_unidade, f"Desconhecida ({codigo_unidade})")
        print(f"Unidade de medida: {unidade_nome}")
        
        dados_brutos = []
        
        for entidade in msp:
            tipo = entidade.dxftype()
            camada_original = entidade.dxf.layer
            
            if tipo == 'LINE':
                ponto_inicio = entidade.dxf.start
                ponto_fim = entidade.dxf.end
                
                linha_info = {
                    "tipo_entidade": "LINE",
                    "camada": camada_original,
                    "inicio": {"x": round(ponto_inicio.x, 4), "y": round(ponto_inicio.y, 4), "z": round(ponto_inicio.z, 4)},
                    "fim": {"x": round(ponto_fim.x, 4), "y": round(ponto_fim.y, 4), "z": round(ponto_fim.z, 4)}
                }
                dados_brutos.append(linha_info)
                
            elif tipo == 'INSERT':
                try:
                    for sub_entidade in entidade.virtual_entities():
                        if sub_entidade.dxftype() == 'LINE':
                            sub_inicio = sub_entidade.dxf.start
                            sub_fim = sub_entidade.dxf.end
                            camada_interna = sub_entidade.dxf.layer
                            
                            linha_info = {
                                "tipo_entidade": "LINE_FROM_BLOCK",
                                "camada": camada_interna, 
                                "bloco_origem": camada_original,
                                "inicio": {"x": round(sub_inicio.x, 4), "y": round(sub_inicio.y, 4), "z": round(sub_inicio.z, 4)},
                                "fim": {"x": round(sub_fim.x, 4), "y": round(sub_fim.y, 4), "z": round(sub_fim.z, 4)}
                            }
                            dados_brutos.append(linha_info)
                except Exception:
                    pass
                    
        print(f"Total bruto extraído: {len(dados_brutos)} linhas.")
        
        # Usando 'List Comprehension' do Python para filtrar rápido
        # Mantemos a linha se a camada dela (ou do bloco de onde ela veio) estiver na nossa lista alvo
        dados_filtrados = [
            linha for linha in dados_brutos 
            if linha['camada'] in CAMADAS_ALVO or linha.get('bloco_origem') in CAMADAS_ALVO
        ]
        
        print(f"Após o filtro estrutural, restaram: {len(dados_filtrados)} linhas.")
        
        # Gravando no arquivo JSON
        with open(caminho_saida_json, 'w', encoding='utf-8') as arquivo_json:
            # indent=4 deixa o JSON formatado e bonito para leitura
            json.dump(dados_filtrados, arquivo_json, indent=4, ensure_ascii=False)
            
        print(f"Sucesso! Arquivo JSON gerado em: {caminho_saida_json}")

    except Exception as e:
        print(f"Erro ao processar o arquivo: {e}")

if __name__ == "__main__":
    arquivo_entrada = "teste.dxf"
    arquivo_saida = "planta_estrutural.json"
    extrair_dxf_para_json(arquivo_entrada, arquivo_saida)