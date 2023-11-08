#! /usr/bin/env python3

# Copyright 2023 Hal W Canary III, Lindsay R Saunders PhD.
# Use of this program is governed by contents of the LICENSE file.

import csv
import io
import logging
import sys
import unittest

import ranked_match


# https://1000randomnames.com/
TEST_NAMES = [
    'Francesca Russo',
    'Jamie Costa',
    'Robin Ortega',
    'Kobe Davis',
    'Mia Beard',
    'Nathanael Rangel',
    'Gloria Conley',
    'Marvin Richmond',
    'Whitney Wang',
    'Cohen Aguilar',
    'Josie Rodriguez',
    'Henry Zimmerman',
    'Ariyah Valdez',
    'Kyler McDaniel',
    'Dahlia Taylor',
    'Jackson Avalos',
    'Paloma Williams',
    'Oliver Moon',
    'Naya Riley',
    'Amari Fischer',
    'Maci Fuentes',
    'Bowen Potter',
    'Rory Pollard',
    'Jad Warren',
    'Sloane Pham',
    'Russell Tapia',
    'Michaela Rodriguez',
    'Henry Archer',
    'Kadence Lyons',
    'Cyrus Ball',
    'Abby Decker',
]

TEST_DATA = '''
36,68,37,77, 7,77,55,13, 6,19,72,34,77,37, 7,38,36,57,55,35,37,36,53,63,27,63,43,49,71,77,77
33, 6,34,76,19,76, 1,15,19,59,44,35,76,35,19,39,52,19,57,53,35,24,10,57,26,69,60,13, 6,  ,
32,36,35,75,10,53,52,26,36,65,67,33,10,10,20,36,55,10,63,50,36,35,50,65,39,13,71,15, 3,  ,
34, 4,33,37,71,57,10,27,37,33,54,32,14,71,13,33,57,59, 3,52,38,34,52,74,57,28,69,48,73,  ,
35,35,38,55,57,32,20, 7,41,37,42,31, 7,33,43,31,24,41,71,31,54,31,63,64, 5,65,10,43,28,  ,
31, 1,36,53,63,75,16,36,  ,76,37,37,19,13,28,40,  ,65,40,33,13,32,75,43,  ,76, 9,38,59,  ,
37,53,31,13, 4, 4,14,19,  ,  ,24,38,37,19,14,30,  ,28, 7,41,75,37,55,  ,  ,43,  ,36,63,  ,
13,64,32,36,37,13,38,31,  ,  ,15,36,  ,20,63,76,  ,15,48,20,51,53,65,  ,  ,  ,  , 7,  ,  ,
14,22,42,35,13,  ,32, 2,  ,  ,13,21,  ,51,65,77,  ,52,22,  ,50,33,43,  ,  ,  ,  ,42,  ,  ,
76,59,41,32,24,  ,77,  ,  ,  ,  , 4,  ,32,  ,  ,  ,31,31,  ,60,76,32,  ,  ,  ,  ,41,  ,  ,
  ,  ,  ,  ,30,  ,  ,  ,  ,  ,  ,  ,  ,  ,  ,  ,  ,  ,  ,  ,  ,  ,  ,  ,  ,  ,  ,  ,  ,  ,
'''

EXPECTED = [
    ('Francesca Russo',    36,   1),
    ('Jamie Costa',        68,   1),
    ('Robin Ortega',       37,   1),
    ('Kobe Davis',         77,   1),
    ('Mia Beard',          7,    1),
    ('Nathanael Rangel',   76,   2),
    ('Gloria Conley',      55,   1),
    ('Marvin Richmond',    13,   1),
    ('Whitney Wang',       6,    1),
    ('Cohen Aguilar',      19,   1),
    ('Josie Rodriguez',    72,   1),
    ('Henry Zimmerman',    34,   1),
    ('Ariyah Valdez',      10,   3),
    ('Kyler McDaniel',     35,   2),
    ('Dahlia Taylor',      20,   3),
    ('Jackson Avalos',     38,   1),
    ('Paloma Williams',    52,   2),
    ('Oliver Moon',        57,   1),
    ('Naya Riley',         63,   3),
    ('Amari Fischer',      53,   2),
    ('Maci Fuentes',       54,   5),
    ('Bowen Potter',       24,   2),
    ('Rory Pollard',       50,   3),
    ('Jad Warren',         65,   3),
    ('Sloane Pham',        27,   1),
    ('Russell Tapia',      69,   2),
    ('Michaela Rodriguez', 43,   1),
    ('Henry Archer',       49,   1),
    ('Kadence Lyons',      71,   1),
    ('Cyrus Ball',         None, 1),
    ('Abby Decker',        None, 1),
]

