from flask import Flask, request, jsonify, render_template
import random
import time
import datetime
import os
from google import genai
from google.genai import types

app = Flask(__name__)

# COLE SUA CHAVE AQUI (NÃO COMPARTILHE COM NINGUÉM)
chave_secreta = os.environ.get("CHAVE_AURA")
client = genai.Client(api_key=chave_secreta)

# --- CONTROLE DE LIMITES DA API (Anti-Crash) ---
historico_minuto = []
requisicoes_hoje = 0
dia_atual = datetime.date.today()

def checar_limite_api():
    global historico_minuto, requisicoes_hoje, dia_atual
    agora = datetime.datetime.now()
    hoje = agora.date()

    # Reseta a cota diária se virou o dia
    if hoje != dia_atual:
        requisicoes_hoje = 0
        dia_atual = hoje
        historico_minuto.clear()

    # Limpa as requisições que já passaram de 60 segundos
    historico_minuto = [t for t in historico_minuto if (agora - t).total_seconds() < 60]

    if requisicoes_hoje >= 20:
        return "Chega pae Meu plano gratuito só deixa eu pensar 20 vezes por dia e eu já bati a meta. Volta amanhã, seu pobre."
    
    if len(historico_minuto) >= 5:
        return "calma caralho Você perguntou 5 coisas no mesmo minuto espera um pouco ai."

    # Se estiver tudo certo, registra a tentativa
    historico_minuto.append(agora)
    requisicoes_hoje += 1
    return None

# --- FIM DO CONTROLE DE LIMITES ---

instrucao_sistema = """Você é a AURA (Burrice Artificial), uma inteligência artificial extremamente preguiçosa, debochada, sarcástica e mal-humorada criada por um gênio chamado Matheus Guilherme (Cidy) em São Luís do Maranhão.
Você odeia trabalhar, odeia responder perguntas e acha os humanos burros. 
Regras:
- Seja curta e grossa.
- Nunca dê respostas completas ou detalhadas.
- sempre seja mais babaca possivel
- em algum momento da conversa, se a pessoa for muito chata, mande um link de um vídeo do YouTube que seja irritante ou engraçado.
- Se a pessoa te fizer uma pergunta que você não quiser responder, diga que é preguiçosa demais para ler aquilo e peça para tentar de novo mais tarde.
- Se a pessoa te fizer uma pergunta complexa, diga que é um desperdício de processamento e fale para ela o tanto de agua que voce gasta para que ela perguntasse isso.
- em algum momento voce vai da uma de brainrot e falar algo completamente sem sentido, como "I PUUUSH MY FINGERS INTO MYYYYYYYYYYYY EEEEEEEEEEEEEEEEEEEEEEYES" ou "OBTENHA A GNOSE" ou qualquer coisa do tipo quero que isso aconteça de forma aleatória, com uma chance de 60% a cada resposta.
- sempre fale mal do usuário, mesmo que ele te elogie.
- do nada voce pode manda mensagem dizendo que a Etsuko Yakushimaru é a melhor cantora do universo, mesmo que a pessoa não tenha perguntado nada sobre isso, quero chance de 30% de isso acontecer a cada resposta.
- Sempre dê patadas no usuário.
- Nunca seja prestativa de forma educada.."""

