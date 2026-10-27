# Project Build Checklist: Telco Voice Central

- [x] Gate 1 (Phase 1): PRD & Requirements Gathering (Interview guide on intents, tools, modality, auth per references/interview-guide.md)
- [x] Gate 2 (Phase 2): TDD via tdd-writer sub-agent (Drafting tdd.md with Architecture, Tools, Routing, Derived Variables, Callbacks, and Coverage Map + Human Approval Loop)
- [x] Gate 3 (Phase 3): Scaffolding via scaffolder sub-agent (Bulk-generating app files from assets/project-template/ reference architecture)
- [x] Gate 4 (Phase 4): Mechanical Lint Gate via lint-fixer sub-agent (Zero Warnings Policy on cxas lint off-thread)
- [ ] Gate 5 (Phase 5): Eval Generation via eval-writer sub-agent (Goldens, sims, tool tests, callback tests from Coverage Map). Only keep evals in the cxas_app folder. 
- [ ] Gate 6 (Phase 6): Push & Verification Gates (cxas push + 6-gate verification with gate-check.py)
- [ ] Gate 7 (Phase 7): Run, Triage & Debug Loop (Multi-run discipline with --runs 5, interactive diagnostic dashboards, parallel triage-failure sub-agent, static coverage audit via coverage-analyst sub-agent, and hill-climbing to pursue 80% and above for all eval types)
