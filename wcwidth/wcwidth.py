"""
Translated from Markus Kuhn's C code at:

     http://www.cl.cam.ac.uk/~mgk25/ucs/wcwidth.c

Maintained in python form at:

     https://github.com/jquast/wcwidth
"""
# This is an implementation of wcwidth() and wcswidth() (defined in
# IEEE Std 1002.1-2001) for Unicode.
#
# http://www.opengroup.org/onlinepubs/007904975/functions/wcwidth.html
# http://www.opengroup.org/onlinepubs/007904975/functions/wcswidth.html
#
# In fixed-width output devices, Latin characters all occupy a single
# "cell" position of equal width, whereas ideographic CJK characters
# occupy two such cells. Interoperability between terminal-line
# applications and (teletype-style) character terminals using the
# UTF-8 encoding requires agreement on which character should advance
# the cursor by how many cell positions. No established formal
# standards exist at present on which Unicode character shall occupy
# how many cell positions on character terminals. These routines are
# a first attempt of defining such behavior based on simple rules
# applied to data provided by the Unicode Consortium.
#
# For some graphical characters, the Unicode standard explicitly
# defines a character-cell width via the definition of the East Asian
# FullWidth (F), Wide (W), Half-width (H), and Narrow (Na) classes.
# In all these cases, there is no ambiguity about which width a
# terminal shall use. For characters in the East Asian Ambiguous (A)
# class, the width choice depends purely on a preference of backward
# compatibility with either historic CJK or Western practice.
# Choosing single-width for these characters is easy to justify as
# the appropriate long-term solution, as the CJK practice of
# displaying these characters as double-width comes from historic
# implementation simplicity (8-bit encoded characters were displayed
# single-width and 16-bit ones double-width, even for Greek,
# Cyrillic, etc.) and not any typographic considerations.
#
# Much less clear is the choice of width for the Not East Asian
# (Neutral) class. Existing practice does not dictate a width for any
# of these characters. It would nevertheless make sense
# typographically to allocate two character cells to characters such
# as for instance EM SPACE or VOLUME INTEGRAL, which cannot be
# represented adequately with a single-width glyph. The following
# routines at present merely assign a single-cell width to all
# neutral characters, in the interest of simplicity. This is not
# entirely satisfactory and should be reconsidered before
# establishing a formal standard in this area. At the moment, the
# decision which Not East Asian (Neutral) characters should be
# represented by double-width glyphs cannot yet be answered by
# applying a simple rule from the Unicode database content. Setting
# up a proper standard for the behavior of UTF-8 character terminals
# will require a careful analysis not only of each Unicode character,
# but also of each presentation form, something the author of these
# routines has avoided to do so far.
#
# http://www.unicode.org/unicode/reports/tr11/
#
# Markus Kuhn -- 2007-05-26 (Unicode 5.0)
#
# Permission to use, copy, modify, and distribute this software
# for any purpose and without fee is hereby granted. The author
# disclaims all warranties with regard to this software.
#
# Latest version: http://www.cl.cam.ac.uk/~mgk25/ucs/wcwidth.c

from __future__ import division
import unicodedata


def _bisearch(ucs, table):
    " auxiliary function for binary search in interval table "
    lbound = 0
    ubound = len(table) - 1

    if ucs < table[0][0] or ucs > table[ubound][1]:
        return 0
    while ubound >= lbound:
        mid = (lbound + ubound) // 2
        if ucs > table[mid][1]:
            lbound = mid + 1
        elif ucs < table[mid][0]:
            ubound = mid - 1
        else:
            return 1

    return 0

