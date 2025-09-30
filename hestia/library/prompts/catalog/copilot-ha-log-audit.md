

Analyze the contents of all `home-assistant.log*` files in this workspace, focusing on entries from the last hour, 24 hours, and up to one week (adjusting the time window based on error frequency and Home Assistant restart events).

1. **Methodology:**  
   - Parse and group log entries by error/warning type, component, and timestamp.
   - Synthesize recurring errors into main "Issues" (an Issue may consist of multiple related error instances).
   - For each Issue, provide:
     - Impact assessment (effect on HA runtime, data loss, integration failures, etc.)
     - Debugging difficulty (simple config, code patch, multi-component, etc.)
     - Coding language(s) and components involved.
     - Frequency and recency of occurrence.
   - Flag configuration errors (e.g., duplicate IDs, invalid YAML) separately from code errors.
   - Ignore warnings about untested custom integrations unless they directly impact runtime or stability.
   - For complex or multi-component errors, visualize dependencies (e.g., recorder → history/logbook/energy) in the output.
   - Include links to relevant documentation or error references for complex issues.

2. **Prioritization:**  
   - Rank Issues by severity, runtime impact, and complexity.
   - Note dependencies (e.g., recorder errors blocking history/logbook/energy).

3. **Patch Plan Scaffold:**  
   - For each prioritized Issue, outline a patch plan:
     - Identify referenced code/config files.
     - Retrieve and inspect relevant code snippets.
     - Propose targeted fixes or configuration changes.
     - Note any required follow-up (e.g., integration updates, dependency checks).
     - Recommend automated tests or validation steps after patching.

4. **Mini-Prompt for Operator:**  
   - “Using the synthesized error audit and patch plan, walk the workspace to retrieve and inspect the referenced code/config files. For each Issue, propose and apply a targeted fix, then validate resolution in the logs. Suggest further hardening steps if needed.”

5. **Final Output:**  
   - Present a fully resolved patch plan, referencing actual code/config changes, ready for operator review and implementation.