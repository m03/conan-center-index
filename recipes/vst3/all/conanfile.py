#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from conans import CMake, ConanFile, tools


class ConanVst3(ConanFile):
    name = 'vst3'
    version = '3.6.12'
    description = 'Steinberg VST Plug-in interface'
    homepage = 'https://www.steinberg.net/en/company/developers.html'
    url = 'https://github.com/steinbergmedia/vst3sdk'
    license = 'Proprietary Steinberg VST3 License'
    topics = ('audio', 'plugin', 'vst', 'vst3')

    exports_sources = ['CMakeLists.txt']
    generators = 'cmake', 'xcode'
    settings = ('arch', 'build_type', 'compiler', 'os')
    options = {
        'fPIC': [True, False],
        'shared': [True, False],
    }
    default_options = {
        'fPIC': True,
        'shared': False,
    }

    _build_folder = 'build'
    _source_folder = 'source'


    def config_options(self):
        """ Set the OS-specific configuration options """
        if self.settings.os == 'Windows':
            self.options.remove('fPIC')


    def configure(self):
        """ Set the compiler settings """
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx


    @property
    def _latest_version(self):
        """ Get the latest version from the conan data config """
        latest = self.version

        for current in self.conan_data['sources']:
            if tools.Version(current) > tools.Version(latest):
                latest = current

        return latest


    def source(self):
        """
        Get the remote sources and store them in the local source directory.
        """
        repo = self.conan_data['sources'][self.version]

        # https://docs.conan.io/en/latest/reference/tools.html#tools-git
        git = tools.Git(folder=self._source_folder)
        git.clone(url=repo['url'], branch=repo['tag'], args='--recursive --single-branch', shallow=False)


    def _configure_cmake(self):
        """ Set the cmake configuration """
        cmake_params = dict()

        if self.settings.os == 'Macos':
            cmake_params['generator'] = 'Xcode'
            self.output.info('Using generator: %s' % cmake_params['generator'])

        cmake = CMake(self, **cmake_params)

        # Disable building the sample projects.
        cmake.definitions['SMTG_ADD_VST3_PLUGINS_SAMPLES'] = False

        cmake.configure(source_folder=self._source_folder, build_folder=self._build_folder)

        return cmake


    def build(self):
        """ Configure and run the cmake build and tests """
        cmake = self._configure_cmake()
        cmake.build()
        # cmake.test()


    def package(self):
        """ Create the package and perform any cleanup steps """
        library_path = os.path.join(self._build_folder, 'lib', str(self.settings.build_type))
        self.output.info('Using source library path: %s' % library_path)

        self.copy(pattern='LICENSE*', dst='licenses', src=self._source_folder, ignore_case=True, keep_path=False)
        self.copy(pattern='*.a', dst='lib', src=library_path, keep_path=False)
        self.copy(pattern='*.h', dst='include', src=self._source_folder, keep_path=True)


    def package_id(self):
        """ Define the settings that cause a new package ID to be generated """
        del self.info.settings.compiler


    def package_info(self):
        """ Define the build information that is provided to consumers """
        self.cpp_info.libs = tools.collect_libs(self)
        self.output.info('Package libraries: %s' % ', '.join(self.cpp_info.libs))
