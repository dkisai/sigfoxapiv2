def make_sigfox_url(endpoint: str):
    return f"https://api.sigfox.com/v2{endpoint}"


def try_add_optional_arg(arg_list: dict, key: str, value: any):
    """
    Tries to add optional arguments to JSON
    :arg_list dictionary of data to try append to
    :key The key name of the item to be added
    :value the value to be added. If this "none", then nothing is added
    """
    if value is not None:
        arg_list[key] = value
