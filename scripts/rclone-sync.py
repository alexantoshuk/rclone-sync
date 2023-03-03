#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import watchdog
import logging
from watchdog.observers import Observer
import subprocess
from pathlib import Path
import json
import os


class RClone:
    """
    Wrapper class for rclone.
    """

    def __init__(self, logger=None):
        self.log = logger or logging.root

    def _execute(self, command_with_args, warning_in_debug=False):
        """
        Execute the given `command_with_args` using Popen
        Args:
            - command_with_args (list) : An array with the command to execute,
                                         and its arguments. Each argument is given
                                         as a new element in the list.
        """
        self.log.info("Invoking : %s", " ".join(command_with_args))
        try:
            with subprocess.Popen(
                    command_with_args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE) as proc:
                (out, err) = proc.communicate()

                # out = proc.stdout.read()
                # err = proc.stderr.read()

                self.log.debug(out)
                if err:
                    if warning_in_debug:
                        self.log.debug(err.decode(
                            "utf-8").replace("\\n", "\n"))
                    else:
                        self.log.warning(err.decode(
                            "utf-8").replace("\\n", "\n"))

                return {
                    "code": proc.returncode,
                    "out": out,
                    "error": err
                }
        except FileNotFoundError as not_found_e:
            self.log.error("Executable not found. %s", not_found_e)
            return {
                "code": -20,
                "error": not_found_e
            }
        except Exception as generic_e:
            self.log.exception("Error running command. Reason: %s", generic_e)
            return {
                "code": -30,
                "error": generic_e
            }

    def run_cmd(self, command, extra_args=[], warning_in_debug=False):
        """
        Execute rclone command
        Args:
            - command (string): the rclone command to execute.
            - extra_args (list): extra arguments to be passed to the rclone command
        """

        command_with_args = ["rclone", command]
        command_with_args += extra_args
        command_result = self._execute(command_with_args, warning_in_debug)

        return command_result

    def copyto(self, source, dest, flags=[], warning_in_debug=False):
        """
        Executes: rclone copyto source:path dest:path [flags]
        Args:
        - source (string): A string "source:path"
        - dest (string): A string "dest:path"
        - flags (list): Extra flags as per `rclone copyto --help` flags.
        """
        return self.run_cmd(command="copyto", extra_args=[source] + [dest] + flags, warning_in_debug=warning_in_debug)

    def mkdir(self, dest, flags=[], warning_in_debug=False):
        """
        Executes: rclone mkdir dest:path [flags]
        Args:
        - dest (string): A string "dest:path"
        - flags (list): Extra flags as per `rclone mkdir --help` flags.
        """
        return self.run_cmd(command="mkdir", extra_args=[dest] + flags, warning_in_debug=warning_in_debug)

    def rmdir(self, dest, flags=[], warning_in_debug=False):
        """
        Executes: rclone rmdir dest:path [flags]
        Args:
        - dest (string): A string "dest:path"
        - flags (list): Extra flags as per `rclone rmdir --help` flags.
        """
        return self.run_cmd(command="rmdir", extra_args=[dest] + flags, warning_in_debug=warning_in_debug)

    def copy(self, source, dest, flags=[], warning_in_debug=False):
        """
        Executes: rclone copy source:path dest:path [flags]
        Args:
        - source (string): A string "source:path"
        - dest (string): A string "dest:path"
        - flags (list): Extra flags as per `rclone copy --help` flags.
        """
        return self.run_cmd(command="copy", extra_args=[source] + [dest] + flags, warning_in_debug=warning_in_debug)

    def sync(self, source, dest, flags=[], warning_in_debug=False):
        """
        Executes: rclone sync source:path dest:path [flags]
        Args:
        - source (string): A string "source:path"
        - dest (string): A string "dest:path"
        - flags (list): Extra flags as per `rclone sync --help` flags.
        """
        return self.run_cmd(command="sync", extra_args=[source] + [dest] + flags, warning_in_debug=warning_in_debug)

    def listremotes(self, flags=[], warning_in_debug=False):
        """
        Executes: rclone listremotes [flags]
        Args:
        - flags (list): Extra flags as per `rclone listremotes --help` flags.
        """
        return self.run_cmd(command="listremotes", extra_args=flags, warning_in_debug=warning_in_debug)

    def ls(self, dest, flags=[], warning_in_debug=False):
        """
        Executes: rclone ls remote:path [flags]
        Args:
        - dest (string): A string "remote:path" representing the location to list.
        """
        return self.run_cmd(command="ls", extra_args=[dest] + flags, warning_in_debug=warning_in_debug)

    def lsd(self, dest, flags=[], warning_in_debug=False):
        """
        Executes: rclone lsd remote:path [flags]
        Args:
        - dest (string): A string "remote:path" representing the location to list.
        """
        return self.run_cmd(command="lsd", extra_args=[dest] + flags, warning_in_debug=warning_in_debug)

    def lsjson(self, dest, flags=[], warning_in_debug=False):
        """
        Executes: rclone lsjson remote:path [flags]
        Args:
        - dest (string): A string "remote:path" representing the location to list.
        """
        return self.run_cmd(command="lsjson", extra_args=[dest] + flags, warning_in_debug=warning_in_debug)

    def delete(self, dest, flags=[], warning_in_debug=False):
        """
        Executes: rclone delete remote:path
        Args:
        - dest (string): A string "remote:path" representing the location to delete.
        """
        return self.run_cmd(command="delete", extra_args=[dest] + flags, warning_in_debug=warning_in_debug)

    def deletefile(self, dest, flags=[], warning_in_debug=False):
        """
        Executes: rclone deletefile remote:path
        Args:
        - dest (string): A string "remote:path" representing the location to delete.
        """
        return self.run_cmd(command="deletefile", extra_args=[dest] + flags, warning_in_debug=warning_in_debug)

    def purge(self, dest, flags=[], warning_in_debug=False):
        """
        Executes: rclone purge remote:path
        Args:
        - dest (string): A string "remote:path" representing the location to delete.
        """
        return self.run_cmd(command="purge", extra_args=[dest] + flags, warning_in_debug=warning_in_debug)


