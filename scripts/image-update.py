import getopt, sys
import base64
from ruamel.yaml import YAML


def usage():
    print('Usage: cat ... | {} -t <type=containers|initContainers> -n <name> -i <image>'.format(sys.argv[0]))
    print(
"""
Example:
cat sample/deployment.yml | python3 {} -t containers -n sample-foo -i busybox:1.31.1-uclibc
""".format(sys.argv[0])
    )

def getArgs():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ht:n:i:", ["help", "type=", "name=", "image="])
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

def main():
    opts = getArgs()
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-t", "--type"):
            c_type = a
        elif o in ("-n", "--name"):
            c_name = a
        elif o in ("-i", "--image"):
            c_image = a
        else:
            assert False, "unhandled option"
    yaml = YAML()
    yaml.explicit_start = True
    yaml.allow_unicode = True
    yaml.width = 300
    result = []
    for data in list(yaml.load_all(sys.stdin)):
        if data is not None:
            if (data['kind'] == "Deployment") or \
               (data['kind'] == "DaemonSet") or \
               (data['kind'] == "StatefulSet"):
                # update image
                container_ls = [c['name'] for c in data['spec']['template']['spec'][c_type]]
                for n,c in enumerate(container_ls):
                    if c == c_name:
                        data['spec']['template']['spec'][c_type][n]['image'] = c_image
                result.append(data)
            elif data['kind'] == "CronJob":
                # update image
                container_ls = [c['name'] for c in data['spec']['jobTemplate']['spec']['template']['spec'][c_type]]
                for n,c in enumerate(container_ls):
                    if c == c_name:
                        data['spec']['jobTemplate']['spec']['template']['spec'][c_type][n]['image'] = c_image
                result.append(data)
            elif 'kind' in data.keys():
                result.append(data)
    yaml.dump_all(result, sys.stdout)

# run the main function
if __name__ == "__main__":
    main()
