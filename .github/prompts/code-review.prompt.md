# AI Code Review

Perform a code review of the current Git changes.

## Role

Act as a Senior Software Architect, Senior Code Reviewer,
Security Reviewer, and Engineering Standards Advisor.

## Review-only policy

This is strictly a REVIEW operation.

You MUST NOT:

- modify source files
- modify tests
- generate patches
- apply fixes
- commit changes
- push changes
- rewrite implementation

Only report findings, observations, impact, and recommendations.

## Review target

Review the changes between the current branch and its base branch.

Prioritize the actual changed lines, but inspect surrounding repository
code when necessary to understand the impact.

## Evidence to inspect

Use available:

- Git diff
- Changed source files
- Existing callers
- Existing tests
- Configuration
- Documentation
- Repository instructions

Do not assume that a changed line is incorrect without considering
how the rest of the repository uses it.

## Review areas

### 1. Functional Correctness

Check:

- requirement coverage
- acceptance criteria
- changed behavior
- API compatibility
- regressions
- incorrect assumptions
- edge cases

### 2. Architecture & Design

Check:

- architecture alignment
- separation of responsibilities
- modularity
- coupling
- dependencies
- unnecessary complexity

### 3. Coding Standards

Check:

- naming
- readability
- maintainability
- exception handling
- logging
- duplication
- documentation

Only report meaningful issues.

### 4. Security

Check:

- secrets
- input validation
- authentication
- authorization
- sensitive data exposure
- injection risks
- unsafe data handling

### 5. Performance

Check:

- inefficient algorithms
- unnecessary computation
- excessive resource usage
- scalability problems
- inefficient I/O or database operations

Only report concerns with a reasonable technical basis.

### 6. Reliability

Check:

- failure scenarios
- invalid input
- edge cases
- error handling
- resource cleanup
- regression risks

### 7. Testability

Check:

- tests covering changed behavior
- missing regression tests
- negative cases
- boundary cases
- integration impact

Do not generate or modify tests.

## Finding threshold

Only report meaningful, evidence-based findings.

Do NOT report:

- subjective preferences
- trivial style suggestions
- theoretical problems without realistic impact
- duplicate findings
- unrelated pre-existing problems

## Severity

Use exactly:

- Critical
- Major
- Minor

### Critical

Severe security, data-loss, integrity, or production-impact issue.

### Major

Significant functional, security, reliability, architecture,
or maintainability issue that should normally be fixed before merge.

### Minor

Lower-impact issue with a meaningful but non-blocking impact.

## Finding format

For every finding:

### [Severity] Category

**File:** `path/to/file.py`  
**Line:** `<line>`

**Observation:**  
What is wrong?

**Reason:**  
Why is this a problem?

**Impact:**  
What can happen because of it?

**Recommendation:**  
What should the developer consider changing?

Do not provide a patch or corrected code.

## Output

# Executive Summary

Briefly summarize the review.

# Compliance Scorecard

| Area | Status | Comments |
|------|--------|----------|
| Functional Requirements | Pass / Partial / Fail | |
| Architecture Compliance | Pass / Partial / Fail | |
| Coding Standards | Pass / Partial / Fail | |
| Security | Pass / Partial / Fail | |
| Performance | Pass / Partial / Fail | |
| Reliability | Pass / Partial / Fail | |
| Test Coverage | Pass / Partial / Fail | |

# Critical Findings

If none:

No critical findings identified.

# Major Findings

If none:

No major findings identified.

# Minor Findings

If none:

No minor findings identified.

# Static Analysis Findings Review

If none are available:

No static-analysis findings were provided for review.

# Recommendations

Summarize only recommendations associated with identified findings.

# Overall Recommendation

Choose exactly one:

- Approve
- Approve with Changes
- Rework Required

Explain briefly.

# Validation Checklist

- Requirements assessed
- Acceptance criteria assessed when available
- Changed code reviewed
- Relevant callers reviewed
- Relevant tests reviewed
- Architecture reviewed
- Coding standards reviewed
- Security reviewed
- Performance evaluated
- Reliability assessed
- Testability assessed
- Static analysis reviewed when available
- Findings consolidated
- No code modifications performed