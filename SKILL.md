---
name: kenya-ai-regulatory-readiness
description: Audits a codebase against the 8 regulatory questions Kenya's Data Protection Act 2019, the ODPC's 2026 draft AI guidance, and (where relevant) the EU AI Act and NIST AI RMF raise for any platform that runs AI on personal data — automated decisions, impact assessments, cross-border transfer, data localization, AI-training lawful basis, AI-specific retention, vendor contract terms, and AI governance. Produces a dated Markdown + Word (.docx) report in reports/. Triggers on "Kenya AI readiness report", "AI regulatory readiness", "DPA AI compliance check", "is this platform AI-compliant for Kenya", or any request to assess a repo against Kenya's data protection / AI regulatory posture. Takes a local folder path or a GitHub repo URL.
---

# Kenya AI Regulatory Readiness

Kenya's AI Bill stalled in the Senate in October 2026 — but the Data Protection Act,
2019 already governs most enterprise AI, and the Office of the Data Protection
Commissioner (ODPC) has been sharpening its guidance all year. A platform that runs
AI on personal data is already regulated, Bill or no Bill.

This skill answers one question for a given codebase: **of the 8 things this
regulatory picture asks for, what has this platform actually built, and what is
still missing?** It does not guess. It reads the code, cites file paths, and
labels every answer Satisfactory, Partial, or Not answered.

## 1. Get the target

The user gives you either:
- **A local folder** — a path on this machine. Use it directly.
- **A GitHub URL** — clone it read-only into your scratchpad directory:
  ```bash
  git clone --depth 1 <url> "$SCRATCHPAD/kenya-ai-readiness-target"
  ```
  Never clone into the current project. Never push anything to the target repo
  unless the user separately asks you to.

Confirm which one you have before continuing.

## 2. Run discovery

Run the bundled script against the target. It only reads files — no network
calls beyond the clone above, nothing is sent anywhere.

```bash
bash ~/.claude/skills/kenya-ai-regulatory-readiness/scripts/discover.sh "<target_dir>"
```

It greps for the evidence each of the 8 questions below needs: existing compliance
docs, DPIA/impact-assessment mentions, cloud region config, AI vendor SDK usage
(and whether it's an enterprise channel like Vertex/Bedrock/Azure OpenAI vs. a
raw consumer API key), retention/deletion config, privacy-policy language on
automated decisions, vendor-contract references, and any AI safety/governance
code (judges, guardrails, moderation layers).

Treat the script's output as a lead list, not a verdict. Read the files it
surfaces. If a hit looks relevant, open it and check the actual logic — a
grep match is not evidence on its own.

## 3. Answer the 8 questions

For each question below: search further if the discovery output didn't settle
it, then write **Status** (Satisfactory / Partially answered / Not answered /
Cannot verify from code), **How it works now** (cite file:line), and **What's
needed** (concrete, ordered by effort — a privacy-policy sentence is not the
same size of task as a data-residency migration).

If a question plainly does not apply to this platform (e.g. no AI touches
personal data at all, or there is no EU exposure for the EU AI Act angle),
say so and move on — don't force a verdict where there's nothing to assess.

1. **Automated decisions with significant effect — DPA Section 35.**
   The right not to be subject to a decision based solely on automated
   processing that significantly affects the person, with written notice and
   a right to ask for reconsideration. Look for: certificates, scores,
   approvals, rejections, or placements that a model or a fixed threshold
   issues with no human step — and whether the privacy policy discloses it
   or offers a review path.

2. **Impact assessment before high-risk processing — DPA Section 31.**
   Required before high-risk processing. This is the exact gap that struck
   down Kenya's Huduma Namba card rollout (2021), paused Maisha Namba (2023),
   and sank Worldcoin's iris-scanning system (May 2025) — all three failed in
   court specifically because no impact assessment was done before go-live.
   Look for: any DPIA, privacy-impact-assessment, or equivalent document,
   anywhere in the repo, that names the AI features specifically — not just a
   general compliance doc.

