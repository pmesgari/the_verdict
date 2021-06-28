def unflatten(adict, separator='.'):
    result = {}
    for key, value in adict.items():
        _unflatten(key, value, result, separator)
    return result


def _unflatten(key, value, out, separator):
    key, *rest = key.split(separator, 1)
    if rest:
        _unflatten(rest[0], value, out.setdefault(key, {}), separator)
    else:
        out[key] = value