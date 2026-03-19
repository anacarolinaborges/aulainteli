import json
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.openrouter import OpenRouterModel

load_dotenv()

# =====================================================================
# Ferramentas internas usadas somente QUANDO o usuário enviar seu problema
# =====================================================================

def decompor_problema(contexto: str) -> dict:
    """
    Identifica subtarefas relevantes dentro do contexto.
    """
    tarefas = []
    ctx = contexto.lower()

    if any(w in ctx for w in ["analisar", "análise", "sentimento", "classificar"]):
        tarefas.append({
            "name": "Análise de Conteúdo",
            "independent": False,
            "requires_specialist": True,
            "tools": ["modelo de classificação", "métodos de análise de sentimentos"]
        })

    if any(w in ctx for w in ["extrair", "dados", "coletados", "input"]):
        tarefas.append({
            "name": "Extração / Parsing",
            "independent": True,
            "requires_specialist": False,
            "tools": ["parser de texto", "limpeza de dados"]
        })

    if any(w in ctx for w in ["gerar", "relatório", "síntese", "produzir"]):
        tarefas.append({
            "name": "Síntese e Geração",
            "independent": False,
            "requires_specialist": False,
            "tools": ["modelo generativo"]
        })

    if not tarefas:
        tarefas = [
            {
                "name": "Entendimento do Problema",
                "independent": False,
                "requires_specialist": False,
                "tools": ["interpretação semântica"]
            }
        ]

    return {"subtasks": tarefas}


def recomendar_arquitetura(subtasks: list) -> dict:
    """
    Decide qual arquitetura multiagente é mais indicada.
    """
    n = len(subtasks)

    if n == 1:
        return {
            "architecture": "Routing",
            "reason": "A tarefa é simples e exige um único agente especializado."
        }

    if n > 1 and all(t.get("independent") for t in subtasks):
        return {
            "architecture": "Parallelization",
            "reason": "As subtarefas são independentes e podem ser executadas simultaneamente."
        }

    if any(t.get("requires_specialist") for t in subtasks):
        return {
            "architecture": "Orchestrator-Workers",
            "reason": "As tarefas exigem especialistas coordenados por um orquestrador."
        }

    return {
        "architecture": "Prompt Chaining",
        "reason": "As subtarefas dependem umas das outras em sequência lógica."
    }


def montar_agentes(subtasks: list) -> dict:
    """
    Cria agentes baseados nas subtarefas.
    """
    agentes = []

    for task in subtasks:
        agentes.append({
            "name": f"Agente de {task['name']}",
            "responsibilities": task["name"],
            "tools": task["tools"],
            "inputs": ["contexto"] if task["name"] == "Entendimento do Problema" else ["saída anterior"],
            "outputs": [f"resultado de {task['name']}"]
        })

    return {"agents": agentes}


# =====================================================================
# AGENTE PRINCIPAL – estilo idêntico ao seu código original
# =====================================================================

orquestrador = Agent(
    model=OpenRouterModel("openai/gpt-4o-mini"),
    tools=[decompor_problema, recomendar_arquitetura, montar_agentes],
    system_prompt=(
        "Você é um agente orquestrador multiagente. "
        "Primeiro, sempre cumprimente e pergunte: "
        "'Com o que posso ajudar hoje?'\n"
        "\n"
        "Quando o usuário enviar um PROBLEMA ou CONTEXTO, faça o seguinte:\n"
        "1. Use a ferramenta 'decompor_problema' para identificar subtarefas.\n"
        "2. Use a ferramenta 'montar_agentes' para propor os agentes necessários.\n"
        "3. Use 'recomendar_arquitetura' para escolher a arquitetura ideal.\n"
        "4. Retorne tudo em JSON com:\n"
        "   - quantidade de agentes\n"
        "   - agentes e ferramentas\n"
        "   - arquitetura recomendada\n"
        "   - justificativa\n"
        "\n"
        "IMPORTANTE: só use ferramentas QUANDO o usuário trouxer um problema real.\n"
        "Antes disso, apenas pergunte como pode ajudar."
    )
)

# =====================================================================
# EXEMPLO DE USO – mesmo estilo do seu código didático
# =====================================================================

if __name__ == "__main__":
    print("\n============================================")
    print("AGENTE ORQUESTRADOR — TESTE")
    print("============================================\n")

    # 1º contato → deve perguntar “com o que posso ajudar?”
    r1 = orquestrador.run_sync("Oi, tudo bem?")
    print("\n→ Resposta 1:")
    print(r1.output)

    # 2º contato → agora sim envia o problema real
    contexto = ()
