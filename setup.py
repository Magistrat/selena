from setuptools import setup  # type: ignore


with open('requirements.txt', 'r', encoding='UTF-8') as f:
    requirements = f.read().split()


VERSION = '1.0.7'
DESCRIPTION = 'Python-пакет для работы над Selenium'


setup(
    name='custom_selenium_qa',
    version=VERSION,
    author='Nistratov Konstantin',
    author_email='k.nistratov@keyauto.ru',
    url='https://github.com/Magistrat/selena.git',
    keywords='python selenium QA',
    description=DESCRIPTION,
    long_description=DESCRIPTION,
    long_description_content_type='text/markdown',
    packages=['custom_selenium_qa'],
    install_requires=requirements,
    classifiers=[
        'Natural Language :: Russian',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.8',
    project_urls={
        'GitLab': 'https://github.com/Magistrat/selena.git',
        'Changes': 'https://github.com/Magistrat/selena/-/blob/main/CHANGELOG.txt',
    },
)
