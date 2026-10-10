ASUS UGen AI League — Agent Regulation

This file defines mandatory rules for any AI agent working on this repository.

These rules are derived from the ASUS UGen AI League competition requirements provided by the team.

The purpose of this file is to prevent an agent from accidentally producing code, documentation, claims, assets, or submission materials that violate competition requirements.

If a task conflicts with this document, this document takes priority over convenience, implementation speed, or feature completeness.

⸻

1. Competition Context

This project is intended for:

Competition: ASUS UGen AI League
Stage: Stage I
Selected Battlefield: Battlefield Lightning
Target Hardware: ASUS UGen300 AI Accelerator / Hailo-10H
Project: PrivacyLens
Primary Domain: AI-assisted privacy processing for recorded video

The Stage I prototype may run on:

* a laptop;
* a desktop computer;
* a virtual machine;
* an SBC;
* other suitable development hardware.

Actual UGen300 execution is not required for Stage I based on the competition rules supplied to the team.

Do not claim that the prototype currently runs on UGen300 unless this has actually been implemented and verified.

⸻

2. Submission Deadline

According to the competition information supplied to the team, the Stage I competition submission deadline is:

October 14, 2026, 17:00 — Asia/Taipei

This is different from any later course-assignment deadline.

When prioritizing work near the deadline:

A complete and valid competition submission takes priority over optional features.

Do not delay submission for:

* additional model integration;
* performance optimization;
* UI polish;
* real-time processing;
* additional sensitive-information categories;
* experimental features.

⸻

3. Originality

The submitted work must be the team’s own competition entry.

According to the competition rules supplied to the team, the submitted work must not have previously been:

* publicly published;
* entered into another competition;
* publicly exhibited;
* awarded.

The existence of similar research, products, or ideas does not by itself mean that this project must be abandoned.

However, agents must never:

* copy another project’s implementation and present it as original work;
* copy another team’s submission;
* copy substantial documentation without attribution;
* copy figures and present them as team-created figures;
* copy demo footage;
* present another system’s results as PrivacyLens results;
* deliberately conceal relevant prior work;
* claim that an existing technique was invented by this team.

If the eligibility of a specific reused artifact or previous team work is uncertain, flag it for human review rather than assuming it is allowed.

⸻

4. Intellectual Property and Licensing

All external resources used by the project must have appropriate usage rights.

This includes:

* source code;
* libraries;
* pretrained models;
* model weights;
* datasets;
* images;
* icons;
* fonts;
* videos;
* audio;
* figures;
* documentation excerpts;
* other third-party assets.

Before adding a substantial third-party component, verify its license.

Do not assume that:

“open source” = “unrestricted use.”

Model weights may have different licenses from the software framework used to execute them.

When appropriate, record:

Component
Source
Version
License
Usage

in the repository documentation.

If licensing cannot be verified, do not silently include the asset. Flag it for human review.

⸻

5. Privacy

PrivacyLens is a privacy-related project.

The development and demonstration process must itself respect privacy.

Demo material should use synthetic information.

Examples:

sk-demo-123456789
demo@example.com
192.168.10.24
DEMO_PASSWORD=example123

Do not intentionally include:

* real API keys;
* real passwords;
* authentication tokens;
* private SSH keys;
* private conversations;
* confidential documents;
* personal information belonging to unrelated individuals;
* credentials belonging to the team;
* credentials belonging to third parties.

Never expose a real secret merely to demonstrate that PrivacyLens can remove it.

⸻

6. Prohibited Content

Competition materials must not intentionally contain content prohibited by the competition rules supplied to the team, including content involving:

* unlawful activity;
* criminal activity;
* privacy invasion;
* defamatory material;
* pornography;
* inappropriate violent material;
* other prohibited or illegal material.

When uncertain whether a proposed demo asset creates a privacy or rights issue, replace it with synthetic content.

⸻

7. Truthfulness of Technical Claims

Never claim that a feature exists unless it has actually been implemented or clearly label it as proposed/future work.

Use the following distinction consistently.

Implemented

May be described as:

“PrivacyLens detects…”

only when demonstrated by the current prototype.

Planned

Use language such as:

“We plan to…”

“The proposed Stage II system will…”

“Future work includes…”