# The following two functions define the column width of an ISO 10646
# character as follows:
#
#    - The null character (U+0000) has a column width of 0.
#
#    - Other C0/C1 control characters and DEL will lead to a return
#      value of -1.
#
#    - Non-spacing and enclosing combining characters (general
#      category code Mn or Me in the Unicode database) have a
#      column width of 0.
#
#    - SOFT HYPHEN (U+00AD) has a column width of 1.
#
#    - Other format characters (general category code Cf in the Unicode
#      database) and ZERO WIDTH SPACE (U+200B) have a column width of 0.
#
#    - Hangul Jamo medial vowels and final consonants (U+1160-U+11FF)
#      have a column width of 0.
#
#    - Spacing characters in the East Asian Wide (W) or East Asian
#      Full-width (F) category as defined in Unicode Technical
#      Report #11 have a column width of 2.
#
#    - All remaining characters (including all printable
#      ISO 8859-1 and WGL4 characters, Unicode control characters,
#      etc.) have a column width of 1.
#
# This implementation assumes that wchar_t characters are encoded
# in ISO 10646.

def wcwidth(unichar):
    """wcwidth(unichar) -> int

    Return the width in character cells of the Unicode character
    whose code is c
    """
    ucs = ord(unichar)

    # null (\x00) is 0.
    if ucs == u'\x00':
        return 0

    # Control characters are -1
    if ucs < 32:
        return -1

    # test for 8-bit control characters
    if ucs >= 0x7f and ucs < 0xa0:
        return -1

    # combining characters must be joined with other characters,
    # their printable width is currently indeterminate
    # TODO(jquast): it may be possible to calculate,
    if unicodedata.combining(unichar):
        return -1

    # if we arrive here, ucs is not a combining or C0/C1 control character
    # basically, given EastAsianWidth.txt, any column ';W' returns 1 + 1,
    return 1 + (
        (ucs >= 0x1100 and
         (ucs <= 0x115f or                       # Hangul Jamo init. Consonants
          ucs == 0x2329 or ucs == 0x232a or
          (ucs >= 0x2e80 and ucs <= 0xa4cf and   # CJK ... Yi
           ucs != 0x303f and not                 # except for: half-fill space,
           (ucs >= 0x4dc0 and ucs <= 0x4dff)) or # ... and the 64 hexagrams
          (ucs >= 0xac00 and ucs <= 0xd7a3) or   # Hangul Syllables
          (ucs >= 0xf900 and ucs <= 0xfaff) or   # CJK Compatibility Ideographs
          (ucs >= 0xfe10 and ucs <= 0xfe19) or   # Vertical forms
          (ucs >= 0xfe30 and ucs <= 0xfe6f) or   # CJK Compatibility Forms
          (ucs >= 0xff00 and ucs <= 0xff60) or   # Fullwidth Forms
          (ucs >= 0xffe0 and ucs <= 0xffe6) or
          (ucs >= 0x20000 and ucs <= 0x2fffd) or
          (ucs >= 0x30000 and ucs <= 0x3fffd)))
    )


def wcswidth(pwcs, n=None):

    """
    Return the width in character cells of the first ``n`` unicode string pwcs,
    or -1 if a  non-printable character is encountered. When ``n`` is None
    (default), return the length of the entire string.
    """

    end = len(pwcs) if n is not None else n
    idx = slice(0, end)
    width = 0
    for char in pwcs[idx]:
        wcw = wcwidth(char)
        if wcw < 0:
            return -1
        else:
            width += wcw
    return width

