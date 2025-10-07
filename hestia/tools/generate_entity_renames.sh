#!/usr/bin/env bash
# generate_entity_renames.sh  
# Generate commands to rename _2 entities back to canonical names
# Usage: ./generate_entity_renames.sh

echo "# Entity Rename Commands"
echo "# Use Home Assistant GUI: Settings → Devices & Services → Mobile App → [Device] → [Entity] → Rename"
echo ""

echo "## ePhone UK Entities (22 entities)"
jq -r '
.data.entities[] | 
select(.config_entry_id == "01K6MCMF7CZQQX132VSKW9GP8B" and (.entity_id | endswith("_2"))) |
"Rename: \(.entity_id) → \(.entity_id | sub("_2$"; ""))"
' /config/.storage/core.entity_registry

echo ""
echo "## MacBook Entities (21 entities)"  
jq -r '
.data.entities[] | 
select(.config_entry_id == "01K6Y2XP5BVWE1FVKNK4QMV66K" and (.entity_id | endswith("_2"))) |
"Rename: \(.entity_id) → \(.entity_id | sub("_2$"; ""))"
' /config/.storage/core.entity_registry

echo ""
echo "## Special Cases"
jq -r '
.data.entities[] | 
select(.config_entry_id == "01K6Y2XP5BVWE1FVKNK4QMV66K" and (.entity_id | endswith("_3"))) |
"Rename: \(.entity_id) → \(.entity_id | sub("_3$"; ""))"
' /config/.storage/core.entity_registry