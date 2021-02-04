__true_map = ['true', 't', '1', 'y', 'yes']
__false_map = ['false', 'f', '0', 'n', 'no']


def str2bool(s):
    if s.lower() in __true_map:
        return True
    if s.lower() in __false_map:
        return False
    raise ValueError(f'"{s}" is not a valid boolean value!')
