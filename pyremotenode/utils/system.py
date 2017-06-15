import fcntl
import os


class pid_file:
    def __init__(self, path):
        self._path = path

        if os.path.exists(path):
            raise PidFileExistsError

        self._f = open(path, mode='w')
        fcntl.lockf(self._f, fcntl.LOCK_EX)
        self._f.write(str(os.getpid()))
        self._f.flush()

    def __enter__(self):
        return self._f

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._f.close()
        os.unlink(self._path)


class PidFileExistsError(IOError):
    pass