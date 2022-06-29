import json
import logging
import functools
import traceback

from target.common.config import Config
from logging.handlers import TimedRotatingFileHandler

logger = logging.getLogger(__name__)

logger.setLevel(Config.logfile_level)

# Console Handler
console_handler = logging.StreamHandler()
console_handler.setLevel(Config.console_level)
console_handler.setFormatter(logging.Formatter(
    "[%(levelname)s] %(asctime)s: %(message)s"))
logger.addHandler(console_handler)

# Log file Handler
file_handler = TimedRotatingFileHandler(
    Config.logfile_path,
    when='D',
    interval=Config.logfile_interval,
    backupCount=Config.logfile_backup_count
)
file_handler.setLevel(Config.logfile_level)
file_handler.setFormatter(logging.Formatter(
    "[%(levelname)s] %(asctime)s: %(message)s"))
logger.addHandler(file_handler)

# Error log file Handler
error_handler = TimedRotatingFileHandler(
    Config.logfile_path + '.error',
    when='D',
    interval=Config.logfile_interval,
    backupCount=Config.logfile_backup_count
)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter(
    "[%(levelname)s] %(asctime)s: %(message)s"))
logger.addHandler(error_handler)


CALL_LEVEL = -1
PLACEHOLDER = " " * 4


def functionLog(func):
    """ Auto logging decorator to function calling

    Function is excepeted return tuple as (suc, data).
    Logging arguements of this function and return value.
    Handling all exception occured in this function, logging traceback and return False.

    """
    @functools.wraps(func)
    def wrapper(*args, **kw):
        global CALL_LEVEL, PLACEHOLDER
        CALL_LEVEL += 1

        if CALL_LEVEL == 0:
            logger.debug("{placeholder}[{module}.{func}] << {args} {kw}".format(
                        placeholder=PLACEHOLDER*CALL_LEVEL,
                        module=func.__module__,
                        func=func.__qualname__,
                        args=",".join(["{}".format(_arg) for _arg in args]),
                        kw=",".join(["{} = {}".format(k, v) for k, v in kw.items()])))
        else:
            logger.debug("{placeholder}[{module}.{func}] << {args} {kw}".format(
                placeholder=PLACEHOLDER*CALL_LEVEL,
                module=func.__module__,
                func=func.__qualname__,
                args=",".join(["{}".format(_arg) for _arg in args]),
                kw=",".join(["{} = {}".format(k, v) for k, v in kw.items()])))

        try:
            suc, res = func(*args, **kw)

        except Exception as e:
            logger.error('[{module}.{func}] {trace}'.format(
                module=func.__module__,
                func=func.__qualname__,
                trace=traceback.format_exc()))
            CALL_LEVEL -= 1
            return False, e

        else:
            if suc:
                if CALL_LEVEL == 0:
                    logger.debug("{placeholder}[{module}.{func}] >> {out}".format(
                        placeholder=PLACEHOLDER*CALL_LEVEL,
                        module=func.__module__,
                        func=func.__qualname__,
                        out=res))
                else:
                    logger.debug("{placeholder}[{module}.{func}] >> {out}".format(
                        placeholder=PLACEHOLDER*CALL_LEVEL,
                        module=func.__module__,
                        func=func.__qualname__,
                        out=res))

            else:
                logger.warning("{placeholder}[{module}.{func}] {error}".format(
                    placeholder=PLACEHOLDER*CALL_LEVEL,
                    module=func.__module__,
                    func=func.__qualname__,
                    error=res))
            CALL_LEVEL -= 1
            return suc, res

    return wrapper


def normalFuncLog(func):
    """ More general auto logging decorator to function call

    Function can return any form of data.
    Handling all exception occured in this function, logging traceback and return None.

    """
    @functools.wraps(func)
    def wrapper(*args, **kw):
        global CALL_LEVEL, PLACEHOLDER
        CALL_LEVEL += 1

        if CALL_LEVEL == 0:
            logger.debug("{placeholder}[{module}.{func}] << {args} {kw}".format(
                placeholder=PLACEHOLDER*CALL_LEVEL,
                module=func.__module__,
                func=func.__qualname__,
                args=",".join(["{}".format(_arg) for _arg in args]),
                kw=",".join(["{} = {}".format(k, v) for k, v in kw.items()])))
        else:
            logger.debug("{placeholder}[{module}.{func}] << {args} {kw}".format(
                placeholder=PLACEHOLDER*CALL_LEVEL,
                module=func.__module__,
                func=func.__qualname__,
                args=",".join(["{}".format(_arg) for _arg in args]),
                kw=",".join(["{} = {}".format(k, v) for k, v in kw.items()])))

        try:
            out = func(*args, **kw)

        except Exception:
            logger.error('[{module}.{func}] {trace}'.format(
                module=func.__module__,
                func=func.__qualname__,
                trace=traceback.format_exc()))
            CALL_LEVEL -= 1
            return None

        else:
            if CALL_LEVEL == 0:
                logger.debug("{placeholder}[{module}.{func}] >> {out}".format(
                    placeholder=PLACEHOLDER*CALL_LEVEL,
                    module=func.__module__,
                    func=func.__qualname__,
                    out=out))
            else:
                logger.debug("{placeholder}[{module}.{func}] >> {out}".format(
                    placeholder=PLACEHOLDER*CALL_LEVEL,
                    module=func.__module__,
                    func=func.__qualname__,
                    out=out))

            CALL_LEVEL -= 1
            return out

    return wrapper