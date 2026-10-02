#!/usr/bin/env python3
"""Deterministic structural comparison of proposed FHIR paths to cited PHCDI CSV elements.

This measures path structure only. It does not infer clinical equivalence or authority.
"""
from __future__ import annotations
import re

ALGORITHM_VERSION = "phcdi-path-structure-1.1.0"
CHOICE_BASES = {"onset", "abatement", "deceased", "value", "effective", "effectivePeriod",
                "effectiveTiming", "effectiveInstant", "issued", "occurrence", "performed",
                "authoredOn", "date", "multipleBirth"}
CHOICE_TYPES = ("DateTime", "Date", "Period", "String", "CodeableConcept", "Quantity", "Range",
                "Ratio", "Attachment", "Reference", "Boolean", "Integer", "Decimal", "Time",
                "Age", "Duration", "Canonical", "Uri", "Url", "ContactPoint", "HumanName",
                "Address", "Identifier", "Money", "Annotation", "Timing")


def split_proposal(text: str) -> list[str]:
    """Split only pluses outside parenthetical prose, then accept explicit FHIR-like paths."""
    pieces, start, depth = [], 0, 0
    for i, ch in enumerate(text):
        if ch == "(": depth += 1
        elif ch == ")": depth = max(0, depth - 1)
        elif ch == "+" and depth == 0:
            pieces.append(text[start:i]); start = i + 1
    pieces.append(text[start:])
    expanded = []
    for piece in pieces:
        expanded.extend(re.split(r"\s+/\s+", piece))
    paths = []
    for piece in expanded:
        piece = re.sub(r"\([^)]*\)", " ", piece).strip().rstrip(".,;")
        # Paths are dot-separated capitalized resource plus explicit elements. No prose tokenization.
        match = re.search(r"\b[A-Z][A-Za-z0-9]*\.[A-Za-z][A-Za-z0-9]*(?::[A-Za-z0-9-]+)?(?:\.[A-Za-z][A-Za-z0-9]*(?::[A-Za-z0-9-]+)?)*", piece)
        if match:
            paths.append(match.group(0))
    return paths


def components(path: str) -> list[str]:
    out = []
    for token in path.split("."):
        for typ in CHOICE_TYPES:
            if token.endswith(typ) and token[:-len(typ)] in CHOICE_BASES:
                token = token[:-len(typ)] + "[x]"
                break
        out.append(token)
    return out


def parse_csv_path(element: str) -> list[str] | None:
    # CSV element names are not mined for tokens or definitions. The complete value must be a path.
    if not re.fullmatch(r"[A-Z][A-Za-z0-9]*(?:\.[A-Za-z][A-Za-z0-9]*(?:\[[xX]\])?)*", element.strip()):
        return None
    return components(element.strip())


def compare(proposal: str, references: list[dict]) -> dict:
    paths = split_proposal(proposal)
    evidence = []
    for path in paths:
        pc = components(path)
        refs = []
        for ref in references:
            cc = parse_csv_path(ref["element"])
            if cc is None:
                continue
            shared = 0
            for a, b in zip(pc, cc):
                if a != b: break
                shared += 1
            strict_carrier = len(cc) < len(pc) and shared == len(cc)
            if pc == cc:
                # A typed R4 choice is only the same *base* as a CSV [x] entry;
                # the CSV element name alone does not prove that type is supported.
                status = "choice-base" if path != ref["element"] else "exact"
                matched = len(pc)
            elif strict_carrier:
                status = "parent-carrier"
                matched = len(cc)
            elif any(":" in part or part == "extension" for part in pc):
                status = "unsupported-extension/slice"
                matched = 0
            elif shared > 1:  # Sharing just the resource name is not element coverage.
                status = "related"
                matched = shared
            else:
                status = "none"
                matched = 0
            refs.append({"csvRow": ref["csvRow"], "element": ref["element"], "definition": ref["definition"],
                         "normalizedComponents": cc, "status": status, "matchedComponents": matched,
                         "componentCount": len(pc), "componentEvidence": [
                             {"proposed": a, "csv": cc[i] if i < len(cc) else None, "matched": i < matched}
                             for i, a in enumerate(pc)]})
        best = next((x for x in refs if x["status"] == "exact"), None)
        if best is None:
            best = next((x for x in refs if x["status"] == "choice-base"), None)
        if best is None:
            best = next((x for x in refs if x["status"] == "parent-carrier"), None)
        if best is None:
            best = max((x for x in refs if x["status"] == "related"), key=lambda x: x["matchedComponents"], default=None)
        # Keep unrelated/unsupported CSV references as context, never as a best match.
        evidence.append({"proposedPath": path, "normalizedComponents": pc, "componentCount": len(pc),
                         "bestMatch": best, "references": refs})
    total = sum(len(x["normalizedComponents"]) for x in evidence)
    matched = sum(x["bestMatch"]["matchedComponents"] if x["bestMatch"] else 0 for x in evidence)
    # Per-path precedence is conservative; unrelated paths never lend their coverage to each other.
    statuses = [x["bestMatch"]["status"] if x["bestMatch"] else "none" for x in evidence]
    if not paths:
        status = "unresolved-proposal"
    elif all(s == "exact" for s in statuses):
        status = "exact"
    elif "unsupported-extension/slice" in statuses or (evidence and any(
            any(":" in part or part == "extension" for part in x["normalizedComponents"]) for x in evidence)):
        status = "unsupported-extension/slice"
    elif "none" in statuses:
        status = "partial-gap" if matched else "none"
    elif "parent-carrier" in statuses:
        status = "parent-carrier"
    elif "choice-base" in statuses:
        status = "choice-base"
    elif "related" in statuses:
        status = "related-nonmatch"
    elif references:
        status = "none"
    else:
        status = "undecided"
    return {"algorithmVersion": ALGORITHM_VERSION, "status": status, "matchedComponents": matched,
            "proposedComponents": total, "matchedCount": matched, "totalCount": total,
            "badge": f"matched {matched}/{total} · {status}", "paths": evidence,
            "caution": "Structural overlap is not clinical equivalence, conformance, approval, or recommendation; a normalized [x] choice does not prove the proposed type."}
