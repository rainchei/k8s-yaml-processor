import sys
import base64
from ruamel.yaml import YAML


def main():
    yaml = YAML()
    yaml.explicit_start = True
    yaml.allow_unicode = True
    yaml.width = 300
    result = []
    for data in list(yaml.load_all(sys.stdin)):
        if data is not None:
            if data['kind'] == 'Secret':
                for k,v in data['data'].items():
                    data['data'][k] = base64.b64encode(v.encode('utf-8')).decode('utf-8')
                result.append(data)
            elif data['kind'] == 'Namespace':
                result.append(data)
    yaml.dump_all(result, sys.stdout)

# run the main function
if __name__ == "__main__":
    main()
