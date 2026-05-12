# {{GRIMOIRE_NAME}} Domain Grimoire

This is the **{{GRIMOIRE_NAME}} domain grimoire** — containing chapters specific to {{GRIMOIRE_PURPOSE_DETAILED}}.

Universal assets (invocations, formulae, rites, docs) live in Arcana (`~/grimoires/arcana/`). See [Arcana README](GRIMOIRE_ARCANA/README.md) for details.

## Chapters

{{CHAPTER_LIST}}

## How to Use

1. Start with `INDEX.md` (root router)
2. Follow routing to relevant chapter (e.g., `chapters/{{EXAMPLE_CHAPTER}}/INDEX.md`)
3. Read the minimal page docs needed for your task

### Creating New Chapters
Use `/grm-domain-create-chapter [topic]` or read [create_chapter.md](GRIMOIRE_ARCANA/invocations/grimoire/create_chapter.md).

## Repository Layout

```
{{GRIMOIRE_DIRECTORY}}/
├── INDEX.md                    # Root router
├── README.md                   # This file
└── chapters/                   # Domain knowledge
{{CHAPTER_TREE}}
```

## Maintenance

### When Adding/Updating Knowledge
1. Use the page template: `GRIMOIRE_ARCANA/formulae/page.formula.md`
2. Include a `Primary Sources` section when referencing external files/repos/systems
3. For drift-sensitive values, use query commands to extract current state

### Principles
- Keep all knowledge content under `chapters/`
- Keep paths relative inside the repository
- Keep routers explicit and deterministic
- Keep page docs concise; add TODOs instead of guessing unknown conventions

## Agent Integration

Registered in `~/grimoires/library.json`:

```json
"{{GRIMOIRE_DIRECTORY}}": {
  "local_path": "$HOME/grimoires/{{GRIMOIRE_DIRECTORY}}",
  "online_path": null
}
```

This grimoire's identity (name, namespace, description) is declared in `grimoire.json` at the repository root:

```json
{
  "name": "{{GRIMOIRE_DIRECTORY}}",
  "namespace": "{{SKILL_NAMESPACE}}",
  "description": "{{GRIMOIRE_PURPOSE}}"
}
```

Skills under `skills/` register as `/{{SKILL_NAMESPACE}}-<area>-<verb>-<object>` (the registration rite reads `namespace` from `grimoire.json` and substitutes it into each `SKILL.md`'s `{{NAMESPACE}}-<slug>` placeholder).

The summoning rite (`GRIMOIRE_ARCANA/rites/summon.sh`) handles registration automatically.

## Getting Help

- **Domain content**: Ask in #{{DOMAIN_CHANNEL}} domain channel
- **Grimoire commands**: Use `/grm-meta-help` to list all available invocations
- **Arcana docs**: See `GRIMOIRE_ARCANA/README.md` and `GRIMOIRE_ARCANA/docs/`
