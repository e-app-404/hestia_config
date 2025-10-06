#!/bin/bash

# Manual Entity Takeover for Mobile Devices
# This script manually performs the takeover operations since API renaming isn't available

echo "🔄 MANUAL MOBILE DEVICE ENTITY TAKEOVER"
echo "======================================="
echo
echo "The automated takeover failed because Home Assistant doesn't support entity renaming via API."
echo "Here's what you need to do manually in the Home Assistant UI:"
echo

# Read the plan file and generate manual instructions
PLAN_FILE="/config/hestia/workspace/reports/checkpoints/ENTITY_DEDUP/mobile_devices_cleanup_plan_final.json"

if [[ -f "$PLAN_FILE" ]]; then
    echo "📋 MANUAL TAKEOVER INSTRUCTIONS:"
    echo "================================"
    echo
    
    jq -r '.[] | 
      . as $group | 
      ([.candidates[] | select(.disabled_by == null)] | sort_by(.entity_id) | reverse | .[0].entity_id) as $winner |
      
      if $winner != $group.base then
        "GROUP: " + $group.base + "\n" +
        "1. Go to Settings → Devices & Services → Entities\n" +
        "2. Find: " + $group.base + "\n" +
        "3. Disable the old entity: " + $group.base + "\n" +
        "4. Find: " + $winner + "\n" +
        "5. Click on " + $winner + " → Entity Settings\n" +
        "6. Change Entity ID from: " + $winner + "\n" +
        "7. Change Entity ID to: " + $group.base + "\n" +
        "8. Click Update\n" +
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
      else
        ""
      end
    ' "$PLAN_FILE"
    
    echo
    echo "📊 SUMMARY:"
    echo "==========="
    
    TOTAL_GROUPS=$(jq 'length' "$PLAN_FILE")
    TAKEOVER_COUNT=$(jq '[.[] | . as $group | ([.candidates[] | select(.disabled_by == null)] | sort_by(.entity_id) | reverse | .[0].entity_id) as $winner | select($winner != $group.base)] | length' "$PLAN_FILE")
    
    echo "• Total Groups: $TOTAL_GROUPS"
    echo "• Takeover Operations Needed: $TAKEOVER_COUNT"
    echo "• Simple Disables: $((TOTAL_GROUPS - TAKEOVER_COUNT))"
    echo
    echo "⚡ QUICK METHOD:"
    echo "==============="
    echo "Instead of manual UI work, you can also:"
    echo "1. Keep using the _2 entities (they're the current ones)"
    echo "2. Just disable the old base entities without renaming"
    echo "3. Update any automations/dashboards to use the _2 entity IDs"
    echo
    echo "This achieves the same result with less manual work!"
    
else
    echo "❌ Plan file not found: $PLAN_FILE"
fi

echo
echo "🛡️ BACKUP LOCATION:"
echo "==================="
echo "Your complete .storage backup is at:"
echo "/config/hestia/workspace/archive/backups/20251006T230755Z/"
echo
echo "If anything goes wrong, run:"
echo "./restore.sh"
echo