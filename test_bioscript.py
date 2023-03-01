#! /usr/bin/env python3

# Copyright 2023 Hal W Canary III, Lindsay R Saunders PhD.
# Use of this program is governed by contents of the LICENSE file.

import collections
import io
import logging
import random
import unittest

import bestSequenceEachSpecies as bioscript

TestSequence = collections.namedtuple(
    'TestSequence', [
        'accession', 'genus', 'epithet', 'extra',
        'description', 'sequence', 'fasta', 'species', 'translated'])


def makeTestSequence(accession, genus, epithet, extra, sequence):
    description = ' '.join([accession, genus, epithet, extra])
    fasta = '>%s\n%s\n\n' % (description, bioscript.split_str(sequence, 70))
    species = genus + '_' + epithet
    translated = ' '.join([species, accession, extra])
    return TestSequence(accession, genus, epithet, extra, description,
                        sequence, fasta, species, translated)


def makeRandomSequence(seed):
    r = random.Random(seed)
    n = r.randrange(700, 2100)
    weights = [99, 99, 99, 99, 1, 1, 1, 1, 1]
    return ''.join(r.choices('ACGTYKRSW', weights=weights, k=n))


TESTDATA_1 = makeTestSequence(
    'KF787109.1', 'Arthrobacter', 'nicotianae',
    'strain BSc 4 16S ribosomal RNA gene, partial sequence',
    makeRandomSequence(1))

TESTDATA_2 = makeTestSequence(
    'KP684097.1', 'Arthrobacter', 'nicotianae',
    'strain BS20 16S ribosomal RNA gene, partial sequence',
    makeRandomSequence(2))

TESTDATA_3 = makeTestSequence(
    'NR_947583.1', 'Glutamicibacter', 'arilaitensis',
    'strain Ind Int 3 16S ribosomal RNA gene, type strain Foo',
    makeRandomSequence(3))


class NewDatabaseOneSequencePerSpeciesTestCase(unittest.TestCase):
    def test_split_str(self):
        for s in [40, 400, 99, 900]:
            for n in [10, 70, 80, 100, 10000]:
                sequence = makeRandomSequence(s)
                result = bioscript.split_str(sequence, n)
                self.assertEqual(sequence, ''.join(result.split()))

    def test_parse_fasta_format_1(self):
        self.assertEqual(
            list(bioscript.parse_fasta_format(io.StringIO(TESTDATA_1.fasta))),
            [(TESTDATA_1.description, TESTDATA_1.sequence)])

    def test_parse_fasta_format_2(self):
        t1, t2 = TESTDATA_1, TESTDATA_2
        self.assertEqual(
            list(bioscript.parse_fasta_format(
                    io.StringIO(t1.fasta + t2.fasta))), [
                (t1.description, t1.sequence),
                (t2.description, t2.sequence)])

    def test_print_fasta_description_1(self):
        self.maxDiff = None
        t1, t2 = TESTDATA_1, TESTDATA_2
        buffer = io.StringIO()
        bioscript.print_fasta_description(buffer, t1.description, t1.sequence)
        bioscript.print_fasta_description(buffer, t2.description, t2.sequence)
        self.assertEqual(buffer.getvalue(), t1.fasta + t2.fasta)

    def test_get_values_matching_genus_1(self):
        t1, t2, t3 = TESTDATA_1, TESTDATA_2, TESTDATA_3
        self.assertEqual(
            bioscript.get_values_matching_genus('', [
                (t1.description, t1.sequence),
                (t2.description, t2.sequence),
                (t3.description, t3.sequence)], logging.getLogger()),
            (3, {t1.species: [(t1.accession, t1.translated, t1.sequence),
                              (t2.accession, t2.translated, t2.sequence)],
                 t3.species: [(t3.accession, t3.translated, t3.sequence)]}))

    def test_get_values_matching_genus_2(self):
        self.assertEqual(
            bioscript.get_values_matching_genus(
                TESTDATA_3.species,
                [(TESTDATA_1.description, TESTDATA_1.sequence)],
                logging.getLogger()),
            (1, {}))

    def test_get_values_matching_genus_3(self):
        t1, t2, t3 = TESTDATA_1, TESTDATA_2, TESTDATA_3
        self.assertEqual(
            bioscript.get_values_matching_genus(t1.genus, [
                (t1.description, t1.sequence),
                (t2.description, t2.sequence),
                (t3.description, t3.sequence)], logging.getLogger()),
            (3, {t1.species: [(t1.accession, t1.translated, t1.sequence),
                              (t2.accession, t2.translated, t2.sequence)]}))

    def test_process_values_1(self):
        t1 = TESTDATA_1
        self.assertEqual(
            bioscript.process_values([
                (t1.accession, t1.translated, t1.sequence)]),
            (t1.translated, t1.sequence))

    def test_process_values_2(self):
        t1, t2 = TESTDATA_1, TESTDATA_2
        self.assertEqual(
            bioscript.process_values([
                (t1.accession, t1.translated, t1.sequence),
                (t2.accession, t2.translated, t2.sequence)]),
            (t2.translated, t2.sequence))

    def test_get_score(self):
        s = [
            (0, 962.0/975,   0, 975),
            (0, 805.0/815,   0, 815),
            (1, 1173.0/1187, 1, 1187),
        ]
        td = [TESTDATA_1, TESTDATA_2, TESTDATA_3]
        self.assertEqual(s, [bioscript.get_score(
            t.accession, t.description, t.sequence) for t in td])
        self.assertTrue(s[1] > s[0])
        self.assertTrue(s[2] > s[0])
        self.assertTrue(s[2] > s[1])


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s:  %(message)s', level='INFO')
    unittest.main()
