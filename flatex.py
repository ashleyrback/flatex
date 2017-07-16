#! /usr/bin/env python
import argparse
import os
import re
import sys

def is_input(line):
    """
    Determines whether or not a read in line contains an uncommented out
    \input{} statement. Allows only spaces between start of line and
    '\input{}'.
    """
    #tex_input_re = r"""^\s*\\input{[^}]*}""" # input only
    tex_input_re = r"""(^[^\%]*\\input{[^}]*})|(^[^\%]*\\include{[^}]*})"""
        # input or include
    return re.search(tex_input_re, line)


def is_subimport(line):
    """
    Determines whether or not a read in line contains an uncommented out
    \subimport{} statement. Allows only spaces between start of line and
    '\subimport{}'.
    """
    tex_input_re = r"""((^[^\%]*\\subimport{[^}]*}))"""  # subimport
    return re.search(tex_input_re, line)


def get_input(line):
    """
    Gets the file name from a line containing an input statement.
    """
    tex_input_filename_re = r"""{[^}]*"""
    m = re.search(tex_input_filename_re, line)
    return m.group()[1:]


def get_subimport(line):
    """
    Gets the file name from a line containing a subimport statement.
    """

    tex_input_filename_re = r"""{[^}]*"""
    directory = re.findall(tex_input_filename_re, line)[0][1:]
    filename = re.findall(tex_input_filename_re, line)[-1][1:]
    return directory + filename


def combine_path(base_path, relative_ref):
    """
    Combines the base path of the tex document being worked on with the
    relate reference found in that document.
    """
    #if (base_path != ""):
    #    os.chdir(base_path)
    #    print os.getcwd()
    # Handle if .tex is supplied directly with file name or not
    base_file = os.path.split(relative_ref)[1]
    if not base_file.endswith('.tex') and not base_file.endswith('.pgf'):
        base_file += '.tex'
    relative_path = os.path.split(relative_ref)[0]
    if relative_path:
        if relative_path.startswith(".."):
            relpath = relative_path
        else:
            relpath = os.path.relpath(relative_path, base_path)
        if base_path:
            print os.path.relpath(relative_path, base_path)
            current_path = os.path.normpath(
                base_path + "/" + relpath)
            if current_path[-1] == ".":
                current_path = current_path[:-1]
        else:
            current_path = relative_path
    else:
        current_path = base_path
    return base_file, current_path


def expand_file(base_file, current_path, include_bbl):
    """
    Recursively-defined function that takes as input a file and returns it
    with all the inputs replaced with the contents of the referenced file.
    """
    output_lines = []
    print os.path.normpath(current_path + "/" + base_file)
    if current_path:
        f = open(current_path + "/" + base_file, "r")
    else:
        f = open(base_file, "r")
    for line in f:
        if is_input(line):
            base_file, current_path = combine_path(
                current_path, get_input(line))
            output_lines += expand_file(
                base_file, current_path, include_bbl)
            output_lines.append('\n')  # add a new line after each file input
        elif is_subimport(line):
            base_file, current_path = combine_path(
                current_path, get_subimport(line))
            output_lines += expand_file(
                base_file, current_path, include_bbl)
            output_lines.append('\n')  # add a new line after each file input
        elif include_bbl and line.startswith("\\bibliography") and (not line.startswith("\\bibliographystyle")):
            output_lines += bbl_file(base_file)
        else:
            output_lines.append(line)
    f.close()
    return output_lines


def bbl_file(base_file):
    """
    Return content of associated .bbl file
    """
    bbl_path = os.path.abspath(os.path.splitext(base_file)[0]) + '.bbl'
    return open(bbl_path).readlines()

def main(base_file, output_file, include_bbl = False):

    """
    This "flattens" a LaTeX document by replacing all \input{X} lines w/ the
    text actually contained in X. See associated README.md for details.
    """
    current_path = os.path.split(base_file)[0]
    print current_path
    g = open(output_file, "w")
    g.write(''.join(expand_file(base_file, current_path, include_bbl)))
    g.close()
    return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("base_file", type=str, help="Path of base file")
    parser.add_argument("output_file", type=str, help="Path to output file")
    parser.add_argument("--include_bbl", type=bool, default=False,
                        help="Include bbl")
    args = parser.parse_args()

    main(**vars(args))
