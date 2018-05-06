#!/usr/bin/env python

"""
Takes a list of atomic contacts as input and generates a json representing a
temporal flare which can be visualized using flareplots.

A subset of interaction types can be selected using the --itype argument which
is formatted as a comma-separated list of abbreviations corresponding to
    sb             salt bridges
    pc             pi-cation
    ps             pi-stacking
    ts             t-stacking
    vdw            van der Waals
    hb             hydrogen bonds
    lhb            ligand hydrogen bonds
    hbbb           backbone-backbone hydrogen bonds
    hbsb           backbone-sidechain hydrogen bonds
    hbss           sidechain-sidechain hydrogen bonds
    wb             water bridges
    wb2            extended water bridges
    hls            ligand-sidechain residue hydrogen bonds
    hlb            ligand-backbone residue hydrogen bonds
    lwb            ligand water bridges
    lwb2           extended ligand water bridges

By default, the labels on the plot will reflect the residue identifier.
Optionally, a "flare-label" file can be supplied which indicates how residue
identifiers should be translated to flare-plot labels. The flare-label file is
a tab-separated text-file where each line has one field that indicates a colon-
separated residue identifier and one field that indicates the corresponding
flareplot label. Dots in the flareplot labels can be used to group and organize
labels. A valid flare-label file would look like this:
    A:ARG:4  Root.Helix1.1x30
    A:LYS:5  Root.Helix1.1x31
    ...
    A:PRO:45 Root.Helix2.2x36
    A:MET:46 Root.Helix2.2x37
    ...
The flare-label file can also act as a filter, as interactions between residues
that are not included in the file will be excluded from the plot. For
convenience it's not necessary to include the second column if the label file
is just used as a filter. A third column can be supplied indicating a color in
CSS-format (e.g. '#FF0000' or 'red').
"""

__author__ = 'Rasmus Fonseca <fonseca.rasmus@gmail.com>'
__license__ = "Apache License 2.0"

from contact_calc.flare import *
from contact_calc.transformations import *
import sys


def main():
    """
    Main function called once at the end of this module. Configures and parses command line arguments, parses input
    files and generates output files.
    """
    # Parse command line arguments
    import argparse as ap
    parser = ap.ArgumentParser(description=__doc__, formatter_class=ap.RawTextHelpFormatter)
    optional = parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    parser._action_groups.append(optional)  # added this line

    required.add_argument('--input',
                          required=True,
                          type=ap.FileType('r'),
                          help='A multi-frame contact-file generated by dynamic_contact.py')
    required.add_argument('--output',
                          required=False,
                          type=str,
                          help='The json file to write flare to')

    optional.add_argument('--itype',
                          required=False,
                          default="all",
                          type=str,
                          help='Interaction types to include (comma separated list) [default: all]')
    optional.add_argument('--flarelabels',
                          required=False,
                          default=None,
                          type=ap.FileType('r'),
                          help='Flare-label file')

    args = parser.parse_args()

    if args.output:
        print("Parsing %s contacts from %s" % (args.itype, args.input.name))

    # Read contacts and generate graph
    itypes = parse_itypes(args.itype)
    contacts = parse_contacts(args.input, itypes)
    labels = parse_residuelabels(args.flarelabels)
    graph = create_flare(contacts, labels)  # create_graph(contacts, labels)

    # Write output
    if args.output:
        write_json(graph, args.output)
        print("Done - wrote flare-json to %s" % args.output.name)
    else:
        write_json(graph, sys.stdout)


def parse_itypes(itype_argument):
    """Parses the itype argument and returns a set of strings with all the selected interaction types """
    if "all" in itype_argument:
        return ["sb", "pc", "ps", "ts", "vdw", "hb", "lhb", "hbbb", "hbsb",
                "hbss", "wb", "wb2", "hls", "hlb", "lwb", "lwb2"]
    return set(itype_argument.split(","))