CSV_DATA = [
    TEST_NAMES,
    [36, 68, 37, 77, 7, 77, 55, 13, 6, 19, 72, 34, 77, 37, 7, 38, 36, 57, 55, 35, 37, 36, 53, 63,
     27, 63, 43, 49, 71, 77, 77],
    [33, 6, 34, 76, 19, 76, 1, 15, 19, 59, 44, 35, 76, 35, 19, 39, 52, 19, 57, 53, 35, 24, 10, 57,
     26, 69, 60, 13, 6, None, None],
    [32, 36, 35, 75, 10, 53, 52, 26, 36, 65, 67, 33, 10, 10, 20, 36, 55, 10, 63, 50, 36, 35, 50,
     65, 39, 13, 71, 15, 3, None, None],
    [34, 4, 33, 37, 71, 57, 10, 27, 37, 33, 54, 32, 14, 71, 13, 33, 57, 59, 3, 52, 38, 34, 52, 74,
     57, 28, 69, 48, 73, None, None],
    [35, 35, 38, 55, 57, 32, 20, 7, 41, 37, 42, 31, 7, 33, 43, 31, 24, 41, 71, 31, 54, 31, 63, 64,
     5, 65, 10, 43, 28, None, None],
    [31, 1, 36, 53, 63, 75, 16, 36, None, 76, 37, 37, 19, 13, 28, 40, None, 65, 40, 33, 13, 32, 75,
     43, None, 76, 9, 38, 59, None, None],
    [37, 53, 31, 13, 4, 4, 14, 19, None, None, 24, 38, 37, 19, 14, 30, None, 28, 7, 41, 75, 37, 55,
     None, None, 43, None, 36, 63, None, None],
    [13, 64, 32, 36, 37, 13, 38, 31, None, None, 15, 36, None, 20, 63, 76, None, 15, 48, 20, 51,
     53, 65, None, None, None, None, 7, None, None, None],
    [14, 22, 42, 35, 13, None, 32, 2, None, None, 13, 21, None, 51, 65, 77, None, 52, 22, None, 50,
     33, 43, None, None, None, None, 42, None, None, None],
    [76, 59, 41, 32, 24, None, 77, None, None, None, None, 4, None, 32, None, None, None, 31, 31,
     None, 60, 76, 32, None, None, None, None, 41, None, None, None],
    [None, None, None, None, 30, None, None, None, None, None, None, None, None, None, None,
     None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
     None]
]

