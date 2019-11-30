import os
from conans import CMake, ConanFile, tools


class ConanVst3(ConanFile):
    name = 'vst3'
    description = 'Steinberg VST Plug-in interface'
    homepage = 'https://www.steinberg.net/en/company/developers.html'
    url = 'https://github.com/steinbergmedia/vst3sdk'
    license = 'Proprietary Steinberg VST3 License'
    topics = ('audio', 'plugin', 'vst', 'vst3')

    exports_sources = ['CMakeLists.txt']
    generators = 'cmake'
    settings = ('arch', 'build_type', 'compiler', 'os')
    options = {
        'fPIC': [True, False],
        'shared': [True, False],
    }
    default_options = {
        'fPIC': True,
        'shared': False,
    }

    _source_subfolder = 'source_subfolder'
    _build_subfolder = 'build_subfolder'


    def config_options(self):
        """ Set the OS-specific configuration options """
        if self.settings.os == 'Windows':
            self.options.remove('fPIC')


    def configure(self):
        """ Set the compiler settings """
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx


    def source(self):
        """ Get the remote sources and store them in the local source directory """
        repo = self.conan_data['sources'][self.version]
        git = tools.Git(folder=_source_subfolder)
        git.clone(url=repo['url'], branch=repo['tag'], args='--recursive', shallow=True)


    def _configure_cmake(self):
        """ Set the cmake configuration """
        cmake = CMake(self)
        cmake.configure(build_folder=self._build_subfolder)
        return cmake


    def build(self):
        """  """
        cmake = self._configure_cmake()
        cmake.build()


    def package(self):
        """  """
        cmake = self._configure_cmake()
        cmake.install()

        self.copy(pattern='COPYING', src=self._source_subfolder, dst='licenses', keep_path=False)

        tools.rmdir(os.path.join(self.package_folder, 'lib', 'cmake'))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))
        tools.rmdir(os.path.join(self.package_folder, 'share'))


    def package_info(self):
        """  """
        self.cpp_info.libs = tools.collect_libs(self)
