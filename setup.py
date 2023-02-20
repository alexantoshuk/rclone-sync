from setuptools import setup

setup(
    name='rclone-sync',
    version='0.1.0',
    scripts=['scripts/rclone-sync.py'],
    license='Apache Software License',
    description='Monitor changes in selected local folder and sync (one-way) to selected cloud storage',
    long_description=open('README.md').read(),
    install_requires=['python-rclone', 'watchdog'],
    url='https://github.com/alexantoshuk/rclone-sync',
    author='Alexander Antoshuk',
    author_email='alexander.antoshuk@gmail.com',
)
