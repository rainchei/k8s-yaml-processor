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
                data['spec']['template']['metadata']['labels']['tag'] = tag[-63:]
                # add label: imageName, imageVersion
                image_ls = [c['image'] for c in data['spec']['template']['spec']['containers']]
                image_name = 'x_' + '_'.join(i.split(':')[0][i.split(':')[0].rfind('/')+1:][-16:] for i in image_ls)           # remove all chars before the last '/', and
                image_version = 'x_' + '_'.join(i.split(':')[1][-16:] for i in image_ls)                                       # each was truncated to last 16 chars, and
                data['spec']['template']['metadata']['labels']['imageName'] = image_name                                       # starts with 'x_'
                data['spec']['template']['metadata']['labels']['imageVersion'] = image_version
                result.append(data)
            elif data['kind'] == "CronJob":
                # add label: tag
                data['spec']['jobTemplate']['spec']['template']['metadata']['labels']['tag'] = tag[-63:]
                # add label: imageName, imageVersion
                image_ls = [c['image'] for c in data['spec']['jobTemplate']['spec']['template']['spec']['containers']]
                image_name = 'x_' + '_'.join(i.split(':')[0][i.split(':')[0].rfind('/')+1:][-16:] for i in image_ls)           # remove all chars before the last '/', and
                image_version = 'x_' + '_'.join(i.split(':')[1][-16:] for i in image_ls)                                       # each was truncated to last 16 chars
                data['spec']['jobTemplate']['spec']['template']['metadata']['labels']['imageName'] = image_name                # starts with 'x_'
                data['spec']['jobTemplate']['spec']['template']['metadata']['labels']['imageVersion'] = image_version
                result.append(data)
            elif 'kind' in data.keys():
                result.append(data)
    yaml.dump_all(result, sys.stdout)

# run the main function
if __name__ == "__main__":
    main()
