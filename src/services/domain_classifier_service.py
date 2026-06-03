from __future__ import annotations

import math
import re
from typing import Dict, List, Set

from config.domain_list import DOMAIN_LIST
from config.domain_profiles import (
    DOMAIN_PROFILES,
    FLAG_WEIGHT,
    GRAPH_PROPAGATION_FACTOR,
    IDENTIFIER_WEIGHT,
    IMPORT_WEIGHT,
    MIN_REPORTED_SCORE,
    NAME_WEIGHT,
    PATH_WEIGHT,
    SCORE_SCALE,
    TABLE_WEIGHT,
    DomainProfile,
)
from src.model.file_node import FileNode

_TOKEN_RE = re.compile(r"[a-z0-9_]+")

DOMAIN_BY_KEY = {domain.lower(): domain for domain in DOMAIN_LIST}


def _domain_key(domain: str) -> str:
    return domain.lower()


def _tokens(text: str) -> Set[str]:
    return set(_TOKEN_RE.findall(text.lower()))


def _term_matches(term: str, corpus: str, tokens: Set[str]) -> bool:
    term = term.lower()
    if not term:
        return False
    if " " in term or "-" in term:
        return term.replace("-", "_") in corpus or term in corpus
    if term in tokens:
        return True
    if len(term) <= 3:
        return (
            f"/{term}/" in corpus
            or f"_{term}_" in corpus
            or f"-{term}-" in corpus
            or corpus.endswith(f"/{term}")
            or corpus.startswith(f"{term}/")
            or f"/{term}." in corpus
        )
    return (
        f"_{term}_" in corpus
        or f"/{term}/" in corpus
        or f"/{term}." in corpus
        or f".{term}." in corpus
        or f"{term}_" in corpus
        or f"_{term}" in corpus
        or corpus.endswith(f"/{term}")
        or corpus.endswith(f"_{term}")
    )


def _join_corpus(node: FileNode) -> str:
    parts: List[str] = [
        node.file_path or "",
        node.file_name or "",
    ]
    for collection in (
        node.class_list,
        node.function_list,
        node.import_list,
        node.database_tables,
        node.crypto_algorithm,
        node.graph_incoming_edges,
        node.graph_outgoing_edges,
    ):
        if collection:
            parts.extend(str(item) for item in collection)
    return " ".join(parts).lower()


def _profile_hits(profile: DomainProfile, corpus: str, tokens: Set[str]) -> float:
    score = 0.0

    for term in profile.path_terms:
        if _term_matches(term, corpus, tokens):
            score += PATH_WEIGHT
    for term in profile.name_terms:
        if _term_matches(term, corpus, tokens):
            score += NAME_WEIGHT
    for term in profile.import_terms:
        if _term_matches(term, corpus, tokens):
            score += IMPORT_WEIGHT
    for term in profile.identifier_terms:
        if _term_matches(term, corpus, tokens):
            score += IDENTIFIER_WEIGHT
    for term in profile.table_terms:
        if _term_matches(term, corpus, tokens):
            score += TABLE_WEIGHT

    return score


def _flag_hits(
    profile: DomainProfile,
    node: FileNode,
    taxonomy_hits: float,
    domain: str,
) -> float:
    security_flags_only = domain == "Security" and taxonomy_hits <= 0
    if taxonomy_hits <= 0 and not security_flags_only:
        return 0.0
    score = 0.0
    for flag_name, boost in profile.flag_boosts.items():
        if getattr(node, flag_name, False):
            score += boost * FLAG_WEIGHT
    return score


def _raw_domain_scores(node: FileNode) -> Dict[str, float]:
    corpus = _join_corpus(node)
    tokens = _tokens(corpus)
    scores: Dict[str, float] = {}

    for domain in DOMAIN_LIST:
        profile = DOMAIN_PROFILES.get(domain)
        if profile is None:
            continue
        taxonomy = _profile_hits(profile, corpus, tokens)
        raw = taxonomy + _flag_hits(profile, node, taxonomy, domain)
        scores[domain] = raw

    return scores


