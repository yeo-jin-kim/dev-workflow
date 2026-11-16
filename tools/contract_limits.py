"""Optional frozen execution ceilings shared by intake and W1 dispatch."""


def validate_contract_limits(contract, seconds, cycles):
    limits = contract.get('execution_limits')
    if limits is None:
        return  # Historical contracts retain their existing budget rules.
    if not isinstance(limits, dict):
        raise ValueError('Contract execution_limits must be an object.')
    for key, value in [('total_seconds_max', seconds), ('max_cycles_max', cycles)]:
        maximum = limits.get(key)
        if type(maximum) is not int or maximum < 1 or type(value) is not int or not 1 <= value <= maximum:
            raise ValueError('Execution exceeds or invalidates frozen contract limit: ' + key)
