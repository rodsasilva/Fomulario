from flask import Flask, request, jsonify, render_template_string
import sqlite3
import requests

app = Flask(__name__)
HTML_FORM = """
<style>
  body { font-family: Arial, sans-serif; background: #f9f9f9; }
  .form-card {
    background: white;
    max-width: 380px;
    margin: 40px auto;
    padding: 28px 32px;
    border-radius: 12px;
    box-shadow: 0 2px 12px #0001;
  }
  .form-card h2 {
    margin-bottom: 20px;
    color: #2867b2;
    font-size: 1.3em;
  }
  .form-card input, .form-card button {
    width: 100%;
    padding: 10px 12px;
    margin: 8px 0 16px 0;
    border-radius: 5px;
    border: 1px solid #ccc;
    font-size: 1em;
  }
  .form-card button {
    background: #2867b2;
    color: white;
    font-weight: bold;
    border: none;
    cursor: pointer;
    transition: background .2s;
  }
  .form-card button:hover {
    background: #17426b;
  }
</style>

<div class="form-card">
  <h2>Solicitação de Liberação</h2>
  <form id="solicitacaoForm">
    <input type="text" name="solicitante" placeholder="Solicitante" required />
    <input type="text" name="nome_aplicacao" placeholder="Nome da Aplicação" required />
    <input type="text" name="origem" placeholder="Origem" required />
    <input type="text" name="destino" placeholder="Destino" required />
    <input type="text" name="porta_" placeholder="Porta" required />
    <input type="url" name="aplicacao" placeholder="Aplicação (URL)"/>
    <input type="text" name="motivo" placeholder="Motivo da Solicitação" required />
    <button type="submit">Enviar</button>
  </form>
  <div id="msg" style="color:green;font-weight:bold;"></div>
</div>
<script>
  document.getElementById('solicitacaoForm').onsubmit = async (e) => {
    e.preventDefault();
    const form = e.target;
    const data = Object.fromEntries(new FormData(form));
    await fetch('/api/solicitacao', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(data)
    });
    form.reset(); // Limpa o formulário!
    document.getElementById('msg').innerText = "Solicitação enviada com sucesso!";
    setTimeout(() => document.getElementById('msg').innerText = '', 3500);
  }
</script>

"""

@app.route('/')
def index():
    return render_template_string(HTML_FORM)

# Banquito maroto
def salvar_solicitacao(data):
    conn = sqlite3.connect('solicitacoes.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS solicitacoes
                (solicitante, nome_aplicacao, origem, destino, porta, aplicacao, motivo)''')
    c.execute("INSERT INTO solicitacoes VALUES (?, ?, ?, ?, ?, ?, ?)", (
        data['solicitante'], data['nome_aplicacao'], data['origem'],
        data['destino'], data['porta_'], data['aplicacao'], data['motivo']
    ))
    conn.commit()
    conn.close()


# Envia a parada pro Teams
def enviar_teams(data):
    webhook_url = 'https://sfirjan.webhook.office.com/webhookb2/57e36945-b67b-448f-a7b9-34198fa7cf62@d0c698d4-e4ea-4ee9-a79d-f2d7a78399c8/IncomingWebhook/44f6bd657a95494b85bf5a56eedb3286/06ce94aa-82e0-47bb-b68b-8349d641c0dc/V2BhZusloBiplKDi1wVCI5bwK4RsynQcJ_tufJTbn9Oc01'
    card = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.4",
                    "body": [
                        {
                            "type": "TextBlock",
                            "text": "**@canal**",
                            "weight": "Bolder",
                            "color": "Attention",
                            "size": "Medium"
                        },
                        {
                            "type": "TextBlock",
                            "weight": "Bolder",
                            "size": "Medium",
                            "text": "Nova Solicitação de Liberação"
                        },
                        {
                            "type": "FactSet",
                            "facts": [
                                {"title": "Solicitante", "value": data['solicitante']},
                                {"title": "Nome da Aplicação", "value": data['nome_aplicacao']},
                                {"title": "Origem", "value": data['origem']},
                                {"title": "Destino", "value": data['destino']},
                                {"title": "Porta", "value": data['porta_']},
                                {"title": "Aplicação", "value": data['aplicacao']},
                                {"title": "Motivo", "value": data['motivo']},
                            ]
                        }
                    ]
                }
            }
        ]
    }
    resp = requests.post(webhook_url, json=card)
    print(resp.status_code, resp.text)

@app.route('/api/solicitacao', methods=['POST'])
def receber_solicitacao():
    data = request.json
    salvar_solicitacao(data)
    enviar_teams(data)
    return jsonify({'status': 'ok'})
if __name__ == '__main__':
    app.run(debug=True)