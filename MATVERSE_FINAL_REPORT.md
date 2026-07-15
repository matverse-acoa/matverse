# Relatório de Governança MatVerse: Demonstração Local Corrigida

**Estado revisado em:** 2026-07-15  
**Escopo:** gerador e manifesto de gênese com fixture sintética  
**Maturidade demonstrada:** `TESTED_FIXTURE`

## Correção epistemológica

A versão anterior deste relatório declarava **TRL 7**, **fechamento institucional**, tripla ancoragem pública e reprodução externa. O código associado, porém, utilizava valores explicitamente mock/sintéticos e um caminho absoluto dependente do ambiente local.

Por isso, as afirmações históricas ficam reclassificadas:

```text
TRL 7: HOLD_UNVERIFIED
INSTITUTIONALLY_CLOSED: HOLD_UNVERIFIED
Sepolia anchoring: NOT_VERIFIED_IN_THIS_REPOSITORY
Zenodo DOI: NOT_VERIFIED_IN_THIS_REPOSITORY
Hugging Face publication: NOT_VERIFIED_IN_THIS_REPOSITORY
external reproducibility: NOT_ESTABLISHED
local deterministic fixture replay: TESTED
```

O commit histórico não foi apagado. Este documento registra a correção e impede que demonstração local seja tratada como validação externa.

## 1. O que o artefato realmente demonstra

O arquivo `genesis_builder.py`:

- lê um dataset com classe epistemológica explícita;
- valida os campos numéricos no intervalo `[0, 1]`;
- calcula `Omega` e uma decisão de gate;
- gera hashes SHA-256 determinísticos para cada registro;
- calcula a raiz de Merkle;
- grava o manifesto de forma atômica em caminho configurável;
- detecta alteração de registros ou da raiz durante replay;
- preserva compatibilidade com o hash da demonstração de 2026-04-08.

Isso prova o comportamento desse caminho de código com uma fixture sintética. Não prova eficácia científica, segurança do ecossistema completo, operação institucional ou implantação pública.

## 2. Fixture e raiz retida

A fixture está em:

```text
data/fixtures/genesis_synthetic.json
```

Sua classificação obrigatória é:

```text
dataset_class: SYNTHETIC_FIXTURE
claim_scope: LOCAL_DETERMINISTIC_DEMONSTRATION_ONLY
external_validity: NOT_ESTABLISHED
```

A raiz histórica reproduzível permanece:

```text
87431dea7addb8a7aa0cfe6774739a98f3cd019313c2ef56e2722006f03d56fb
```

A preservação da raiz demonstra compatibilidade do algoritmo de hash com os mesmos valores e representação canônica. Ela não transforma os valores sintéticos em dados externos.

## 3. Execução reproduzível

Construir o manifesto com timestamp fixo:

```bash
python genesis_builder.py \
  --input data/fixtures/genesis_synthetic.json \
  --output /tmp/genesis_manifest.json \
  --timestamp 2026-04-08T13:21:54.739841+00:00
```

Verificar o replay:

```bash
python genesis_builder.py \
  --output /tmp/genesis_manifest.json \
  --verify-only
```

Executar os testes:

```bash
python -m unittest discover -s tests -v
```

Para builds reproduzíveis sem `--timestamp`, também é aceito `SOURCE_DATE_EPOCH`.

## 4. Testes cobertos

- raiz conhecida permanece estável;
- timestamp fixo produz manifesto idêntico;
- alteração de registro é detectada;
- métrica fora do intervalo é bloqueada;
- entrada e saída funcionam em diretórios temporários, sem caminho absoluto;
- workflow de CI reconstrói, verifica e confere a raiz retida.

## 5. Métricas e decisão

A fórmula implementada permanece:

```text
Omega = 0.4*Psi + 0.3*Theta_hat + 0.2*(1-CVaR) + 0.1*PoLE
```

Regra de decisão do demonstrador:

```text
Psi < 0.85 or CVaR > 0.05 -> BLOCK
Omega >= 0.85              -> PASS
otherwise                  -> CONDITIONAL
```

Esses limiares são parâmetros do código. Não são garantias científicas até que sejam justificados e validados contra dados adequados.

## 6. Estado atual correto

| Item | Estado |
|---|---|
| Fixture sintética identificada | PASS |
| Caminhos portáveis | PASS |
| Hash de registros | PASS |
| Raiz de Merkle reproduzível | PASS |
| Detecção de adulteração | PASS |
| Testes automatizados locais | PASS |
| CI do PR | PENDING_EXECUTION |
| Replay em segundo ambiente independente | HOLD |
| Evidência pública de Sepolia/Zenodo/Hugging Face | NOT_VERIFIED |
| Claim científico | BLOCK |
| Claim TRL 7 | HOLD_UNVERIFIED |
| Fechamento institucional | HOLD_UNVERIFIED |

## 7. Próximo gate

Para promover a maturidade, é necessário substituir ou complementar a fixture com dados de proveniência verificável, gerar um evidence pack completo e reproduzir a execução em um segundo ambiente independente.

Até lá, a formulação autorizada é:

> O MatVerse possui uma demonstração local, portátil e testada de manifesto de gênese com hash e replay sobre dados sintéticos; validade externa e fechamento institucional ainda não foram estabelecidos.
