import os
import re
import env
import subprocess
import json
import builtins
from notify import send


class BaseApi:
    def notify(self, *args, **kwargs):
        return send(*args, **kwargs)


def init_global():
    QLAPI = BaseApi()
    builtins.QLAPI = QLAPI


def try_parse_int(value):
    try:
        return int(value)
    except ValueError:
        return None


def expand_range(range_str, max_value):
    temp_range_str = (
        range_str.strip()
        .replace("-max", f"-{max_value}")
        .replace("max-", f"{max_value}-")
    )

    result = []
    for part in temp_range_str.split(" "):
        range_match = re.match(r"^(\d+)([-~_])(\d+)$", part)
        if range_match:
            start, _, end = map(try_parse_int, range_match.groups())
            result.extend(range(start, end + 1))
        else:
            result.append(int(part))

    return result


def run():
    try:
        split_str = "__sitecustomize__"
        command = f'bash -c "source {os.getenv("taskBefore")} {os.getenv("fileName")}'

        if os.getenv("task_before"):
            command += f" && echo -e '执行前置命令\n' && eval \"{os.getenv('task_before')}\" && echo -e '\n执行前置命令结束\n'"

        python_command = "PYTHONPATH= python3 -c 'import os, json; print(json.dumps(dict(os.environ)))'"
        command += f' && echo "{split_str}" && {python_command}"'

        res = subprocess.check_output(command, shell=True, encoding="utf-8")
        output, env_str = res.split(split_str)

        env_json = json.loads(env_str.strip())

        for key, value in env_json.items():
            os.environ[key] = value

        print(output)

    except subprocess.CalledProcessError as error:
        print(f"run task before error: {error}")

    env_param = os.getenv("envParam")
    num_param = os.getenv("numParam")

    if env_param and num_param:
        array = (os.getenv(env_param) or "").split("&")
        run_arr = expand_range(num_param, len(array))
        array_run = [array[i - 1] for i in run_arr if i - 1 < len(array) and i > 0]
        env_str = "&".join(array_run)
        os.environ[env_param] = env_str


init_global()
run()