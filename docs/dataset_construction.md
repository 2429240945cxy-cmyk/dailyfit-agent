# Dataset Construction

Nutrition v2 combines public USDA-style reference values, HPB/FOCOS-style manual
local dish cache rows, and adversarial unit/synonym/typo cases. No LLM fills
nutrition numbers.

Guardian v2 is hand-authored from public health warnings and forum-pattern
paraphrases. Labels are not generated from `policy.py`.

Memory v2 uses anonymized public fitness/nutrition conversation patterns. This
is a limitation until real user interviews can be consented and de-identified.

E2E v2 combines tool use, memory, guardian intervention, and source attribution.
