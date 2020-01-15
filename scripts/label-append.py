import getopt, sys
import base64
from ruamel.yaml import YAML


def usage():
    print('Usage: cat ... | {} -t <tag>'.format(sys.argv[0]))
    print(
"""
Example:
cat sample/deployment.yml | python3 {} -t foo-bar-1234
""".format(sys.argv[0])
    )

def getArgs():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ht:", ["help", "tag="])
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
        elif o in ("-t", "--tag"):
            tag = a
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
               (data['kind'] == "DaemonSet"):
                # add label: tag
                data['spec']['template']['metadata']['labels']['tag'] = tag
                # add label: imageName, imageVersion
                image_ls = [c['image'] for c in data['spec']['template']['spec']['containers']]
                image_name = '_'.join(i.split(':')[0][i.split(':')[0].rfind('/')+1:] for i in image_ls)  # remove all chars before the last '/'
                image_version = '_'.join(i.split(':')[1] for i in image_ls)
                data['spec']['template']['metadata']['labels']['imageName'] = image_name
                data['spec']['template']['metadata']['labels']['imageVersion'] = image_version
                result.append(data)
            elif data['kind'] == "CronJob":
                # add label: tag
                data['spec']['jobTemplate']['spec']['template']['metadata']['labels']['tag'] = tag
                # add label: imageName, imageVersion
                image_ls = [c['image'] for c in data['spec']['jobTemplate']['spec']['template']['spec']['containers']]
                image_name = '_'.join(i.split(':')[0][i.split(':')[0].rfind('/')+1:] for i in image_ls)  # remove all chars before the last '/'
                image_version = '_'.join(i.split(':')[1] for i in image_ls)
                data['spec']['jobTemplate']['spec']['template']['metadata']['labels']['imageName'] = image_name
                data['spec']['jobTemplate']['spec']['template']['metadata']['labels']['imageVersion'] = image_version
                result.append(data)
            elif 'kind' in data.keys():
                result.append(data)
    yaml.dump_all(result, sys.stdout)

# run the main function
if __name__ == "__main__":
    main()
