from __future__ import annotations

import hashlib
import json
import re
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Iterable, Mapping, Sequence


class EpistemicClass(str, Enum):
    OBSERVED_TEXT = "OBSERVED_TEXT"
    DERIVED_MENTION = "DERIVED_MENTION"
    DERIVED_INFERENCE = "DERIVED_INFERENCE"
    CONDITIONAL_HYPOTHESIS = "CONDITIONAL_HYPOTHESIS"


class GateDecision(str, Enum):
    QUARANTINE = "QUARANTINE"
    ADMIT_FOR_VALIDATION = "ADMIT_FOR_VALIDATION"


def _utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True, slots=True)
class RawObservation:
    raw_content: str
    source_ref: str
    offsets: tuple[int, int] | None = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    observed_at: str = field(default_factory=_utc_now)
    content_sha256: str = field(init=False)
    epistemic_class: EpistemicClass = field(default=EpistemicClass.OBSERVED_TEXT, init=False)

    def __post_init__(self) -> None:
        if not self.raw_content:
            raise ValueError("raw_content não pode ser vazio")
        if not self.source_ref:
            raise ValueError("source_ref não pode ser vazio")
        if self.offsets is not None:
            start, end = self.offsets
            if start < 0 or end < start:
                raise ValueError("offsets inválidos")
        object.__setattr__(self, "content_sha256", _sha256(self.raw_content))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "epistemic_class": self.epistemic_class.value,
            "raw_content": self.raw_content,
            "source_ref": self.source_ref,
            "offsets": list(self.offsets) if self.offsets is not None else None,
            "observed_at": self.observed_at,
            "content_sha256": self.content_sha256,
        }


@dataclass(frozen=True, slots=True)
class AspectLexicon:
    aliases: Mapping[str, tuple[str, ...]]
    positive_terms: frozenset[str]
    negative_terms: frozenset[str]
    contrast_terms: tuple[str, ...] = ("mas", "porém", "todavia", "contudo", "embora")
    detail_terms: frozenset[str] = frozenset(
        {
            "erro", "falha", "travou", "trava", "crash", "pagamento", "login",
            "pedido", "protocolo", "nota", "fiscal", "resposta", "dias", "horas",
            "minutos", "versão", "versao", "android", "ios", "cpf", "cartão", "cartao",
        }
    )

    @classmethod
    def ptbr_product_default(cls) -> "AspectLexicon":
        return cls(
            aliases={
                "design": ("design", "visual", "interface", "layout"),
                "atendimento": ("atendimento", "suporte", "serviço", "servico"),
                "performance": ("velocidade", "performance", "carregamento", "lento", "rápido", "rapido"),
                "preço": ("preço", "preco", "custo", "caro", "barato", "valor"),
                "funcionalidade": ("funcionalidade", "função", "funcao", "recurso", "feature"),
                "pagamento": ("pagamento", "checkout", "cartão", "cartao", "pix"),
            },
            positive_terms=frozenset(
                {"bom", "boa", "ótimo", "otimo", "excelente", "lindo", "linda", "rápido", "rapido", "eficiente", "amei", "adorei", "vale", "justo", "funciona"}
            ),
            negative_terms=frozenset(
                {"ruim", "péssimo", "pessimo", "lento", "lenta", "caro", "cara", "travou", "trava", "inútil", "inutil", "odiei", "horrível", "horrivel", "erro", "falha", "demora"}
            ),
        )


@dataclass(frozen=True, slots=True)
class DerivedMention:
    source_obs_id: str
    aspect: str
    sentiment: float
    confidence: float
    specificity_signal: float
    evidence_span: tuple[int, int]
    extractor_version: str
    method: str
    epistemic_class: EpistemicClass = field(default=EpistemicClass.DERIVED_MENTION, init=False)

    def __post_init__(self) -> None:
        if not -1.0 <= self.sentiment <= 1.0:
            raise ValueError("sentiment fora do intervalo [-1, 1]")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence fora do intervalo [0, 1]")
        if not 0.0 <= self.specificity_signal <= 1.0:
            raise ValueError("specificity_signal fora do intervalo [0, 1]")

    def to_dict(self) -> dict[str, Any]:
        return {
            "epistemic_class": self.epistemic_class.value,
            "source_obs_id": self.source_obs_id,
            "aspect": self.aspect,
            "sentiment": self.sentiment,
            "confidence": self.confidence,
            "specificity_signal": self.specificity_signal,
            "evidence_span": list(self.evidence_span),
            "extractor_version": self.extractor_version,
            "method": self.method,
        }


