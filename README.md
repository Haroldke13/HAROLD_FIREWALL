# HAROLD_FIREWALL

By Harold IT Data. Website: harolditdata.uk

# HAROLD_FIREWALL

A small app for viewing and applying a Linux nftables NAT policy: masquerade for container and VM subnets, and no inbound port forwarding. One Kivy codebase builds for Linux, Windows, macOS and Android.

| Platform | What the app does |
|---|---|
| Linux | Shows the policy state. Applies or rolls back the policy through a root helper. Every change asks first. |
| Windows, macOS, Android | Status viewer only. Open a saved `nft list ruleset` output from a Linux host. Nothing is changed. |

nftables exists only on Linux, so the other platforms can't apply or roll back the policy.

## Download

Go to **Releases** and pick the file for your system:

- `HAROLD_FIREWALL-linux-x86_64.tar.gz`, plus `HAROLD_FIREWALL-linux-helper.tar.gz` for the root helper
- `HAROLD_FIREWALL-Setup.exe` (Windows installer) or `HAROLD_FIREWALL.exe` (portable)
- `HAROLD_FIREWALL-macos.zip` (unzip, then open `HAROLD_FIREWALL.app`)
- `HAROLD_FIREWALL-android-debug.apk`

Check each file against the matching `SHA256SUMS-*.txt`:

```
sha256sum -c SHA256SUMS-linux.txt
```

Windows and macOS builds are **unsigned**, so the OS will warn you. The Android APK is a **debug** build: allow installing from your browser or file manager first.

## Linux: install the policy control

1. Unpack the helper and run from its folder:
   ```
   sudo bash linux/install_root.sh
   ```
   This installs a root helper, a root-owned copy of the policy, and a sudo rule that lets your user run only that helper, without a password.
2. Edit the subnets in `policy/nac-nat-policy.nft` to match your Docker and libvirt bridges, then run step 1 again.
3. Start the app. Apply and Roll back work from there.

To remove everything: `sudo nac-nat-policy rollback`, then delete `/usr/local/sbin/nac-nat-policy`, `/usr/local/share/nac-nat/` and `/etc/sudoers.d/nac-nat-policy`.

## Status viewer (Windows, macOS, Android)

On a Linux host, run `sudo nft list ruleset > ruleset.txt`, copy the file to the device, and press **Open status file** in the app.

## Limits

- Kernel IP forwarding stays on, because Docker and libvirt need it. The policy works through the forward chain's default-drop policy.
- The policy changes only its own two tables. Other firewall rules are left alone.
- Android and macOS builds cannot control nftables.
- Use this only on hosts and networks you administer.

## Build from source

- Python 3.11, then `pip install -r requirements.txt`
- Run: `python main.py`
- Windows exe: `pyinstaller --onefile --windowed --name HAROLD_FIREWALL main.py`
- Android: `buildozer -v android debug` (needs Java 17 and the Android SDK; the CI workflow shows the steps)

Releases are built by `.github/workflows/build.yml` when a `v*` tag is pushed.
