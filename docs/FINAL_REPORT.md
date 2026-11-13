# Final report: Integer Programming with Python and Google OR-Tools

This report records what the course holds, how it was checked, where it is published, and what is still open.

## What the course holds

- 15 sections, 57 modules and 237 lessons, from foundations to the capstone, the four grown projects and the mock interviews.
- 478 practices:
  - 2 or 3 code practices in each lesson of sections 1–12;
  - one project practice in each lesson of the projects section.
- 719 quiz questions.
- Every lesson opens its models with the full formulation (sets, parameters, bounded variables, objective, labelled constraints), and its Reference ends with **Further reading**.
- GridCap, the running dataset, is fictional and every page that uses it says so.
- GPU material is section 11's module 57. Its GPU numbers are marked as measured on one machine; the CPU image runs every practice, and the GPU checks are silent there.
- The projects section ends with a spec-driven project (module 58) that runs the real OpenSpec CLI in the runner image.

## How it was checked

- **Programs.** Every code block that prints output is a program in the module's `src/`, run in the course's runner image. Its output on the page is verified by `scripts/verify_lessons.py`. Each module's tests pass in the runner.
- **Practices.** StudyForge's gates (G1–G5) clear for every lesson:
  - the reference passes;
  - the starter fails on an assertion;
  - each planted fault fails only its own case;
  - the cited passages exist.
- **Quizzes.** Each question passed two readers:
  - a page-free reader that must not be able to pick the key from the wording alone;
  - a page reader that must find the key on the page and refute every wrong option with a quote.
- **Learner judges.** One judge per section took the lessons as a learner would and ran the practices in the runner without reading the tests. Every quiz answer from every judge was right. Every gap a judge reported was fixed, or recorded below with its reason.
- **Archive.** The full StudyForge ingest and audit is valid with 0 findings.
- **Personal data.** A scan of every tracked file found no email, name, home path or host name. The only account names are in links to public GitHub repositories.

## Framework and toolchain

- The course is pinned to a local StudyForge build, recorded in `.studyforge/pin.json`. It includes the site redesign and these fixes made for this course:
  - version numbers are no longer read as lesson numbers;
  - a link label may hold brackets;
  - a file new in a project step starts as its reference, with only the methods to write stubbed;
  - a project's build file is listed read-only;
  - the corpus walk skips git-ignored folders.
- The runner and editor images carry Python and Node (for the OpenSpec CLI) in the optimization profile of the toolchain.
- The GPU runner is a separate image built from the same profile, with Node.
- No solver licence is built into any image. Learners mount their own.

## Where it is published

- **Source and learner tree.** The course's GitHub repository holds the learner tree on `main` and this source on `studyforge/build`. The read-only site is served from `main` by GitHub Pages.
- **Images.** The course's runner, editor and site images are on Docker Hub, built on the optimization profile's runner and editor. Their digests match the pinned bases.
- **GPU runner.** Published on its own as `studyforge-code-toolchain-runner-optimization-gpu`; it is not part of the learner tree's compose files.

## Findings handed back to StudyForge

The course's sorted findings log is `.studyforge/findings.md`, and StudyForge keeps a copy under `docs/course-logs/`. Its lasting entries are now in StudyForge's catalogue, and the framework holes it found were fixed there: the catalogue ships with the framework and every skill points to it, release checks every precondition at once and requires a sorted log, publishing pushes and scans only the course's own images, re-pinning is one command, and a gate refuses a project step whose page gives its practice away.

## Open items

- **Hold-back design.** Projects 54–56 show each step's full change on the page, so their practices can be passed by copying. Project 58 holds back one piece per lesson. StudyForge's new hold-back gate (H1), run read-only on projects 54 and 58, refused none of their 14 steps: copying the code a page shows still fails the step's tests. It was not run on 55 and 56. The course is pinned to the framework build before that gate.
- **Tie dependence (F90).** In 14.1.2 and 14.1.3 the expected report depends on the model's build order. The statements give the order.
- **GPU skips (F82).** The opt-in GPU skip in StudyForge is not yet used by module 57's practices.
- **StudyForge baseline failures.** StudyForge has three test failures that were already there at the course's first pin: `floor/test_init`, `gate_coverage` and `execute/test_docker_context`.

Every behaviour of a solver or a tool that the course works around is listed in `docs/FINDINGS.md` (F1–F90).