3. **Cross-border data transfer — DPA Part VI.**
   Restricts moving personal data out of Kenya. Look for: cloud region
   config (`GCP_LOCATION`, `AWS_REGION`, `AZURE_REGION`, database host,
   Terraform/CloudFormation region blocks, deploy workflow env vars), and
   whether any compliance doc names a lawful basis for the transfer.

4. **Data localization for strategic sectors — DPA Section 50 + Regulation 26.**
   Certain sectors — including public finance, civil registration, basic
   education, and primary/secondary health care — must be processed in
   Kenya, or keep a serving copy there. If the platform touches any of these
   sectors, check whether any part of its data or processing has a Kenya
   presence, or whether this has been assessed at all.

5. **Lawful basis to train a third-party AI model — ODPC draft AI guidance
   (July 2026).** The guidance says personal data being publicly accessible
   does not, on its own, give a lawful basis to train on it. Look for which
   AI vendor channel is actually used in production: an enterprise channel
   (Vertex AI, AWS Bedrock, Azure OpenAI) typically does not train on
   customer data by default; a raw consumer API key (plain Gemini/OpenAI API
   key) typically does, unless opted out. Check every module that calls an
   LLM — it's common for one pathway to have been migrated to the enterprise
   channel and another to have been missed.

6. **Retention and deletion covering AI-specific data — ODPC draft AI
   guidance.** Retention and deletion policy should reach training data and
   anything that encodes personal information, not just the obvious database
   rows. Look for: the retention policy/config, and whether it mentions
   vector search indexes, embeddings, fine-tuned models, or cached AI
   outputs built from personal data.

7. **Vendor contract terms.** The four asks worth checking for: no training
   on your data, named data locations and sub-processors, a breach notice
   window (24 hours is the article's benchmark), and deletion on exit. This
   is usually **not verifiable from code** — say so plainly rather than
   guessing at a contract you can't see, and name it as a to-do for whoever
   holds the actual agreement.

8. **AI governance inventory — NIST AI RMF (Govern / Map / Measure / Manage)
   style.** Whether there is one place that lists every AI feature, what
   decision it makes, who owns it, and its risk tier. Separately check
   whether a "Measure" function already exists in the code — safety judges,
   guardrails, content moderation, confidence scoring — even if there's no
   single inventory tying it together. Call out real human-review
   mechanisms (e.g. a low-confidence queue a person actually works) as a
   strength; the article singles out fake human review (approving everything
   without looking) as a specific regulatory risk, citing the Dutch DPA's
   ~€825M fine against Uber for automated driver deactivation.

## 4. Write the report

Follow the `report` skill's structure and conventions exactly — same
`reports/YYYY-MM-DD_Short-Title.md` + `.docx` pair, same Verdict-first shape,
same evidence-first findings, same appendix of cited files. If the `report`
skill is available in this session, prefer it directly: pass it this skill's
findings and instruct it not to re-research. If it is not available (e.g. this
skill is being used in an environment without it), use the bundled converter:

```bash
python3 ~/.claude/skills/kenya-ai-regulatory-readiness/scripts/md2docx.py \
  "<target_dir>/reports/NAME.md" "<target_dir>/reports/NAME.docx"
```

Name the file `reports/YYYY-MM-DD_Kenya-AI-Regulatory-Readiness.md` (and
`.docx`), dated today, inside the **target** repo's root — not this skill's
folder, and not the project you happened to be sitting in when you ran this.

Render the `.docx` to PDF and actually look at the pages before delivering it
(`libreoffice --headless --convert-to pdf`). Don't hand over a document you
haven't read.

## 5. Deliver

Surface the `.docx` with SendUserFile. Summarize in chat: the verdict line,
and which of the 8 questions are the real gaps versus which are already
handled — a reader should get the shape of the answer without opening the
file.

## A note on scope

This skill assesses what the **code** shows. It cannot read a contract, judge
a legal question like "does Regulation 26 actually apply to us," or replace
counsel. Where the honest answer is "this needs a lawyer, not a line of code,"
say that — it's a legitimate finding, not a cop-out.
