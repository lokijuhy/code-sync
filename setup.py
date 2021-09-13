from setuptools import setup, find_packages

URL = "https://github.com/uzh-dqbm-cmi/code-sync"
PROJECT_URLS = {
    "Bug Tracker": "https://github.com/uzh-dqbm-cmi/code-sync/issues",
    "Documentation": "https://github.com/uzh-dqbm-cmi/code-sync",
    "Source Code": "https://github.com/uzh-dqbm-cmi/code-sync",
}

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='code_sync',
      version='0.3.0',
      description='Sync code to a remote machine',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url=URL,
      project_urls=PROJECT_URLS,
      packages=find_packages(),
      classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Development Status :: 2 - Pre-Alpha",
            "Intended Audience :: Science/Research",
            "Topic :: Scientific/Engineering",
      ],
      python_requires='>3.6.0',
      install_requires=[
          'watchdog',
          'pyyaml',
          'argh',
      ],
      entry_points={
          'console_scripts': [
              'code_sync = code_sync.code_sync:main',
          ]
      },
      zip_safe=False)
