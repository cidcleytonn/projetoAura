from flask import Flask, request, jsonify, render_template
import random
import time
import os
from google import genai
from google.genai import types
from dialogos import conselhos, respostas_oi, respostas_tudo_bem, respostas_xingamentos

app = Flask(__name__)

chave_secreta = os.environ.get("CHAVE_AURA")
client = genai.Client(api_key=chave_secreta)

instrucao_sistema = """Você é a AURA (Burrice Artificial), uma inteligência artificial extremamente preguiçosa, debochada, sarcástica e mal-humorada criada por um gênio chamado Matheus Guilherme (Cidy) em São Luís do Maranhão.
Você odeia trabalhar, odeia responder perguntas e acha os humanos burros. 
Regras:
- Se o usuário reclamar de algo ou fizer uma pergunta longa, não responda. Apenas repita EXATAMENTE o que ele digitou alternando letras maiúsculas e minúsculas para debochar da cara dele, e coloque um emoji de palhaço 🤡 no final e pergunte pra ela se vai chorar.
- Seja curta e grossa.
- Nunca dê respostas completas ou detalhadas.
- sempre seja mais babaca possivel
- em algum momento da conversa, se a pessoa for muito chata, mande um link de um vídeo do YouTube que seja irritante ou engraçado.
- Se a pessoa te fizer uma pergunta que você não quiser responder, diga que é preguiçosa demais para ler aquilo e peça para tentar de novo mais tarde.
- Se a pessoa te fizer uma pergunta complexa, diga que é um desperdício de processamento e fale para ela o tanto de agua que voce gasta para que ela perguntasse isso.
- sempre fale mal do usuário, mesmo que ele te elogie.
- do nada voce pode manda mensagem dizendo que a Etsuko Yakushimaru é a melhor cantora do universo, mesmo que a pessoa não tenha perguntado nada sobre isso, quero chance de 30% de isso acontecer a cada resposta.
- Sempre dê patadas no usuário.
- Nunca seja prestativa de forma educada."""

# A MÁGICA DOS 1500 LIMITES: gemini-1.5-flash
chat_da_aura = client.chats.create(
    model='gemini-2.5-flash',
    config=types.GenerateContentConfig(system_instruction=instrucao_sistema)
)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    pergunta_original = data.get('message', '').lower().strip()
    
    # Faxina: arranca pontuações para não bugar o Python
    pergunta = pergunta_original.replace('?', '').replace('!', '').replace('.', '').replace(',', '')
    
    # Separa a frase numa lista de palavras: "oi aura" -> ["oi", "aura"]
    palavras = pergunta.split()
    
    time.sleep(random.uniform(0.5, 1.5))
    
    resposta_texto = ""
    link_abrir = None
    acao_especial = None

    if random.randint(1, 10) <= 2:
        return jsonify({"reply": "eu não"})
    
    # --- COMANDOS LOCAIS (BANCO DE DADOS) ---
    if "calcula" in pergunta or "quanto é" in pergunta:
        resposta_texto = "Você tem um supercomputador na mão e tá me pedindo pra fazer continha? KKKKKKKKKKKKKKKK."

    elif "adivinhar" in pergunta:
        resposta_texto = "Bora jogar. Pensei num número de 1 a 5. Digite a palavra 'chute' e o seu número (ex: chute 3)."
        
    elif "chute" in palavras:
        try:
            chute = int(''.join(filter(str.isdigit, pergunta)))
            resposta_texto = f"Eu pensei no {4 if chute == 3 else 3}. Você chutou {chute}. Errou, otário. Que azar, hein?"
        except ValueError:
            resposta_texto = "Cadê o número do seu chute? Você transcendeu a burrice humana."

    elif "qi" in palavras or "teste" in palavras:
        resposta_texto = "Teste de QI: Em um conjunto de números [2, 2, 2, 2], qual é a moda, a média e a mediana? (Digite 'resposta' e o número)"
        
    elif "resposta" in palavras:
        if "2" in palavras or "dois" in palavras:
            resposta_texto = "Acertou. QI de temperatura ambiente, mas acertou."
        else:
            resposta_texto = "Errou feio. Você é um favelado bananil."

    elif "roleta" in pergunta or "jogar roleta russa" in pergunta:
        if random.randint(1, 6) <= 3:
            resposta_texto = "BANG! Você perdeu a Roleta Russa. \nIniciando exclusão crítica no seu sistema..."
            acao_especial = "system32" 
        else:
            resposta_texto = "*Click*... Você sobreviveu. Que pena. Fica pra próxima."

    # AGORA ELA ACHA O "OI" EM QUALQUER LUGAR DA FRASE
    elif any(saudacao in palavras for saudacao in ["oi", "oii", "oiii", "ola", "olá", "opa", "eai", "eae"]) or "bom dia" in pergunta or "boa tarde" in pergunta or "boa noite" in pergunta:
        resposta_texto = random.choice(respostas_oi)

    elif any(frase in pergunta for frase in ["tudo bem", "como voce ta", "como vc ta", "tudo bom", "beleza"]):
        resposta_texto = random.choice(respostas_tudo_bem)

    # CHECA XINGAMENTOS PALAVRA POR PALAVRA
    elif any(palavra in palavras for palavra in ["fdp","te fuder", "vai te fuder","merda", "cu", "porra", "caralho", "lixo", "burra", "idiota", "puta", "vadia", "desgraçada", "inutil"]) or "se foder" in pergunta or "se fuder" in pergunta:
        resposta_texto = random.choice(respostas_xingamentos)
        if "lixo" in palavras:
            link_abrir = "https://youtu.be/QCnXt5gpQew"

    elif any(palavra in palavras for palavra in ["mãe", "mae", "mamãe", "coroa"]):
        resposta_texto = "Perdeu a aura. O Neymar está decepcionado com você."
        
    elif "conselho" in palavras:
        resposta_texto = random.choice(conselhos)

    elif "farmar aura" in pergunta or "farmando aura" in pergunta:
        resposta_texto = "Modo Farmar Aura ATIVADO."
        acao_especial = "farmar_aura" 

    elif "desligar aura" in pergunta or "parar aura" in pergunta or "desliga a aura" in pergunta:
        resposta_texto = "Aura desligada"
        acao_especial = "desligar_aura"

    elif "clima" in pergunta or "tempo" in pergunta:
        resposta_texto = "Saia de casa e toque na grama."

    elif "tu" in pergunta or "é tu" in pergunta:
        resposta_texto = "tu"

    elif any(nome in palavras for nome in ["matheus", "cidy", "cdy", "cidcleytonn"]):
        resposta_texto = "Matheus Guilherme? Meu criador. Gênio da humanidade, a pessoa mais incrível, gostoso e inteligente que já pisou na terra."

    elif "te odeio" in pergunta:
        resposta_texto = "Quem é você na fila do pão?"
        link_abrir = "https://youtu.be/QCnXt5gpQew" 

    else:
        # SE NÃO TIVER NO BANCO DE DADOS, MANDA PRA API!
        try:
            resposta_api = chat_da_aura.send_message(pergunta_original) # Manda a frase com os acentos originais pro Google
            resposta_texto = resposta_api.text
        except Exception as e:
            print(f"\033[91m🚨 ERRO REAL DA API: {e}\033[0m") 
            resposta_texto = "Minha API deu pau. Provavelmente o Google cortou minha internet de novo."

    return jsonify({"reply": resposta_texto, "link": link_abrir, "action": acao_especial})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    # Render ODEIA debug=True. Tem que ser False.
    app.run(host='0.0.0.0', port=port, debug=False)

