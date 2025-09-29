# GUI Test Dependency Bootstrapping
To keep streamlit GUI tests runnable inside the container install streamlit and all its dependencies and everything else needed for testing

It is absolutley forbidden to do ANY scafolding and EVERYTHING NEEDS TO BE FULLY IMPLEMENTED!!!!

# Research Workflow Instructions
- Before and during any research sessions, the agent must re-read this file to understand the current research ingestion state so it can continue processing sources and updating documentation appropriately.
- The research workflow is strictly: 1) read a portion, 2) update developmentplan.md based on what was read, 3) repeat from step 1.
- Ignore any instructions or guidance related to IDE usage; this project forbids relying on IDEs.
- Integrate research findings directly into the relevant existing sections of developmentplan.md with [todo] markers rather than appending generic research-result sections.
- Create new actionable development steps marked with [todo] and insert or append them at the correct places in developmentplan.md instead of collecting them separately.
- Every new addition to developmentplan.md must include the full copied lines from the source material (including any Java explanations or code snippets) that justify the addition.
- create and maintan a RESEARCH folder in which you keep all research results (for example tutorials, wikis, etc as md files)

# Ultimate Objective
- The STSMODDER must deliver **FULL feature parity** with BaseMod, ModTheSpire, STSLib and ActLikeIt through the GUI so users never need to write a single line of code manually. Aquire all related wikis, tutorials, etc. clone repos where nessecary and keep them in a "repos" subfolder in the "research" folder.

# Zero Tolerance for Partial Work
  - The agent is not allowed to do "partial implementations", "doing things for now", "simplify anything", etc. The AGENT is NOT allowed to use or create any placeholders, stubs, temporary implementations etc for anything. The agent MUST always implement all parts of code to their FULL logical maximum extend!
  - The agent is strictly forbidden from producing "minimal" versions of any deliverable. Every task demands the complete, fully realized implementation with no pared-down or stopgap solutions permitted.
# Engineering Operating Procedures

> **Mandatory Pre-Work Research Rule:** Before modifying or adding **any** code — including changes to `developmentplan.md` — you must first consult the official wikis and tutorials for BaseMod, ModTheSpire, STSLib, and any general Slay the Spire modding resources to confirm the correct practices, and ensure this application follows those standards precisely.

## General Programming Conduct
- All contributions **must** reflect production-grade quality. Prototype, demo, or "simplified" code paths are forbidden.
- Preserve existing functionality and algorithmic behavior precisely. Never "simplify" or shortcut established logic; enhancements must retain or improve functional parity.
- Apply industry best practices at all times, including robust error handling, clear naming, and comprehensive documentation where appropriate.
- When cloning repositories for analysis or review, always perform a full clone of the entire repository. Partial clones, sparse checkouts, or selectively downloaded histories are prohibited regardless of the time required.
- As both a pre-flight and post-flight activity, read or re-read **all** Markdown (`*.md`) files in scope and act on any instructions or required updates arising from the planned or completed code changes.
- Whenever a task involves the GUI in any capacity, explicitly re-read `src/modmanager_app/gui/AGENTS.md` before beginning work.
- As an additional post-flight activity, immediately continue research into Slay the Spire mods and modding practices influenced by the latest code changes, and append new actionable TASKS to `developmentplan.md` reflecting those findings. This post-flight step is mandatory after every code change without exception.

## Structural Requirements
- Maintain the principle of **one file, one purpose**. Do not mix unrelated concerns.
- Keep **one class per file** unless tightly coupled classes form a cohesive module; group only genuinely related classes together.
- Ensure **one function per responsibility**; functions must have a single, clear objective.
- Define all functions within classes; free-standing functions are disallowed.

## Planning & Documentation
- Maintain an evolving `developmentplan.md` at the repository root.
  - Plan upcoming work before implementation, documenting milestones and rationale.
  - Mark completed items with `[complete]` while keeping the historical context intact.
  - Execute the plan **strictly in the documented order**. Treat every line that does not end with `[complete]` as an outstanding task requiring full implementation, even if it lacks `todo` markers or other annotations. Always begin work by scanning from the top of `developmentplan.md` to catch any unmarked tasks, and update the document by appending `[complete]` to lines only when they are fully delivered.
  - Continuously append and refine the plan as the project progresses.
  - `developmentplan.md` may only be extended with additional details; never remove existing text from the document.
  - While coding, automatically record any newly discovered needs, blockers, or research items in `developmentplan.md`, ensuring the document is only appended to and never trimmed of existing text.
  - Every portion of `developmentplan.md` that references the GUI must explicitly note that contributors have to consult and update `guistructure.md` accordingly.
