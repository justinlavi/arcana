# Quality Enhancement Invocations

Advanced invocations for improving Arcana quality beyond basic validation.

## Purpose

Quality invocations go beyond "is it correct?" to "is it excellent?" They focus on:
- Eliminating duplication (DRY principle)
- Improving clarity and accessibility
- Ensuring maintainability
- Validating automation quality

## Available Invocations

### Content Quality
- **[detect_duplication.md](detect_duplication.md)** - Find and eliminate duplicate content (DRY enforcement)
- **[improve_documentation.md](improve_documentation.md)** - Enhance clarity, completeness, and accessibility

### Automation Quality
- **[validate_rites.md](validate_rites.md)** - Ensure rite scripts are robust and maintainable

## When to Use

**Quality invocations are typically invoked**:
- During improve-arcana workflow (Phases 6-7)
- Before major releases
- After significant documentation updates
- As part of quarterly quality reviews
- When technical debt accumulates

**They complement the validator invocations**:
- Validators: "Is it structurally correct?"
- Quality invocations: "Is it excellent?"

## Workflow Integration

### During improve-arcana

Quality invocations integrate into improve-arcana workflow:

**Phase 6: Duplication Detection**
```
/grm-arcana-improve
```
- Scans for duplicate content
- Enforces DRY principle
- Consolidates to single source

**Phase 4: Documentation Coherence**
```
/grm-arcana-improve
```
- Reviews clarity and completeness
- Audits navigation
- Tests beginner experience
- Grades documentation quality

**Phase 7.5: Rite Validation**
```
/grm-arcana-improve
```
- ShellCheck validation
- Portability testing
- Error handling review
- Documentation check

### Independent Usage

Quality invocations can run independently:

```bash
# After adding documentation
/grm-arcana-improve

# After creating rite script
/grm-arcana-improve

# During refactoring
/grm-arcana-improve
```

## Quality vs Validation

**Validators** (required):
- Binary pass/fail
- Automated checks
- Enforced by CI/CD
- Block releases if failing

**Quality Enhancements** (aspirational):
- Graded quality (A-F)
- Require human judgment
- Continuous improvement
- Inform but don't block

## Measurement

Quality invocations provide metrics:

**Documentation Quality Score** (A-F):
- Clarity
- Completeness
- Accessibility
- Consistency
- Maintainability

**DRY Compliance**:
- Duplicate lines detected
- Lines consolidated
- Single sources identified

**Rite Quality Score** (A-F):
- ShellCheck pass rate
- Portability coverage
- Error handling
- Documentation
- Performance

## Related

- **Validators**: [validators/INDEX.md](../validators/INDEX.md)
- **Orchestrator**: [improve_arcana.md](../improve_arcana.md)
- **Principles**: [docs/operating_model.md](../../../docs/operating_model.md)

## Notes

**Manual vs Automated**: Quality invocations combine automated checks (shellcheck, grep) with human judgment (clarity assessment).

**Continuous Improvement**: Quality scores establish baseline and track improvement over time.
