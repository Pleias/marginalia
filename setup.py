from setuptools import setup, find_packages

setup(
    name='Vllm-json',
    version='0.1.0',
    description='A Python package for structured annotation at scale with LLM',
    author='Pierre-Carl Langlais',
    url='https://github.com/Pleias/vllm-json',
    packages=find_packages(),
    install_requires=[
        'vllm'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11'
    ],
)
