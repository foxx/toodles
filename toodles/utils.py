class TooLongError(ValueError):
    pass


def pad(seq, target_length, padding=None):
    """Extend the sequence seq with padding (default: None) so as to make
    its length up to target_length. Return seq. If seq is already
    longer than target_length, raise TooLongError.

    >>> pad([], 5, 1)
    [1, 1, 1, 1, 1]
    >>> pad([1, 2, 3], 7)
    [1, 2, 3, None, None, None, None]
    >>> pad([1, 2, 3], 2)
    ... # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
      ...
    TooLongError: sequence too long (3) for target length 2

    """
    length = len(seq)
    if length > target_length:
        raise TooLongError("sequence too long ({}) for target length {}"
                           .format(length, target_length))
    seq.extend([padding] * (target_length - length))
    return seq


def ensure_instance(value, types):
    """
    Ensure value is an instance of a certain type
    >>> ensure_instance(1, [str])
    Traceback (most recent call last):
    TypeError:
    >>> ensure_instance(1, str)
    Traceback (most recent call last):
    TypeError:
    >>> ensure_instance(1, int)
    >>> ensure_instance(1, (int, str))
    :attr types: Type of list of types
    """
    if not isinstance(value, types):
        raise TypeError(
            "expected instance of {}, got {}".format(
                types, value))

def makelist(data):
    """
    Thanks bottle
    XXX: needs UT
    """
    if isinstance(data, (list, set, tuple)):
        return list(data)
    elif data:
        return [data]
    else:
        return []



def padded_split(value, sep, maxsplit=None, pad=None):
    """
    Modified split() to include padding
    See http://code.activestate.com/lists/python-ideas/3366/

    :attr value: see str.split()
    :attr sep: see str.split()
    :attr maxsplit: see str.split()
    :attr pad: Value to use for padding maxsplit

    >>> padded_split('text/html', ';', 1)
    ['text/html', None]
    >>> padded_split('text/html;q=1', ';', 1)
    ['text/html', 'q=1']
    >>> padded_split('text/html;a=1;b=2', ';', 1)
    ['text/html', 'a=1;b=2']
    >>> padded_split('text/html', ';', 1, True)
    ['text/html', True]
    >>> padded_split('text/html;a=1;b=2', ';', 2)
    ['text/html', 'a=1', 'b=2']
    >>> padded_split('text/html;a=1', ';', 2)
    ['text/html', 'a=1', None]
    """
    result = value.split(sep, maxsplit)
    if maxsplit is not None:
        result.extend(
            [pad] * (1+maxsplit-len(result)))
    return result

