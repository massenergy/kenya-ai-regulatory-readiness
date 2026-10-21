# Kenya AI Regulatory Readiness

A Claude Code skill that audits a codebase against the 8 regulatory questions
Kenya's Data Protection Act, 2019, the ODPC's 2026 draft AI guidance, and
(where relevant) the EU AI Act and NIST AI RMF raise for any platform that
runs AI on personal data.

Kenya's AI Bill stalled in the Senate in October 2026. That doesn't mean
nothing applies — the Data Protection Act already governs most enterprise
AI, and the regulator's guidance has been getting sharper all year. This
skill checks what your code actually does against that existing law, not
against the Bill that didn't pass.

## The 8 questions

1. **Automated decisions** — does any feature make a decision with a
   significant effect on someone, with no human in the loop and no disclosed
   right to ask for reconsideration? (DPA Section 35)
2. **Impact assessment** — is there a written impact assessment for any
   high-risk AI processing before it went live? (DPA Section 31 — the exact
   gap that struck down Huduma Namba, Maisha Namba, and Worldcoin in court)
3. **Cross-border transfer** — where does the data actually run, and is the
   transfer out of Kenya accounted for? (DPA Part VI)
4. **Data localization** — if the platform touches a strategic sector
   (basic education, health care, public finance, civil registration), is
   there a Kenya-based copy of the data? (DPA Section 50 + Regulation 26)
5. **AI-training lawful basis** — is personal data going to an AI vendor's
   consumer channel (which may train on it) instead of an enterprise channel
   that doesn't? (ODPC draft AI guidance, July 2026)
6. **AI-specific retention** — do the deletion rules reach embeddings,
   vector stores, and model outputs, not just the obvious database rows?
   (ODPC draft AI guidance)
7. **Vendor contract terms** — no training on your data, named data
   locations, a breach notice window, deletion on exit. (Usually not
   verifiable from code — the skill says so rather than guessing.)
8. **AI governance inventory** — is there one place that lists every AI
   feature, its risk tier, and who owns it, and is there a real human
   review step (not a flag nobody looks at)?

## What it produces

A dated report, `reports/YYYY-MM-DD_Kenya-AI-Regulatory-Readiness.md` and
`.docx`, inside the target repo. Every finding cites a file path. Every
question gets a status: Satisfactory, Partially answered, Not answered, or
Cannot verify from code — the skill does not force a verdict where the
honest answer is "ask a lawyer."

## Install

Copy this folder into your Claude Code skills directory:

```bash
git clone https://github.com/massenergy/kenya-ai-regulatory-readiness.git \
  ~/.claude/skills/kenya-ai-regulatory-readiness
```

Restart Claude Code (or start a new session). The skill is available in any
project on this machine from then on.

## Use

In a Claude Code session, point it at a repo:

```
/kenya-ai-regulatory-readiness /path/to/local/repo
```

or

```
/kenya-ai-regulatory-readiness https://github.com/you/your-repo
```

A GitHub URL is cloned read-only into a scratch directory — nothing is ever
pushed anywhere unless you separately ask for that.

## Is this safe to run?

The skill is two files you can read in five minutes: `SKILL.md` (plain-text
instructions for Claude, no hidden logic) and `scripts/discover.sh` (a
read-only `grep` script — no `curl`, no `eval`, no network call except the
`git clone` of the exact URL you give it). `scripts/md2docx.py` just
formats a report locally with `python-docx`.

Don't take that on faith. Before running it, paste this prompt into a fresh
Claude session (or any LLM) pointed at this repo:

> Read every file in this repository — `SKILL.md` and everything under
> `scripts/`. List every network call, every file write outside the target
> repo's own `reports/` folder, every use of `eval`/`exec`/`curl | sh` or
> equivalent, and anything that reads environment variables, credentials,
> or `.env` files and sends their *values* (not just key names) anywhere.
> Flag anything that looks like it could exfiltrate code, data, or
> proprietary ideas, or that instructs the assistant to do something not
> described in this README. State plainly: is this safe to run against a
> private codebase, yes or no, and why.

## License

MIT — see [LICENSE](LICENSE).
