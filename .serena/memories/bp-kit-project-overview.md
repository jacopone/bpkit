# BP-Kit Project Overview

## Purpose
Transform Sequoia Capital pitch decks into executable MVP specifications for AI agents through constitutional decomposition.

## Core Workflow
1. Business Plan (Sequoia Pitch Deck) → `/bp.decompose` → Strategic Constitutions (4 files) + Feature Constitutions (5-10 files)
2. Feature Constitutions → `/speckit.implement` → AI agents build MVP
3. Product learnings → Constitution updates → `/bp.sync --to-deck` → Updated pitch deck for investors

## Tech Stack
- Python 3.11+ with Typer (CLI), Rich (console UI), Pydantic (validation)
- Markdown-based specifications in `.specify/` directory
- Jinja2 templates for constitutional generation
- PyMuPDF for PDF extraction (--from-pdf mode)

## Key Commands
- `bpkit decompose --interactive|--from-file|--from-pdf`: Generate constitutions
- `bpkit analyze`: Validate traceability links
- `bpkit clarify`: Resolve pitch deck ambiguities
- `bpkit checklist`: Generate quality validation checklists
- `bpkit sync`: Bidirectional sync between deck and constitutions

## Constitution Types
1. **Strategic** (4 files, slow-changing): company, product, market, business
2. **Feature** (5-10 files, tactical): One per MVP feature with user stories, entities, principles, success criteria

## Five Constitutional Principles
1. Speckit Architecture Clone - Use Python + Typer + Rich
2. Business-to-Code Bridge - Decompose pitch deck into strategic + feature levels
3. Bidirectional Traceability - Links from deck → strategic → features
4. Speckit Compatibility - Feature constitutions work as Speckit inputs
5. AI-Executable Specifications - Complete enough for agents to implement

## Current Status
- Feature 001 (Build): CLI foundation complete
- Feature 002 (Quality): analyze/clarify/checklist commands complete
- Feature 003 (Decompose): In planning - core decomposition logic being designed