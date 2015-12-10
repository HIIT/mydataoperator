# -*- coding: utf-8 -*-
__author__ = 'Aleksi Palomäki'
import json


def magic(jsoni, ident):
    for single_object in jsoni:
        if isinstance(jsoni[single_object], dict):
            print("{}{}:".format(ident * "  ", single_object))
            ident = ident + 1
            print("{}type: object".format(ident * "  "))
            print("{}properties:".format(ident * "  "))
            magic(jsoni[single_object], ident + 1)
            ident = ident - 1
        elif isinstance(jsoni[single_object], str) or isinstance(jsoni[single_object], unicode):
            print("{}{}:".format(ident * "  ", single_object))
            ident = ident + 1
            print("{}type: string".format(ident * "  "))
            print("{}description: string containing {}".format(ident * "  ", single_object))
            ident = ident - 1
        elif isinstance(jsoni[single_object], list):
            print("{}{}:".format(ident * "  ", single_object))
            ident = ident + 1
            print("{}type: array".format(ident * "  "))
            print("{}items:".format(ident * "  "))
            if len(jsoni[single_object]) > 0:
                item_type = ""
                if type(jsoni[single_object][0]) is str or unicode:
                    item_type = "string"
                elif type(jsoni[single_object][0]) is int:
                    item_type = "integer"
                print("  {}type: {}".format(ident * "  ", item_type))
            ident = ident - 1
        elif isinstance(jsoni[single_object], int):
            print("{}{}:".format(ident * "  ", single_object))
            ident = ident + 1
            print("{}type: integer".format(ident * "  "))
            print("{}description: integer containing {}".format(ident * "  ", x))
            ident = ident - 1
            # magic(jsoni[x], ident+1)

# Insert JSON here and run
sample_json = '''
{

}
            '''

magic(json.loads(sample_json), 2)
