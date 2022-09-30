import datetime

START = datetime.datetime.toordinal(datetime.datetime(year=2022, month=9, day=19))

communities = [
    'governors-retreat',
    '/wescott/',
    'maidstone-village',
    'central-crossing',
    'rutland-grove',
    'mosaic',
    'fox-creek-homestead',
    '/giles/',
    'greenwich-walk',
    '/magnolia-green/',
    'magnolia-green-townhomes',
    'twin-rivers',
    'sandler-station',
    'taylor-farm',
    'giles-townhomes',
    'the-townes-at-giles',
    'quarterpath-at-williamsburg-condos',
    'river-highlands',
    'meadows-landing',
    'banks-pointe',
    'dayton-woods',
    'enclave-at-leesville',
    'enclaveatleesville',
    'granite-falls-estates',
    'the-reserve-at-wackena',
    'sandhurst-south',
    'river-mill-townhomes',
    '/river-mill/',
    'the-pointe-at-twin-hickory',
    'wescott-condos',
    'brookwood',
    'sanford',
    'edgewater',
    'carpenters-pointe',
    'traywick-at-sandhurst',
    'the-townes-at-innsbrook-square'
]


def neighborhood_check(neighborhood):
    if neighborhood in ['banks-pointe', 'dayton-woods', 'enclave-at-leesville', 'granite-falls-estates',
                        'the-reserve-at-wackena', 'enclaveatleesville', 'traywick-at-sandhurst', 'brookwood',
                        'sanford', 'carpenters-pointe', 'sandhurst-south']:
        return 'H3'
    elif neighborhood in ['maidstone-village', 'quarterpath-at-williamsburg-condos', 'river-highlands',
                          'meadows-landing', 'edgewater']:
        return 'H2'
    elif neighborhood in ['central-crossing', 'rutland-grove', '/giles/', 'magnolia-green-townhomes',
                          'twin-rivers', 'taylor-farm', 'giles-townhomes', 'the-townes-at-giles',
                          'river-mill-townhomes', '/river-mill/', 'the-pointe-at-twin-hickory',
                          'the-townes-at-innsbrook-square']:
        return 'H1 - Danielle'
    elif neighborhood in ['governors-retreat', '/wescott/', 'mosaic', 'fox-creek-homestead', 'greenwich-walk',
                          '/magnolia-green/', 'sandler-station', 'wescott-condos']:
        return 'H1 - Eric'
    else:
        return 'assignment pending'