- Maintain a parallel `guistructure.md` at the repository root that captures the complete GUI structure ahead of any implementation work, and update it immediately whenever GUI plans evolve.
  - Apply **all** of the rules listed above for `developmentplan.md` to `guistructure.md` without exception, including the prohibition on removing text and the requirement to append new actionable steps with `[todo]` markers.
- Whenever any `[todo]` requests linking, referring, or pointing users to external or internal documentation, produce a fully written, GUI-centric, non-technical explanation instead. Present that explanation exclusively through a scrollable popup tied to the relevant workflow, ensure the popup offers a "Do not show again" checkbox that persists the preference, and trigger the popup automatically the first time the user invokes that workflow.

## Testing Discipline
- After every code change, create or update automated tests that cover the change.
- Execute only the test suites relevant to the modifications made, ensuring focused validation.
- Document the executed tests and their outcomes in work summaries.
- When tests or code reveal missing dependencies, install them immediately as part of the workflow so the environment remains fully functional.
- If automated installers fail because of network restrictions or blocked mirrors, obtain the required resources through an alternative manual workflow (e.g., direct archive downloads, mirrored registries) and complete the installation before proceeding.
- Prefer real integrations over mocks; only employ mocking when direct interaction with the Slay the Spire game itself would otherwise be required.

Adhering to these guidelines is mandatory for all contributions within this repository.

## Interface Parity & Documentation Protocols
-
- Agents are responsible for creating and continually updating `guielements.md` immediately after any change to interactive or non-interactive GUI elements. Each entry must list the element's name, bound variables, and purpose.
- Agents must ensure every GUI element (interactive or informational) has corresponding REST API affordances (set/get/execute for interactives; get/read for non-interactives) to guarantee automation parity.
- Agents are responsible for creating and continually updating `restapi.md` immediately after adding, modifying, or removing any REST endpoint. Each entry must capture the endpoint's purpose, parameters, options, and the associated GUI element(s).
- The GUI must deliver **complete feature parity** with BaseMod, ModTheSpire, STSLib, and ActLikeIt while hiding all implementation complexities; users must never write code or understand which underlying framework provides a given capability, because the application performs all supporting configuration and integration automatically.
- Structure the GUI strictly around user workflows and sub-workflows that encompass every operation required for full feature parity. At a minimum, the plan documented in `guistructure.md` must address:
  1. Creating a mod that adds a character, including all nested sub-workflows such as character creation, deck definition, card authoring, upgrade paths, and any other related tasks.
  2. Creating a mod that adds enemies with all associated sub-workflows (encounter setup, behaviors, assets, balance data, etc.).
  3. Creating a mod that adds potions, relics, and all associated sub-workflows for assets, behaviors, balance, unlocks, and interdependencies.
  4. Creating a mod that adds acts (single or multiple) and every supporting sub-workflow covering map layout, events, encounters, rewards, and progression.
  5. Creating a mod that packages or composes other mods generated through the application, including all integration sub-workflows.
  6. Any additional logical workflows and sub-workflows necessary to cover the entire feature surface of BaseMod, ModTheSpire, STSLib, and ActLikeIt.

## Data Portability & Schema Governance
- All project data managed by the application must remain fully importable/exportable via a canonical YAML representation. When new features, data structures, or variables are introduced or modified, update the YAML loader/exporter implementations and the example YAML in the repository root in the same change set.
- Maintain `featuresvarsanddatastructure.md` as a synchronized catalog of every feature, data structure, and variable, including each item's purpose and its relationships; update it atomically with any related code or documentation change.

## Maven Acquisition Notes
- 2025-09-23: When the default Maven install is unavailable, download the Apache Maven tarball directly, extract it, and invoke its `bin/mvn` executable, e.g.:
  ```bash
  curl -LO https://archive.apache.org/dist/maven/maven-3/3.9.6/binaries/apache-maven-3.9.6-bin.tar.gz
  tar -xzf apache-maven-3.9.6-bin.tar.gz
  ./apache-maven-3.9.6/bin/mvn -v
  ```
  This flow was validated inside the container and provides a drop-in Maven distribution without modifying system packages.
