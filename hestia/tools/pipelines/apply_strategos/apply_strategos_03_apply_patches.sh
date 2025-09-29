#!/usr/bin/env bash
set -euo pipefail
: "${HA_MOUNT:=$HOME/hass}"
source ${HA_MOUNT}/hestia/tools/apply_strategos_00_env.sh >/dev/null

: "${OUT_DIR:?OUT_DIR not set}"
: "${TMP_DIR:?TMP_DIR not set}"
: "${SCRATCH_TGZ:?SCRATCH_TGZ not set}"
: "${SCRATCH_DIR:?SCRATCH_DIR not set}"

MERGED="${OUT_DIR}/merged/config/hestia/core"
mkdir -p "${MERGED}"
SCRATCH_TMP="${TMP_DIR}/scratch"
mkdir -p "${SCRATCH_TMP}"

# Acquire scratch files (from tgz or dir)

if [[ -f "${SCRATCH_TGZ}" ]]; then
tar -xzf "${SCRATCH_TGZ}" -C "${TMP_DIR}"
SRC="${TMP_DIR}/scratch"
else
SRC="${SCRATCH_DIR}"
fi

PRIMARY="${SRC}/20250907-patch-network.conf.diff"
SECONDARY="${SRC}/20250907-patch-network.conf-secondary.diff"

if [[ ! -f "${PRIMARY}" ]]; then
	echo "ERROR: Primary patch file not found: ${PRIMARY}" >&2
	exit 2
fi
if [[ ! -f "${SECONDARY}" ]]; then
	echo "ERROR: Secondary patch file not found: ${SECONDARY}" >&2
	exit 2
fi

pushd "${MERGED}" >/dev/null

# Init ephemeral git for 3-way apply resilience


git init -q
git config user.email "evert.app@proton.me"
git config user.name "Copilot"

# Ensure all files are tracked before initial commit
git add .
if [[ -n $(git status --porcelain) ]]; then
	git commit -qm "base"
else
	echo "No files to commit for base; continuing patch step."
fi

apply_patch() {
	local DIFF="$1"
	local TAG="$2"
	# Use git apply for git-formatted diffs
	if git apply --allow-empty "$DIFF"; then
		git add -A
		git commit -qm "apply $TAG (git apply)"
	else
		echo "BLOCKED: VALIDATION -> patch:${TAG} failed to apply cleanly" >&2
		exit 3
	fi
}

apply_patch "${PRIMARY}" "primary"
apply_patch "${SECONDARY}" "secondary"
popd >/dev/null