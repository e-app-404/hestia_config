# Keychain lookup snippets

This small collection contains helper functions to retrieve SMB passwords from the macOS Keychain and fall back to an interactive prompt when required.

## Files

- `keychain_snippets.sh` — Shell functions you can source into your mount helper.

## Overview

The helpers try to locate credentials in the macOS Keychain first and, if not available, prompt the user on the controlling terminal. They are intentionally small and designed to be sourced into an existing mount helper script.

## Functions

- get_password_by_label <label>
  - Tries `security find-generic-password -l <label> -w` then `security find-internet-password -l <label> -w`.
  - Prints the password on stdout and returns exit status 0 on success.

- get_password_by_server_account <server> <account>
  - Uses `security find-internet-password -s <server> -a <account> -w` to locate internet passwords.

- pw_lookup_or_prompt <label> <server> <account>
  - Attempts `get_password_by_label`, then `get_password_by_server_account`, and finally prompts the user on `/dev/tty` when necessary.
  - Prints the password to stdout; the caller should immediately URL-encode and unset the plaintext variable.

## Integration guidance

- Do NOT log or echo plaintext passwords. Example usage (caller must URL-encode and unset immediately):

```bash
PW=$(pw_lookup_or_prompt "ha_nas_system" "192.168.0.104" "babylonrobot")
PW_ENC=$(urlenc "$PW")
unset PW
```

- Prefer storing labels that map to Keychain entries rather than embedding usernames and passwords in scripts.

## Security notes

- These helpers access the system or login Keychain. The `security` tool may prompt for permission to access items depending on keychain ACLs.
- Avoid writing plaintext passwords to disk or logs.

## Example

See the commented example at the bottom of `keychain_snippets.sh` which demonstrates integrating the helper into the mount flow.

## Validation

Quick test performed locally:

- URL-encoding function verified: input `p@ssw:rd!` produced `p%40ssw%3Ard%21`.
- Keychain lookup: the `get_password_by_label 'ha_nas_system'` call successfully returned the keychain item on this host (the test printed the password to stdout). If the keychain item is absent or access is denied, the command prints an error and returns non-zero.

Important: the validation run captured the password output into `/tmp/ha_keychain_test_output.txt`. Treat that file as sensitive and remove it after inspection:

```bash
rm /tmp/ha_keychain_test.sh /tmp/ha_keychain_test_output.txt \
  /tmp/ha_keychain_test_lookup.txt /tmp/ha_keychain_test_urlenc.txt
```

Sample safe output (URL-encoding only):

```
URLENC: p%40ssw%3Ard%21
```
## Security & cleanup reminders

- The `security` tool may prompt for permission to access keychain items; this is expected.
- Never leave plaintext passwords in temporary files. Remove any `/tmp/ha_keychain_test_*` artifacts after your test.

## Integration suggestion

Use `pw_lookup_or_prompt` from `keychain_snippets.sh` in your mount helper and immediately encode and unset the plaintext password:

```bash
PW=$(pw_lookup_or_prompt "ha_nas_system" "192.168.0.104" "babylonrobot")
PW_ENC=$(urlenc "$PW")
unset PW

# now use $PW_ENC in your mount_smbfs URL and avoid logging plaintext values
```