# def create_graph(contacts, resi_labels):
#     """
#     Creates a graph from the contacts and residue labels formatted as a dict that can be trivially dumped to a json that
#     can be read by flareplot. An "edge" key mapping to a list of edge specifiers with "name1", "name2", and "frames"
#     attributes will always be generated and if `resi_labels` isn't `None` then the "trees" and "tracks" will be
#     generated as well.
#
#     Parameters
#     ----------
#     contacts : list of tuples of (str, str, tuple, tuple [[, tuple], tuple])
#         Each entry specifies a frame-number, an interaction type, and 2 to 4 atom-tuples depending on the interaction
#         type. Water mediated and water-water mediated interactions will have waters in the third and fourth tuples.
#
#     resi_labels : dict of (str : dict of (str : str))
#         Each key is a residue identifier and the associated value is a dictionary with the label, tree-path, and color
#         that are consistent with the format of flareplots.
#
#     Returns
#     -------
#     dict of str : list
#         The types of the list contents varies depending on the key, but the format corresponds to the specifications of
#         jsons used as input for flareplot. For example
#         >>> {
#         >>>   "edges": [
#         >>>     {"name1": "ARG1", "name2": "ALA3", "frames": [0,4,10]},
#         >>>     {"name1": "ALA3", "name2": "THR2", "frames": [1,2]}
#         >>>   ],
#         >>>   "trees": [
#         >>>     {"treeName": "DefaultTree", "treePaths": ["Group1.ARG1", "Group1.THR2", "Group2.ALA3", "Group2.CYS4"]}
#         >>>   ],
#         >>>   "tracks": [
#         >>>     {"trackName": "DefaultTrack", "trackProperties": [
#         >>>       {"nodeName": "ARG1", "size": 1.0, "color": "red"},
#         >>>       {"nodeName": "THR2", "size": 1.0, "color": "red"},
#         >>>       {"nodeName": "ALA3", "size": 1.0, "color": "blue"},
#         >>>       {"nodeName": "CYS4", "size": 1.0, "color": "blue"}
#         >>>     ]}
#         >>>   ]
#         >>> }
#     """
#     ret = {
#         "edges": []
#     }
#
#     # print(resi_labels)
#     # Strip atom3, atom4, and atom names
#     # unique_chains = set([c[2][0] for c in contacts] + [c[3][0] for c in contacts])
#     contacts = [(c[0], c[1], c[2][0:3], c[3][0:3]) for c in contacts]
#
#     resi_edges = {}
#     for contact in contacts:
#         # Compose a key for atom1 and atom2 that ignores the order of residues
#         a1_key = ":".join(contact[2][0:3])
#         a2_key = ":".join(contact[3][0:3])
#         if a1_key == a2_key:
#             continue
#         if a1_key > a2_key:
#             a1_key, a2_key = a2_key, a1_key
#         contact_key = a1_key + a2_key
#
#         # Look up labels
#         if resi_labels:
#             if a1_key not in resi_labels or a2_key not in resi_labels:
#                 print("Omitting contact "+str(contact)+" as it doesn't appear in flare-label file")
#                 continue
#             a1_label = resi_labels[a1_key]["label"]
#             a2_label = resi_labels[a2_key]["label"]
#         else:
#             a1_label = a1_key
#             a2_label = a2_key
#
#         # Create contact_key if it doesn't exist
#         if contact_key not in resi_edges:
#             edge = {"name1": a1_label, "name2": a2_label, "frames": []}
#             resi_edges[contact_key] = edge
#             ret["edges"].append(edge)
#
#         resi_edges[contact_key]["frames"].append(int(contact[0]))
#
#     # Sort edge frames and ensure that there are no duplicates
#     for e in ret["edges"]:
#         e["frames"] = sorted(set(e["frames"]))
#
#     # Create "trees" and "tracks" sections if resi_labels specified
#     if resi_labels is not None:
#         tree = {"treeLabel": "DefaultTree", "treePaths": []}
#         ret["trees"] = [tree]
#
#         track = {"trackLabel": "DefaultTrack", "trackProperties": []}
#         ret["tracks"] = [track]
#
#         for rlabel in resi_labels.values():
#             tree["treePaths"].append(rlabel["treepath"])
#             track["trackProperties"].append({
#                 "nodeName": rlabel["label"],
#                 "color": rlabel["color"],
#                 "size": 1.0
#             })
#
#     return ret


if __name__ == "__main__":
    main()