EXPECTED_PREFS = [
    [36, 33, 32, 34, 35, 31, 37, 13, 14, 76],
    [68, 6, 36, 4, 35, 1, 53, 64, 22, 59],
    [37, 34, 35, 33, 38, 36, 31, 32, 42, 41],
    [77, 76, 75, 37, 55, 53, 13, 36, 35, 32],
    [7, 19, 10, 71, 57, 63, 4, 37, 13, 24, 30],
    [77, 76, 53, 57, 32, 75, 4, 13],
    [55, 1, 52, 10, 20, 16, 14, 38, 32, 77],
    [13, 15, 26, 27, 7, 36, 19, 31, 2],
    [6, 19, 36, 37, 41],
    [19, 59, 65, 33, 37, 76],
    [72, 44, 67, 54, 42, 37, 24, 15, 13],
    [34, 35, 33, 32, 31, 37, 38, 36, 21, 4],
    [77, 76, 10, 14, 7, 19, 37],
    [37, 35, 10, 71, 33, 13, 19, 20, 51, 32],
    [7, 19, 20, 13, 43, 28, 14, 63, 65],
    [38, 39, 36, 33, 31, 40, 30, 76, 77],
    [36, 52, 55, 57, 24],
    [57, 19, 10, 59, 41, 65, 28, 15, 52, 31],
    [55, 57, 63, 3, 71, 40, 7, 48, 22, 31],
    [35, 53, 50, 52, 31, 33, 41, 20],
    [37, 35, 36, 38, 54, 13, 75, 51, 50, 60],
    [36, 24, 35, 34, 31, 32, 37, 53, 33, 76],
    [53, 10, 50, 52, 63, 75, 55, 65, 43, 32],
    [63, 57, 65, 74, 64, 43],
    [27, 26, 39, 57, 5],
    [63, 69, 13, 28, 65, 76, 43],
    [43, 60, 71, 69, 10, 9],
    [49, 13, 15, 48, 43, 38, 36, 7, 42, 41],
    [71, 6, 3, 73, 28, 59, 63],
    [77],
    [77],
]

EXPECTED_OUTPUT = '''Francesca Russo    topic=36 (ranked=1)
Jamie Costa        topic=68 (ranked=1)
Robin Ortega       topic=37 (ranked=1)
Kobe Davis         topic=77 (ranked=1)
Mia Beard          topic=7 (ranked=1)
Nathanael Rangel   topic=76 (ranked=2)
Gloria Conley      topic=55 (ranked=1)
Marvin Richmond    topic=13 (ranked=1)
Whitney Wang       topic=6 (ranked=1)
Cohen Aguilar      topic=19 (ranked=1)
Josie Rodriguez    topic=72 (ranked=1)
Henry Zimmerman    topic=34 (ranked=1)
Ariyah Valdez      topic=10 (ranked=3)
Kyler McDaniel     topic=35 (ranked=2)
Dahlia Taylor      topic=20 (ranked=3)
Jackson Avalos     topic=38 (ranked=1)
Paloma Williams    topic=52 (ranked=2)
Oliver Moon        topic=57 (ranked=1)
Naya Riley         topic=63 (ranked=3)
Amari Fischer      topic=53 (ranked=2)
Maci Fuentes       topic=54 (ranked=5)
Bowen Potter       topic=24 (ranked=2)
Rory Pollard       topic=50 (ranked=3)
Jad Warren         topic=65 (ranked=3)
Sloane Pham        topic=27 (ranked=1)
Russell Tapia      topic=69 (ranked=2)
Michaela Rodriguez topic=43 (ranked=1)
Henry Archer       topic=49 (ranked=1)
Kadence Lyons      topic=71 (ranked=1)
Cyrus Ball         topic=None (ranked=1)
Abby Decker        topic=None (ranked=1)
'''


class RankedMatchTestCase(unittest.TestCase):
    def test_csv_parse(self):
        buffer = io.StringIO()
        tmp = csv.writer(buffer)
        tmp.writerow(TEST_NAMES)
        csv_data = ranked_match.parseCSVFile(
            io.StringIO(buffer.getvalue() + TEST_DATA))
        self.assertEqual(csv_data, CSV_DATA)

    def test_get_prefs(self):
        self.assertEqual((TEST_NAMES, EXPECTED_PREFS), ranked_match.getPrefs(CSV_DATA))

    def test_ranked_match(self):
        self.assertEqual(ranked_match.rankedMatch(TEST_NAMES, EXPECTED_PREFS), EXPECTED)

    def test_print(self):
        buffer = io.StringIO()
        ranked_match.print_students(buffer, [ranked_match.Result(*e) for e in EXPECTED])
        self.assertEqual(buffer.getvalue(), EXPECTED_OUTPUT)


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s:  %(message)s', level='WARNING')
    unittest.main()