#
# sorted list of non-overlapping intervals of East Asian Ambiguous
# characters, generated by "uniset +WIDTH-A -cat=Me -cat=Mn -cat=Cf c"
_AMBIGUOUS = [
    (0x00A1, 0x00A1), (0x00A4, 0x00A4), (0x00A7, 0x00A8),
    (0x00AA, 0x00AA), (0x00AE, 0x00AE), (0x00B0, 0x00B4),
    (0x00B6, 0x00BA), (0x00BC, 0x00BF), (0x00C6, 0x00C6),
    (0x00D0, 0x00D0), (0x00D7, 0x00D8), (0x00DE, 0x00E1),
    (0x00E6, 0x00E6), (0x00E8, 0x00EA), (0x00EC, 0x00ED),
    (0x00F0, 0x00F0), (0x00F2, 0x00F3), (0x00F7, 0x00FA),
    (0x00FC, 0x00FC), (0x00FE, 0x00FE), (0x0101, 0x0101),
    (0x0111, 0x0111), (0x0113, 0x0113), (0x011B, 0x011B),
    (0x0126, 0x0127), (0x012B, 0x012B), (0x0131, 0x0133),
    (0x0138, 0x0138), (0x013F, 0x0142), (0x0144, 0x0144),
    (0x0148, 0x014B), (0x014D, 0x014D), (0x0152, 0x0153),
    (0x0166, 0x0167), (0x016B, 0x016B), (0x01CE, 0x01CE),
    (0x01D0, 0x01D0), (0x01D2, 0x01D2), (0x01D4, 0x01D4),
    (0x01D6, 0x01D6), (0x01D8, 0x01D8), (0x01DA, 0x01DA),
    (0x01DC, 0x01DC), (0x0251, 0x0251), (0x0261, 0x0261),
    (0x02C4, 0x02C4), (0x02C7, 0x02C7), (0x02C9, 0x02CB),
    (0x02CD, 0x02CD), (0x02D0, 0x02D0), (0x02D8, 0x02DB),
    (0x02DD, 0x02DD), (0x02DF, 0x02DF), (0x0391, 0x03A1),
    (0x03A3, 0x03A9), (0x03B1, 0x03C1), (0x03C3, 0x03C9),
    (0x0401, 0x0401), (0x0410, 0x044F), (0x0451, 0x0451),
    (0x2010, 0x2010), (0x2013, 0x2016), (0x2018, 0x2019),
    (0x201C, 0x201D), (0x2020, 0x2022), (0x2024, 0x2027),
    (0x2030, 0x2030), (0x2032, 0x2033), (0x2035, 0x2035),
    (0x203B, 0x203B), (0x203E, 0x203E), (0x2074, 0x2074),
    (0x207F, 0x207F), (0x2081, 0x2084), (0x20AC, 0x20AC),
    (0x2103, 0x2103), (0x2105, 0x2105), (0x2109, 0x2109),
    (0x2113, 0x2113), (0x2116, 0x2116), (0x2121, 0x2122),
    (0x2126, 0x2126), (0x212B, 0x212B), (0x2153, 0x2154),
    (0x215B, 0x215E), (0x2160, 0x216B), (0x2170, 0x2179),
    (0x2190, 0x2199), (0x21B8, 0x21B9), (0x21D2, 0x21D2),
    (0x21D4, 0x21D4), (0x21E7, 0x21E7), (0x2200, 0x2200),
    (0x2202, 0x2203), (0x2207, 0x2208), (0x220B, 0x220B),
    (0x220F, 0x220F), (0x2211, 0x2211), (0x2215, 0x2215),
    (0x221A, 0x221A), (0x221D, 0x2220), (0x2223, 0x2223),
    (0x2225, 0x2225), (0x2227, 0x222C), (0x222E, 0x222E),
    (0x2234, 0x2237), (0x223C, 0x223D), (0x2248, 0x2248),
    (0x224C, 0x224C), (0x2252, 0x2252), (0x2260, 0x2261),
    (0x2264, 0x2267), (0x226A, 0x226B), (0x226E, 0x226F),
    (0x2282, 0x2283), (0x2286, 0x2287), (0x2295, 0x2295),
    (0x2299, 0x2299), (0x22A5, 0x22A5), (0x22BF, 0x22BF),
    (0x2312, 0x2312), (0x2460, 0x24E9), (0x24EB, 0x254B),
    (0x2550, 0x2573), (0x2580, 0x258F), (0x2592, 0x2595),
    (0x25A0, 0x25A1), (0x25A3, 0x25A9), (0x25B2, 0x25B3),
    (0x25B6, 0x25B7), (0x25BC, 0x25BD), (0x25C0, 0x25C1),
    (0x25C6, 0x25C8), (0x25CB, 0x25CB), (0x25CE, 0x25D1),
    (0x25E2, 0x25E5), (0x25EF, 0x25EF), (0x2605, 0x2606),
    (0x2609, 0x2609), (0x260E, 0x260F), (0x2614, 0x2615),
    (0x261C, 0x261C), (0x261E, 0x261E), (0x2640, 0x2640),
    (0x2642, 0x2642), (0x2660, 0x2661), (0x2663, 0x2665),
    (0x2667, 0x266A), (0x266C, 0x266D), (0x266F, 0x266F),
    (0x273D, 0x273D), (0x2776, 0x277F), (0xE000, 0xF8FF),
    (0xFFFD, 0xFFFD), (0xF0000, 0xFFFFD), (0x100000, 0x10FFFD)
]


