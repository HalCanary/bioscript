#! /usr/bin/env python3

# Copyright 2023 Hal W Canary III, Lindsay R Saunders PhD.
# Use of this program is governed by contents of the LICENSE file.

import collections
import io 
import logging
import unittest

import New_Database_One_Sequence_per_Species as bioscript

TestSequence = collections.namedtuple(
    'TestSequence', ['accession', 'genus', 'epithet', 'extra', 'seq',
                     'description', 'sequence', 'fasta', 'species', 'translated'])

def MakeTestSequence(accession, genus, epithet, extra, seq):
    description = ' '.join([accession, genus, epithet, extra])
    sequence = ''.join(seq.split())
    fasta = '>%s\n%s\n' %(description, seq)
    species = genus + '_' + epithet
    translated = ' '.join([species, accession, extra])
    return TestSequence(
        accession, genus, epithet, extra, seq, description, sequence, fasta, species, translated)


TESTDATA_1 = MakeTestSequence(
    'KF787109.1',
    'Arthrobacter',
    'nicotianae',
    'strain BSc 4 16S ribosomal RNA gene, partial sequence',
    '''GCGAACGGGTGAGTAACACGTGAGTAACCTGCCCCCGACTCTGGGATAAGCCCGGGAAACTGGGTCTAAT
ACCGGATATGACCTCGCACCGCATGGTGCGGGGTGGAAAGATTTATCGGTGGGGGATGGACTCGCGGCCT
ATCAGCTTGTTGGTGAGGTAATGGCTCACCAAGGCGACGACGGGTAGCCGGCCTGAGAGGGTGACCGGCC
ACACTGGGACTGAGACACGGCCCAGACTCCTACGGGAGGCAGCAGTGGGGAATATTGCACAATGGGCGAA
AGCCTGATGCAGCGACGCCGCGTGAGGGATGACGGCCTTCGGGTTGTAAACCTCTTTCAGTAGGGAAGAA
GCGAAAGTGACGGTACCTGCAGAAGAAGCGCCGGCTAACTACGTGCCAGCAGCCGCGGTAATACGTAGGG
CGCACGCGTTATCCGGATTTATTGGGCGTAAAGAGCTCGTAGGCGGTTTGTCGCGTCTGCCGTGAAAGTC
CGAGGCTCAACCTCGGATCTGCGGTGGGTACGGGCAGACTAGAGTGATGTAGGGGAGACTGGAATTCCTG
GTGTAGCGGTGAAATGCGCAGATATCAGGAGGAACACCGATGGCGAAGGCAGGTCTCTGGGCATTTACTG
ACGCTGAGGAGCGAAAGCATGGGGAGCGAACAGGATTAGATACCCTGGTAGTCCATGCCGTAAACGTTGG
GCACTAGGTGTGTGGGACATTCCACGTTTTCCTCGCCGTAGCTAACGCATTAAGTGCCCCGCCTGGGGAG
TACGGCCGCAAGGCTAAAACTCAAAGGAATTGACGGGGGCCCGCACAAGCGGCGGAGCATGCGGATTAAT
TCGATGCAACGCGAAGAACCTTACCAAGGCTTGACATGTGCCAGACCGCTCCAGAGATGGGGTTTCCCTT
CGGGGGTGGTTCACAGGTGGTGCATGGTTGTCGTCAGCTCGTGTCGTGAGATGTTGGGTTAAGTCCCGCA
ACGAGCGCAACCCTCGTTCCATGTTGCCAGCACGTAGTGGTGGGGACTCATGGGAGACTGCCGGGGTCAA
CTCGGAGGAAGGTGGGGATGACGTCAAATCATCATGCCCCTTATGTCTTGGGCTTCACGCATGCTACACA
ATGGCCGGTACAACAAGGTTGCCATACGTGTGAGGTGGAGCTAATCCCTAAAAGCCGGTCTCAGTTCGGA
TTGGGGTCTGCAACTCGACCCCATGAAGTCGGAGTCGCTAGTAATCGCAGATCAGCAACGCTGCGGTGAA
TACGTTCCCGGGCCTTGTACACACCGCCCGTCAAGTCACGAAAGTTGGTAACACCCGAAGCCGATGGCCT
AAC
''')

class NewDatabaseOneSequencePerSpeciesTestCase(unittest.TestCase):
    def test_parse_fasta_format_1(self):
        result = list(bioscript.parse_fasta_format(io.StringIO(TESTDATA_1.fasta)))
        self.assertEqual(len(result), 1)
        for r in result:
            self.assertEqual(r, (TESTDATA_1.description, TESTDATA_1.sequence))
        
    def test_parse_fasta_format_2(self):
        result = list(bioscript.parse_fasta_format(io.StringIO(TESTDATA_1.fasta * 2)))
        self.assertEqual(len(result), 2)
        for r in result:
            self.assertEqual(r, (TESTDATA_1.description, TESTDATA_1.sequence))
        
    def test_print_fasta_description_1(self):
        buffer = io.StringIO()
        bioscript.print_fasta_description(buffer, TESTDATA_1.description, TESTDATA_1.sequence)
        self.assertEqual(buffer.getvalue(), TESTDATA_1.fasta)

    def test_get_values_matching_genus_1(self):
        source = [(TESTDATA_1.description, TESTDATA_1.sequence)]
        count, all_values = bioscript.get_values_matching_genus('', source)
        self.assertEqual(count, len(source))
        expected = {
            TESTDATA_1.species: [(TESTDATA_1.accession, TESTDATA_1.translated, TESTDATA_1.sequence)]
        }
        self.assertEqual(all_values, expected)

    # TODO (halcanary): more test cases for get_values_matching_genus
    def test_get_values_matching_genus_2(self):
        source = [(TESTDATA_1.description, TESTDATA_1.sequence)]
        count, all_values = bioscript.get_values_matching_genus('Glutamicibacter', source)
        self.assertEqual(count, len(source))
        self.assertEqual(all_values, {})

    # TODO (halcanary): more test cases for process_values
    def test_process_values(self):
        vs = [(TESTDATA_1.accession, TESTDATA_1.translated, TESTDATA_1.sequence)]
        d, s = (bioscript.process_values(TESTDATA_1.species, vs))
        self.assertEqual(d, TESTDATA_1.translated)
        self.assertEqual(s, TESTDATA_1.sequence)


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)-5s:  %(message)s', level='INFO')
    unittest.main()
