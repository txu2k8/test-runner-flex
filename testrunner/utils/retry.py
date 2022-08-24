#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:retry
@time:2022/04/03
@email:tao.xu2008@outlook.com
@description: 重试装饰器
"""

import traceback
import random
import functools
from functools import partial

from loguru import logger
from tpRunner.utils.util import print_progressbar

try:
    from decorator import decorator
except ImportError:
    def decorator(caller):
        """ Turns caller into a decorator.
        Unlike decorator module, function signature is not preserved.
        :param caller: caller(f, *args, **kwargs)
        """
        def decor(f):
            @functools.wraps(f)
            def wrapper(*args, **kwargs):
                return caller(f, *args, **kwargs)
            return wrapper
        return decor


default_logger = logger  # logging.getLogger(__name__)


def _retry_internal(f, exceptions=Exception, tries=-1, delay=0, max_delay=None, backoff=1, jitter=0,
                    raise_exception=True, logger=default_logger):
    """
    Executes a function and retries it if it failed.
    :param f: the function to execute.
    :param exceptions: an exception or a tuple of exceptions to catch. default: Exception.
    :param tries: the maximum number of attempts. default: -1 (infinite).
    :param delay: initial delay between attempts. default: 0.
    :param max_delay: the maximum value of delay. default: None (no limit).
    :param backoff: multiplier applied to delay between attempts. default: 1 (no backoff).
    :param jitter: extra seconds added to delay between attempts. default: 0.
                   fixed if a number, random if a range tuple (min, max)
    :param logger: logger.warning(fmt, error, delay) will be called on failed attempts.
                   default: retry.default_logger. if None, logging is disabled.
    :returns: the result of the f function.
    """
    _tries, _delay = tries, delay
    while _tries:
        try:
            return f()
        except exceptions as e:
            if 'An error occurred (500)' in str(e) and _tries > 2:
                # _tries = 2
                pass

            _tries -= 1

            if logger is not None:  # and tries not in (-1, 0, 1)
                if not _tries:
                    logger.error('{err}, retry <{f_name}> times arrived!!!({tries}/{total_tries})'.format(
                        err=e, f_name=f.func.__name__, delay=_delay, tries=(tries - _tries), total_tries=tries))
                    logger.warning(traceback.format_exc())

                    if raise_exception is True:
                        raise e
                    else:
                        return False
                else:
                    logger.warning('{err}, retry <{f_name}> after {delay} seconds...({tries}/{total_tries})'.format(
                        err=e, f_name=f.func.__name__, delay=_delay, tries=(tries - _tries), total_tries=tries))
                    if tries - _tries == 1:
                        logger.debug(traceback.format_exc())
            else:
                print('{err}, retry <{f_name}> after {delay} seconds...({tries}/{total_tries})'.format(
                    err=e, f_name=f.func.__name__, delay=_delay, tries=(tries - _tries), total_tries=tries))
                if not _tries and raise_exception is True:
                    raise e
                else:
                    return False

            # time.sleep(_delay)
            print_progressbar(_delay)
            _delay *= backoff

            if isinstance(jitter, tuple):
                _delay += random.uniform(*jitter)
            else:
                _delay += jitter

            if max_delay is not None:
                _delay = min(_delay, max_delay)


def retry(exceptions=Exception, tries=-1, delay=0, max_delay=None, backoff=1, jitter=0, raise_exception=True,
          logger=default_logger):
    """Returns a retry decorator.
    :param exceptions: an exception or a tuple of exceptions to catch. default: Exception.
    :param tries: the maximum number of attempts. default: -1 (infinite).
    :param delay: initial delay between attempts. default: 0.
    :param max_delay: the maximum value of delay. default: None (no limit).
    :param backoff: multiplier applied to delay between attempts. default: 1 (no backoff).
    :param jitter: extra seconds added to delay between attempts. default: 0.
                   fixed if a number, random if a range tuple (min, max)
    :param raise_exception: raise exception every retry if True
    :param logger: logger.warning(fmt, error, delay) will be called on failed attempts.
                   default: retry.default_logger. if None, logging is disabled.
    :returns: a retry decorator.
    """

    @decorator
    def retry_decorator(f, *fargs, **fkwargs):
        args = fargs if fargs else list()
        kwargs = fkwargs if fkwargs else dict()
        return _retry_internal(partial(f, *args, **kwargs), exceptions, tries, delay, max_delay, backoff, jitter,
                               raise_exception, logger)

    return retry_decorator


def retry_call(f, fargs=None, fkwargs=None, exceptions=Exception, tries=-1, delay=0, max_delay=None, backoff=1,
               jitter=0, raise_exception=True, logger=default_logger):
    """
    Calls a function and re-executes it if it failed.
    :param f: the function to execute.
    :param fargs: the positional arguments of the function to execute.
    :param fkwargs: the named arguments of the function to execute.
    :param exceptions: an exception or a tuple of exceptions to catch. default: Exception.
    :param tries: the maximum number of attempts. default: -1 (infinite).
    :param delay: initial delay between attempts. default: 0.
    :param max_delay: the maximum value of delay. default: None (no limit).
    :param backoff: multiplier applied to delay between attempts. default: 1 (no backoff).
    :param jitter: extra seconds added to delay between attempts. default: 0.
                   fixed if a number, random if a range tuple (min, max)
    :param raise_exception: raise exception every retry if True
    :param logger: logger.warning(fmt, error, delay) will be called on failed attempts.
                   default: retry.default_logger. if None, logging is disabled.
    :returns: the result of the f function.
    """
    args = fargs if fargs else list()
    kwargs = fkwargs if fkwargs else dict()
    return _retry_internal(partial(f, *args, **kwargs), exceptions, tries, delay, max_delay, backoff, jitter,
                           raise_exception, logger)


@retry(tries=3, delay=1, raise_exception=False)
def test(a):
    if a < 3:
        raise Exception('err')


if __name__ == '__main__':
    pass
    # disable decorator by call the func.__wrapped__()
    # retry_call(test.__wrapped__, fkwargs={'a': 1}, tries=3, delay=2)
    test(1)
