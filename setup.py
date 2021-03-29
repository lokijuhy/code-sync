from setuptools import setup, find_packages

setup(name='code_sync',
      version='0.0.1',
      description='',
      url='https://github.com/uzh-dqbm-cmi/code-sync',
      packages=find_packages(),
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
