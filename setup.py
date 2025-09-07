import setuptools

# Read the contents of the README file for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="reolink-mqtt-bridge",
    version="0.1.0",
    author="Curtis  Maddalozzo",
    author_email="curtis@maddalozzo.ca",
    description="A simple Flask web server to forward Reolink webhooks to an MQTT topic.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cmaddalozzo/reolink-mqtt-bridge", # Replace with your project's URL

    # py_modules is used for single-file Python modules.
    py_modules=["app"],

    # List of dependencies required by the project
    install_requires=[
        "Flask>=2.0",
        "paho-mqtt>=1.6",
    ],

    # Defines the command-line script that will be created.
    entry_points={
        "console_scripts": [
            "reolink-bridge=app:main",
        ],
    },

    # Classifiers help users find your project by browsing PyPI.
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: Flask",
        "Topic :: Home Automation",
        "Topic :: System :: Networking",
    ],
    python_requires='>=3.8',
)

