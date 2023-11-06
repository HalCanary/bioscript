#! /usr/bin/env python3

# Copyright 2023 Hal W Canary III, Lindsay R Saunders PhD.
# Use of this program is governed by contents of the LICENSE file.

import logging
import unittest
import io
import csv

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
    (36, 1),
    (68, 1),
    (37, 1),
    (77, 1),
    (7, 1),
    (76, 2),
    (55, 1),
    (13, 1),
    (6, 1),
    (19, 1),
    (72, 1),
    (34, 1),
    (10, 3),
    (35, 2),
    (20, 3),
    (38, 1),
    (52, 2),
    (57, 1),
    (63, 3),
    (53, 2),
    (54, 5),
    (24, 2),
    (50, 3),
    (65, 3),
    (27, 1),
    (69, 2),
    (43, 1),
    (49, 1),
    (71, 1),
    (None, 2),
    (None, 2),
]


class RankedMatchTestCase(unittest.TestCase):
    def test_ranked_match(self):
        buffer = io.StringIO()
        tmp = csv.writer(buffer)
        tmp.writerow(TEST_NAMES)
        buffer.write(TEST_DATA)
        names, inverse_prefs = ranked_match.parseCSVFile(
            io.StringIO(buffer.getvalue() + TEST_DATA))
        students = ranked_match.rangedMatch(names, inverse_prefs)
        for idx, student in enumerate(students):
            self.assertLess(idx, len(TEST_NAMES))
            self.assertLess(idx, len(EXPECTED))
            self.assertEqual(TEST_NAMES[idx], student.name)
            self.assertEqual(EXPECTED[idx][0], student.topic)
            self.assertEqual(EXPECTED[idx][1], student.choice)


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s:  %(message)s', level='WARNING')
    unittest.main()
