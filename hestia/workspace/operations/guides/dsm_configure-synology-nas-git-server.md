---
title: "Configure Synology NAS as Git Server"
description: "Step-by-step guide to hosting bare Git repositories on a Synology DiskStation (e.g., DS414 running DSM 5.0)."
authors: 
  - "walkerjeffd"
source: gist.github.com
date:
last_updated:
url: [https://gist.github.com/walkerjeffd/374750c366605cd5123d]
tags: [synology, git, diskstation, dsm, ssh]
references:
  - [http://blog.osdev.org/git/2014/02/13/using-git-on-a-synology-nas.html](http://blog.osdev.org/git/2014/02/13/using-git-on-a-synology-nas.html)
  - [https://stackoverflow.com/questions/20074692/set-up-git-on-a-nas-with-synologys-official-package](https://stackoverflow.com/questions/20074692/set-up-git-on-a-nas-with-synologys-official-package)
  - [http://www.heidilux.com/2014/02/setup-git-server-synology-nas/](http://www.heidilux.com/2014/02/setup-git-server-synology-nas/)
---

# Configure Synology NAS as Git Server

Instructions for setting up a Git server on a Synology NAS with DiskStation Manager (DSM). Example device: **DS414**, DSM **5.0**.

## 1) Set up user and shared folder

1. Create a user **`gituser`** in DSM and grant:

   * **File Station** access
   * **WebDAV** privileges (if you plan to use WebDAV; optional for SSH-only)
2. Create a shared folder **`git`** at `/volume1/git`.

   * Give **read/write** permissions to `gituser` and `admin`.
3. Install the **Git Server** package from **Package Center**.
4. Open **Git Server** and **allow `gituser`** in the permitted users list.
5. Enable SSH:

   * **Control Panel → Terminal & SNMP → Enable SSH service**.

## 2) Configure SSH access for `gituser`

Create the SSH key directory and upload your public key.

```sh
# Create .ssh for gituser (run from your machine)
ssh admin@diskstation.local 'mkdir -p /volume1/homes/gituser/.ssh'

# Copy your public key up to the NAS
scp ~/.ssh/id_rsa.pub admin@diskstation.local:/volume1/homes/gituser/.ssh
```

Rename the uploaded key to `authorized_keys` and set permissions:

```sh
ssh root@diskstation.local
mv /volume1/homes/gituser/.ssh/id_rsa.pub /volume1/homes/gituser/.ssh/authorized_keys
chown -R gituser:users /volume1/homes/gituser/.ssh
chmod 700 /volume1/homes/gituser/.ssh
chmod 644 /volume1/homes/gituser/.ssh/authorized_keys
```

> Tip: If `authorized_keys` already exists, append instead:
>
> ```sh
> cat /volume1/homes/gituser/.ssh/id_rsa.pub >> /volume1/homes/gituser/.ssh/authorized_keys
> ```

## 3) Create a bare repository on the NAS

```sh
ssh root@diskstation.local
cd /volume1/git/
git --bare init <repo-name>.git
chown -R gituser:users <repo-name>.git
cd <repo-name>.git
git update-server-info   # optional; useful for dumb HTTP transport
```

> Note: `git update-server-info` is mainly required for the “dumb” HTTP protocol. For SSH usage it’s typically not needed.

## 4) Use the NAS repo from your local machine

Clone via SSH (or add as a remote to an existing repo):

```sh
# Clone
git clone ssh://gituser@diskstation.local/volume1/git/<repo-name>.git

# OR add NAS as a remote to an existing local repo
git remote add origin ssh://gituser@diskstation.local/volume1/git/<repo-name>.git
git push -u origin main
```
