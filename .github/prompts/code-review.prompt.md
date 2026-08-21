Your task is to perform an automated code review on the provided git diff using the surrounding unit tests, AST dependency callers, and local test results as input.

Strictly output your analysis using the following standardized markdown template. Do not omit any sections, do not deviate from the headings, and do not make any auto-corrections to the code.

# Output Template

## Executive Summary
[Provide a high-level summary of the review, noting key risks, security issues, and overall quality]

## Compliance Scorecard

| Area | Status | Comments |
|--------|---------|---------|
| Functional Requirements | [Pass / Partial / Fail] | |
| Architecture Compliance | [Pass / Partial / Fail] | |
| Coding Standards | [Pass / Partial / Fail] | |
| Security | [Pass / Partial / Fail] | |
| Performance | [Pass / Partial / Fail] | |
| Reliability | [Pass / Partial / Fail] | |
| Test Coverage | [Pass / Partial / Fail] | |

## Critical Findings
[List findings of Critical severity here. Each finding should contain File, Line, Observation, Reason, Impact, and Recommendation. If none, write "No critical findings identified."]

## Major Findings
[List findings of Major severity here. Each finding should contain File, Line, Observation, Reason, Impact, and Recommendation. If none, write "No major findings identified."]

## Minor Findings
[List findings of Minor severity here. Each finding should contain File, Line, Observation, Reason, Impact, and Recommendation. If none, write "No minor findings identified."]

## Static Analysis Findings Review
[Analyze static-analysis results if provided. If none are provided, write "No static-analysis findings were provided for review."]

## Recommendations
[Provide a numbered list of clear, actionable recommendations based on the findings]

## Overall Recommendation
[Approve / Approve with Changes / Rework Required]

# Validation Checklist
- [x] Requirement coverage assessed
- [x] Acceptance criteria validated
- [x] Architecture compliance verified
- [x] Coding standards and best practices reviewed
- [x] Security reviewed
- [x] Performance evaluated
- [x] Reliability assessed
- [x] Testability and coverage reviewed
- [x] Static analysis findings reviewed
- [x] Actionable recommendations provided
