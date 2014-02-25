import os
import shutil
import subprocess
import urllib2

from distutils.command.build_ext import build_ext as _build_ext
from distutils.core import setup, Extension


DEFAULT_DISCOUNT_VERSION = '2.1.6'


DEFAULT_DISCOUNT_DOWNLOAD_URL = (
    'http://github.com/Orc/discount/tarball/v%s'
) % DEFAULT_DISCOUNT_VERSION


DEFAULT_DISCOUNT_CONFIGURE_OPTS = (
    # DL tag extension
    '--enable-dl-tag '

    # Use pandoc-style header blocks
    '--enable-pandoc-header '

    # A^B becomes A<sup>B</sup>
    '--enable-superscript '

    # Set tabstops to N characters (default is 4)
    '--with-tabstops=4 '

    # Enable >%id% divisions
    '--enable-div '

    # Enable (a)/(b)/(c) lists
    '--enable-alpha-list '

    # Enable memory allocation debugging
    # '--enable-amalloc '

    # Turn on all stable optional features
    # '--enable-all-features '

    # Build shared library
    '--shared '
)


class build_ext(_build_ext):
    user_options = _build_ext.user_options + [
        ('discount-src-path=', None,
         'Path to discount source files.'),

        ('discount-download-url=', None,
         'Download url of the discount source files.'),

        ('discount-configure-opts=', None,
         'Default options passed to ./configure.sh'),
    ]

    def initialize_options(self):
        _build_ext.initialize_options(self)
        self.discount_src_path = None
        self.discount_download_url = DEFAULT_DISCOUNT_DOWNLOAD_URL
        self.discount_configure_opts = DEFAULT_DISCOUNT_CONFIGURE_OPTS

    def build_extension(self, ext):
        if self.discount_src_path is None:
            filepath = os.path.join(self.build_temp, 'discount.tar.gz')
            if not os.path.lexists(self.build_temp):
                os.makedirs(self.build_temp)

            if not os.path.exists(filepath):
                print 'Downloading %s...' % self.discount_download_url

                data = urllib2.urlopen(self.discount_download_url)
                fp = open(filepath, 'wb')
                fp.write(data.read())
                fp.close()

            print 'Extracting %s...' % filepath

            subprocess.call(
                ['tar', 'xzf', filepath, '-C', self.build_temp]
            )

            # find extracted source dir
            for name in os.listdir(self.build_temp):
                candidate_path = os.path.join(self.build_temp, name)
                if (os.path.isdir(candidate_path) and
                    os.path.exists(os.path.join(candidate_path, 'markdown.h'))):
                    discount_src_path = candidate_path

        else:
            discount_src_path = self.discount_src_path

        current_dir = os.getcwd()
        os.chdir(discount_src_path)
        subprocess.call(
            ['./configure.sh',] + self.discount_configure_opts.split(),
            env=os.environ
        )
        subprocess.call(['make',], env=os.environ)
        os.chdir(current_dir)
        shutil.copy(
            os.path.realpath(os.path.join(discount_src_path, 'libmarkdown')),
            self.get_ext_fullpath(ext.name),
        )
        

setup(
    name='discount',
    license='BSD',
    version='0.2.1STABLE',

    author='Trapeze',
    author_email='tkemenczy@trapeze.com',
    url="http://github.com/trapeze/python-discount",
    download_url='http://pypi.python.org/pypi/discount',
    description='A Python interface for Discount, the C Markdown parser',
    long_description=open('README.rst').read(),
    keywords='markdown discount ctypes',

    provides=[
        'discount',
    ],

    py_modules=[
        'discount',
        'discount.libmarkdown',
    ],

    ext_modules=[
        Extension(
            '_discount',
            sources=[],
        )
    ],

    cmdclass={
        'build_ext': build_ext
    },

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: C',
        'Programming Language :: Python',
        'Topic :: Text Processing :: Markup'
    ],
)