@dataclass(frozen=True, slots=True)
class AspectInference:
    id: str
    aspect: str
    source_obs_ids: tuple[str, ...]
    mention_count: int
    positive_count: int
    negative_count: int
    neutral_count: int
    positive_share: float
    negative_share: float
    tension_score: float
    detailed_negative_count: int
    mean_confidence: float
    epistemic_class: EpistemicClass = field(default=EpistemicClass.DERIVED_INFERENCE, init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "epistemic_class": self.epistemic_class.value,
            "aspect": self.aspect,
            "source_obs_ids": list(self.source_obs_ids),
            "mention_count": self.mention_count,
            "positive_count": self.positive_count,
            "negative_count": self.negative_count,
            "neutral_count": self.neutral_count,
            "positive_share": self.positive_share,
            "negative_share": self.negative_share,
            "tension_score": self.tension_score,
            "detailed_negative_count": self.detailed_negative_count,
            "mean_confidence": self.mean_confidence,
        }


@dataclass(frozen=True, slots=True)
class ProductHypothesis:
    id: str
    inference_id: str
    aspect: str
    kind: str
    action: str
    rationale: str
    priority: str
    source_obs_ids: tuple[str, ...]
    epistemic_class: EpistemicClass = field(default=EpistemicClass.CONDITIONAL_HYPOTHESIS, init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "epistemic_class": self.epistemic_class.value,
            "inference_id": self.inference_id,
            "aspect": self.aspect,
            "kind": self.kind,
            "action": self.action,
            "rationale": self.rationale,
            "priority": self.priority,
            "source_obs_ids": list(self.source_obs_ids),
        }


@dataclass(frozen=True, slots=True)
class GateResult:
    hypothesis_id: str
    decision: GateDecision
    reasons: tuple[str, ...]
    receipt_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "hypothesis_id": self.hypothesis_id,
            "decision": self.decision.value,
            "reasons": list(self.reasons),
            "receipt_sha256": self.receipt_sha256,
        }


