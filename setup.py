from setuptools import setup, find_packages

setup(
    name='BERTransfer',
    version='0.1.0',
    description='A Python package for topic transfer based on BERTopic',
    author='Pierre-Carl Langlais',
    url='https://github.com/opinionscience/BERTransfer',
    packages=find_packages(),
    install_requires=[
        'numpy', 'pandas', 'bertopic', 'sentence_transformers'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
