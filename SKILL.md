---
name: matverse-blackstart
description: Automação para institucionalização científica e bootstrap de organismos digitais MatVerse. Use para publicar papers no Zenodo com DOI, organizar datasets no Hugging Face e executar o bootstrap de infraestruturas soberanas (Atlas, Runtime, Twin).
---

# MatVerse Blackstart Skill

Esta Skill automatiza o processo de transição de arquiteturas conceituais para objetos científicos operacionais e institucionalizados.

## Workflows Principais

### 1. Institucionalização Epistemológica (Zenodo)
- **Objetivo**: Obter DOIs permanentes para papers e artefatos.
- **Ação**: Use o script `scripts/zenodo_publish.py` para automatizar o upload de tarballs LaTeX/PDF.
- **Regra**: Sempre inclua o ORCID do autor e a afiliação "MatVerse Institute".

### 2. Organização do MatverseHub (Hugging Face)
- **Objetivo**: Centralizar datasets, modelos e documentação estratégica.
- **Ação**: Criar repositórios do tipo `dataset` para o Observatório Científico.
- **Arquivos Essenciais**: `MANIFESTO_DOIS.md`, `TEORIA_GERAL_UNIFICADA.md`, `SOVEREIGN_BOOTSTRAP_KIT.zip`.

### 3. Bootstrap do Organismo (Blackstart)
- **Objetivo**: Ativar a infraestrutura viva do MatVerse.
- **Ação**: Executar `scripts/bootstrap_organism.sh`.
- **Componentes**:
    - **Atlas**: Constituição selada com Merkle Root.
    - **Runtime**: Motor de execução com protocolo PBSE (PASS/BLOCK/SILENCE/ESCALATE).
    - **Twin**: Gêmeo digital espelhado para simulação e replay.

## Modelo de 3 Corpos (Invariantes)
Ao operar o organismo, siga rigorosamente a separação ontológica:
1. **Organismo**: Validação constitucional (Ψ ≥ 0.72).
2. **Cognição**: Geração de hipóteses (sem identidade "eu sou").
3. **Automação**: Registro de evidências e medição de falhas (α > 1).

## Recursos Bundled
- `scripts/bootstrap_organism.sh`: Script de criação de diretórios e invariantes base.
- `references/general_theory_template.md`: Template para o Paper de Unificação.
- `scripts/zenodo_publish.py`: Utilitário para integração com API Zenodo.

---
**Status**: Operacional - Nível de Soberania Digital: Blackstart.
