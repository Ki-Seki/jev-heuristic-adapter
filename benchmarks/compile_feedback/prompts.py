"""Frozen experiment prompts; the adapter's default prompt is unchanged."""

from jev_heuristic_adapter._prompt import SYSTEM_PROMPT

DESIGN = """# Classification objective
The runtime state is an English text string. Compile a classifier that covers
diverse unseen expressions, not just literal keywords from the label names.
Optimize both coverage and separation of confusable labels. Do not sacrifice
coverage merely to keep the source short. The complete task definition is binding.

# Evidence design
Choose a mechanism suited to this task. For intent classification, represent the
object, requested action, status, actor and transaction direction separately, then
combine those factors. Preserve competing interpretations until enough evidence
is available. Use supporting and excluding evidence for closely related labels.
For topic classification, distinguish the main event from incidental mentions.
For sentiment, distinguish an asserted quality from a desired or missing quality;
handle negation, concessions and contrast within their actual scope.

# Language coverage
Cover ordinary paraphrases, inflections, contractions, punctuation and reordered
clauses. Use reusable normalization and compositional features. Think beyond the
wording of the label descriptions. A long list of narrow regexes alone can leave
most real sentences unmatched. Check complete word forms and regex boundaries.

# Decision rules
Generic topic words alone do not establish a specific problem or requested action.
Specific supported evidence should outrank a broad phrase-prefix match. Handle
absent evidence and ties explicitly; label ordering must not silently decide the
prediction. Fallbacks do not substitute for coverage. Do not treat hand-written
scores as calibrated probabilities. Return exactly one of the allowed labels.

# Review
Consider positive examples, paraphrases and near-neighbour counterexamples for
each label. Check rule precedence, negative evidence and morphological variants.
Improve reusable mechanisms, not exact-string memorization. Return only source.
"""

IMPROVED_PROMPT = SYSTEM_PROMPT.replace(
    SYSTEM_PROMPT.split("# Generalization\n", 1)[1].split("# Source format", 1)[0],
    DESIGN + "\n",
)

SYNTHESIS_PROMPT = """Create a synthetic diagnostic dataset from a fixed text
classification task. You receive the complete question and target labels.
For each target label, produce exactly count_per_label independent English texts
with that answer. Vary wording, clause order, contractions and grammatical forms.
Include both easy cases and cases contrasting closely related labels. Many texts
should avoid copying the label's literal words. Use realistic standalone inputs,
not explanations or category names. For movie sentiment, use varied review-style
sentences, including indirect praise/criticism and concessive clauses. For news,
use short headline-plus-description inputs. For banking, use customer messages.
Respect the supplied category descriptions; do not invent extra category rules.
Do not retrieve or reproduce benchmark items. Do not include ambiguous cases that
the supplied definitions cannot resolve. Return only a JSON array of objects with
exactly two keys: state (text string) and answer (one of the target label strings).
"""

REVISION_INSTRUCTIONS = """Revise the previous program using actual execution
feedback from a fixed synthetic diagnostic set. These labels were model-generated
and can be imperfect; follow the task definition if a synthetic label contradicts
it. Improve general coverage and competing-evidence handling. Do not memorize
whole inputs, create exact-string overrides, or special-case test IDs. Retain
correct general behavior. Return the complete replacement Python source with the
same predict(state) contract. You will be evaluated on unseen real inputs.
"""
