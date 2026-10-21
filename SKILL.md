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

### Primary sources beat paraphrase

If the target repo (or the user's workspace) has the actual legal texts —
the Act, the Regulations, ODPC guidance PDFs, often downloaded from
odpc.go.ke into a folder like `kdpa/` — **read them directly before writing
a legal citation.** Don't rely on a news article's summary, a secondary
source's paraphrase, or your own memory of what a section says.

This matters concretely: an earlier version of this skill described
Regulation 26's localization duty as covering "education, health care, and
public finance — run by state organs." That's wrong. The regulation's
actual text scopes the state-organ qualifier to the public-finance clause
only; the education and health-care clauses carry no such limit. That
difference changes whether the rule applies to a private platform at all.
Getting a citation like this wrong doesn't just misstate a fact — it can
flip a finding from "applies" to "doesn't apply." Pull the primary PDF,
`grep` or read it directly, and quote the operative sentence rather than
describing it from recollection.

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

3. **Cross-border data transfer — DPA Sections 48–49.**
   Section 48: "A data controller or data processor may transfer personal
   data to another country only where— (a)/(b) [proof to the Data
   Commissioner of] appropriate safeguards... or (c) the transfer is
   necessary— (i) for the performance of a contract between the data
   subject and the data controller... (ii) ...in the interest of the data
   subject... (iii) for any matter of public interest; (iv) for the
   establishment, exercise or defence of a legal claim; (v) [to protect]
   vital interests...; or (vi) for the purpose of compelling legitimate
   interests..." This is a **safeguards-or-necessity test that applies to
   every data controller, every transfer, for any reason** — it is the
   universal baseline, lighter in substance than Question 4 but much
   broader in reach. It does not ban data from leaving Kenya; it requires
   the controller to be able to show why the transfer is sound. Look for:
   cloud region config (`GCP_LOCATION`, `AWS_REGION`, `AZURE_REGION`,
   database host, Terraform/CloudFormation region blocks, deploy workflow
   env vars), and whether any document names which Section 48 ground is
   being relied on — most platforms can rely on 48(c)(i), contract
   performance, but it is rarely written down anywhere.

4. **Data localization for strategic sectors — DPA Section 50 + Regulation
   26(2).** Section 50 is the enabling power ("the Cabinet Secretary may
   prescribe... certain nature of processing that shall only be effected
   through a server or a data centre located in Kenya"). Regulation 26 is
   where that power was exercised. Regulation 26(1): a controller
   processing data for one of six listed purposes must "(a) process such
   personal data through a server and data centre located in Kenya; **or**
   (b) store at least one serving copy of the concerned personal data in a
   data centre located in Kenya" — note the "or": one serving copy
   satisfies it, a full migration is not required. The six purposes in
   Regulation 26(2), and **only these six**:
   - (a) civil registration / legal identity management systems
   - (b) running elections
   - (c) administering public finances, **"by any state organ"**
   - (d) a system designated "protected" under the Computer Misuse and
     Cybercrime Act, 2018
   - (e) **"offering any form of early childhood education and basic
     education under the Basic Education Act, 2013"**
   - (f) primary or secondary health care for a data subject in the country

   **The state-organ qualifier in (c) applies only to (c).** It is not a
   header over the whole list. Clauses (a), (b), (d), (e), and (f) carry no
   such limit — they apply to whoever carries out that activity, public or
   private. This is easy to get wrong by paraphrase (an earlier draft of
   this skill read it as "education and health care run by state organs,"
   which the regulation's actual text does not say). **Always read the
   regulation's own text before writing a verdict on this question** — see
   the note below on primary sources.

   Build a table like the one above, applying each of the six clauses to
   the target platform directly, with a yes/no and why. If any clause
   applies (most commonly (e), for any platform that delivers curriculum
   content, tutoring, or assessment to school-age students), the status is
   Not answered unless the repo shows a Kenya-based server or a Kenya-based
   serving copy of the data — and the fix to recommend is the lighter of
   the two options in 26(1), a serving copy, not a full regional migration.

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
