import sys
import base64
from ruamel.yaml import YAML


def main():
    """Apply policy check for kubernetes yaml files.

    Stdin:
      yaml

    Returns:
      bool
    """
    yaml = YAML()
    for data in list(yaml.load_all(sys.stdin)):
        if data is not None:
            # policy 1: validate_required_for_container.
            required = ['name', 'image', 'resources']
            if not validate_required_for_container(data=data, c_req=required):
                # policy 1: failed.
                sys.exit(2)

def validate_required_for_container(data, c_req):
    """Validate required keys for container in k8s object.

    Args:
      data: dict
      c_req: list

    Returns:
      bool
    """
    c_req_set = set(c_req)
    result = True
    if (data['kind'] == "Deployment") or \
       (data['kind'] == "DaemonSet") or \
       (data['kind'] == "StatefulSet"):
        for i,c in enumerate(data['spec']['template']['spec']['containers']):
            d_set = set(c.keys())
            if not d_set >= c_req_set:
                missing_keys = list(c_req_set - d_set)
                print(
                    err_msg(
                        lvl="ERR",
                        sub="Missing required keys in containers",
                        msg=", ".join(str(e) for e in missing_keys)
                    ),
                    file=sys.stderr
                )
                result = False
    elif data['kind'] == "CronJob":
        for i,c in enumerate(data['spec']['jobTemplate']['spec']['template']['spec']['containers']):
            d_set = set(c.keys())
            if not d_set >= c_req_set:
                missing_keys = list(c_req_set - d_set)
                print(
                    err_msg(
                        lvl="ERR",
                        sub="Missing required keys in containers",
                        msg=", ".join(str(e) for e in missing_keys)
                    ),
                    file=sys.stderr
                )
                result = False
    return result

def err_msg(lvl, sub, msg):
    """Generate error message.

    Args:
      lvl: str
      sub: str
      msg: str

    Returns:
      str
    """
    return "{lvl} - {sub}: {msg}".format(
        lvl=lvl,
        sub=sub,
        msg=msg
    )


# run the main function
if __name__ == "__main__":
    main()
