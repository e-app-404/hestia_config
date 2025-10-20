---
id: prompt_20251001_2a4bbe
slug: gpt-output-template-ha-config-declaration-mapper
title: Gpt Output Template Ha Config Declaration Mapper
date: '2025-10-01'
tier: "beta"
domain: operational
persona: generic
status: candidate
tags: []
version: '1.0'
source_path: gpt-validate-config/gpt-output-template-ha-config-declaration-mapper.csv
author: Unknown
related: []
last_updated: '2025-10-09T02:33:25.530866'
redaction_log: []
---

unique_id,configuration_line_number,configuration_value,configuration_target,declaration_type,is_valid,target_type,target_value,target_content,content_valid,parent_block,error_reason,recursion_depth
abcd1234,12,automation: !include_dir_merge_list hestia/automations,/config/hestia/automations,include_dir_merge_list,True,folder,automations,automation,True,automation,,1
efgh5678,34,input_number: !include hestia/helpers/input_number.yaml,/config/hestia/helpers/input_number.yaml,include,True,file,input_number.yaml,input,False,input_number,invalid_yaml,1
ijkl9012,55,phanes: !include_dir_merge_named hestia/packages/phanes,/config/hestia/packages/phanes,include_dir_merge_named,False,folder,phanes,package,False,homeassistant.packages,not_found,1

