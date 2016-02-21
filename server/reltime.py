'''
    A relative time parser

    parsers english time strings and returns the number of seconds that the 
    input represents.  Throws a
    ValueError if the input can't be parsed as a time string.

    Some examples:

    parse_to_rel_time("1 month") -> 2592000
    parse_to_rel_time("2 days 2 hours") -> 180000
    parse_to_rel_time("3 years 2 months 2 days") -> 99964800
    parse_to_rel_time("3 years 2 months and 2 days ago") -> 99964800
    parse_to_rel_time("3 years, 2 months and 22 days ago!") -> 101692800
    parse_to_rel_time("  3    years,  2 months and 22 days ago!   ") -> 101692800
    parse_to_rel_time("1 h 3 w 2 d") -> 1990800
    parse_to_rel_time("last week") -> 604800
    parse_to_rel_time("six weeks") -> 3628800
    parse_to_rel_time("a week ago") -> 604800
    parse_to_rel_time("twenty days ago") -> 1728000

'''

import re

#    1m
#    5Y3M2W4D3h2m2s
#    5 years 3 months 2 weeks 4 days 3 hours 2 mins 2 secs
#    5 Y 3 M 2 W 4 D 3h 2 m 2 s

def parse_to_rel_time(str):
    stop_words = set(['and', 'ago', 'since'])
    delta_types = {
        'second':1,
        'sec':1,
        'secs':1,
        'seconds':1,
        'second':1,
        'minute':60,

        'm':60,
        'min':60,
        'minute':60,
        'minutes':60,

        'h':3600,
        'hr':3600,
        'hrs':3600,
        'hour':3600,
        'hours':3600,

        'day':60 * 60 * 24,
        'd':60 * 60 * 24,
        'days':60 * 60 * 24,

        'fortnight':60 * 60 * 2 * 7,

        'week':60 * 60 * 24 * 7,
        'weeks':60 * 60 * 24 * 7,
        'wks':60 * 60 * 24 * 7,
        'w':60 * 60 * 24 * 7,

        'month':60 * 60 * 24 * 30,
        'months':60 * 60 * 24 * 30,
        'mth':60 * 60 * 24 * 30,
        'mths':60 * 60 * 24 * 30,
        'mnth':60 * 60 * 24 * 30,
        'mnths':60 * 60 * 24 * 30,

        'year':60 * 60 * 24 * 365,
        'years':60 * 60 * 24 * 365,
        'yr':60 * 60 * 24 * 365,
        'yrs':60 * 60 * 24 * 365,
        'y':60 * 60 * 24 * 365,
    }

    num_subs = {
        'last': 1, 'a': 1, 'one': 1, 'two': 2, 'three': 3,
        'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8,
        'nine': 9, 'ten': 10, 'eleven': 11, 'twelve': 12, 'thirteen': 13,
        'fourteen': 14, 'fifteen': 15, 'sixteen': 16, 'seventeen': 17,
        'eighteen': 18, 'nineteen': 19, 'twenty': 20,
    }

    delta = 0
    words = re.findall(r"[\w]+", str)
    words = [w for w in words if w not in stop_words]
    if len(words) % 2 == 1:
        raise ValueError('bad time format: ' + str)
        
    for i in xrange(0, len(words), 2):
        snum = words[i]
        type = words[i + 1].lower()

        if snum in num_subs:
            num = num_subs[snum]
        else:
            try:
                num = int(snum)
            except:
                raise ValueError('number expected, but found ' + snum + ' instead in ' + str)

        if type in delta_types:
            delta += delta_types[type] * num
        else:
            raise ValueError('type expected, but found ' + type + ' instead in ' + str)

    return delta

if __name__ == '__main__':
    HOUR = 60 * 60
    DAY = 60 * 60 * 24
    WEEK = 60 * 60 * 24 * 7
    MONTH = 60 * 60 * 24 * 30
    YEAR = 60 * 60 * 24 * 365

    tests = [
        ("1 month",  1 * MONTH),
        ("2 days 2 hours", 2 * DAY + 2 * HOUR),
        ("3 years 2 months 2 days", 3 * YEAR + 2 * MONTH + 2 * DAY),
        ("3 years 2 months and 2 days ago", 3 * YEAR + 2 * MONTH + 2 * DAY),
        ("3 years, 2 months and 22 days ago!", 3 * YEAR + 2 * MONTH + 22 * DAY),
        ("  3        years,    2 months and 22 days ago!   ", 3 * YEAR + 2 * MONTH + 22 * DAY),
        ("1 h 3 w 2 d", 1 * HOUR + 3 * WEEK + 2 * DAY),
        ("last week",  1 * WEEK),
        ("last year and 3 weeks ago",  1 * YEAR + 3 * WEEK),
        ("six weeks",  6 * WEEK),
        ("a week ago",  1 * WEEK),
        ("twenty days ago",  20 * DAY),
        ("6 mnths, 2 wks",  6 * MONTH + 2 * WEEK),
    ]

    bad_patterns = [
        "1",
    ]

    for stest, res in tests:
        time = parse_to_rel_time(stest)
        if time == res:
            print "GOOD", stest, time
        else:
            print "BAD", stest, res, time

    print
    print 'testing bad patterns'
    for bp in bad_patterns:
        try:
            time = parse_to_rel_time(bp)
            print 'BAD', 'unexpected parse of', bp
        except ValueError as e:
            print 'GOOD', e

    print "some time examples"
    for stest, res in tests:
        print 'parse_to_rel_time("' + stest + '")', '->', res

    print "some time examples"
    for stest, res in tests:
        print "<li>" + stest + "</li>"
    print

