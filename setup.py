from setuptools import setup


requirements = ["aioredis>=1.3.1"]
with open("README.md", "r") as fh:
	long_description = fh.read()

setup(name='pymockache',
      version='0.0.1',
      description='Caching for separated functions',
      long_description=long_description,
      long_description_content_type="text/markdown",
      packages=['pymockache'],
      install_requires=requirements,
      author_email='kirill.s.job@gmail.com',
      classifiers=[
            "Programming Language :: Python :: 3.7",
      ],
      python_requires='>=3.7')