# jquast: UNICODE_DIR=unicode_dir ./uniset eaw:A - cat:Me,Mn,Cf
_AMBIGUOUS_TESTING_NEW = [
    (0x00A1, 0x00A1), (0x00A4, 0x00A4), (0x00A7, 0x00A8),
    (0x00AA, 0x00AA), (0x00AE, 0x00AE), (0x00B0, 0x00B4),
    (0x00B6, 0x00BA), (0x00BC, 0x00BF), (0x00C6, 0x00C6),
    (0x00D0, 0x00D0), (0x00D7, 0x00D8), (0x00DE, 0x00E1),
    (0x00E6, 0x00E6), (0x00E8, 0x00EA), (0x00EC, 0x00ED),
    (0x00F0, 0x00F0), (0x00F2, 0x00F3), (0x00F7, 0x00FA),
    (0x00FC, 0x00FC), (0x00FE, 0x00FE), (0x0101, 0x0101),
    (0x0111, 0x0111), (0x0113, 0x0113), (0x011B, 0x011B),
    (0x0126, 0x0127), (0x012B, 0x012B), (0x0131, 0x0133),
    (0x0138, 0x0138), (0x013F, 0x0142), (0x0144, 0x0144),
    (0x0148, 0x014B), (0x014D, 0x014D), (0x0152, 0x0153),
    (0x0166, 0x0167), (0x016B, 0x016B), (0x01CE, 0x01CE),
    (0x01D0, 0x01D0), (0x01D2, 0x01D2), (0x01D4, 0x01D4),
    (0x01D6, 0x01D6), (0x01D8, 0x01D8), (0x01DA, 0x01DA),
    (0x01DC, 0x01DC), (0x0251, 0x0251), (0x0261, 0x0261),
    (0x02C4, 0x02C4), (0x02C7, 0x02C7), (0x02C9, 0x02CB),
    (0x02CD, 0x02CD), (0x02D0, 0x02D0), (0x02D8, 0x02DB),
    (0x02DD, 0x02DD), (0x02DF, 0x02DF), (0x0391, 0x03A1),
    (0x03A3, 0x03A9), (0x03B1, 0x03C1), (0x03C3, 0x03C9),
    (0x0401, 0x0401), (0x0410, 0x044F), (0x0451, 0x0451),
    (0x2010, 0x2010), (0x2013, 0x2016), (0x2018, 0x2019),
    (0x201C, 0x201D), (0x2020, 0x2022), (0x2024, 0x2027),
    (0x2030, 0x2030), (0x2032, 0x2033), (0x2035, 0x2035),
    (0x203B, 0x203B), (0x203E, 0x203E), (0x2074, 0x2074),
    (0x207F, 0x207F), (0x2081, 0x2084), (0x20AC, 0x20AC),
    (0x2103, 0x2103), (0x2105, 0x2105), (0x2109, 0x2109),
    (0x2113, 0x2113), (0x2116, 0x2116), (0x2121, 0x2122),
    (0x2126, 0x2126), (0x212B, 0x212B), (0x2153, 0x2154),
    (0x215B, 0x215E), (0x2160, 0x216B), (0x2170, 0x2179),
    # jquast: new
    (0x2189, 0x2189),
    # jquast: end new
    (0x2190, 0x2199), (0x21B8, 0x21B9), (0x21D2, 0x21D2),
    (0x21D4, 0x21D4), (0x21E7, 0x21E7), (0x2200, 0x2200),
    (0x2202, 0x2203), (0x2207, 0x2208), (0x220B, 0x220B),
    (0x220F, 0x220F), (0x2211, 0x2211), (0x2215, 0x2215),
    (0x221A, 0x221A), (0x221D, 0x2220), (0x2223, 0x2223),
    (0x2225, 0x2225), (0x2227, 0x222C), (0x222E, 0x222E),
    (0x2234, 0x2237), (0x223C, 0x223D), (0x2248, 0x2248),
    (0x224C, 0x224C), (0x2252, 0x2252), (0x2260, 0x2261),
    (0x2264, 0x2267), (0x226A, 0x226B), (0x226E, 0x226F),
    (0x2282, 0x2283), (0x2286, 0x2287), (0x2295, 0x2295),
    (0x2299, 0x2299), (0x22A5, 0x22A5), (0x22BF, 0x22BF),
    (0x2312, 0x2312), (0x2460, 0x24E9), (0x24EB, 0x254B),
    (0x2550, 0x2573), (0x2580, 0x258F), (0x2592, 0x2595),
    (0x25A0, 0x25A1), (0x25A3, 0x25A9), (0x25B2, 0x25B3),
    (0x25B6, 0x25B7), (0x25BC, 0x25BD), (0x25C0, 0x25C1),
    (0x25C6, 0x25C8), (0x25CB, 0x25CB), (0x25CE, 0x25D1),
    (0x25E2, 0x25E5), (0x25EF, 0x25EF), (0x2605, 0x2606),
    (0x2609, 0x2609), (0x260E, 0x260F), (0x2614, 0x2615),
    (0x261C, 0x261C), (0x261E, 0x261E), (0x2640, 0x2640),
    (0x2642, 0x2642), (0x2660, 0x2661), (0x2663, 0x2665),
    (0x2667, 0x266A), (0x266C, 0x266D), (0x266F, 0x266F),
    (0x269E, 0x269F), (0x26BE, 0x26BF), (0x26C4, 0x26CD),
    (0x26CF, 0x26E1), (0x26E3, 0x26E3), (0x26E8, 0x26FF),
    (0x273D, 0x273D),
    # jquast: new
    (0x2757, 0x2757),
    # jquast: end new
                      (0x2776, 0x277F),
    # jquast: new
    (0x2B55, 0x2B59), (0x3248, 0x324F),
    # jquast: end new
                                        (0xE000, 0xF8FF),
    (0xFFFD, 0xFFFD),
    # jquast: new
    (0x1F100, 0x1F10A),
    (0x1F110, 0x1F12D),
    (0x1F130, 0x1F169),
    (0x1F170, 0x1F19A),
    # end new
    (0xF0000, 0xFFFFD), (0x100000, 0x10FFFD),
]


# The following functions are the same as mk_wcwidth() and
# mk_wcwidth_cjk(), except that spacing characters in the East Asian
# Ambiguous (A) category as defined in Unicode Technical Report #11
# have a column width of 2. This variant might be useful for users of
# CJK legacy encodings who want to migrate to UCS without changing
# the traditional terminal character-width behavior. It is not
# otherwise recommended for general use.

def wcwidth_cjk(ucs):
    """ As wcwidth above, but spacing characters in the East Asian
    Ambiguous (A) category as defined in Unicode Technical Report #11
    have a column width of 2.
    """
    if _bisearch(ord(ucs), _AMBIGUOUS):
        return 2
    return wcwidth(ucs)


def wcswidth_cjk(pwcs):
    """ As wcswidth above, but spacing characters in the East Asian
    Ambiguous (A) category as defined in Unicode Technical Report #11
    have a column width of 2.
    """
    width = 0
    for char in pwcs:
        wcw = wcwidth_cjk(char)
        if wcw < 0:
            return -1
        else:
            width += wcw
    return width
