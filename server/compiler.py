import pbl
import engine
from components import inventory

OK = 'ok'

'''
    Programs are of the form:

    {
        "components": {
            "yfc" : { 
                "_type": "PlaylistSource",
                "name" : "Your Favorite Cofeehouse"
            },

            "tp" : { 
                "_type": "PlaylistSource",
                "name" : "Teen Party"
            },

            "alt" : {
                "_type": "Alternator",
                "source_list" : ["yfc", "tp"]
            },

            "filter": {
                "_type":"AttributeRangeFilter",
                "attr": "echonest.energy",
                "max_val" : 0.5,
                "source": "alt"
            },

            "sorter": {
                "_type":"Sorter",
                "attr": "echonest.loudness",
                "source": "filter"
            }
        },
        "main": "sorter"
    }
'''

def convert_val_to_type(val, type, program):
    if type in inventory['types']:
        return OK, val
    if type == 'string':
        return OK, str(val)
    elif type == 'string_list':
        return OK, val
    elif type == 'uri':
        return OK, str(val)
    elif type == 'uri_list':
        return OK, val
    elif type == 'number':
        #return OK, float(val)
        return OK, val
    elif type == 'bool':
        return OK, bool(val)
    elif type == 'source':
        status, compiled_program = compile_object(val, program)
        return status, compiled_program
    elif type == 'source_list':
        list = []
        for name in val:
            status, compiled_program = compile_object(name, program)
            if status == OK:
                list.append(compiled_program)
            else:
                return status, None
        return OK, list
    else:
        return 'unknown type ' + type, None
            

def get_param_val(param, val, spec, program):
    spec_params = spec['params']
    if param in spec_params:
        param_spec = spec_params[param]
        status, outval = convert_val_to_type(val, param_spec['type'], program)
        return status, outval
    else:
        return 'unknown param "' + param + '"', None

def get_spec_by_type(type):
    for component in inventory['components']:
        if type == component['name']:
            return component
    return None
    
def compile_object(objname, program):
    components = program['components']
    symbols = program['symbols']
    hsymbols = program['hsymbols']
    if objname in symbols:
        return OK, symbols[objname]
    else:
        if objname in components:
            comp = components[objname]
            spec = get_spec_by_type(comp['_type'])
            if spec:
                params = { }
                for param, val in comp.items():
                    if param == '_type':
                        continue
                    status, cval = get_param_val(param, val, spec, program)
                    print status, param, cval, val, spec
                    if status == OK:
                        params[param] = cval
                    else:
                        return status + " in " + objname, None
                try:
                    print 'creating', comp['_type'], params
                    obj = spec['class'](**params)
                    symbols[objname] = obj
                    hsymbols[obj] = objname
                    return OK, obj
                except:
                    raise pbl.PBLException(None, "creation failure", objname)
            else:
                return 'unknown type ' + comp['_type'] + ' for ' + objname, None
        else:
            return 'missing object ' + objname, None
    
def compile(program):
    if 'main' in program and program['main']:
        program['symbols'] = {}
        program['hsymbols'] = {}
        status, compiled_program = compile_object(program['main'], program)
        print 'hsymbols', program['hsymbols']
        print 'symbols', program['symbols']
        return status, compiled_program
    else:
        return 'no main', None


if __name__ == '__main__':
    import sys
    import json

    if len(sys.argv) > 1:
        path = sys.argv[1]
        source = open(path).read()
        source_obj = json.loads(source)

        status, obj = compile(source_obj)
        if status == OK:
            print 'compiled! = running'
            pbl.show_source(obj, props= ['src', 'duration'])
        else:
            print 'Whoops', status
