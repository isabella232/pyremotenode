import logging
import re
import shlex
import subprocess

from pyremotenode.tasks import BaseTask, TaskException

RE_OUTPUT = re.compile(r'^.*(ok|warning|critical|invalid)\s*\-.+', flags=re.IGNORECASE)

# TODO: Make Command / BaseTask responsible for initiating the activities that are configured within an action


class Command(BaseTask):
    def __init__(self, path, name=None, **kwargs):
        BaseTask.__init__(self, **kwargs)
        self._name = name if name else path
        self._args = [path]
        self._proc = None

        for k, v in kwargs.items():
            if k in ["id", "scheduler"]:
                continue
            self._args.append("--{0}".format(k))
            self._args.append(v)
        logging.debug("Command: {0}".format(self._args))

    def default_action(self, **kwargs):
        logging.info("Checking command {0}".format(self._name))
        ret = None

        try:
            ret = subprocess.check_output(args=shlex.split(" ".join(self._args)), universal_newlines=True)
        except subprocess.CalledProcessError as e:
            logging.warning("Got error code {0} and message: {1}".format(e.returncode, e.output))
            # TODO: Evaluate how this will be handled in the end
            raise TaskException("The called command failed with an out of bound return code...")

        logging.debug("Check return output: {0}".format(ret))
        self.state = ret.strip()
        return self.process_check_output(ret)

    def process_check_output(self, output):
        try:
            status = RE_OUTPUT.match(str(output)).group(1)
        except Exception:
            status = None

        if not status:
            raise TaskException("An unparseable status was received from the called process: {}".format(str(output)))
        attr = "{0}".format(status.upper())

        logging.debug("Got valid status output: {0}".format(status))

        # TODO: Change this to have configuration parsing in the BaseTask
        if hasattr(self, attr):
            return getattr(self, attr)

        return self.INVALID
