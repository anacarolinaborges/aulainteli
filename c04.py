import requests
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.openrouter import OpenRouterModel

load_dotenv()

HEADERS = {"User-Agent": "AppPedidos/1.0"}


# ─────────────────────────────────────────────────────────────
# Ferramenta 1: consultar dados do cliente no app
# ─────────────────────────────────────────────────────────────
def buscar_usuario_app(cliente_id: int) -> dict:
    """
    Busca informações sobre o cliente no nosso backend fictício.
    Ex.: nível de digitalização, uso de promoções, clube de vantagens etc.
    """

    try:
        resposta = requests.get(
            f"https://api.exemplo.com/clientes/{cliente_id}",
            timeout=5,
            headers=HEADERS,
        )

        if resposta.status_code != 200:
            return {
                "erro": True,
                "mensagem": f"Cliente {cliente_id} não encontrado."
            }

        return resposta.json()

    except Exception as e:
        return {"erro": True, "mensagem": str(e)}



# ─────────────────────────────────────────────────────────────
# Ferramenta 2: gerar sugestões para aumentar o uso do app
# ─────────────────────────────────────────────────────────────
def gerar_recomendacao_adesao(perfil: dict) -> str:
    """
    Gera dicas práticas e personalizadas para aumentar a adesão do cliente
    aos recursos digitais do app.
    """

    nome = perfil.get("nome", "Cliente")
    usa_clube = perfil.get("usa_clube", False)
    usa_promos = perfil.get("usa_promocoes", False)
    pedidos_app = perfil.get("pedidos_app", 0)

    mensagens = [f"Recomendações para {nome}:\n"]

    if not usa_clube:
        mensagens.append(
            "- Ele ainda não participa do nosso Clube de Benefícios. "
            "Sugira a adesão destacando vantagens imediatas (ex.: cashback, pontos, descontos exclusivos)."
        )

    if not usa_promos:
        mensagens.append(
            "- Não está usando promoções. Recomende mostrar onde ficam as promoções no app e destacar 1 ou 2 que fazem sentido para ele."
        )

    if pedidos_app < 3:
        mensagens.append(
            "- Possivelmente não está familiarizado com o app. Sugira um passo a passo simples (2–3 passos) para realizar pedidos."
        )

    if usa_clube and usa_promos and pedidos_app > 10:
        mensagens.append(
            "- Cliente já bem digitalizado! Sugira recursos avançados como favoritos, lembretes e ofertas personalizadas."
        )

    return "\n".join(mensagens)



# ─────────────────────────────────────────────────────────────
# Modelo
# ─────────────────────────────────────────────────────────────
modelo = OpenRouterModel("openai/gpt-4o-mini")

agente = Agent(
    model=modelo,
    tools=[buscar_usuario_app, gerar_recomendacao_adesao],
    system_prompt=(
        "Você é um consultor de engajamento digital. "
        "Sempre consulte os dados do cliente e gere recomendações personalizadas "
        "usando as ferramentas disponíveis."
    ),
)


# Execução
pergunta = "Quero recomendações para aumentar o uso do app do cliente 42."
resposta = agente.run_sync(pergunta)

print(resposta.output)
print("\nChamadas à API:", resposta.usage().requests)