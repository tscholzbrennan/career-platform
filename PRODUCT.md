# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Primary: recruiters and hiring managers filling full-time **data analyst** and **business analyst** roles, screening a candidate who graduates in May 2027. They arrive from a resume, LinkedIn, or a forwarded link, often with many candidate tabs open, and decide in under a minute whether to reach out.

Secondary (from the original spec): early-stage founders, startup teams, collaborators, and professional network contacts.

## Product Purpose

A personal career site for Tristan Scholz-Brennan. It exists to get the right recruiter to contact him for a full-time data/business analyst role after graduation. Success means a recruiter can tell within seconds who he is, what role he is targeting, and why he is credible, then reach him by email or LinkedIn, or get his resume.

## Positioning

An analyst who knows AI and uses it in ways that add value for stakeholders. That claim rests on:
- an Information Systems & Business Analytics degree at LMU (May 2027, 3.8 GPA);
- hands-on operations experience in budget analysis, contract oversight, scheduling, and live event production;
- having built and run this site himself (FastAPI, SQLite, Azure VM).

The combination of analytics training, real operations experience, and practical AI use is the claim a generic analytics graduate could not truthfully copy.

## Operating Context

- Recruiters evaluate the site next to his resume and LinkedIn profile, so the facts must match across all three.
- Content is stored in SQLite (`career_platform.db`), covering profile, experiences, projects, education, skills, and media. The FastAPI app renders it with Jinja templates.
- The site runs on an Azure VM over HTTPS (see `docs/superpowers/plans/`).

## Capabilities and Constraints

- Pages: Home, About, Experience, Projects, Project detail, Resume, Contact, and the `/api/profile` JSON endpoint.
- **The site must stay readable when the database is unavailable.** It serves a fallback snapshot (`data/fallback-profile.json`) with core identity, summary, featured projects, and contact links.
- Content is edited in the database, not hard-coded in templates.
- v1 scope does not include authentication, user accounts, a job board, or a CMS beyond a lightweight editor.
- Open: whether an inquiry form on Contact is wanted. The spec lists it as optional.

## Brand Commitments

- His full name, Tristan Scholz-Brennan, is the identity. The site currently fails to show it.
- Target role language: "data analyst" and "business analyst", full-time, starting after the May 2027 graduation.

## Evidence on Hand

- **Education:** Loyola Marymount University, BBA in Information Systems and Business Analytics, May 2027. GPA 3.8/4.0. Arrupe Scholarship (merit-based). Dean's List.
- **Experience:**
  - Facility Production Intern, West EFX: budget analysis, contract oversight, scheduling. May 2018 – Aug 2024 (dates confirmed by Tristan on 2026-10-08).
  - Event Operations Technician, Collins Visual Media & Step and Repeat LA (May–Aug 2025).
  - Member, Info Systems and Business Statistics Society (since Aug 2023).
- **Skills:**
  - Technical: SQL, Python, NoSQL, Excel, Access, PowerPoint, Word, trend analysis, data scraping, hardware configuration.
  - Certifications: Microsoft Office Excel Associate, Bloomberg Market Concepts.
- **Project:** Career Platform, this site. It is a class project involving AI and cloud computing services. Tristan built it with AI coding agents (Claude Code), using plugins such as Superpowers to keep the work organized and the code sound, through written specs, plans, and test-driven changes. The process is documented in `docs/superpowers/specs/` and `docs/superpowers/plans/`. It is deployed on an Azure VM with HTTPS (`docs/how-this-site-is-secured.md`). **This is the evidence behind the AI positioning.**
- **LinkedIn:** https://www.linkedin.com/in/tristan-scholz-brennan-a7a1922a0 (confirmed 2026-10-08; the database still holds the bare `https://www.linkedin.com`)
- **Source resume:** `Tristan resume 9:29:2026.docx` (untracked, in repo root).
- **Missing; must not be invented:**
  - a resume PDF;
  - a headshot (`profile_image` is empty; not available for now, so design must work without one);
  - project screenshots;
  - quantified outcomes or metrics;
  - **any AI work beyond the Career Platform project.** Do not fabricate other AI projects, tools, or results.

## Product Principles

1. **Identity first.** His name, target role, and graduation date are readable in the first seconds on every page and in every browser tab.
2. **Every claim is backed.** Show the evidence (GPA, roles, skills, built-and-deployed site) instead of adjectives. Never invent metrics or AI accomplishments.
3. **The contact path never breaks.** Email, LinkedIn, and resume download work from any page, including in fallback mode.
4. **Analyst plus operator plus AI.** Present the analytics, operations, and AI pieces as one connected story, not three separate lists.
5. **Maintained in the database.** Content changes happen in the data, not in the templates.
