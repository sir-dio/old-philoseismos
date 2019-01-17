import struct
from math import frexp, ceil


def unpack_ibm32(bytearray_: bytearray, endian: str) -> float:
    """ Unpacks a bytearray containing the 4 byte IBM floating point value.

    The way it works is by unpacking a value as a unsigned long and
    dissasembling it bit by bit. """

    # It is 32 bits long. First bit is sign, then 7 bits of exponent,
    # then 24 bits of fraction

    # first, unpack the bytes as an unsigned integer -> it will just get all
    # the bits
    ibm = struct.unpack(endian + 'L', bytearray_)[0]

    # now we have an integer -> straight interpretation of the bits.
    # we can extract all the information from it

    # first, get the last bit - sign:
    sign = ibm >> 31
    # # get 7 last bits (8 by shift and remove one by &) - exponent:
    exponent = ibm >> 24 & 0b1111111
    # the first 24 bits (get them with &) are fraction. get them and divide
    # by 2 to the power of 24:
    fraction = (ibm & 0b111111111111111111111111) / float(pow(2, 24))

    # the result is (-1) ** sign * fraction * 16 ** (exponent - 64)
    return (1 - 2 * sign) * fraction * pow(16, exponent - 64)


def pack_ibm32(value: float, endian: str) -> bytearray:
    """ Packs a floating point value into a  4 byte IBM floating point.

    Works the opposite way of unpack_ibm32 -> constructs an unsigned long
    from given float. """

    # first, we check for obvious values:
    if value == 0:
        return bytes(4)
    elif abs(value) > 7.2370051459731155e+75:
        print('The value is too large to be packed as IBM!')
        return
    elif abs(value) < 5.397605346934028e-79:
        print('The value is too small to be packed as IBM!')

    # check what the sign bit shoud be:
    if value < 0:
        sign = 1
        value *= -1
    else:
        sign = 0

    # value = M * pow(2, E). M - mantissa, E - exponent, can be found with:
    M, E = frexp(value)
    # in IBM base is not 2, however, it's 16. So
    # we need to change M and E (to N and F) so that
    # value = N * pow(16, F)
    # where N is tne new mantissa and F is the new exponent.

    # note that pow(16, F) is the same as pow(2, 4F).
    # -> F = E / 4
    f = E / 4

    # an exponent always must be an integer, so we have to round it up:
    F = ceil(f)
    # the F we have now is F = f + f_err,
    # where f is the true value, and f_err is the integer error.
    # we have to know the error to adjust the mantissa:
    f_err = F - f

    # We know that
    # value = M * pow(2, E) = N * pow(2, 4F) ->
    # N = M * pow(2, E - 4F)
    # since F = f + f_err, and f = E / 4, we get: F = E/4 + f_err
    # so the formula to correct the mantissa is:
    # N = M * pow(2, -4 * f_err)

    N = M * pow(2, -4 * f_err)

    # we also now that the exponent bias is 64, so we add it to the value:
    F += 64
    # and that there are 24 bits of fraction, so we multily it by
    # 2 to the power of 24:
    N = int(N * pow(2, 24))

    # now to construct the unsigned integer:
    # first byte is sign, the 7 bytes of exponent, then 24 bytes of fraction:
    uint = (((sign << 7) | F) << 24) | N

    # and finally, we pack the value as a uint:
    return struct.pack(endian + 'L', uint)

##################################################################


def unpack_ibm32_series(bytearray_: bytearray, endian: str) -> tuple:
    """ Unpacks a byterray containing multiple IBM values. """

    out = []
    for i in range(int(len(bytearray_) / 4)):
        out.append(unpack_ibm32(bytearray_[i * 4: (i + 1) * 4], endian=endian))

    return tuple(out)


def pack_ibm32_series(values: list, endian: str) -> bytearray:
    """ Packs an array of values into a bytearray of IBM 32 packed bytes. """

    out = bytearray(len(values) * 4)
    for i, value in enumerate(values):
        out[i * 4: (i + 1) * 4] = pack_ibm32(value=value, endian=endian)
    return out
