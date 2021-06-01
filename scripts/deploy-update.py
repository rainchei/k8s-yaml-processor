import getopt, sys
import base64
from ruamel.yaml import YAML
from collections.abc import Mapping

def usage():
    print('Usage: cat ... | {} -k <key> -v <value>'.format(sys.argv[0]))
    print(
"""
Example:
cat sample/deployment.yml | python3 {} -k <key> -v <value>
""".format(sys.argv[0])
    )

def getArgs():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hk:v:", ["help", "key=", "value="])
        if opts:
            return opts
        else:
            usage()
            sys.exit(2)
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

def update_data(ori_d, ref_d):
    for k, v in ref_d.items():
        if isinstance(v, Mapping):
            ori_d[k] = update_data(ori_d.get(k, {}), v)
        else:
            ori_d[k] = v
    return ori_d

def main():
    opts = getArgs()
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-k", "--key"):
            key_to_update = a
        elif o in ("-v", "--value"):
            value_to_update = a
        else:
            assert False, "unhandled option"

    yaml = YAML()
    yaml.explicit_start = True
    yaml.allow_unicode = True
    yaml.width = 300

    data_list = key_to_update.split(".")
    data_to_refer = value_to_update
    for k in data_list[::-1]:
        data_to_refer = {k: data_to_refer}

    result = []
    for data in list(yaml.load_all(sys.stdin)):
        if data is not None:
            data = update_data(data, data_to_refer)
            result.append(data)
    yaml.dump_all(result, sys.stdout)

# run the main function
if __name__ == "__main__":
    main()
