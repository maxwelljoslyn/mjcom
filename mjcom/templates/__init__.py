from calendar import month_name
from pprint import pformat

import pendulum
import web
from web import tx
from web.microformats import discover_post_type

__all__ = [
    "discover_post_type",
    "month_name",
    "pendulum",
    "pformat",
    "post_mkdn",
    "tx",
    "andlist",
]


def post_mkdn(content):
    return web.mkdn(content)  # XXX , globals=micropub.markdown_globals)


def andlist(l, separator):
    """Format a list for human-facing display, with the last item set off by 'and'.
    >>> andlist([1, 2, 3], ', ')
    '1, 2 and 3'
    """
    if not l:
        raise ValueError(f"argument list must have at least one item")
    elif len(l) == 1:
        return l[0]
    elif len(l) == 2:
        return f"{l[0]} and {l[1]}"
    else:
        initials = separator.join([str(x) for x in l[:-1]])
        final = f" and {l[-1]}"
        return initials + final