def _calibrate(raw: float) -> float:
    if raw <= 0:
        return 0.0
    return round(1.0 - math.exp(-raw / SCORE_SCALE), 2)


def _security_flag_domains(node: FileNode) -> Dict[str, float]:
    """Direct security-domain assignment from analyzer flags (not generic I/O)."""
    domains: Dict[str, float] = {}
    if node.contains_crypto_usage:
        domains["security"] = max(domains.get("security", 0.0), 0.45)
    if node.contains_auth_usage:
        domains["security"] = max(domains.get("security", 0.0), 0.35)
    return domains


def _select_candidate_domains(calibrated: Dict[str, float]) -> Dict[str, float]:
    positive = {d: s for d, s in calibrated.items() if s > 0}
    if not positive:
        return {}

    ordered = sorted(positive.items(), key=lambda item: item[1], reverse=True)
    primary_score = ordered[0][1]

    selected: Dict[str, float] = {}
    for domain, score in ordered:
        if score >= MIN_REPORTED_SCORE:
            selected[_domain_key(domain)] = score
        elif primary_score >= MIN_REPORTED_SCORE and score >= primary_score * 0.35:
            selected[_domain_key(domain)] = score

    return selected


def _graph_propagate(
    file_nodes: List[FileNode],
    domain_scores: Dict[str, Dict[str, float]],
) -> Dict[str, Dict[str, float]]:
    path_to_node = {node.file_path: node for node in file_nodes}
    adjusted = {path: dict(scores) for path, scores in domain_scores.items()}

    for node in file_nodes:
        neighbors: List[FileNode] = []
        for edge_path in node.graph_outgoing_edges or []:
            neighbor = path_to_node.get(edge_path)
            if neighbor:
                neighbors.append(neighbor)
        for edge_path in node.graph_incoming_edges or []:
            neighbor = path_to_node.get(edge_path)
            if neighbor:
                neighbors.append(neighbor)

        if not neighbors:
            continue

        propagated: Dict[str, float] = {}
        for neighbor in neighbors:
            for domain, score in domain_scores.get(neighbor.file_path, {}).items():
                propagated[domain] = max(propagated.get(domain, 0.0), score)

        if not propagated:
            continue

        current = adjusted[node.file_path]
        for domain, score in propagated.items():
            boost = round(score * GRAPH_PROPAGATION_FACTOR, 2)
            if boost <= 0:
                continue
            merged = round(min(1.0, current.get(domain, 0.0) + boost), 2)
            if merged > 0:
                current[domain] = merged

    return adjusted


def _classify_node(node: FileNode, graph_adjusted: Dict[str, float]) -> Dict[str, float]:
    raw = _raw_domain_scores(node)
    calibrated = {domain: _calibrate(value) for domain, value in raw.items()}

    for domain_key, score in _security_flag_domains(node).items():
        domain_name = DOMAIN_BY_KEY.get(domain_key)
        if domain_name:
            calibrated[domain_name] = round(max(calibrated.get(domain_name, 0.0), score), 2)

    for domain_key, score in graph_adjusted.items():
        domain_name = DOMAIN_BY_KEY.get(domain_key)
        if not domain_name:
            continue
        existing = calibrated.get(domain_name, 0.0)
        calibrated[domain_name] = round(min(1.0, max(existing, score)), 2)

    return _select_candidate_domains(calibrated)


def classify_file_nodes(file_nodes: List[FileNode]) -> List[FileNode]:
    preliminary: Dict[str, Dict[str, float]] = {}
    for node in file_nodes:
        raw = _raw_domain_scores(node)
        calibrated = {domain: _calibrate(value) for domain, value in raw.items()}
        preliminary[node.file_path] = _select_candidate_domains(calibrated)

    propagated = _graph_propagate(file_nodes, preliminary)

    assignments: Dict[str, Dict[str, float]] = {}
    for node in file_nodes:
        assignments[node.file_path] = _classify_node(
            node,
            propagated.get(node.file_path, {}),
        )

    for node in file_nodes:
        node.candidate_domains = assignments[node.file_path]

    return file_nodes
