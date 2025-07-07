from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mac-notifications",
    version="2.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Mac notification monitoring system with MCP server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mac-notifications",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: System :: Monitoring",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=[
        "mcp>=0.1.0",
        "psutil>=5.9.0",
        "python-dotenv>=0.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
            "pre-commit",
        ],
    },
    entry_points={
        "console_scripts": [
            "mac-notifications-daemon=mac_notifications.daemon.notification_daemon:main",
            "mac-notifications-server=mac_notifications.mcp_server.server:main",
        ],
    },
)
