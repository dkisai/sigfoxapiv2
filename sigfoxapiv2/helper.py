def make_sigfox_url(endpoint: str, fargs: dict = None):
    """
    Tries to add optional arguments to JSON
    :endpoint Sigfox API endpoints
    :key The key name of the item to be added
    :value the value to be added. If this "none", then nothing is added
    :return: sigfox api url
    """
    url_str = "https://api.sigfox.com/v2/{}".format(endpoint)
    if fargs is not None:
        url_str = url_str.format(**fargs)
    return url_str


def try_add_optional_arg(arg_list: dict, key: str, value: any):
    """
    Tries to add optional arguments to JSON
    :arg_list dictionary of data to try append to
    :key The key name of the item to be added
    :value the value to be added. If this "none", then nothing is added
    """
    if value is not None:
        arg_list[key] = value
