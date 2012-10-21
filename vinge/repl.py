from kct.argparse import ArgumentParser
import kct.output as output
import sys

import vinge.cmd as cmd
import vinge.help

class _CommandParsingError(Exception):
    def __init__(self, message):
        self.message = message

class _DontDieArgumentParser(ArgumentParser):
    """
    ArgumentParser prints a message then calls exit upon reaching an error.
    Override the error method to raise an exception instead. This is used to
    parse the input on our REPL.
    """
    def error(self, message):
        raise _CommandParsingError(message)

def _setup_command_parser():
    command_parser = _DontDieArgumentParser(description='foo')
    subparsers = command_parser.add_subparsers()

    # go command
    go_parser = subparsers.add_parser('go', aliases=['g'])
    go_parser.add_argument('idx', type=int)
    go_parser.set_defaults(func=cmd.go_by_neighbor_index)

    help_parser = subparsers.add_parser('help')
    help_parser.add_argument('topic', nargs='*')
    help_parser.set_defaults(func=vinge.help.do_help)

    # info
    info_parser = subparsers.add_parser('info', aliases=['i'])
    info_parser.add_argument('node-ref', nargs='?')
    info_parser.set_defaults(func=cmd.node_info)

    # quit
    quit_parser = subparsers.add_parser('quit')
    quit_parser.set_defaults(func=cmd.quit)

    # regex commands
    regex_parser = subparsers.add_parser('regex', aliases=['r'])
    regex_sparser = regex_parser.add_subparsers()

    # regex list
    regex_list_parser = regex_sparser.add_parser('list', aliases=['l'])
    regex_list_parser.set_defaults(func=cmd.regex_list)

    # regex add
    regex_add_parser = regex_sparser.add_parser('add', aliases=['a'])
    regex_add_parser.add_argument('name')
    regex_add_parser.add_argument('regex-str', nargs='+')
    regex_add_parser.set_defaults(func=cmd.regex_add)

    # regex toggle
    regex_toggle_parser = regex_sparser.add_parser('toggle')
    regex_toggle_parser.add_argument('name')
    regex_toggle_parser.set_defaults(func=cmd.regex_toggle)

    return command_parser

def repl(ctx):
    parser = _setup_command_parser()
    while True:
        output.pp("> ", newline=False)
        str_args = sys.stdin.readline().rstrip()
        parser_args = str_args.split()
        try:
            args = parser.parse_args(parser_args)
        except _CommandParsingError, cpe:
            print "Error %s" % cpe.message
            continue
        args.func(ctx, args)
