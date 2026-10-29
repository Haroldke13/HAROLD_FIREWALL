"""HAROLD_FIREWALL: one Kivy app for Linux, Windows, macOS and Android.

Linux (nftables): shows the policy state and can apply or roll back it through the
root helper installed by linux/install_root.sh. Every change asks first.

Windows, macOS, Android: status viewer only. Open a saved `nft list ruleset` output
from a Linux host to read it. Nothing is changed on those systems.
"""
import subprocess
import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.utils import platform

HELPER = "/usr/local/sbin/nac-nat-policy"
BRAND = "HAROLD_FIREWALL · Harold IT Data"
IS_LINUX = platform == "linux"          # Android reports its own platform, not 'linux'
MAX_IMPORT_BYTES = 1_000_000


def helper(action):
    """Run one fixed helper action through sudo. No shell, no free-form arguments."""
    proc = subprocess.run(["sudo", "-n", HELPER, action],
                          capture_output=True, text=True, timeout=60)
    out = (proc.stdout + proc.stderr).strip()
    if proc.returncode != 0:
        raise RuntimeError(out or f"helper exited {proc.returncode}")
    return out


def summarize(text):
    """Tell loaded from not loaded for both tables, from helper output or an nft dump."""
    tables = {"inet nac_policy": ("table inet nac_policy", "inet nac_policy: LOADED"),
              "ip nac_nat": ("table ip nac_nat", "ip nac_nat: LOADED")}
    lines = []
    for name, markers in tables.items():
        loaded = any(m in text for m in markers)
        lines.append(f"{name}: {'loaded' if loaded else 'not loaded'}")
    return "\n".join(lines)


class PolicyApp(App):
    title = "HAROLD_FIREWALL"

    def build(self):
        self.root_box = BoxLayout(orientation="vertical", padding=12, spacing=8)
        self.status = Label(text="Starting…", size_hint_y=None, height=90, halign="left", valign="middle")
        self.status.bind(size=lambda w, s: setattr(w, "text_size", (s[0], None)))
        self.root_box.add_widget(self.status)

        row = BoxLayout(size_hint_y=None, height=52, spacing=8)
        self.btn_refresh = Button(text="Refresh", on_release=lambda *_: self.refresh())
        self.btn_apply = Button(text="Apply policy", on_release=lambda *_: self.confirm_apply())
        self.btn_rollback = Button(text="Roll back", on_release=lambda *_: self.confirm_rollback())
        self.btn_import = Button(text="Open status file", on_release=lambda *_: self.open_file())
        for b in (self.btn_refresh, self.btn_apply, self.btn_rollback, self.btn_import):
            row.add_widget(b)
        self.root_box.add_widget(row)

        scroll = ScrollView()
        self.output = Label(text="", size_hint_y=None, font_name="RobotoMono-Regular",
                            font_size="12sp", halign="left", valign="top")
        self.output.bind(texture_size=lambda w, s: setattr(w, "height", s[1]))
        self.output.bind(size=lambda w, s: setattr(w, "text_size", (s[0], None)))
        scroll.add_widget(self.output)
        self.root_box.add_widget(scroll)
        self.root_box.add_widget(Label(text=BRAND, size_hint_y=None, height=24,
                                       font_size="12sp", color=(0.6, 0.6, 0.6, 1)))

        if not IS_LINUX:
            self.btn_apply.disabled = True
            self.btn_rollback.disabled = True
            self.btn_refresh.disabled = True
            self.status.text = ("Status viewer on this platform. nftables runs on Linux only.\n"
                                "Open an `nft list ruleset` file saved from a Linux host.")
        else:
            self.refresh()
        return self.root_box

    # ----- Linux: helper calls off the UI thread -----
    def run_action(self, action):
        self.set_busy(True)
        threading.Thread(target=self._worker, args=(action,), daemon=True).start()

    def _worker(self, action):
        try:
            result = (True, helper(action))
        except Exception as exc:  # shown in the UI, never crashes the app
            result = (False, str(exc))
        Clock.schedule_once(lambda _dt: self.finish(action, *result))

    def finish(self, action, ok, text):
        self.set_busy(False)
        if not ok:
            self.status.text = f"{action} failed:\n{text}"
            return
        if action == "status":
            self.show(text)
        else:
            self.status.text = f"{action}: {text}"
            self.refresh()

    def refresh(self):
        self.run_action("status")

    def set_busy(self, busy):
        for b in (self.btn_refresh, self.btn_apply, self.btn_rollback):
            b.disabled = busy

    def show(self, text):
        self.status.text = summarize(text)
        self.output.text = text

    # ----- confirmations -----
    def confirm(self, message, on_yes):
        box = BoxLayout(orientation="vertical", padding=10, spacing=10)
        box.add_widget(Label(text=message))
        row = BoxLayout(size_hint_y=None, height=48, spacing=10)
        popup = Popup(title="Confirm", content=box, size_hint=(0.9, 0.45))
        yes = Button(text="Yes")
        no = Button(text="No")
        yes.bind(on_release=lambda *_: (popup.dismiss(), on_yes()))
        no.bind(on_release=lambda *_: popup.dismiss())
        row.add_widget(yes)
        row.add_widget(no)
        box.add_widget(row)
        popup.open()

    def confirm_apply(self):
        self.confirm("Load the masquerade and no-port-forwarding policy?\n"
                     "A ruleset backup is saved first.",
                     lambda: self.run_action("apply"))

    def confirm_rollback(self):
        self.confirm("Remove the nac_policy and nac_nat tables?\n"
                     "Docker and libvirt rules are not touched.",
                     lambda: self.run_action("rollback"))

    # ----- status file import (all platforms) -----
    def open_file(self):
        chooser = FileChooserListView(path=self.user_data_dir, filters=["*.txt", "*.nft", "*"])
        box = BoxLayout(orientation="vertical")
        box.add_widget(chooser)
        popup = Popup(title="Choose a status file", content=box, size_hint=(0.95, 0.9))

        def load(*_):
            if not chooser.selection:
                return
            path = chooser.selection[0]
            popup.dismiss()
            try:
                with open(path, "rb") as fh:
                    data = fh.read(MAX_IMPORT_BYTES + 1)
                if len(data) > MAX_IMPORT_BYTES:
                    raise ValueError("file is larger than 1 MB")
                self.show(data.decode("utf8", "replace"))
            except (OSError, ValueError) as exc:
                self.status.text = f"Could not open file: {exc}"

        row = BoxLayout(size_hint_y=None, height=48)
        row.add_widget(Button(text="Open", on_release=load))
        row.add_widget(Button(text="Cancel", on_release=lambda *_: popup.dismiss()))
        box.add_widget(row)
        popup.open()


if __name__ == "__main__":
    PolicyApp().run()