“The architecture is designed to support…”

Do not convert planned functionality into present-tense implementation claims.

⸻

8. Hardware Claims

The project targets the Lightning battlefield and UGen300/Hailo-10H.

However, Stage I laptop experiments must not be presented as UGen300 results.

Never fabricate:

* Hailo latency;
* Hailo FPS;
* Hailo throughput;
* TOPS utilization;
* memory usage;
* power consumption;
* accelerator speedup;
* end-to-end latency;
* model compatibility.

If a number comes from official documentation rather than our own experiment, explicitly identify it as a vendor specification or published reference result.

If a model has not been verified as deployable on Hailo-10H, do not state that it is supported as fact.

Use wording such as:

“Candidate model pending deployment verification.”

when necessary.

⸻

9. Experimental Results

All reported experimental results must come from actual experiments performed by the team.

Never invent:

* accuracy;
* precision;
* recall;
* F1;
* FPS;
* latency;
* throughput;
* memory consumption;
* detection rates;
* false-positive rates;
* false-negative rates.

If an experiment has not been performed, use:

TBD

or describe it as planned evaluation.

Never manufacture numbers because they make a presentation look more complete.

⸻

10. AI Claims

Do not exaggerate the role of AI.

If a component is implemented using:

Regex
Rule matching
String replacement
OpenCV rendering

do not describe that component itself as AI.

PrivacyLens may contain both deterministic and AI components.

A valid architecture may therefore be:

Video
  ↓
OCR / Visual Model
  ↓
Extracted Context
  ↓
┌───────────────────────────┐
│ Rule-Based Detection      │
│ AI Contextual Detection   │
└───────────────────────────┘
  ↓
Privacy Decision
  ↓
Semantic Replacement

Clearly distinguish between:

* neural inference;
* deterministic processing;
* heuristics;
* rule-based processing;
* AI reasoning.

⸻

11. Novelty Claims

Do not use claims such as:

“the first”

“the world’s first”

“no existing system”

“unprecedented”

“completely novel”

unless strong evidence has been collected and the team explicitly approves the claim.

PrivacyLens should not claim to have invented:

* privacy redaction;
* PII detection;
* OCR-based redaction;
* video privacy filtering;
* content replacement;
* screen privacy protection.

The project’s intended focus is:

Context-aware detection of sensitive information in recorded video and semantic replacement that hides sensitive values while preserving useful context.

Related work must be acknowledged where appropriate.

⸻

12. References

Do not fabricate references.

Every reference included in the final proposal must correspond to a real source that has been verified.

For academic papers, verify when possible:

* title;
* authors;
* venue;
* year;
* publication URL or DOI.

For products or technical documentation, use the original or official source whenever possible.

Do not cite a source merely because another AI system mentioned it.

If a citation cannot be verified:

remove it or mark it for verification.

⸻

13. Stage I Proposal Requirements

According to the competition rules supplied to the team, the Stage I proposal must be written in English.

The main body must not exceed:

20 pages

excluding allowed appendix material where applicable.

The proposal must include the required competition content, including:

1. Scenario / background and problem definition
2. Proposed solution
3. Tools, technologies, and methodology
4. Hardware/software architecture and system planning
5. Expected benefits and outputs
6. References
7. GitHub repository link

The team should also ensure that all additional course-specific requirements are satisfied.

Do not remove required sections merely to improve presentation aesthetics.

⸻

14. GitHub Repository

The final submission must reference the project’s GitHub repository.

The repository should contain enough information to understand and reproduce the Stage I prototype.

At minimum, aim to provide:

README.md
requirements / dependency information
source code
example or synthetic input
instructions for running the prototype
architecture description
license / attribution information where necessary

Never upload secrets to GitHub.

Before committing, check for:

.env
API keys
tokens
passwords
SSH keys
private certificates
personal information

Use .gitignore where appropriate.

⸻

15. Demo Video

The Stage I demo video should primarily use English according to the competition information supplied to the team.

The competition suggests keeping the video within approximately:

3 minutes

The final video should be uploaded using the submission method required by the competition, including an unlisted YouTube link where applicable.

The demo must represent the actual prototype honestly.

Do not:

