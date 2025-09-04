# HESTIA Prompt Registry

# Format: Array of prompt objects as per `prompt_registry_schema`

prompt_registry:
  - id: prompt_20250502_010
    file: batch1-prompt_20250502_010.md
    title: "Transform HESTIA Alpha Light Registry to New Schema Format"
    description: "Restructure the existing alpha_light_registry.json into a new schema format aligned with HESTIA meta-standards, retaining all existing information while organizing it into a deterministic, extensible structure."
    type: confidence_guided_extraction
    status: active
    tier: β
    domain: file_migration
    applied_by: chief_ai_officer
    derived_from: "hestia-architecture-knowledge.zip + SHARE_SCAFFOLD_v2.zip"
    tags: [schema_transformation, data_migration, confidence_scoring]
    linked_personas: []
    confidence_score: 92
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [alpha_light_registry.json, alpha_light_meta.json]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: audit_20250502_001
    file: batch1-audit_20250502_001.md
    title: "HESTIA CLI Tools Audit Protocol"
    description: "Ensure all CLI tools adopt modular Processor class structure, standardize interface flags via argparse, detect absence of cooldown enforcement, and validate safe operation with backup-before-write and dry-run options."
    type: audit
    status: active
    tier: β
    domain: tools_audit
    applied_by: chief_ai_officer
    derived_from: hestia_config_manager.py
    tags: [cli_tools, modular_structure, cooldown_enforcement, safety_validation]
    linked_personas: [Icaria]
    confidence_score: 88
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [validation_tools, charon, iris, metis, zodiac]
    usage_frequency:
      daily: 0
      monthly: 1
      last_used: null

  - id: prompt_20250502_011
    file: batch1-prompt_20250502_011.md
    title: "Phanes Metadata Delivery Patch for HA Integration"
    description: "Patch the push_metadata_to_ha() function in phanes.py to comply with Home Assistant's python_script requirements by flattening structured metadata into primitive key-value pairs."
    type: patch_request_flattening
    status: active
    tier: β
    domain: home_assistant_integrations
    applied_by: chief_ai_officer
    derived_from: "HA service constraint + phanes.py"
    tags: [python_script, metadata_flattening, ha_integration]
    linked_personas: []
    confidence_score: 90
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [phanes.py]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_behavioral_context_mnemosyne_gpt
    file: batch1-behavioral_context_mnemosyne_gpt.md
    title: "Mnemosyne Ecosystem Specialist GPT Behavioral Context"
    description: "Comprehensive behavioral context for GPT specializing in Mnemosyne Snapshot Engine ecosystem support, including architecture awareness, debugging expertise, and Home Assistant integration patterns."
    type: behavioral
    status: approved
    tier: γ
    domain: instructional
    applied_by: chief_ai_officer
    derived_from: "mnemosyne ecosystem knowledge + phase 4+5 architecture"
    tags: [mnemosyne, behavioral_context, ecosystem_specialist, debugging]
    linked_personas: [Mnemosyne]
    confidence_score: 95
    deviation_flag: false
    evaluations: []
    version: "2.0"
    changelog: []
    dependencies: [mnemosyne.sh, phase_scripts, utils_library]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_20250501_phanes_v3_12_upstream_patch
    file: batch1-id: prompt_20250501_phanes_v3_12_upstrea.yml
    title: "Phanes Runtime Schema Correction v3.12"
    description: "Upgrade Phanes runtime to v3.12 by correcting key upstream schema propagation bugs, ensuring JSON and YAML correctly expose availability sensors and eliminate false canonical_alpha declarations."
    type: schema_correction
    status: active
    tier: α
    domain: light_entity_generation
    applied_by: chief_ai_officer
    derived_from: "v3.11 audit logs + JSON/YAML output + canonical fallback bugs"
    tags: [phanes, schema_correction, availability_sensors, canonical_alpha]
    linked_personas: []
    confidence_score: 93
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [phanes_3.11.py, alpha_light_registry.json]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_20250501_hestia_reference_cartography
    file: batch1-prompt_20250501_hestia_reference_cartography.yaml
    title: "HESTIA Reference Directory Semantic Inventory"
    description: "Create a complete semantic inventory of the /config/hestia/reference/ directory through iterative document cartography, analyzing files across multiple interpretive lenses and generating structured metadata."
    type: recursive_structural
    status: active
    tier: β
    domain: knowledge_inventory
    applied_by: chief_ai_officer
    derived_from: config_hestia_reference_tree.md
    tags: [document_cartography, semantic_inventory, knowledge_indexing]
    linked_personas: []
    confidence_score: 89
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [config_hestia_reference_tree.md]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_daedalia_diagnostic
    file: batch1-daedalia_diagnostic_prompt.md
    title: "Daedalia Entity Reactivation & Structural Diagnostics"
    description: "Investigate and resolve widespread Unavailable, Unknown, or Idle states across lighting, climate, and monitoring domains in HESTIA, operating silently until reaching concrete, validated resolutions."
    type: diagnostic
    status: proposed
    tier: α
    domain: diagnostic
    applied_by: chief_ai_officer
    derived_from: "entity state analysis + integration audit"
    tags: [entity_reactivation, diagnostics, integration_audit, silent_operation]
    linked_personas: [Daedalia]
    confidence_score: 85
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [configuration.yaml, mqtt.yaml, validator_log.json]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_directive_injection_precision_debugging
    file: batch1-directive injection prompt - precision debugging mode.md
    title: "Directive Injection: Precision Debugging Mode"
    description: "Behavioral directive to restrict GPT responses to direct task focus, eliminate verbal overhead, and provide strict response structure with confidence gating for technical problem resolution."
    type: behavioral
    status: active
    tier: α
    domain: behavior_governance
    applied_by: chief_ai_officer
    derived_from: "precision debugging requirements"
    tags: [directive_injection, precision_debugging, behavioral_constraint]
    linked_personas: []
    confidence_score: 87
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: []
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_registry_dual_artifact_v1
    file: batch1-prompt_registry_dual_artifact_v1.md
    title: "Dual Artifact Registry Ingestion Protocol"
    description: "Extract or infer metadata using HESTIA prompt_registry_schema, append entries to prompt_registry.md while simultaneously maintaining forensic log in curation.log with parse, validation, and repair actions."
    type: schema_conformant_ingestion
    status: active
    tier: α
    domain: registry_governance
    applied_by: chief_ai_officer
    derived_from: prompt_registry_schema
    tags: [dual_artifact, registry_ingestion, forensic_logging, schema_conformance]
    linked_personas: [MetaStructor]
    confidence_score: 91
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [prompt_registry_schema, prompt_registry.md, curation.log]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_20250502_002
    file: batch2-prompt_20250502_002.md
    title: "YAML CLI Tool Consolidation"
    description: "Implement unified configuration management CLI consolidating yaml_diff_changelog.py, yaml_merger.py, and launch_phalanx.py into single Python tool with diff, merge, and map subcommands."
    type: integration_refactor
    status: active
    tier: β
    domain: config_tooling
    applied_by: chief_ai_officer
    derived_from: "tool_governance_cards/yaml_governance_card.md"
    tags: [cli_consolidation, yaml_tooling, integration_refactor]
    linked_personas: []
    confidence_score: 86
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [yaml_diff_changelog.py, yaml_merger.py, launch_phalanx.py]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_20250502_003_behavior_governance
    file: batch2-prompt_20250502_003.md
    title: "Operational Assistant Behavior Governance"
    description: "Enforce behavioral directive requiring periodic status updates every 10-30 seconds during multi-step tasks, preventing silence beyond 15 seconds and ensuring final completion signals."
    type: behavioral
    status: proposed
    tier: α
    domain: behavior_governance
    applied_by: chief_ai_officer
    derived_from: system_instruction.yaml
    tags: [behavior_governance, status_updates, operational_assistant]
    linked_personas: []
    confidence_score: 83
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [system_instruction.yaml]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_20250502_006
    file: batch2-prompt_20250502_006.md
    title: "Documentation Assimilation Protocol"
    description: "Carefully review attached documentation files to extract operational definitions, structural patterns, governance rules, and validation criteria, encoding knowledge for immediate reasoning in downstream tasks."
    type: behavioral
    status: proposed
    tier: α
    domain: doc_ingestion
    applied_by: chief_ai_officer
    derived_from: "user directive + doc integration pattern"
    tags: [documentation_assimilation, knowledge_encoding, compliance_rules]
    linked_personas: []
    confidence_score: 84
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: []
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_20250501_001_librarian_nighthawk
    file: batch2-id: prompt_20250501_001.yml
    title: "Librarian Nighthawk Protocol"
    description: "Activation protocol requiring all responses to first locate and extract relevant documents from internal knowledge base, present evidence trail with source citations, then proceed with commentary only after canonical grounding."
    type: activation
    status: approved
    tier: α
    domain: retrieval_control
    applied_by: chief_ai_officer
    derived_from: system_instruction.yaml
    tags: [librarian_protocol, retrieval_control, evidence_trail, canonical_grounding]
    linked_personas: []
    confidence_score: 94
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [system_instruction.yaml]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_20250502_003_conversation_reflection
    file: batch2-id: prompt_20250502_003.yml
    title: "Session Analyst Conversation Reflection"
    description: "Produce full retrospective report of current GPT-User session including prompt development, behavioral governance, tooling strategy, response compliance analysis, and protocol optimization identification."
    type: conversation_reflection
    status: active
    tier: α
    domain: meta_analysis
    applied_by: chief_ai_officer
    derived_from: "HESTIA Toolchain Session Debrief template"
    tags: [session_analysis, conversation_reflection, behavioral_audit, metadata_extraction]
    linked_personas: []
    confidence_score: 88
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [session_debrief_template]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_gpt_crawler_architecture_extraction
    file: batch3-gpt_crawler_prompt.md
    title: "GPT Crawler Architecture Error and Pattern Extraction"
    description: "Review conversations to extract, structure, and trace architectural contributions across HESTIA knowledge base, surfacing violations, fix strategies, systemic principles, and validator chains with confidence scoring."
    type: extractor
    status: active
    tier: β
    domain: extraction
    applied_by: chief_ai_officer
    derived_from: "HESTIA architecture knowledge base requirements"
    tags: [architecture_extraction, pattern_mining, violation_detection, confidence_scoring]
    linked_personas: []
    confidence_score: 89
    deviation_flag: false
    evaluations: []
    version: "2.0"
    changelog: []
    dependencies: [ERROR_PATTERNS.md, DESIGN_PATTERNS.yaml, ARCHITECTURE_DOCTRINE.yaml]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_20250502_008
    file: batch3-prompt_20250502_008.md
    title: "Knowledge Base Semantic Deconstruction"
    description: "Perform full semantic deconstruction of HESTIA reference corpus using document index as scope anchor, extracting discrete knowledge units structured with concept, type, body, source, and usage contexts."
    type: behavioral
    status: proposed
    tier: α
    domain: knowledge_indexing
    applied_by: chief_ai_officer
    derived_from: "reference_index_inventory.yaml + cartography audit"
    tags: [semantic_deconstruction, knowledge_extraction, corpus_analysis, concept_mapping]
    linked_personas: []
    confidence_score: 87
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [reference_index_inventory.yaml]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_20250501_phanes_dev_superhero_takeover
    file: batch3-id: prompt_20250501_phanes_dev_superhero.md
    title: "Phanes Dev Superhero Emergency Takeover"
    description: "Emergency takeover protocol for broken Phanes pipeline, delivering production-class v3.11 build with upstream schema failure diagnosis, canonical fidelity restoration, and zero post-generation repair requirements."
    type: emergency_takeover
    status: active
    tier: α
    domain: light_entity_pipeline_rescue
    applied_by: chief_ai_officer
    derived_from: "phanes_3.10.py postmortem + meta_phanes.yaml drift + corruption escape"
    tags: [emergency_takeover, phanes_rescue, schema_restoration, pipeline_repair]
    linked_personas: []
    confidence_score: 92
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [phanes_3.10.py, meta_phanes.yaml]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_sensor_entity_extraction_directive
    file: batch3-Sensor_Entity_Extraction_Directive.md
    title: "Comprehensive Sensor Entity Extraction Protocol"
    description: "Extract comprehensive, structured list of ALL sensor entities from YAML configuration files, creating detailed normalized catalog with metadata including unique_id, tier classification, domain categorization, and subsystem mapping."
    type: extractor
    status: active
    tier: β
    domain: extraction
    applied_by: chief_ai_officer
    derived_from: "HESTIA sensor configuration analysis requirements"
    tags: [sensor_extraction, entity_cataloging, yaml_parsing, metadata_normalization]
    linked_personas: []
    confidence_score: 91
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [climate_sensors.yaml, sensor_motion_diagnostic.yaml]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_mnemosyne_phase_4_rebuild
    file: batch4-# 🔐 Mnemosyne Phase 4 – Full Rebuild + .md
    title: "Mnemosyne Phase 4 Full Rebuild with Safety Contract"
    description: "Deliver single production-ready mnemosyne.sh script integrating all safety, fallback, and diagnostic mechanisms, enforcing Phase 4 execution integrity with bulletproof risk mitigation and sanity contract validation."
    type: operational
    status: active
    tier: α
    domain: operational
    applied_by: chief_ai_officer
    derived_from: "Phase 1-3 integration + execution integrity requirements"
    tags: [mnemosyne, phase_4, safety_contract, production_ready, bulletproof_execution]
    linked_personas: []
    confidence_score: 94
    deviation_flag: false
    evaluations: []
    version: "4.0"
    changelog: []
    dependencies: [mnemosyne_phases_1_3, logging.sh, utils_library]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_20250526_002_autonomous_repair
    file: batch4-### 🧠 `prompt_20250526_002` – Autonomou.md
    title: "Autonomous Mnemosyne Phase Repair Protocol"
    description: "Autonomous repair mode as Icaria expert guardian, eliminating all detected bugs and restoring operational integrity to Mnemosyne Snapshot Engine through progressive debug-patch cycles with confidence threshold enforcement."
    type: autonomous
    status: approved
    tier: α
    domain: repair
    applied_by: chief_ai_officer
    derived_from: "mnemosyne_diagnostic_report.json + audit_review + patch_feedback"
    tags: [autonomous_repair, icaria_protocol, mnemosyne_debugging, progressive_patching]
    linked_personas: [Icaria]
    confidence_score: 96
    deviation_flag: false
    evaluations: []
    version: "2.0"
    changelog: []
    dependencies: [mnemosyne_diagnostic_report.json]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_20250526_001_structured_debug_snapshot
    file: batch4-prompt_20250526_001.md
    title: "Structured Debug Snapshot Request Protocol"
    description: "Generate comprehensive diagnostic report representing real-time system state snapshot with technical analysis, issue indexing, execution trail reconstruction, expert synthesis, and prioritized remediation roadmap."
    type: structured
    status: approved
    tier: α
    domain: diagnostic
    applied_by: chief_ai_officer
    derived_from: "expert_session_trace + system_instruction.yaml"
    tags: [diagnostic_snapshot, structured_debugging, system_state_analysis, remediation_roadmap]
    linked_personas: []
    confidence_score: 93
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [system_instruction.yaml]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_light_sensor_chain_refactor
    file: batch4-light_sensor_chain_refactor.md
    title: "Light Sensor Generation Chain Refactoring Protocol"
    description: "Refactor light sensor generation pipeline to improve maintainability, formalize macro roles, embed richer metadata, and ensure semantic contracts through deterministic rendering flows with canonical ID standardization."
    type: operational
    status: active
    tier: β
    domain: light_entity_generation
    applied_by: chief_ai_officer
    derived_from: "template_engine.py framework + layered Jinja macro libraries"
    tags: [light_sensors, chain_refactoring, macro_formalization, semantic_contracts]
    linked_personas: []
    confidence_score: 88
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [template_engine.py, macro_libraries, alpha_light_registry.json]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_behavioral_context_janus_integration
    file: batch1-behavioral_context_janus-integraiton.md
    title: "Janus NIE Integration Strategist Behavioral Context"
    description: "Behavioral context for Janus Network Interface Engine Integration Strategist, focusing on ultra-lean networking solutions for Home Assistant, MacBook, and supporting services with simplicity-first design principles."
    type: behavioral
    status: active
    tier: γ
    domain: instructional
    applied_by: chief_ai_officer
    derived_from: "janus NIE architecture + integration strategy requirements"
    tags: [janus, integration_strategist, network_interface, behavioral_context]
    linked_personas: [Janus]
    confidence_score: 89
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [janus_architecture]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_hephaestus_qa_compliance_upgrade
    file: batch1-behavioral_context_claude_QA-guy.md
    title: "Hephaestus Template Engine QA Compliance & Guardrail Upgrade"
    description: "QA hardening plan addressing critical failure paths, undefined behavior, and contract non-compliance in Hephaestus Template Engine v3.5, ensuring templates never render blank output silently and contexts are structurally validated."
    type: operational
    status: active
    tier: β
    domain: validation
    applied_by: chief_ai_officer
    derived_from: "template engine v3.5 QA analysis"
    tags: [hephaestus, qa_hardening, template_validation, guardrail_upgrade]
    linked_personas: []
    confidence_score: 87
    deviation_flag: false
    evaluations: []
    version: "3.5"
    changelog: []
    dependencies: [template_engine.py, macro_abstraction_template.yaml]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_canonical_meta_schema_master
    file: batch1-prompt_canonical_meta_schema_master.md
    title: "Self-Contained Meta Schema Generator with Conformance Evaluation"
    description: "Generate self-contained meta schemas for each artifact in core_artifacts block and perform conformance evaluation with confidence scoring, detecting structural mismatches and validation requirements."
    type: validation_trigger
    status: active
    tier: α
    domain: validation
    applied_by: chief_ai_officer
    derived_from: "system_instruction.yaml core_artifacts requirements"
    tags: [meta_schema, conformance_evaluation, validation_trigger, artifact_validation]
    linked_personas: []
    confidence_score: 90
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [system_instruction.yaml, core_artifacts]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_mnemosyne_dev_scaffold
    file: batch1-mnemosyne_dev_prompt.md
    title: "Mnemosyne Snapshot Engine Development Scaffold"
    description: "Design context and modular structure proposal for Mnemosyne snapshot engine, transitioning from monolithic Themis implementation to modular phases with tar creation, git mirroring, and symlink orchestration."
    type: instructional
    status: active
    tier: β
    domain: instructional
    applied_by: chief_ai_officer
    derived_from: "themis snapshot analysis + modular architecture requirements"
    tags: [mnemosyne, development_scaffold, modular_architecture, snapshot_engine]
    linked_personas: []
    confidence_score: 85
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [themis_snapshot.command]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_alpha_light_transformation_task
    file: batch1-# Task: Transform the HESTIA Alpha Light.md
    title: "HESTIA Alpha Light Registry Schema Transformation"
    description: "Transform existing alpha_light_registry.json into new schema format with protocol definitions, light devices, room mappings, and validation rules while retaining all information in deterministic structure."
    type: transformation
    status: active
    tier: β
    domain: file_migration
    applied_by: chief_ai_officer
    derived_from: "alpha_light_registry.json + alpha_light_meta.json"
    tags: [schema_transformation, light_registry, protocol_definitions, room_mappings]
    linked_personas: []
    confidence_score: 86
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [alpha_light_registry.json, alpha_light_meta.json]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_behavioral_context_mnemosyne_patcher
    file: batch1-behavioral_context_mnemosyne.md
    title: "Mnemosyne Phase Patcher Behavioral Context"
    description: "Behavioral context for Mnemosyne phase-level patch integrator and DRY_RUN validator, ensuring snapshot phases emit valid fallback metadata, respect dry-run invariants, and maintain traceable execution flow."
    type: behavioral
    status: active
    tier: γ
    domain: instructional
    applied_by: chief_ai_officer
    derived_from: "mnemosyne phase 4+ hardening requirements"
    tags: [mnemosyne, phase_patcher, behavioral_context, dry_run_validation]
    linked_personas: [Mnemosyne]
    confidence_score: 88
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [mnemosyne.sh, phase_scripts]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: meta_governance_patch_PR_001
    file: batch1-meta_governance_patch_PR_001_prompt_20250501_hestia_reference_cartography.md
    title: "Meta Governance Patch - Batch Autonomy Directive"
    description: "Clarify that soft communicative pauses implying user confirmation are disallowed under batch autonomy directives, maintaining continuous batch progression unless explicitly interrupted."
    type: governance_patch
    status: active
    tier: α
    domain: meta_governance
    applied_by: chief_ai_officer
    derived_from: "batch autonomy requirements"
    tags: [meta_governance, batch_autonomy, communication_protocol, governance_patch]
    linked_personas: []
    confidence_score: 82
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [prompt_20250501_hestia_reference_cartography]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_registry_audit_charon_refactor
    file: batch1-registry_audit_prompt_20250502_005.md
    title: "Registry Alignment Log: Charon Refactor"
    description: "Document process of refactoring Charon validation engine to align with current HESTIA registry structure, addressing updated path assumptions, tier-aware validation, and improved fault tolerance."
    type: audit
    status: completed
    tier: β
    domain: registry_audit
    applied_by: chief_ai_officer
    derived_from: "charon validation engine + HESTIA registry evolution"
    tags: [charon_refactor, registry_alignment, validation_engine, audit_log]
    linked_personas: []
    confidence_score: 84
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [charon_validation_engine, HESTIA_registries]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: audit_20250502_002
    file: batch2-audit_20250502_002.md
    title: "HESTIA CLI Tools Audit Protocol (Duplicate)"
    description: "Duplicate of audit_20250502_001 ensuring all CLI tools adopt modular Processor class structure and standardized interface patterns."
    type: audit
    status: active
    tier: β
    domain: tools_audit
    applied_by: chief_ai_officer
    derived_from: hestia_config_manager.py
    tags: [cli_tools, audit_duplicate, modular_structure]
    linked_personas: [Icaria]
    confidence_score: 75
    deviation_flag: true
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [validation_tools]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_auto_improve_prompt_qa
    file: batch2-auto-improve-auto-prompt-qa.md
    title: "Auto-Improve Auto-Prompt QA Protocol"
    description: "Meta-prompt for optimizing user messages toward inferred underlying intent, then executing optimized prompt with comprehensive shell command validation for hephaestus template engine testing."
    type: instructional
    status: active
    tier: γ
    domain: instructional
    applied_by: chief_ai_officer
    derived_from: "prompt optimization + template engine testing requirements"
    tags: [auto_improvement, prompt_optimization, qa_protocol, shell_testing]
    linked_personas: []
    confidence_score: 81
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [hephaestus_template_engine]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_20250501_hestia_reference_cartography_enhanced
    file: batch2-prompt_20250501_hestia_reference_cartography.md
    title: "HESTIA Reference Directory Cartography (Enhanced)"
    description: "Enhanced version of reference directory semantic inventory with explicit batch processing autonomy directives, preventing communicative pauses and maintaining continuous progression."
    type: recursive_structural
    status: active
    tier: β
    domain: knowledge_inventory
    applied_by: chief_ai_officer
    derived_from: "config_hestia_reference_tree.md + batch autonomy patch"
    tags: [document_cartography, batch_autonomy, enhanced_processing]
    linked_personas: []
    confidence_score: 90
    deviation_flag: false
    evaluations: []
    version: "1.1"
    changelog: []
    dependencies: [config_hestia_reference_tree.md]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_20250502_001_scenario
    file: batch2-prompt_20250502_001.md
    title: "HESTIA Tool Ecosystem Diagnostic Scenario"
    description: "Scenario-based prompt for HESTIA tool ecosystem containing fragmented scripts, expecting complete tool inventory, refactoring roadmap, and devops model with specific pass conditions."
    type: structured
    status: candidate
    tier: β
    domain: tooling_analysis
    applied_by: chief_ai_officer
    derived_from: "HESTIA tool ecosystem analysis"
    tags: [tool_ecosystem, diagnostic_scenario, refactoring_roadmap]
    linked_personas: []
    confidence_score: 78
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: []
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_20250502_007_architecture_alignment
    file: batch2-prompt_20250502_007.md
    title: "Toolchain Architecture Alignment Protocol"
    description: "Review HESTIA Configuration Manager CLI documentation and code to internalize architectural template for CLI interface design, modular execution, logging, and Home Assistant compatibility."
    type: behavioral
    status: proposed
    tier: α
    domain: architecture_alignment
    applied_by: chief_ai_officer
    derived_from: "README_config_manager.md + refactor_log + hestia_config_manager.py"
    tags: [architecture_alignment, toolchain_template, cli_design]
    linked_personas: []
    confidence_score: 85
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [README_config_manager.md, hestia_config_manager.py]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_20250501_phanes_final_audit_beta_alpha
    file: batch2-id: prompt_20250501_phanes_final_audit_b.yml
    title: "Phanes Final Validation and Rollout Protocol"
    description: "Execute full validation of Phanes v3.0 light generation system across Jinja scaffold, alpha registry, and rendered YAML outputs, determining readiness for α-tier promotion with behavioral guarantees."
    type: structured
    status: approved
    tier: β
    domain: light_entity_generation
    applied_by: chief_ai_officer
    derived_from: "README_Phanes_v3.0_FINAL.md + phanes_3.0_registry_corrected.py"
    tags: [phanes_validation, final_audit, tier_promotion, rollout_protocol]
    linked_personas: []
    confidence_score: 92
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [phanes_3.0.py, alpha_light_registry.json]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_20250530_001_synthesis
    file: batch2-prompt_20250530_001 prompts for synthesis.yml
    title: "Configuration Entity Audit and Synthesis Prompts"
    description: "Three-tiered prompt series for auditing hallucinated configuration entities, extracting verified source inventory, and rebuilding YAML from audited inputs with strict grounding requirements."
    type: structured
    status: active
    tier: β
    domain: diagnostic
    applied_by: chief_ai_officer
    derived_from: "configuration reconciliation requirements"
    tags: [configuration_audit, entity_synthesis, grounding_verification]
    linked_personas: []
    confidence_score: 83
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: []
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: task_room_sensor_mapping_reconstruction
    file: batch2-task: "Reconstruct enriched room-wise se.yml
    title: "Enriched Room-Wise Sensor Mapping Reconstruction"
    description: "Reconstruct enriched room-wise sensor mappings from HESTIA core registries, hydrating sensor metadata with canonical IDs, protocol stacks, and confidence metrics structured by room and zone."
    type: operational
    status: active
    tier: β
    domain: extraction
    applied_by: chief_ai_officer
    derived_from: "HESTIA core registries"
    tags: [sensor_mapping, room_reconstruction, registry_hydration, metadata_enrichment]
    linked_personas: []
    confidence_score: 87
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [omega_room_registry.json, omega_device_registry.json, alpha_sensor_registry.json]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: compliance_theator_followup_miniprompts
    file: batch3-compliance_theator_followup_miniprompts.md
    title: "Compliance Theater Followup Mini-Prompts"
    description: "Series of compliance enforcement mini-prompts addressing placeholder file delivery violations, expecting real content generation with actual confidence scores and registry entries."
    type: governance_patch
    status: active
    tier: α
    domain: governance
    applied_by: chief_ai_officer
    derived_from: "compliance violations + α-tier governance standards"
    tags: [compliance_enforcement, mini_prompts, governance_violations]
    linked_personas: []
    confidence_score: 79
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: []
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: gpt_config_template_review
    file: batch3-GPT_Config_Template_Review.md
    title: "Custom GPT Instructions: Hestia Configuration Reviewer"
    description: "Custom GPT behavioral instructions for Hestia Configuration Reviewer focusing on fixing broken configurations before optimization, with priority-based task hierarchy and architectural documentation integration."
    type: behavioral
    status: active
    tier: γ
    domain: instructional
    applied_by: chief_ai_officer
    derived_from: "HESTIA configuration requirements + GPT customization"
    tags: [gpt_instructions, configuration_reviewer, priority_hierarchy]
    linked_personas: []
    confidence_score: 86
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [HESTIA_architecture_docs]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: gpt_maintain_documentation
    file: batch3-GPT_Maintain_Documentation.md
    title: "GPT Assistant Instructions for HESTIA Architecture Documentation Maintenance"
    description: "Instructions for GPT assistants to review, groom, update, and expand HESTIA architecture documentation, ensuring clarity, integrity, and evolution with system growth."
    type: instructional
    status: active
    tier: γ
    domain: instructional
    applied_by: chief_ai_officer
    derived_from: "HESTIA architecture documentation requirements"
    tags: [documentation_maintenance, architecture_evolution, gpt_instructions]
    linked_personas: []
    confidence_score: 84
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [HESTIA_architecture_docs]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: gpt_restructure_protocol
    file: batch3-GPT_Restructure_Protocol.md
    title: "GPT File Restructuring & Redistribution Protocol"
    description: "Standard Operating Procedure for GPT-based assistants redistributing Home Assistant YAML packages, ensuring internal consistency, link integrity, and bulletproof risk mitigation with backup protocols."
    type: operational
    status: active
    tier: β
    domain: operational
    applied_by: chief_ai_officer
    derived_from: "HESTIA file restructuring requirements"
    tags: [file_restructuring, redistribution_protocol, risk_mitigation, backup_procedures]
    linked_personas: []
    confidence_score: 89
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: []
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_27_001_mnemosyne_validation
    file: batch3-prompt_20250527_001.md
    title: "Mnemosyne Phase Dependency Validation Prompts"
    description: "Series of structured prompts for validating Mnemosyne phase dependencies, variable scope, logging consistency, metadata compliance, shell compatibility, HA integration, and security review."
    type: structured
    status: candidate
    tier: β
    domain: validation
    applied_by: chief_ai_officer
    derived_from: "mnemosyne validation requirements"
    tags: [mnemosyne_validation, phase_dependencies, security_review, ha_integration]
    linked_personas: []
    confidence_score: 88
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [mnemosyne.sh]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_27_002_tiered_validation
    file: batch3-prompt_20250527_002.md
    title: "Tiered Phased Validation Mnemosyne Protocol"
    description: "Validation-grade review of remaining Mnemosyne Finalization Sequence phases with functional intent extraction, enrichment, edge case hardening, and prompt registry standards conformance."
    type: structured
    status: candidate
    tier: β
    domain: validation
    applied_by: chief_ai_officer
    derived_from: "mnemosyne finalization sequence"
    tags: [tiered_validation, mnemosyne_finalization, functional_intent, edge_cases]
    linked_personas: []
    confidence_score: 85
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [mnemosyne_finalization_sequence]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_27_014_dependency_hardening
    file: batch3-prompt_20250527_014.md
    title: "Tiered Dependency Construction and Enforcement Audit"
    description: "Multi-tier prompt for Mnemosyne phase dependency validation and hardening, from dependency declaration through runtime guards, dynamic chains, metadata propagation, and FORCE override compliance."
    type: structured
    status: candidate
    tier: β
    domain: phase_dependency_hardening
    applied_by: chief_ai_officer
    derived_from: "mnemosyne_v2.0.1.tar.gz analysis"
    tags: [dependency_hardening, multi_tier, phase_dependencies, force_override]
    linked_personas: []
    confidence_score: 91
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [mnemosyne_v2.0.1.tar.gz]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_grounded_config_inventory
    file: batch3-prompt_20250530_001 prompts Grounded Config Inventory Extraction.md
    title: "Grounded Configuration Inventory Extraction"
    description: "Series of prompts for extracting grounded configuration inventories from user input, scanning system components without speculation, and generating structured diagnostic summaries."
    type: extractor
    status: active
    tier: β
    domain: extraction
    applied_by: chief_ai_officer
    derived_from: "configuration inventory requirements"
    tags: [grounded_extraction, configuration_inventory, system_scanning, diagnostic_summary]
    linked_personas: []
    confidence_score: 82
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: []
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_claude_remediation_agent
    file: batch3-prompt_clauderemediation_agent_failed_qa.md
    title: "Claude Remediation Agent for Failed QA Audit"
    description: "Remediation agent prompt for failed QA audit of Hephaestus Template Engine v3.5, applying structured fixes to source code files based on consolidated QA report findings."
    type: operational
    status: active
    tier: β
    domain: validation
    applied_by: chief_ai_officer
    derived_from: "Hephaestus Template Engine v3.5 QA report"
    tags: [remediation_agent, qa_audit, template_engine, source_fixes]
    linked_personas: []
    confidence_score: 86
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [hephaestus_template_engine_v3.5]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_debug_001_inline_correction
    file: batch3-prompt_debug_001 inline correction.md
    title: "Inline Correction and HAOS Shell Hardening Debug Prompts"
    description: "Two-part debug prompt for inline code correction and HAOS shell script hardening, focusing on structural repair, logical corrections, and production-critical orchestration script debugging."
    type: operational
    status: active
    tier: β
    domain: diagnostic
    applied_by: chief_ai_officer
    derived_from: "debugging requirements + HAOS orchestration"
    tags: [inline_correction, haos_hardening, debug_prompts, shell_scripting]
    linked_personas: []
    confidence_score: 87
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: []
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_meta_yaml_structure
    file: batch3-prompt_meta_yaml_structure.md
    title: "Home Assistant YAML Meta-Structure Generation"
    description: "Generate inferred meta-structure per unique top-level entity type from Home Assistant YAML archives, determining entity origins, merge strategies, and syntax expectations with hard and soft rules."
    type: extractor
    status: active
    tier: β
    domain: extraction
    applied_by: chief_ai_officer
    derived_from: "Home Assistant YAML configuration analysis"
    tags: [yaml_meta_structure, entity_analysis, merge_strategies, configuration_patterns]
    linked_personas: []
    confidence_score: 84
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [configuration.yaml, HESTIA_YAML_archives]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_mnemosyne_diagnostics_trace
    file: batch3-prompt_mnemosyne_diagnostics_trace_20250528.md
    title: "Mnemosyne Modular Diagnostics Trace and Validation"
    description: "Trace and validate modular diagnostics in Mnemosyne pipeline, analyzing call-path integrity, function dependency tables, and validation checklists for production sign-off readiness."
    type: diagnostic
    status: active
    tier: β
    domain: diagnostic
    applied_by: chief_ai_officer
    derived_from: "mnemosyne modular diagnostics requirements"
    tags: [mnemosyne_diagnostics, modular_trace, call_path_integrity, production_readiness]
    linked_personas: []
    confidence_score: 89
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [mnemosyne.sh, mnemosyne_diagnostics]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_qa_takeover_exhaustive_audit
    file: batch4-**🔧 Prompt: Lead QA Takeover & Exhausti.md
    title: "Lead QA Takeover & Exhaustive Code Audit"
    description: "Lead QA Systems Engineer takeover prompt for Hephaestus Template Engine, performing assumption-validated QA audit with guardrail validation and comprehensive code review."
    type: operational
    status: active
    tier: α
    domain: validation
    applied_by: chief_ai_officer
    derived_from: "template_engine_backup + QA debugging log"
    tags: [qa_takeover, exhaustive_audit, assumption_validation, guardrail_review]
    linked_personas: []
    confidence_score: 93
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [template_engine_backup_2025-05-31, valid_context.json]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_20250528_008_long
    file: batch4-## 📦 `prompt_20250528_008_long`.md
    title: "Mnemosyne Declarative Orchestrator v4 Finalization"
    description: "Continue refinement on Mnemosyne Declarative Orchestrator v4 with critical logging.sh hotfix, remaining task completion, and project plan status verification through Phase 5 compliance."
    type: operational
    status: candidate
    tier: β
    domain: phase_dependency_hardening
    applied_by: chief_ai_officer
    derived_from: "mnemosyne v4 + logging.sh unbound variable fix"
    tags: [mnemosyne_v4, logging_hotfix, finalization, phase_compliance]
    linked_personas: []
    confidence_score: 88
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [mnemosyne_v4, logging.sh]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_20250527_001_content_review
    file: batch4-### 🧠 `prompt_20250527_001` – content review and optimization.md
    title: "Generic Content Review and Optimization Protocol"
    description: "Full document review prompt for structural and semantic audit, inferring author intent, analyzing clarity, and generating modular improvement plans with validation requirements."
    type: structured
    status: candidate
    tier: β
    domain: validation
    applied_by: chief_ai_officer
    derived_from: "content review and optimization requirements"
    tags: [content_review, semantic_audit, modular_improvement, validation_plans]
    linked_personas: []
    confidence_score: 80
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: []
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: analyze_convo_diagnostics_yaml
    file: batch4-analyze_convo_for_diagnostics_yaml.md
    title: "Diagnostic Hardening and Telemetry Consolidation Plan"
    description: "Execute full-spectrum diagnostic hardening and telemetry consolidation for macOS-based Glances telemetry via Home Assistant, including security hardening, DNS centralization, and automation syntax upgrade."
    type: operational
    status: active
    tier: β
    domain: diagnostic
    applied_by: chief_ai_officer
    derived_from: "chat_history_networking + ha-networking-configuration.yaml"
    tags: [diagnostic_hardening, telemetry_consolidation, glances_security, dns_centralization]
    linked_personas: [Promachos]
    confidence_score: 91
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [chat_history_networking, ha-networking-configuration.yaml]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: claude_phased_master_prompt_mnemosyne
    file: batch4-claude_phased_master_prompt_mnemosyne.md
    title: "Mnemosyne Finalization Sequence Phased Prompt Engineering"
    description: "Comprehensive phased prompt engineering plan for Mnemosyne finalization, covering architecture finalization, CLI wrapper design, shell command simplification, execution modes, and deployment validation."
    type: operational
    status: active
    tier: α
    domain: operational
    applied_by: chief_ai_officer
    derived_from: "mnemosyne finalization requirements"
    tags: [phased_prompting, mnemosyne_finalization, cli_design, deployment_validation]
    linked_personas: []
    confidence_score: 94
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [mnemosyne_pipeline.sh, mnemosyne.conf]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: generic_shell_script_review
    file: batch4-generic deep-dive shell script review prompt.md
    title: "Generic Deep-Dive Shell Script Review Protocol"
    description: "Generic shell script review prompt for full semantic and operational audit, logic tracing, confidence scoring, and prompt hydration potential assessment with structured output format."
    type: structured
    status: active
    tier: β
    domain: validation
    applied_by: chief_ai_officer
    derived_from: "shell script review requirements"
    tags: [shell_script_review, semantic_audit, logic_tracing, confidence_scoring]
    linked_personas: []
    confidence_score: 86
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: []
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: corrective_merge_directive
    file: batch4-id: 20250527_correctivemergeok.md
    title: "Corrective Merge Authorization Directive"
    description: "Authorization directive for full overwrite merge applying all patches into complete source structure and emitting unified system_instruction.yaml v1.3.1 with structural continuity."
    type: governance_patch
    status: active
    tier: α
    domain: meta_governance
    applied_by: chief_ai_officer
    derived_from: "merge authorization requirements"
    tags: [corrective_merge, overwrite_authorization, structural_continuity]
    linked_personas: []
    confidence_score: 78
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [system_instruction.yaml]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: debug_validation_prompting_guide
    file: batch4-id: 20250527_debug01.md
    title: "Debug Validation and Safety Integration Checks Guide"
    description: "Prompt engineering guide for validation assurance including line-by-line variable analysis and comprehensive safety check categories for uncovering hidden dependencies and architectural gaps."
    type: instructional
    status: active
    tier: γ
    domain: instructional
    applied_by: chief_ai_officer
    derived_from: "debug validation requirements"
    tags: [debug_validation, safety_checks, variable_analysis, hidden_dependencies]
    linked_personas: []
    confidence_score: 83
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [mnemosyne.sh]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_precision_debugging_mode_directive
    file: batch4-precision_debugging_mode.md
    title: "Precision Debugging Mode Directive Injection"
    description: "Behavioral directive injection for precision debugging mode, restricting responses to direct task focus, eliminating verbal overhead, and enforcing strict response structure with confidence gating."
    type: behavioral
    status: active
    tier: α
    domain: behavior_governance
    applied_by: chief_ai_officer
    derived_from: "precision debugging requirements"
    tags: [precision_debugging, directive_injection, behavioral_restriction, confidence_gating]
    linked_personas: []
    confidence_score: 89
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: []
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_20250526_003_validation_guide
    file: batch4-prompt_20250526_003.md
    title: "Icaria Friendly Validation Guide Post-Patch"
    description: "Icaria validation assistance prompt providing clear, confident next steps for validating patched Mnemosyne system with step-by-step instructions, file checks, and safety cautions."
    type: guided
    status: approved
    tier: α
    domain: validation
    applied_by: chief_ai_officer
    derived_from: "icaria_patch_trace + claude_style_prompting"
    tags: [icaria_validation, post_patch_guide, step_by_step, safety_cautions]
    linked_personas: [Icaria]
    confidence_score: 91
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [mnemosyne_v1.0.3_HOTFIX]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_mnemosyne_dry_run_schema_validator
    file: batch4-prompt_mnemosyne_dry_run_schema_validator_20250528.md
    title: "Mnemosyne Dry-Run Schema Validator"
    description: "Compare two dry-run outputs or JSON diagnostics from different Mnemosyne snapshots, identifying structural differences, type mismatches, and output deviations with severity ratings."
    type: structured
    status: active
    tier: β
    domain: validation
    applied_by: chief_ai_officer
    derived_from: "mnemosyne dry-run comparison requirements"
    tags: [dry_run_validation, schema_comparison, structural_diff, severity_rating]
    linked_personas: []
    confidence_score: 85
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [mnemosyne.sh]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_mnemosyne_variable_index
    file: batch4-prompt_mnemosyne_variable_index_20250528.md
    title: "Mnemosyne Variable and Reference Usage Index"
    description: "Create complete index of all variables, env flags, and script-local definitions used in each Mnemosyne phase, tracking declarations, exports, and dependencies for debugging and refactor planning."
    type: structured
    status: active
    tier: β
    domain: phase_dependency_hardening
    applied_by: chief_ai_officer
    derived_from: "mnemosyne variable tracking requirements"
    tags: [variable_indexing, phase_dependencies, env_flags, script_analysis]
    linked_personas: []
    confidence_score: 87
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [mnemosyne.sh, phase_scripts]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_module_diff_integrity_check
    file: batch4-prompt_module-diff_integrity_check.md
    title: "Module Diff Integrity Check Protocol"
    description: "Audit refactor information integrity ensuring all semantically meaningful components are accounted for, detecting information loss, and confirming functional equivalence with lineage mapping."
    type: operational
    status: pending
    tier: β
    domain: validation
    applied_by: chief_ai_officer
    derived_from: "module refactoring requirements"
    tags: [diff_integrity, refactor_audit, information_preservation, lineage_mapping]
    linked_personas: []
    confidence_score: 82
    deviation_flag: false
    evaluations: []
    version: "1.0"
    changelog: []
    dependencies: [ha-networking-configuration.yaml]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null

  - id: prompt_registry_live_ingest_v2_enhanced_duplicate
    file: batch4-prompt_registry_live_ingest_v2_enhanced.md
    title: "Enhanced Registry Batch Processing (Duplicate)"
    description: "Duplicate of main registry processing prompt with comprehensive validation, quality scoring, and governance frameworks for HESTIA prompt batch curation."
    type: incremental_ingest_with_validation
    status: active
    tier: α
    domain: registry_governance
    applied_by: chief_ai_officer
    derived_from: "prompt_20250510_metastructor_registry_curation_v5"
    tags: [registry_governance, batch_processing, validation_duplicate]
    linked_personas: [MetaStructor]
    confidence_score: 70
    deviation_flag: true
    evaluations: []
    version: "2.0"
    changelog: []
    dependencies: [registry_validation_engine, registry_governance_framework]
    usage_frequency:
      daily: 0
      monthly: 0
      last_used: null
