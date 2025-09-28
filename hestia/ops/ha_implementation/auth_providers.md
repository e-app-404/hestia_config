---
title: "Authentication providers"
authors: "Home Assistant"
source: "Home Assistant Docs"
slug: "optimize-your-home-assistant-database"
tags: ["home-assistant","database","mariadb","influxdb","ops"]
original_date: "2022-04-05"
last_updated: "2025-05-30"
url: "https://www.home-assistant.io/docs/authentication/providers/"
---

# Authentication providers

> **Caution**: This is an advanced feature. When you log in, an auth provider checks your credentials to make sure you are an authorized user.

Home Assistant configures sensible default authentication providers. You only
need to specify `auth_providers` in `configuration.yaml` if you are configuring
more than one provider. Note that specifying `auth_providers` will disable any
default providers not listed, which may reduce security or cause login issues if
misconfigured.

## Recommended pattern

If you want to add `trusted_networks` but still allow normal login when outside
your LAN, include the default `homeassistant` provider as well:

```yaml
homeassistant:
  auth_providers:
    - type: homeassistant
    - type: trusted_networks
      trusted_networks:
        - 192.168.0.0/24
```

Authentication providers are configured under the `homeassistant:` block in
`configuration.yaml`. If you are moving configuration to packages, the
`auth_providers` configuration must remain in `configuration.yaml` (see upstream
issue 16441).

## Available auth providers

### Home Assistant (default)

This is the built-in provider. The first user created during onboarding is the
owner and can create/manage other users. User credentials are stored under
`.storage` in your config directory; passwords are salted and hashed.

Configuration example (default provider):

```yaml
homeassistant:
  auth_providers:
    - type: homeassistant
```

If no `auth_providers` section is present, Home Assistant will configure the
default provider automatically.

### Trusted networks

`trusted_networks` allows you to allowlist IP addresses or networks so that
users accessing from those addresses won't be prompted for a password. When
accessing from a trusted network, the login form will prompt the user to
select which account to use and will not require a password.

> **Important**: Do not list networks that are also used as `trusted_proxies` — the trusted_networks provider will fail with "Your computer is not allowed" if you do.

Example:

```yaml
homeassistant:
  auth_providers:
    - type: trusted_networks
      trusted_networks:
        - 192.168.0.0/24
        - fd00::/8
```

#### Configuration variables (trusted_networks)

- trusted_networks (list, required): list of IPv4/IPv6 addresses or networks to allowlist.
- trusted_users (map, optional): map of IPs or networks to user IDs (or lists of user IDs) available for selection when logging in from those addresses.
- allow_bypass_login (boolean, optional, default false): when true, and only a single non-system user is available for selection, bypass the login page.

Trusted users example:

```yaml
homeassistant:
  auth_providers:
    - type: trusted_networks
      trusted_networks:
        - 192.168.0.0/24
        - 192.168.10.0/24
        - fd00::/8
      trusted_users:
        192.168.0.1: user1_id
        192.168.0.0/24:
          - user1_id
          - user2_id
        "fd00::/8":
          - user1_id
          - group: system-users
```

> **Notes**:
> - Use user IDs (not usernames) for `trusted_users`. To find a user ID open `/config/users/` in the UI and copy the ID for a user
> - IPv6 addresses in keys must be quoted

## Skip login page (allow bypass)

If `allow_bypass_login` is enabled and exactly one non-system user is available
to choose from, Home Assistant will skip the login page and jump straight to
the main UI. Cookies are not persisted when bypassing the login, so a new
session is created on each page refresh.

Example:

```yaml
homeassistant:
  auth_providers:
    - type: trusted_networks
      trusted_networks:
        - 192.168.0.0/24
        - 127.0.0.1
        - ::1
      allow_bypass_login: true
    - type: homeassistant
```

## Command line auth provider

The `command_line` provider runs an external command to authenticate users.
The environment variables `username` and `password` are passed to the
command; an exit code of 0 grants access. This provider can integrate with
external systems such as LDAP or RADIUS.

Example:

```yaml
homeassistant:
  auth_providers:
    - type: command_line
      command: /absolute/path/to/command
      # args: ["--first", "--second"]
      # meta: true
```

When `meta: true` is set the command can print key/value pairs to stdout to
populate fields in the created user object (only on first authentication). The
format is:

```
name = John Doe
group = system-users
local_only = true
```

Supported meta variables:
- name: the display name for the user
- group: either `system-admin` (administrator) or `system-users` (regular users)
- local_only: if true, the created user can only log in from local networks

Leading/trailing whitespace is stripped from the username before the command is
invoked. Meta variables are only applied on the first authentication for a
given user; subsequent logins reuse the previously created user object.

## Security notes

> **Security considerations**:
> - Do not expose `trusted_networks` entries to untrusted networks
> - Do not commit any secrets or credentials to your repository

---