class ExplicitAspectSentimentExtractor:
    """Deterministic, versioned baseline. It emits no claim beyond matched evidence."""

    VERSION = "explicit-lexicon-v1"
    _WORD_RE = re.compile(r"[\wÀ-ÖØ-öø-ÿ]+", re.UNICODE)

    def __init__(self, lexicon: AspectLexicon | None = None) -> None:
        self.lexicon = lexicon or AspectLexicon.ptbr_product_default()
        self._alias_to_aspect = {
            alias.casefold(): aspect
            for aspect, aliases in self.lexicon.aliases.items()
            for alias in aliases
        }

    def extract(self, observation: RawObservation) -> list[DerivedMention]:
        tokens = [(match.group(0).casefold(), match.start(), match.end()) for match in self._WORD_RE.finditer(observation.raw_content)]
        if not tokens:
            return []

        clauses = self._clause_ranges(tokens, len(observation.raw_content))
        mentions: list[DerivedMention] = []
        seen: set[tuple[str, int, int]] = set()
        for clause_start, clause_end in clauses:
            clause = [token for token in tokens if clause_start <= token[1] < clause_end]
            if not clause:
                continue
            positive = sum(1 for value, _, _ in clause if value in self.lexicon.positive_terms)
            negative = sum(1 for value, _, _ in clause if value in self.lexicon.negative_terms)
            sentiment = self._sentiment(positive, negative)
            detail = self._detail_score(clause)
            if sentiment == 0.0:
                continue
            for value, start, end in clause:
                aspect = self._alias_to_aspect.get(value)
                if aspect is None:
                    continue
                key = (aspect, start, end)
                if key in seen:
                    continue
                seen.add(key)
                confidence = self._confidence(sentiment, positive, negative, detail)
                mentions.append(
                    DerivedMention(
                        source_obs_id=observation.id,
                        aspect=aspect,
                        sentiment=sentiment,
                        confidence=confidence,
                        specificity_signal=detail,
                        evidence_span=(start, end),
                        extractor_version=self.VERSION,
                        method="explicit_lexicon_clause_local",
                    )
                )
        return mentions

    def _clause_ranges(self, tokens: Sequence[tuple[str, int, int]], text_length: int) -> list[tuple[int, int]]:
        starts = [0]
        ends: list[int] = []
        for value, start, end in tokens:
            if value in self.lexicon.contrast_terms:
                ends.append(start)
                starts.append(end)
        ends.append(text_length)
        return [(start, end) for start, end in zip(starts, ends, strict=True) if start < end]

    @staticmethod
    def _sentiment(positive: int, negative: int) -> float:
        total = positive + negative
        if total == 0 or positive == negative:
            return 0.0
        return round((positive - negative) / total, 4)

    def _detail_score(self, clause: Sequence[tuple[str, int, int]]) -> float:
        values = {value for value, _, _ in clause}
        detail_hits = len(values & self.lexicon.detail_terms)
        numeric_hits = sum(1 for value, _, _ in clause if any(char.isdigit() for char in value))
        signal = min(1.0, 0.15 * detail_hits + 0.15 * numeric_hits)
        return round(signal, 4)

    @staticmethod
    def _confidence(sentiment: float, positive: int, negative: int, detail: float) -> float:
        polarity_evidence = min(1.0, (positive + negative) / 2)
        return round(min(0.95, 0.45 + 0.35 * polarity_evidence + 0.20 * detail + 0.10 * abs(sentiment)), 4)


class AspectInferenceEngine:
    VERSION = "aspect-distribution-v1"

    def infer(self, mentions: Iterable[DerivedMention]) -> list[AspectInference]:
        grouped: dict[str, list[DerivedMention]] = defaultdict(list)
        for mention in mentions:
            grouped[mention.aspect].append(mention)

        inferences: list[AspectInference] = []
        for aspect, group in sorted(grouped.items()):
            positive = sum(1 for item in group if item.sentiment > 0)
            negative = sum(1 for item in group if item.sentiment < 0)
            neutral = len(group) - positive - negative
            total = len(group)
            tension = 0.0 if total == 0 else round((4 * positive * negative) / (total * total), 4)
            source_ids = tuple(sorted({item.source_obs_id for item in group}))
            evidence_seed = "|".join([self.VERSION, aspect, *source_ids])
            inferences.append(
                AspectInference(
                    id=str(uuid.uuid5(uuid.NAMESPACE_URL, evidence_seed)),
                    aspect=aspect,
                    source_obs_ids=source_ids,
                    mention_count=total,
                    positive_count=positive,
                    negative_count=negative,
                    neutral_count=neutral,
                    positive_share=round(positive / total, 4),
                    negative_share=round(negative / total, 4),
                    tension_score=tension,
                    detailed_negative_count=sum(1 for item in group if item.sentiment < 0 and item.specificity_signal >= 0.15),
                    mean_confidence=round(sum(item.confidence for item in group) / total, 4),
                )
            )
        return sorted(inferences, key=lambda item: (item.tension_score, item.detailed_negative_count, item.mention_count), reverse=True)


