from setuptools import setup, find_packages


version = __import__('dex').__version__

setup(
    name='django-dex',
    packages=find_packages(),
    include_package_data=True,
    version=version,
    description='Database export tools for Django',
    author='synw',
    author_email='synwe@yahoo.com',
    url='https://github.com/synw/django-dex',
    download_url='https://github.com/synw/django-dex/releases/tag/' + version,
    keywords=['django', 'database_export'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=[
        "goerr",
        "django-introspection",
    ],
    zip_safe=False
)
