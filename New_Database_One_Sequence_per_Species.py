#! /usr/bin/env python

# Copyright 2023 Hal W Canary III, Lindsay R Saunders PhD.
# Use of this program is governed by contents of the LICENSE file.

import collections
import os
import sys

DEFAULT_GENUS = 'Glutamicibacter'
DEFAULT_INPUT_FILE = os.path.expanduser('~/Desktop/SP23_NewGeneraDatabases/Glutamicibacter_spp.fasta')
DEFAULT_PATH_MODIFIER = '_16s'

VERBOSE = True

################################################################################
# FASTA file format parsing functions
# These may be moved to another package at a later time.
################################################################################

def parse_fasta_format(f):
    '''
    @param f file object open for reading in FASTA format.
    '''
    description, sequence = None, None
    for line in f:
        if line.startswith('>'):
            if description and sequence:
                yield (description, sequence)
            #remove '>' character
            description, sequence = line[1:].strip(), ''
        elif sequence is not None:
            sequence += line.strip()
    if description and sequence:
        yield (description, sequence)

def print_fasta_description(o, description, sequence):
    '''
    @param o file object open for writing.
    @param description string describing the sequence.
    @param sequence string in FASTA Sequence Representation.
    '''
    o.write('>%s\n' % description) # prepend '>' character.
    for i in range(0, len(sequence), 70):
        o.write(sequence[i:i+70])
        o.write('\n')
    o.write('\n')

################################################################################

def get_values_matching_genus(given_genus, inputf):
    '''
    @param given_genus If not '', will filter the sequences by genus.
    @param inputf file object open for reading in FASTA format.
           Each description line is expected to be in the form:
           >ACCESSION_NUMBER GENUS EPITHET EXTRA ...
    @return dictionary keyed by species ("{GENUS}_{EPITHET}") with values
            that are lists of tuples, where each tuple is
            `(accession_number, changed_description, sequence)`.
            The new decription is the form:
            >GENUS_EPITHET ACCESSION_NUMBER EXTRA ...
    '''
    all_values = collections.defaultdict(list)
    count = 0
    for description, value in parse_fasta_format(inputf):
        count += 1
        try:
            accession, genus, epithet, extra = description.split(maxsplit=3)
        except ValueError as e:
            sys.stderr.write('ERROR: Unable to parse description: %r\n' % description)
            continue
        if given_genus != '' and genus != given_genus:
            if VERBOSE:
                sys.stderr.write('BAD MATCH:  %r\n' % description)
            continue
        if VERBOSE:
            sys.stderr.write('good match: %r\n' % description)

        species = genus + '_' + epithet
        new_description = ' '.join([species, accession, extra])
        all_values[species].append((accession, new_description, value))
    if VERBOSE:
        match_count = sum(len(v) for v in all_values.values())
        sys.stderr.write('\nMatched %d of %d.\n' % (match_count, count))
    return dict(all_values)


def process(all_values, outputf):
    '''
    @param all_values dictionary in the form returned by `get_values_matching_genus`.
    @param outputf file object open for writing.
    '''
    if VERBOSE:
        sys.stderr.write('\n')
    count = 0
    # Sort output by sepcies for reproducability.
    for species, values in sorted(all_values.items()):
        best_description, best_sequence, best_score = None, None, (-1, -1, -1, -1)
        for accession, description, sequence in values:
            # score is a comparable 4-tuple of non-negative numbers.
            score = (1 if ' type strain ' in description else 0,
                    float(sum(1 for c in sequence if c in ['A', 'G', 'T', 'C'])) / len(sequence),
                    1 if accession.startswith('NR_') else 0,
                    len(sequence))
            if score >= best_score:
                best_description, best_sequence, best_score = description, sequence, score
        if best_description and best_sequence:
            print_fasta_description(outputf, best_description, best_sequence)
            count += 1
            if VERBOSE:
                sys.stderr.write('Species %r, best of %d\n' %(species, len(values)))
    if VERBOSE:
        sys.stderr.write('\n%d of %d species processed.\n\n' % (count, len(all_values)))


def main(given_genus, input_file, pathmod=DEFAULT_PATH_MODIFIER):
    '''
    @param given_genus If not '', will filter the sequences by genus.
    @param input_file The path of the FASTA format input file.
    @param pathmod If imput_file is 'foo/bar.baz.fasta' and pathmod is
           '_filtered', then the output file will be
           'foo/bar.baz_filtered.fasta'.
    @return 0 on success, 1 othewrwise.
    '''
    if pathmod == '':
        pathmod = DEFAULT_PATH_MODIFIER
    pathroot, pathext = os.path.splitext(input_file)
    output_file = pathroot + pathmod + pathext
    if VERBOSE:
        sys.stderr.write('Genus  is %r\n' % given_genus)
        sys.stderr.write('Input  is %r\n' % input_file)
        sys.stderr.write('Output is %r\n\n' % output_file)
    with open(input_file) as f:
        all_values = get_values_matching_genus(given_genus, f)
    if len(all_values) == 0:
        sys.stderr.write('no sequences match.\n')
        return 1
    with open(output_file, 'w') as o:
        process(all_values, o)
    if VERBOSE:
        sys.stderr.write('wrote to %r\n' % (output_file))
    return 0


if __name__ == '__main__':
    if len(sys.argv) == 4:
        sys.exit(main(*sys.argv[1:4]))
    elif len(sys.argv) == 1:
        sys.exit(main(DEFAULT_GENUS, DEFAULT_INPUT_FILE, DEFAULT_PATH_MODIFIER))
    else:
        sys.stderr.write('\nUsage:\n %s GENUS INPUT_FILE_PATH PATH_MODIFIER_STRING\n\n' % sys.argv[0])
        sys.exit(1)