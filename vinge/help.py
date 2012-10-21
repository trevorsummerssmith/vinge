"""
This implements the help command.

I tried for far too long to get argparse to do something intelligent
and just print out the help message formatted in a way that I wanted,
but I just couldn't get it to work. So, here we are. We have this extremely
brittle thing going on. Oh well. :(
"""

from kct.output import pp
import kct.color as color

# First line of a command is printed next to the command name
# Subsequent lines should be indented two spaces
_HELP=\
{'node-ref' :
     {'_msg' : "this is information about a node-ref"},
 'regex' :
     {'_msg' : 'Interact with regexes',
      'add' :
          '<name> <regex>\n'\
          '  And some!',
      'list' :
          '\n'\
          '  Print the current regexes',
      'toggle' :
          '<name>\n  Turns regex on or off'
      },
 'go' :
     {'_msg' : '<index>\n  The neighbor index'},
 'info' :
     {'_msg' :
          '[node-ref]\n'\
          '  If omitted, uses \'current\'.'},
 'quit' :
     {'_msg' : '\n  Quits vinge'}
 }

def do_help(ctx, args):
    topic = args.topic
    # General help message
    if not topic:
        pp("help <topic>")
        for key in sorted(_HELP.iterkeys()):
            pp(key, indent=1)
    # Top level (we're only going one level if this gets much more complex
    # I'm going back to trying to make argparse work)
    elif _HELP.get(topic[0]):
        if len(topic) == 1:
            pp('%s ' % color.bold(topic[0]), newline=False)
            pp(_HELP[topic[0]]['_msg'])
            # Check if there's sub topics
            subtopics = filter(lambda s: s != '_msg', _HELP[topic[0]].keys())
            if len(subtopics) > 0:
                pp('  Subtopics')
                for key in sorted(subtopics):
                    pp(key, indent=2)
        elif _HELP[topic[0]].get(topic[1]):
            pp('%s %s ' % (color.bold(topic[0]), topic[1]), newline=False)
            pp(_HELP[topic[0]][topic[1]])
        else:
            pp("Unknown action: %s" % ' '.join(topic))
    # Nothing
    else:
        pp("Unknown action: %s" % ' '.join(topic))
