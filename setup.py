from setuptools import setup, find_packages

packages = find_packages()

setup(
    name='ginger_auth',  # Replace with your package name
    version='0.0.1',  # Replace with your package version
    author='py-react',  # Replace with your name
    author_email='yksandeep08+reactpy@gmail.com',  # Replace with your email
    description='Auth Helper for gingerJs',  # Replace with a short description
    long_description=open('readme.md').read(),  # Ensure you have a README.md file
    long_description_content_type='text/markdown',  # Use 'text/x-rst' if your README is in reStructuredText
    url='https://github.com/ginger-society/ginger-js',  # Replace with the URL of your package's repository
    packages=packages,  # Automatically find and include your packages
    classifiers=[
        'License :: OSI Approved :: MIT License',  # Replace with your license
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.11.0',  # Specify the minimum Python version required
    install_requires=[
        # List your package dependencies here, e.g.:
    ],
    include_package_data=True,  # Include additional files specified in MANIFEST.in
)
