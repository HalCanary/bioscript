#! /usr/bin/env python

# Copyright 2023 Hal W Canary III, Lindsay R Saunders PhD. ALL RIGHTS RESERVED.

import sys
import os

DEFAULT_GENUS = 'Glutamicibacter'
DEFAULT_INPUT_FILE = os.path.expanduser('~/Desktop/SP23_NewGeneraDatabases/Glutamicibacter_spp.fasta')
DEFAULT_OUTPUT_FILE = os.path.expanduser('~/Desktop/SP23_NewGeneraDatabases/Glutamicibacter_spp_16s.fasta')

VERBOSE = True

################################################################################
# fasta format parsing

def parse_fasta_format(f):
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
    o.write('>%s\n' % description) # prepend '>' character.
    for i in range(0, len(sequence), 70):
        o.write(sequence[i:i+70]) 
        o.write('\n')
    o.write('\n')
    
################################################################################

def get_values_matching_genus(given_genus, inputf):
    #all_values[species_name] = [ (accession_number, desc, sequence), .... ]
    all_values = {}
    count, match_count = 0, 0
    for description, value in parse_fasta_format(inputf):
        count += 1
        accession, genus, epithet, extra = description.split(maxsplit=3)
        species = genus + '_' + epithet
        if extra is None or genus != given_genus:
            if VERBOSE:
                sys.stderr.write('BAD MATCH:  %r\n' % description)
            continue
        sys.stderr.write('good match: %r\n' % description)
        new_description = ' '.join([species, accession, extra])
        if species not in all_values:
            all_values[species] = []
        all_values[species].append((accession, new_description, value))
        match_count += 1
    if VERBOSE:
        sys.stderr.write('\nMatched %d of %d.\n' % (match_count, count))
    return all_values


def calculate_score(accession, description, sequence):
    count = sum(1 for c in sequence if c in ['A', 'G', 'T', 'C'])
    return (1 if ' type strain ' in description else 0,
            count / len(sequence),
            1 if accession.startswith('NR_') else 0,
            len(sequence))


def get_best_sequence(values):
    # values = [ (accession_number, description, sequence), .... ]
    best = (None, None)
    if len(values) > 0:
        best_score = calculate_score(*values[0])
        for accession, description, sequence in values[1:]:
            score = calculate_score(accession, description, sequence)
            if score > best_score:
                best_score = score
                best = (description, sequence)
    return best
    

def process(all_values, outputf):
    if VERBOSE:
        sys.stderr.write('\n')
    #all_values[species_name] = [ (accession_number, description, sequence), .... ]
    #>species accesion_number extra stuff
    count = 0
    for species, values in sorted(all_values.items()):
        assert len(values) > 0
        description, sequence = get_best_sequence(values)
        if description is not None:
            print_fasta_description(outputf, description, sequence)
            count += 1
            if VERBOSE:
                sys.stderr.write('Species %r, best of %d\n' %(species, len(values)))
    if VERBOSE:
        sys.stderr.write('\n%d of %d species processed.\n\n' % (count, len(all_values)))

def main(genus, input_file, output_file):
    if VERBOSE:
        sys.stderr.write('Genus  is %r\n' % genus)
        sys.stderr.write('Input  is %r\n' % input_file)
        sys.stderr.write('Output is %r\n\n' % output_file)
    with open(input_file) as f:
        all_values = get_values_matching_genus(genus, f)
    with open(output_file, 'w') as o:
        process(all_values, o)
    if VERBOSE:
        sys.stderr.write('wrote to %r\n' % (output_file))
                

if __name__ == '__main__':
    if len(sys.argv) == 4:
        main(*sys.argv[1:4])
    else:
        main(DEFAULT_GENUS, DEFAULT_INPUT_FILE, DEFAULT_OUTPUT_FILE)