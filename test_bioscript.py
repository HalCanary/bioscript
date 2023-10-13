#! /usr/bin/env python3

# Copyright 2023 Hal W Canary III, Lindsay R Saunders PhD.
# Use of this program is governed by contents of the LICENSE file.

import collections
import glob
import io
import logging
import os
import random
import shutil
import sys
import tempfile
import unittest

import bestSequenceEachSpecies as bioscript
import concat_fasta as concat


TestSequence = collections.namedtuple(
    'TestSequence', [
        'accession', 'genus', 'epithet', 'extra', 'sequence',
        'description', 'fasta', 'species', 'translated'])


def makeTestSequence(accession, genus, epithet, extra, sequence):
    description = ' '.join([accession, genus, epithet, extra])
    fasta = '>%s\n%s\n\n' % (description, bioscript.split_str(sequence, 70))
    species = genus + '_' + epithet
    translated = ' '.join([species, accession, extra])
    return TestSequence(accession, genus, epithet, extra, sequence,
                        description, fasta, species, translated)


def makeRandomSequence(seed):
    r = random.Random(seed)
    n = r.randrange(700, 2100)
    return ''.join(r.choices('ACGTYKRSW', weights=[99, 99, 99, 99, 1, 1, 1, 1, 1], k=n))


def fasta_string(sequences):
    b = io.StringIO()
    for (description, sequence) in sequences:
        bioscript.print_fasta_description(b, description, sequence)
    return b.getvalue()


def run_test_get_best_sequence_each_species(data, genus):
    buffer = io.StringIO()
    bioscript.get_best_sequence_each_species(io.StringIO(data), buffer, genus, logging.getLogger())
    return buffer.getvalue()


TESTDATA_1 = makeTestSequence(
    'KF787109.1', 'Arthrobacter', 'nicotianae',
    'strain BSc 4 16S ribosomal RNA gene, partial sequence', makeRandomSequence(1))

TESTDATA_2 = makeTestSequence(
    'KP684097.1', 'Arthrobacter', 'nicotianae',
    'strain BS20 16S ribosomal RNA gene, partial sequence', makeRandomSequence(2))

TESTDATA_3 = makeTestSequence(
    'NR_947583.1', 'Glutamicibacter', 'arilaitensis',
    'strain Ind Int 3 16S ribosomal RNA gene, type strain Foo', makeRandomSequence(3))


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
            list(bioscript.parse_fasta_format(io.StringIO(t1.fasta + t2.fasta))), [
                (t1.description, t1.sequence),
                (t2.description, t2.sequence)])

    def test_print_fasta_description_1(self):
        self.maxDiff = None
        td = [TESTDATA_1, TESTDATA_2, TESTDATA_3]
        self.assertEqual(
            fasta_string([(t.description, t.sequence) for t in td]), ''.join(t.fasta for t in td))

    def test_process_sequence_description(self):
        for t in [TESTDATA_1, TESTDATA_2, TESTDATA_3]:
            self.assertEqual(
                bioscript.process_sequence_description(t.description),
                (t.genus, t.species, t.accession, t.translated))

    def test_get_best_sequence_each_species_1(self):
        example = ''.join(t.fasta for t in [TESTDATA_1, TESTDATA_2, TESTDATA_3])
        self.assertEqual(
            run_test_get_best_sequence_each_species(example, None),
            fasta_string([(t.translated, t.sequence) for t in [TESTDATA_2, TESTDATA_3]]))
        self.assertEqual(
            run_test_get_best_sequence_each_species(example, TESTDATA_1.genus),
            fasta_string([(TESTDATA_2.translated, TESTDATA_2.sequence)]))
        self.assertEqual(
            run_test_get_best_sequence_each_species(example, TESTDATA_3.genus),
            fasta_string([(TESTDATA_3.translated, TESTDATA_3.sequence)]))

    def test_get_best_sequence_each_species_2(self):
        example = ''.join(t.fasta for t in [TESTDATA_1, TESTDATA_2, TESTDATA_3])
        foundException = False
        try:
            run_test_get_best_sequence_each_species(example, 'Foobar')
        except RuntimeError as e:
            foundException = True
        self.assertTrue(foundException)

    def test_get_best_sequence_1(self):
        td = [(t.accession, t.translated, t.sequence) for t in [TESTDATA_1]]
        self.assertEqual(
            bioscript.get_best_sequence(td),
            (TESTDATA_1.translated, TESTDATA_1.sequence))

    def test_get_best_sequence_2(self):
        td = [(t.accession, t.translated, t.sequence) for t in [TESTDATA_1, TESTDATA_2]]
        self.assertEqual(
            bioscript.get_best_sequence(td),
            (TESTDATA_2.translated, TESTDATA_2.sequence))

    def test_get_score(self):
        v = [
            (TESTDATA_1, (0, 962.0/975,   0, 975)),
            (TESTDATA_2, (0, 805.0/815,   0, 815)),
            (TESTDATA_3, (1, 1173.0/1187, 1, 1187)),
        ]
        for t, s in v:
            self.assertEqual(s, bioscript.get_score(t.accession, t.description, t.sequence))
        self.assertTrue(v[1][1] > v[0][1])
        self.assertTrue(v[2][1] > v[0][1])
        self.assertTrue(v[2][1] > v[1][1])


class ConcatTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.mkdtemp()
        for idx, t in enumerate([TESTDATA_1, TESTDATA_2, TESTDATA_3]):
            with open(os.path.join(cls.directory, 'data%d.fasta' % idx), 'w') as o:
                bioscript.print_fasta_description(o, t.description, t.sequence)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.directory)

    def test_concat(self):
        files = glob.glob(os.path.join(self.directory, '*'))
        buffer = io.StringIO()
        concat.concat(files, buffer, logging.getLogger())
        self.assertEqual(3343, len(buffer.getvalue()))


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s:  %(message)s', level='WARNING')
    unittest.main()
