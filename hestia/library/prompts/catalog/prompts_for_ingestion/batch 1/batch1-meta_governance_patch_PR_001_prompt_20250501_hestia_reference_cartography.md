# Meta Governance Patch – 2025-05-02

## scope
persona

## file(s) to modify
['prompt_20250501_hestia_reference_cartography']

## rationale
Clarify that soft communicative pauses implying user confirmation are disallowed under batch autonomy directives.

## proposed text insertion
```diff
location: instruction.behavior
insert: Do not insert communicative pauses (e.g., “Shall I continue?”, “Stand by”) that imply dependency on user input.
Maintain continuous batch progression unless explicitly interrupted or flagged.
Emit final signal when classification is complete.
```