class SyncEventHandler(watchdog.events.FileSystemEventHandler):
    def __init__(self, local_dir, remote_dir, dry_run=True, logger=None):
        super().__init__()
        self.local_dir = local_dir
        self.remote_dir = remote_dir
        self.logger = logger or logging.root
        self.rclone = RClone(logger=self.logger)
        self.rclone_args = []
        self.dir_moved_state = False
        if dry_run:
            self.rclone_args.append("--dry-run")

    def _remote_path(self, local_path):
        return local_path.replace(self.local_dir, self.remote_dir, 1)

    def on_moved(self, event):
        self.logger.info('')
        super().on_moved(event)

        if event.is_directory:
            what = 'directory'
            self.logger.info("Moved %s: from %s to %s", what, event.src_path,
                             event.dest_path)
            self.rclone.purge(self._remote_path(
                event.src_path), self.rclone_args + ["--retries", "1"], warning_in_debug=True)

            self.rclone.mkdir(self._remote_path(
                event.dest_path), self.rclone_args)
            return

        what = 'file'
        self.logger.info("Moved %s: from %s to %s", what, event.src_path,
                         event.dest_path)

        self.rclone.deletefile(self._remote_path(
            event.src_path), self.rclone_args + ["--retries", "1"], warning_in_debug=True)
        self.rclone.copyto(event.dest_path, self._remote_path(
            event.dest_path), self.rclone_args)

    def on_created(self, event):
        self.logger.info('')
        super().on_created(event)

        if event.is_directory:
            what = 'directory'
            self.logger.info("Created %s: %s", what, event.src_path)
            self.rclone.mkdir(self._remote_path(
                event.src_path), self.rclone_args)
            return

        what = 'file'
        self.logger.info("Created %s: %s", what, event.src_path)
        self.rclone.copyto(event.src_path, self._remote_path(
            event.src_path), self.rclone_args)

    def on_deleted(self, event):
        self.logger.info('')
        super().on_deleted(event)

        if event.is_directory:
            what = 'directory'
            self.logger.info("Deleted %s: %s", what, event.src_path)
            self.rclone.purge(self._remote_path(
                event.src_path), self.rclone_args)
            return

        what = 'file'
        self.logger.info("Deleted %s: %s", what, event.src_path)
        self.rclone.deletefile(self._remote_path(
            event.src_path), self.rclone_args)

    def on_modified(self, event):
        if event.is_directory:
            super().on_modified(event)
            return

        self.logger.info('')
        super().on_modified(event)
        what = 'file'
        self.logger.info("Modified %s: %s", what, event.src_path)
        self.rclone.copyto(event.src_path, self._remote_path(
            event.src_path), self.rclone_args)


def main():
    conf_template = """
    {
        "local_dir": "/path_to/local_dir_name",
        "remote_dir": "remote:remote_dir_name",
        "dry_run": false,
        "log_level": "INFO"
    }

    """
    home = Path.home()
    conf_path = os.path.join(home, ".rclone-sync.json")
    local_dir = remote_dir = None
    log_level = 'INFO'
    dry_run = False

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    if not os.path.isfile(conf_path):
        msg = "Config '~/.rclone-sync.json' is not exists. Config template:\n" + conf_template
        logging.error(msg)
        raise Exception(msg)

    with open(conf_path, 'r') as conf_file:
        try:
            conf_dict = json.load(conf_file)
            local_dir = conf_dict.get('local_dir')
            remote_dir = conf_dict.get('remote_dir')
            dry_run = conf_dict.get("dry_run", False)
            log_level = conf_dict.get("log_level", 'INFO')
        except:
            pass

    logging.root.setLevel(log_level)

    if (not local_dir) or (not remote_dir):
        msg = "Config '~/.rclone-sync.json' has invalid data. Config template:\n" + conf_template
        logging.error(msg)
        raise Exception(msg)

    if not os.path.isdir(local_dir):
        msg = "Local dir '%s' is not exists" % local_dir
        logging.error(msg)
        raise Exception(msg)

    event_handler = SyncEventHandler(local_dir, remote_dir, dry_run=dry_run)
    if event_handler.rclone.lsd(remote_dir).get('code') == 1:
        msg = "Remote dir '%s' is not exists" % remote_dir
        logging.error(msg)
        raise Exception(msg)

    observer = Observer()
    observer.schedule(event_handler, local_dir, recursive=True)
    observer.start()
    try:
        while observer.is_alive():
            observer.join(1)
    finally:
        observer.stop()
        observer.join()


if __name__ == "__main__":
    main()
