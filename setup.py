import setuptools

install_requires = []
tests_require = ["pytest", "pytest-cov", "pytest-flake8", "asynctest"]
dev_requires = install_requires + tests_require + ["documenteer[pipelines]"]
scm_version_template = """# Generated by setuptools_scm
__all__ = ["__version__"]

__version__ = "{version}"
"""

setuptools.setup(
    name="ts-fiber-spectrograph",
    description="LSST Fiber Spectrograph",
    use_scm_version={
        "write_to": "python/lsst/ts/FiberSpectrograph/version.py",
        "write_to_template": scm_version_template,
    },
    setup_requires=["setuptools_scm", "pytest-runner"],
    install_requires=install_requires,
    package_dir={"": "python"},
    packages=setuptools.find_namespace_packages(where="python"),
    package_data={"": ["*.rst", "*.yaml"]},
    scripts=["bin/run_FiberSpectrograph.py"],
    tests_require=tests_require,
    extras_require={"dev": dev_requires},
    license="GPL",
    project_urls={
        "Bug Tracker": "https://jira.lsstcorp.org/secure/Dashboard.jspa",
        "Source Code": "https://github.com/lsst-ts/ts_FiberSpectrograph",
    },
)