class ProductHypothesisEngine:
    VERSION = "product-hypothesis-v1"

    def generate(self, inferences: Iterable[AspectInference]) -> list[ProductHypothesis]:
        hypotheses: list[ProductHypothesis] = []
        for inference in inferences:
            if inference.detailed_negative_count:
                hypotheses.append(self._build(inference, "VALIDATE_FAILURE", "ALTA", f"Reproduzir e classificar a falha relatada em '{inference.aspect}' antes de qualquer correção.", f"{inference.detailed_negative_count} menção(ões) negativa(s) com sinais de detalhe foram detectadas; a relação com impacto operacional ainda precisa de validação."))
            elif inference.tension_score >= 0.60:
                hypotheses.append(self._build(inference, "SEGMENT_AND_VALIDATE", "MÉDIA", f"Segmentar as percepções sobre '{inference.aspect}' por contexto de uso e validar a causa da divergência.", "Há distribuição de polaridades opostas; isso indica heterogeneidade observada, não uma causa comprovada."))
            elif inference.positive_share >= 0.80 and inference.mention_count >= 3:
                hypotheses.append(self._build(inference, "VALIDATE_STRENGTH", "BAIXA", f"Validar '{inference.aspect}' como possível força de produto com uma amostra adicional.", "A distribuição observada é majoritariamente positiva, mas exige confirmação fora desta amostra."))
        return hypotheses

    def _build(self, inference: AspectInference, kind: str, priority: str, action: str, rationale: str) -> ProductHypothesis:
        seed = "|".join([self.VERSION, inference.id, kind])
        return ProductHypothesis(
            id=str(uuid.uuid5(uuid.NAMESPACE_URL, seed)),
            inference_id=inference.id,
            aspect=inference.aspect,
            kind=kind,
            action=action,
            rationale=rationale,
            priority=priority,
            source_obs_ids=inference.source_obs_ids,
        )


class OmegaGate:
    """Admits only derived hypotheses for validation; it never mutates raw observations."""

    def __init__(self, *, min_source_observations: int = 2, min_mean_confidence: float = 0.60) -> None:
        if min_source_observations < 1:
            raise ValueError("min_source_observations deve ser >= 1")
        if not 0.0 <= min_mean_confidence <= 1.0:
            raise ValueError("min_mean_confidence deve estar entre 0 e 1")
        self.min_source_observations = min_source_observations
        self.min_mean_confidence = min_mean_confidence

    def evaluate(self, hypothesis: ProductHypothesis, inference: AspectInference) -> GateResult:
        reasons: list[str] = []
        if len(hypothesis.source_obs_ids) < self.min_source_observations:
            reasons.append("evidência insuficiente: menos observações independentes que o mínimo configurado")
        if inference.mean_confidence < self.min_mean_confidence:
            reasons.append("confiança média do extrator abaixo do limiar configurado")
        decision = GateDecision.QUARANTINE if reasons else GateDecision.ADMIT_FOR_VALIDATION
        receipt = _sha256(_canonical_json({"hypothesis": hypothesis.to_dict(), "inference": inference.to_dict(), "decision": decision.value, "reasons": reasons}))
        return GateResult(hypothesis_id=hypothesis.id, decision=decision, reasons=tuple(reasons), receipt_sha256=receipt)


class KairosUranoPipeline:
    VERSION = "kairos-urano-v1"

    def __init__(self, extractor: ExplicitAspectSentimentExtractor | None = None, gate: OmegaGate | None = None) -> None:
        self.extractor = extractor or ExplicitAspectSentimentExtractor()
        self.inference_engine = AspectInferenceEngine()
        self.hypothesis_engine = ProductHypothesisEngine()
        self.gate = gate or OmegaGate()

    def run(self, records: Iterable[tuple[str, str]]) -> dict[str, Any]:
        run_id = str(uuid.uuid4())
        observations = [RawObservation(raw_content=text, source_ref=source) for text, source in records]
        mentions = [mention for observation in observations for mention in self.extractor.extract(observation)]
        inferences = self.inference_engine.infer(mentions)
        inference_by_id = {item.id: item for item in inferences}
        hypotheses = self.hypothesis_engine.generate(inferences)
        gate_results = [self.gate.evaluate(hypothesis, inference_by_id[hypothesis.inference_id]) for hypothesis in hypotheses]
        payload = {
            "run_id": run_id,
            "pipeline_version": self.VERSION,
            "executed_at": _utc_now(),
            "observations": [item.to_dict() for item in observations],
            "derived_mentions": [item.to_dict() for item in mentions],
            "inferences": [item.to_dict() for item in inferences],
            "hypotheses": [item.to_dict() for item in hypotheses],
            "gate_results": [item.to_dict() for item in gate_results],
        }
        payload["receipt_sha256"] = _sha256(_canonical_json(payload))
        return payload