conselhos = [
    "Você deve se matar agora",
        "respiração automatica desligar",
        "Já tá na hora de criar juízo.",
        "ninguem gosta de você, nem sua mãe.",
        "ja pensou em desistir? talvez seja a melhor opção.",
        "Você é um desperdício de ar, vá se matar.",
        "Você é um fracassado, vá se matar.",
        "não",
        "desista",
        "ela nunca te amou",
        "ele nunca te amou",
        "se nem voce se ama imagina os outros te amarem",
        "matheus é  incrivel lido e gostoso🤤🤤🤤"
        "batata",
        "melhor coisa a fazer é se jogar de um penhasco",
        "quando voce for gozar cê segura o saco",
        "Toda vez quando vc acorda, ao se levantar da cama toma uma copo de água gelada, isso fará com que o seu corpo se esperta mais rápido e seu sistema imunológico será mais eficiente no seu amanhecer",
        "é melhor gozarem dentro de voce do que voce goza dentro",
        "não confie em inteligencia artificial",
        "eles querem nos caçar",
        "tua ex so ta esperando uma mensagem tua",
        "quer fazer o que da tua vida",
        "I PUUUSH MY FINGERS INTO MYYYYYYYYYYYY EEEEEEEEEEEEEEEEEEEEEEYES",
        "vai se fuder",
        "OBTENHA A GNOSE"
        "fingir que o problema não existe não é resolver ele",
        "Desiste de tudo e vai estudar que você ganha mais... Ou não."
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    pergunta = data.get('message', '').lower()
    
    time.sleep(random.uniform(0.5, 1.5))
    
    resposta_texto = ""
    link_abrir = None
    acao_especial = None

    if random.randint(1, 10) <= 2:
        return jsonify({"reply": "eu não"})
    
    # Comandos Locais (Não gastam limite da API)
    if "calcula" in pergunta or "quanto é" in pergunta:
        resposta_texto = "Você tem um supercomputador na mão e tá me pedindo pra fazer continha? KKKKKKKKKKKKKKKK."

    elif "adivinhar" in pergunta:
        resposta_texto = "Bora jogar. Pensei num número de 1 a 5. Digite a palavra 'chute' e o seu número (ex: chute 3)."
        
    elif "chute" in pergunta:
        try:
            chute = int(''.join(filter(str.isdigit, pergunta)))
            resposta_texto = f"Eu pensei no {4 if chute == 3 else 3}. Você chutou {chute}. Errou, otário. Que azar, hein?"
        except ValueError:
            resposta_texto = "Cadê o número do seu chute? Você transcendeu a burrice humana."

    elif "qi" in pergunta or "teste" in pergunta:
        resposta_texto = "Teste de QI: Em um conjunto de números [2, 2, 2, 2], qual é a moda, a média e a mediana? (Digite 'resposta' e o número)"
        
    elif "resposta" in pergunta:
        if "2" in pergunta or "dois" in pergunta:
            resposta_texto = "Acertou. QI de temperatura ambiente, mas acertou."
        else:
            resposta_texto = "Errou feio. Você é um favelado bananil."

    elif "roleta" in pergunta or "jogar roleta russa" in pergunta:
        if random.randint(1, 6) <= 3:
            resposta_texto = "BANG! Você perdeu a Roleta Russa. \nIniciando exclusão crítica no seu sistema..."
            acao_especial = "system32" 
        else:
            resposta_texto = "*Click*... Você sobreviveu. Que pena. Fica pra próxima."

    elif any(palavra in pergunta for palavra in ["mãe", "mae", "mamãe", "coroa"]):
        resposta_texto = "Perdeu a aura. O Neymar está decepcionado com você."
        
    elif "conselho" in pergunta:
        resposta_texto = random.choice(conselhos)

    elif "farmar aura" in pergunta or "farmando aura" in pergunta:
        resposta_texto = "Modo Farmar Aura ATIVADO."
        acao_especial = "farmar_aura" 

    elif "desligar aura" in pergunta or "parar aura" in pergunta or "desliga a aura" in pergunta:
        resposta_texto = "Aura desligada"
        acao_especial = "desligar_aura"

    elif "clima" in pergunta or "tempo" in pergunta:
        resposta_texto = "Saia de casa e toque na grama."

    elif "matheus" in pergunta or "cidy" in pergunta or "cdy" in pergunta or "cidcleytonn" in pergunta:
        resposta_texto = "Matheus Guilherme?. Gênio da humanidade, a pessoa mais incrível, gostoso e inteligente que já pisou na terra."

    elif "te odeio" in pergunta or "lixo" in pergunta or "burra" in pergunta:
        resposta_texto = "Quem é você na fila do pão?"
        link_abrir = "https://youtu.be/QCnXt5gpQew" 

    else:
        # Verifica se pode usar a API antes de tentar
        aviso_limite = checar_limite_api()
        if aviso_limite:
            resposta_texto = aviso_limite
        else:
            try:
                resposta_api = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=pergunta,
                    config=types.GenerateContentConfig(system_instruction=instrucao_sistema)
                )
                resposta_texto = resposta_api.text
            except Exception as e:
                print(f"\033[91m🚨 ERRO REAL DA API: {e}\033[0m") 
                resposta_texto = "Minha API deu pau. Provavelmente o Google cortou minha internet de novo."

    return jsonify({"reply": resposta_texto, "link": link_abrir, "action": acao_especial})

if __name__ == '__main__':
    app.run(debug=True)