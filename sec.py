from random import randint

def compare(str1, str2):
    return compare_const(str1, str2)

def compare_const(str1, str2):
    """Constant-time string comparasion, to avoid timing attacks.

    Leaks the lenght, but that's ok since we are always comparing
    hashes, and the only information the adversary has to gain by
    the length of a hash as a better guess at what hashing algorithm
    is being used. At which point, i'd like to point out Shannons
    Maxim."""
    length = min(len(str1), len(str2))
    
    ret = True
    for i in xrange(length):
        if str1[i] != str2[i]:
            ret = False
            
    if len(str1) != len(str2):
        ret = False
        
    return ret

def compare_noleak(str1, str2):
    """A non-random version that doesn't leak the length, made for Baldur :)

    str1 should be the user-supplied string, and str2 the string you comare
    against.

    NOTE: Pads with 0x00, only inteded to compare strings, not byte-lists."""

    l1 = len(str1)
    l2 = len(str2)
    
    if l1 > l2:
        # If the user string is longer than the source string, pad.
        delta = l1 - l2
        str2 += "\x00"*delta

    ret = True
    for i in xrange(l1):
        if str1[i] != str2[i]:
            ret = False
        
    return ret


def compare_rnd(str1, str2):
    """Constant-time string comparasion, to avoid timing attacks.
    Start in a random char of the string.

    Doesn't leak the length, since the starting point (and thus the
    breaking point) as randomly chosen."""

    length = min(len(str1), len(str2))
    start = randint(0, length-1)

    for i in xrange(length):
        j = (start+i) % length
        if str1[j] != str2[j]:
            return False

    if len(str1) != len(str2):
        return False
    
    return True
    
