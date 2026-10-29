#!/bin/bash
# Run once on the Linux host, as root, from the repository folder:
#   sudo bash linux/install_root.sh
# Installs the helper, a root-owned copy of the policy, and a sudo rule that lets the
# user who ran sudo (SUDO_USER) run only the helper, without a password.
set -euo pipefail
if [[ $EUID -ne 0 ]]; then echo "run with sudo" >&2; exit 1; fi
USER_NAME=${SUDO_USER:-}
[[ -n "$USER_NAME" && "$USER_NAME" != root ]] || { echo "run via sudo from your normal user account" >&2; exit 1; }
HERE=$(cd "$(dirname "$0")/.." && pwd)

install -o root -g root -m 0755 "$HERE/linux/nac-nat-policy" /usr/local/sbin/nac-nat-policy
install -d -o root -g root -m 0755 /usr/local/share/nac-nat
install -o root -g root -m 0644 "$HERE/policy/nac-nat-policy.nft" /usr/local/share/nac-nat/policy.nft
printf '%s ALL=(root) NOPASSWD: /usr/local/sbin/nac-nat-policy\n' "$USER_NAME" > /etc/sudoers.d/nac-nat-policy
chmod 0440 /etc/sudoers.d/nac-nat-policy
visudo -cf /etc/sudoers.d/nac-nat-policy
echo "installed for user $USER_NAME. Status:"
/usr/local/sbin/nac-nat-policy status
