from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='supervisor-shell-ui',
    version='v0.2.6',
    author='Ciprian Mandache',
    author_email='psyb0t@51k.eu',
    description='A CLI alternative to the built-in web interface of Supervisor, offering a more convenient way to manage processes directly from the terminal.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires='>=3.6',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'supervisor-shell-ui=supervisor_shell_ui.main:main',
        ],
    },
    license='GPL-3.0',
)
