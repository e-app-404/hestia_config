# TEMPLATE: Preview Configuration Files
#
# This directory contains generated configuration previews that may include:
# - SMB/CIFS share configurations
# - Generated service configurations  
# - Preview configurations with embedded credentials
# - Network service configurations
#
# These files are excluded from git tracking as they may contain:
# - Generated credentials
# - Network paths and shares
# - Service-specific configuration with PII
#
# Template structure for preview configs:
# [global]
# server_string = "__SERVER_NAME__"
# workgroup = "__WORKGROUP__"
# 
# [share_name]
# browseable = true
# path = "__SHARE_PATH__"
# valid_users = "__USER_LIST__"
#
# Replace __PLACEHOLDER__ values with actual configuration.
# These files contain generated credentials and are excluded from git tracking.

# Example preview configuration files:
# - smb.conf (Samba/SMB share configuration)