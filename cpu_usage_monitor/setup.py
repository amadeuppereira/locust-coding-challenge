from setuptools import setup

setup(
    name="cpu-usage-monitor",
    version="0.1",
    py_modules=["cpu_usage_monitor"],
    install_requires=["psutil", "requests", "asyncio"],
    entry_points={
        "console_scripts": [
            "cpu-usage-monitor=cpu_usage_monitor:main",
        ],
    },
)