* fake inference results;
* manually prepare an output and claim the system generated it;
* edit the video in a way that misrepresents system behavior;
* show another project’s demo as ours.

It is acceptable to shorten waiting time in video editing if the edit does not misrepresent measured performance.

⸻

16. PrivacyLens Demo Data

All canonical demonstrations should use controlled synthetic data.

Recommended example:

OPENAI_API_KEY=sk-demo-123456789
DATABASE_PASSWORD=demo-password
SERVER_IP=192.168.10.24
EMAIL=demo@example.com

Expected semantic replacement:

OPENAI_API_KEY=<API_KEY>
DATABASE_PASSWORD=<PASSWORD>
SERVER_IP=<IP_ADDRESS>
EMAIL=<EMAIL>

If contextual AI is demonstrated, construct synthetic examples where context affects the privacy decision.

For example:

Documentation:
API_KEY=<YOUR_API_KEY>

may be classified as safe, while:

Production environment:
API_KEY=sk-demo-secret-value

may be classified as sensitive.

No real credential is required to demonstrate this behavior.

⸻

17. Stage I vs. Stage II

Agents must maintain a clear distinction between the two stages.

Stage I

Focus on:

* proof of concept;
* laptop implementation;
* system architecture;
* AI methodology;
* controlled demonstration;
* proposal;
* GitHub;
* demo video.

Stage II / Future Work

May include:

* UGen300 integration;
* Hailo-10H deployment;
* performance optimization;
* more advanced contextual models;
* larger evaluation datasets;
* temporal tracking;
* near-real-time processing;
* additional sensitive-information categories.

Do not implement Stage II features at the expense of completing Stage I.

⸻

18. Scope Protection

The primary goal is to complete a valid Stage I submission.

Before implementing an additional feature, ask:

Is this required for the Stage I submission?
OR
Does this materially improve the core PrivacyLens demonstration?

If both answers are no, defer the feature.

In particular, the following are not automatically required:

Real-time processing
Zoom integration
Google Meet integration
Virtual camera
Generative inpainting
Custom model training
Fine-tuning
Production deployment
30/60 FPS processing
Perfect visual reconstruction
Mobile application
Web service

⸻

19. Submission Completeness

Before considering the project finished, verify that the required submission package is complete.

Checklist:

[ ] Proposal is in English
[ ] Proposal main body is within the page limit
[ ] Problem/background included
[ ] Solution included
[ ] Methodology included
[ ] Hardware/software architecture included
[ ] Expected benefits included
[ ] References included
[ ] GitHub repository exists
[ ] GitHub link included in proposal
[ ] Demo video completed
[ ] Demo video link included
[ ] Team member information is correct
[ ] Competition submission completed before competition deadline
[ ] Course-specific submission requirements completed

If there is a conflict between implementing another feature and completing this checklist:

Complete the checklist first.

⸻

20. Course-Specific Requirements

The team has indicated that the associated course requires successful completion of the competition submission.

The course submission additionally requires the proposal file to follow the required naming convention:

{studentID}_CN_league.pdf

When working as a team, ensure all required team-member names and student IDs are included as required by the course instructions.

Each student remains responsible for their own required course submission.

Competition and course deadlines must not be treated as interchangeable.

⸻

21. Uncertainty Rule

If an agent encounters ambiguity involving:

* competition eligibility;
* intellectual property;
* licensing;
* privacy;
* submission requirements;
* hardware compatibility;
* model compatibility;
* attribution;
* factual claims about competition rules;

the agent must not guess.

Instead:

1. identify the uncertainty;
2. preserve the conservative interpretation;
3. flag the issue for human verification;
4. consult official competition information when available.

The competition organizer’s official interpretation takes precedence over this document.

⸻

22. Priority Order

When trade-offs are necessary, use the following priority:

Competition Compliance
        >
Submission Completeness
        >
Working Prototype
        >
Truthful Demonstration
        >
Core AI Functionality
        >
Presentation Quality
        >
Additional Features
        >
Performance Optimization

No optimization or feature is worth risking submission validity.

⸻

23. Final Agent Rule

Before making a significant project decision, ask:

Does this change keep the project compliant, truthful, reproducible, legally usable, and realistically finishable before submission?

If the answer is uncertain:

Do not silently proceed. Flag the issue for the team.