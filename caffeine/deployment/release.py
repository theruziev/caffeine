from importlib import reload

from jinja2 import Template

from caffeine import app_info

try:
    # available only for dev mode
    import semver
    import git
except ImportError:
    raise TypeError("packages available only for dev")

RELEASE_TEMPLATE = """version = "{{ version }}"
commit_hash = "{{ commit_hash }}"
name = "caffeine"

release_name = f"{name}@{version} ({commit_hash[:6]})"

"""


def get_current_release():
    reload(app_info)
    return app_info.release_name


def get_commit_hash():
    repo = git.Repo(search_parent_directories=True)
    return repo.head.object.hexsha


def new_version(bump_type, commit_hash):
    reload(app_info)
    template = Template(RELEASE_TEMPLATE)
    new_ver = app_info.version
    if bump_type == "major":
        new_ver = semver.bump_major(app_info.version)
    if bump_type == "minor":
        new_ver = semver.bump_minor(app_info.version)
    if bump_type == "patch":
        new_ver = semver.bump_patch(app_info.version)
    res = template.render({"version": new_ver, "commit_hash": commit_hash})
    with open("caffeine/app_info.py", "w") as f:
        f.write(res)
