# coding=utf-8

plugin_identifier = "tapo_bulbs"
plugin_package = "octoprint_tapo_bulbs"
plugin_name = "OctoPrint-TapoBulbs"
plugin_version = "0.1.0"
plugin_description = (
    "Control Matter-connected Tapo bulbs through Home Assistant and automate "
    "print lighting from OctoPrint."
)
plugin_author = "William Vandergraaf"
plugin_author_email = "willtheorangeguy@outlook.com"
plugin_url = "https://github.com/willtheorangeguy/OctoPrint-TapoBulbs"
plugin_license = "AGPLv3"

# OctoPrint already includes requests, so the plugin has no extra runtime
# dependencies.
plugin_requires = []

additional_setup_parameters = {
    "python_requires": ">=3.7,<4",
    "extras_require": {
        "develop": [
            "pytest>=7",
            "requests-mock>=1.10",
        ]
    },
}

from setuptools import find_packages, setup

# Keep builds independent of OctoPrint so pip's isolated build environment
# can produce both wheels and editable installs.
setup(
    name=plugin_name,
    version=plugin_version,
    description=plugin_description,
    author=plugin_author,
    author_email=plugin_author_email,
    url=plugin_url,
    license=plugin_license,
    packages=find_packages(include=[plugin_package, plugin_package + ".*"]),
    package_data={
        plugin_package: ["static/css/*.css", "static/js/*.js", "templates/*.jinja2"]
    },
    entry_points={"octoprint.plugin": [plugin_identifier + " = " + plugin_package]},
    install_requires=["OctoPrint>=1.5.0"] + plugin_requires,
    zip_safe=False,
    **additional_setup_parameters
)
