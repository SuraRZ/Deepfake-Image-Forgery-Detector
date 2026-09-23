"""
Verdict Scoring
================

Combines the two independent signals (ELA hotspot size, metadata flags)
into one human-readable verdict. This is deliberately simple and
transparent — a weighted point system, not a black box — because in
forensics, being able to explain *why* a tool reached its conclusion
matters more than a fancy score. Every point added here has a stated
reason attached, which the UI displays directly to the user.

This is also the natural place to plug in a machine-learning classifier
later (see the README's "Future Work" section) — its confidence score
would just become another weighted input alongside these two.
"""


def build_verdict(metadata_flags, hotspot):
    score = 0
    reasons = []

    if hotspot:
        if hotspot["area_ratio"] > 0.08:
            score += 2
            reasons.append(
                f"Large localized high-error region covering ~{hotspot['area_ratio']*100:.1f}% of the image."
            )
        else:
            score += 1
            reasons.append(
                f"Moderate localized high-error region detected (~{hotspot['area_ratio']*100:.1f}% of image)."
            )

    score += len(metadata_flags)
    reasons.extend(metadata_flags)

    if score == 0:
        verdict = "No strong indicators of manipulation"
    elif score <= 2:
        verdict = "Some indicators present — inconclusive, worth a closer look"
    else:
        verdict = "Multiple indicators of possible manipulation"

    return verdict, reasons, score
