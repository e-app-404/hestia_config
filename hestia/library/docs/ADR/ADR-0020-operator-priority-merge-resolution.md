---
title: "Operator Priority Resolution for Workspace Merge Conflicts"
date: 2025-10-04
last_updated: 2025-10-04T00:00:00Z
status: Accepted
author:
  - "Evert Appels"
related:
  - "ADR-0016: Canonical HA edit root & non-interactive SMB mount"
  - "ADR-0019: Remote topology mirror policy"
  - "ADR-0013: Source→Core Config Merge via extracted_config"
  - "ADR-0012: Four-Pillar Workspace Architecture"
requires:
  - "Active workspace development branch"
  - "Main branch with potential staleness"
  - "Merge conflict resolution capability"
tags: ["merge-strategy", "operator-priority", "workspace-governance", "conflict-resolution"]
notes: "Canonicalizes the merge strategy that prioritizes active development workspace over potentially stale main branch content"
---

# ADR-0020: Operator Priority Resolution for Workspace Merge Conflicts

## 1. Status
**Accepted** (2025-10-04)

## 2. Context

During intensive development sessions, the active workspace (development branch) becomes the canonical source of operational enhancements, architectural improvements, and configuration refinements. When merging back to main, conflicts may arise between:

- **Active workspace content**: Recently developed, tested, and operator-validated configurations
- **Main branch content**: Potentially stale or superseded by recent operational improvements

The merge resolution strategy must preserve operator intent and maintain the integrity of recent development work while ensuring the main branch becomes the definitive canonical codebase.

## 3. Decision

### 3.1 Operator Priority Principle

**The active workspace (development branch) takes precedence over main branch content during merge conflict resolution.**

This principle applies to:
- Automation logic and YAML configurations
- ADR documentation and architectural decisions  
- Operational scripts and deployment pipelines
- Testing infrastructure and validation tools
- Workspace organization and tooling enhancements

### 3.2 Merge Resolution Protocol

1. **Prioritize Active Workspace**: When conflicts arise, prefer the development branch version that contains recent operator edits and enhancements

2. **Preserve Operational Intent**: Maintain all operator-validated configurations, scripts, and architectural improvements from the development session

3. **Canonicalize via Main**: After resolution, the main branch becomes the single source of truth containing all integrated enhancements

4. **Validate Integration**: Ensure merged content maintains functional integrity across all systems (Home Assistant, deployment pipeline, testing infrastructure)

### 3.3 Conflict Categories and Resolution Rules

| Conflict Type | Resolution Strategy | Rationale |
|---------------|-------------------|-----------|
| YAML Configuration | Prefer development branch | Recent operational validation |
| Automation Logic | Prefer development branch | Contains latest syntax updates |
| ADR Documentation | Merge both with development precedence | Preserve architectural evolution |
| Script/Tool Updates | Prefer development branch | Recent testing and refinement |
| File Structure Changes | Prefer development branch | Reflects current workspace organization |

### 3.4 Exception Handling

- **Registry/State Files**: Accept incoming (main) version to preserve system state
- **Generated Artifacts**: Regenerate from canonical sources post-merge
- **Secrets/Credentials**: Manual review required; never auto-resolve

## 4. Implementation

### 4.1 Merge Execution Pattern

```bash
# 1. Backup current state
git checkout -b backup/merge-resolution-$(date +%Y%m%d-%H%M%S)

# 2. Return to main and initiate merge
git checkout main
git merge development/active-workspace

# 3. Resolve conflicts using operator priority
# - Prefer development branch content
# - Preserve operational enhancements
# - Maintain architectural improvements

# 4. Validate and commit resolution
git add .
git commit -m "Merge: operator priority resolution - canonicalize active workspace"

# 5. Push canonical version
git push origin main
```

### 4.2 Post-Merge Validation

- ✅ All automation syntax modernized (platform: → trigger:, service: → action:)
- ✅ ADR documentation reflects current architectural state
- ✅ Operational scripts maintain functionality
- ✅ Testing infrastructure remains intact
- ✅ Deployment pipeline enhancements preserved

## 5. Consequences

### 5.1 Positive Outcomes

- **Preserves Operator Intent**: Maintains all recent development work and enhancements
- **Canonical Main Branch**: Creates single source of truth ready for deployment
- **Operational Continuity**: Ensures all validated configurations remain functional
- **Architectural Integrity**: Preserves recent improvements and modernizations

### 5.2 Trade-offs

- **Potential Loss of Main Branch Changes**: Stale main content may be superseded
- **Manual Validation Required**: Complex merges need operator oversight
- **Documentation Burden**: Requires clear rationale for resolution choices

### 5.3 Risk Mitigation

- Create backup branches before merge operations
- Document resolution rationale in commit messages
- Validate functionality post-merge across all systems
- Maintain audit trail of operator decisions

## 6. Governance

This ADR establishes the canonical merge resolution strategy for workspace conflicts. It should be referenced in:

- Merge conflict resolution procedures
- Development workflow documentation  
- Operator training materials
- CI/CD pipeline conflict handling

---

```yaml
TOKEN_BLOCK:
  adr_id: "ADR-0020"
  governance_scope: "merge-resolution"
  operator_authority: "canonical"
  workspace_impact: "high"
  implementation_status: "active"
  validation_required: true
  audit_trail: true
```