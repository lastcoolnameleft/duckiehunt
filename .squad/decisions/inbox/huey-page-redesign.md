# Huey Page Redesign

- Date: 2025-07-22
- Requested by: Tommy Falgout
- Area: Django templates and homepage view

## Decision

Adopt the existing `detail.html` card-and-stats pattern as the baseline for the homepage and duck list so duck-facing pages share the same visual structure and CTA style.

## Why

- Keeps new marketing and browsing pages visually consistent with the already-modernized duck detail page.
- Lets backend-rendered templates reuse familiar Bootstrap card, stat, list-group, and responsive grid patterns without adding new frontend dependencies.
- Makes future template updates easier because homepage, list, and detail pages now follow the same layout vocabulary.
