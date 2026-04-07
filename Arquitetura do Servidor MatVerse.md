# Arquitetura do Servidor MatVerse

Este documento detalha a arquitetura proposta para o servidor MatVerse, um organismo digital autônomo. A arquitetura é centrada em um kernel Go leve e eficiente, expondo uma API REST e um stream de eventos em tempo real (SSE), complementado por um dashboard web para visualização e interação.

## 1. Visão Geral

O MatVerse é concebido como um sistema vivo, não uma simulação, onde o kernel Go gerencia o ciclo de vida de 'células' digitais. A interação com este organismo ocorre através de uma API bem definida e um dashboard em tempo real. O objetivo é criar um sistema robusto, com deploy simplificado e capacidade de mutação e crescimento.

## 2. Componentes Principais

A arquitetura do MatVerse é composta pelos seguintes elementos:

### 2.1. Kernel Go (matverse.kernel.go)

O coração do sistema, implementado em Go para alta performance e portabilidade. Este kernel é responsável por:

*   **Ciclo de Vida Autônomo**: Gerenciamento do estado e evolução das células digitais, incluindo mutação de parâmetros (`ψ`, `E`) a cada `tick` (3 segundos).
*   **Gerenciamento de Células**: Criação, alocação e decaimento de células na memória.
*   **API REST**: Exposição de endpoints para consulta do estado do organismo e injeção de perturbações/mutações.
*   **Server-Sent Events (SSE)**: Transmissão em tempo real do estado do organismo para clientes conectados.
*   **Persistência (Opcional)**: Embora não explicitamente detalhado no código fornecido, a menção de `artifacts/api-server` e `buf/` para checkpoints JSON brutos sugere uma capacidade de persistência.

### 2.2. API REST e SSE Endpoints

O kernel Go expõe os seguintes endpoints:

| Método | Endpoint                      | Descrição                                                              | Status de Implementação (Kernel Go) |
| :----- | :---------------------------- | :--------------------------------------------------------------------- | :---------------------------------- |
| `GET`  | `/api/organism/state`         | Retorna o estado vivo atual do organismo.                              | Parcial (dados internos)             |
| `GET`  | `/api/organism/stream`        | Stream de eventos em tempo real (SSE) do estado do organismo.          | Implementado                        |
| `GET`  | `/api/cells`                  | Retorna a lista de células vivas e seus parâmetros.                    | Parcial (dados internos)             |
| `GET`  | `/api/ledger`                 | Cadeia causal criptográfica (não implementado no kernel fornecido).    | Não Implementado                    |
| `POST` | `/api/organism/perturb`       | Injeta uma perturbação no organismo (não implementado no kernel fornecido). | Não Implementado                    |
| `POST` | `/api/organism/genome/mutate` | Muta parâmetros genômicos do organismo (não implementado no kernel fornecido). | Não Implementado                    |
| `POST` | `/api/cell/procreate`         | Aceita payload genômico para injetar novas células.                   | Implementado (`/api/cell/spawn`)    |

### 2.3. Dashboard Web (HTML/JS)

Um frontend web leve para visualizar o estado do organismo em tempo real e interagir com ele. Este dashboard consumirá os endpoints da API e o stream SSE para:

*   **Visualização em Tempo Real**: Exibir métricas como `tick`, `ψ` (psi), `cells` e `Ω` (Omega) através do stream SSE.
*   **Interação**: Fornecer uma interface para enviar comandos de mutação ou procriação de células via requisições POST para a API.
*   **Tecnologias**: HTML, CSS e JavaScript puro, possivelmente com bibliotecas leves para gráficos e manipulação de DOM.

## 3. Estrutura de Diretórios Proposta

```
matverse/
├── matverse.kernel.go        # Código fonte do kernel Go
├── matverse.bin              # Binário compilado do kernel Go
├── web/                      # Diretório para o dashboard web
│   ├── index.html            # Página principal do dashboard
│   ├── style.css             # Estilos CSS
│   └── app.js                # Lógica JavaScript para interação e SSE
├── local.pem                 # Certificado para HTTPS local (opcional)
└── buf/                      # Diretório para checkpoints JSON brutos (opcional)
```

## 4. Estratégias de Deploy

O sistema é projetado para ser deployado de forma flexível:

*   **Bare-metal/VPS**: Utilizando `systemd` para gerenciar o serviço do `matverse.bin`, garantindo que o organismo esteja sempre ativo e reinicie automaticamente em caso de falha.
*   **Plataformas PaaS (Railway, Fly.io)**: Através de containers ou imagens pré-construídas, como a imagem Google Cloud Native mencionada, para um deploy rápido e escalável.

## 5. Próximos Passos

1.  **Implementação Completa do Kernel Go**: Refinar e completar os endpoints da API conforme a especificação.
2.  **Desenvolvimento do Dashboard Web**: Criar a interface de usuário para visualização e interação.
3.  **Testes Abrangentes**: Validar o funcionamento de todos os componentes e a comunicação entre eles.
4.  **Documentação Detalhada**: Elaborar guias de deploy e uso para cada plataforma.

---

**Autor**: Manus AI
**Data**: 25 de Março de 2026
