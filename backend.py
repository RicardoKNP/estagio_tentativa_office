from flask import Flask, request, jsonify
import json
import ollama

app = Flask(__name__)

# Função para carregar o dataset
def carregar_dataset(caminho):
    with open(caminho, "r", encoding="utf-8") as f:
        return [json.loads(linha) for linha in f]

# Carregar o dataset de contexto (garanta que o dataset esteja disponível no mesmo local)
dataset = carregar_dataset("dataset_2000.jsonl")

# Função para construir o contexto
def construir_contexto(area, numeros, problema, numeros_problema, impacto, objetivo):
    contexto = ""
    for exemplo in dataset:
        if (
            area.lower() in exemplo['área'].lower() or
            problema.lower() in exemplo['problema'].lower() or
            impacto.lower() in exemplo['impacto'].lower() or
            objetivo.lower() in exemplo['objetivo'].lower()
        ):
            contexto += f"Área: {exemplo['área']}\n"
            contexto += f"Números: {exemplo['números']}\n"
            contexto += f"Problema: {exemplo['problema']}\n"
            contexto += f"Números problema: {exemplo['números_problema']}\n"
            contexto += f"Impacto: {exemplo['impacto']}\n"
            contexto += f"Objetivo: {exemplo['objetivo']}\n"
            contexto += f"Texto: {exemplo['resposta']}\n\n"
    return contexto

# Função para gerar texto com o Ollama
def gerar_texto_ollama(prompt):
    resposta = ollama.chat(
        model='deepseek-coder:6.7b',
        messages=[{'role': 'user', 'content': prompt}]
    )
    return resposta['message']['content']

# Endpoint para geração de texto
@app.route('/generate-text', methods=['POST'])
def generate_text():
    data = request.get_json()
    area = data.get("area")
    numeros = data.get("numeros")
    problema = data.get("problema")
    numeros_problema = data.get("numeros_problema")
    impacto = data.get("impacto")
    objetivo = data.get("objetivo")
    
    # Valida se todos os campos foram enviados
    if not all([area, numeros, problema, numeros_problema, impacto, objetivo]):
        return jsonify({"error": "Falta preencher algum campo"}), 400

    contexto = construir_contexto(area, numeros, problema, numeros_problema, impacto, objetivo)

    prompt = (
        f"Com base nos exemplos abaixo, gere um texto claro e objetivo, "
        f"mantendo o mesmo estilo e estrutura dos exemplos anteriores.\n\n"
        f"{contexto}\n"
        f"Agora, para o seguinte caso, gere o texto:\n"
        f"Área: {area}\n"
        f"Números: {numeros}\n"
        f"Problema: {problema}\n"
        f"Números problema: {numeros_problema}\n"
        f"Impacto: {impacto}\n"
        f"Objetivo: {objetivo}\n\n"
        f"Texto:"
    )

    texto_gerado = gerar_texto_ollama(prompt)
    return jsonify({"texto": texto_gerado})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
