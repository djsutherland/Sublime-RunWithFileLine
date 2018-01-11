import os
import shlex
import subprocess

import sublime_plugin


class RunWithFileLineCommand(sublime_plugin.TextCommand):
    def settings(self):
        return self.view.settings().get("run_with_file_line")

    def is_enabled(self):
        settings = self.settings()
        if settings is None:
            return False

        if "syntax" in settings:
            syn, ext = os.path.splitext(os.path.basename(
                self.view.settings().get("syntax")))
            assert ext in {'.sublime-syntax', '.tmLanguage'}
            if syn != settings['syntax']:
                return False

        if "command" not in settings:
            return False

        return True

    def cwd(self):
        settings = self.settings()
        if 'cwd' in settings:
            return settings['cwd']

        f = self.view.window().project_file_name()
        if f is not None:
            return os.path.dirname(f)

        return None

    def run(self, edit):
        settings = self.settings()
        n = self.view.file_name()
        if n is None:
            return
        l, c = self.view.rowcol(self.view.sel()[0].begin())  # 0-based

        command = os.path.expanduser(
            settings["command"].format(file=n, line=l+1, col=c+1))
        kwargs = {'cwd': self.cwd(), 'stderr': subprocess.STDOUT,
                  'shell': self.settings().get("shell", False)}
        if not kwargs['shell']:
            command = shlex.split(command)

        try:
            print(subprocess.check_output(command, **kwargs).decode(), end='')
        except subprocess.CalledProcessError as e:
            print(e.output.decode(), end='')
            print("[command returned {}]".format(e.returncode))
