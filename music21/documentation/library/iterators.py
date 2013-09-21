# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:         convertIPythonNotebooksToReST.py
# Purpose:      music21 documentation IPython notebook to ReST converter
#
# Authors:      Josiah Wolf Oberholtzer
#
# Copyright:    Copyright © 2013 Michael Scott Cuthbert and the music21 Project
# License:      LGPL, see license.txt
#-------------------------------------------------------------------------------

import os
import types


class Iterator(object):

    ### INITIALIZER ###

    def __init__(self, verbose=True):
        self._verbose = verbose

    ### PUBLIC PROPERTIES ###

    @property
    def verbose(self):
        return self._verbose


class IPythonNotebookIterator(Iterator):
    '''
    Iterates over music21's documentation directory, yielding .ipynb files.
    '''

    ### SPECIAL METHODS ###

    def __call__(self):
        import music21
        rootFilesystemPath = music21.__path__[0]
        documentationPath = os.path.join(
            rootFilesystemPath,
            'documentation',
            'source',
            )
        for directoryPath, unused_directoryNames, fileNames in os.walk(
            documentationPath):
            for fileName in fileNames:
                if fileName.endswith('.ipynb'):
                    filePath = os.path.join(
                        directoryPath,
                        fileName,
                        )
                    yield filePath
        

class ModuleIterator(Iterator):
    '''
    Iterates over music21's packagesystem, yielding module objects:

    ::

        >>> iterator = documentation.ModuleIterator(verbose=False)
        >>> modules = [x for x in iterator]
        >>> for module in sorted(modules, key=lambda x: x.__name__)[:8]:
        ...     module.__name__
        ...
        'music21.abc.base'
        'music21.abc.translate'
        'music21.analysis.correlate'
        'music21.analysis.discrete'
        'music21.analysis.metrical'
        'music21.analysis.neoRiemannian'
        'music21.analysis.patel'
        'music21.analysis.reduceChords'

    '''

    ### CLASS VARIABLES ###

    _ignoredDirectoryNames = (
        'archive',
        'demos',
        'doc',
        'ext',
        'server',
        'source',
        )

    _ignoredFileNames = (
    
        # These modules will crash the module iterator if imported:

        'base-archive.py',
        'exceldiff.py',

        # These modules are now handled by the _DOC_IGNORE_MODULE_OR_PACKAGE
        # flag:
        
        #'chordTables.py',
        #'classCache.py',
        #'configure.py',
        #'phrasing.py',
        #'testFiles.py',
        #'xmlnode.py',
        )

    ### SPECIAL METHODS ###

    def __iter__(self):
        import music21
        rootFilesystemPath = music21.__path__[0]
        for directoryPath, directoryNames, fileNames in os.walk(
            rootFilesystemPath): 
            directoryNamesToRemove = []
            for directoryName in directoryNames:
                if directoryName in self._ignoredDirectoryNames:
                    directoryNamesToRemove.append(directoryName)
            for directoryName in directoryNamesToRemove:
                directoryNames.remove(directoryName)
            if '__init__.py' in fileNames:
                strippedPath = directoryPath.partition(rootFilesystemPath)[2]
                pathParts = [x for x in strippedPath.split(os.path.sep) if x]
                pathParts.insert(0, 'music21')
                packagesystemPath = '.'.join(pathParts)
                try:
                    module = __import__(packagesystemPath, fromlist=['*'])
                    if getattr(module, '_DOC_IGNORE_MODULE_OR_PACKAGE', False):
                        # Skip examining any other file or directory below
                        # this directory.
                        if self.verbose:
                            print '\tIGNORED {0}/*'.format(
                                os.path.relpath(directoryPath))
                        directoryNames[:] = []
                        continue
                except:
                    pass
            for fileName in fileNames:
                if fileName not in self._ignoredFileNames and \
                        not fileName.startswith('_') and \
                        fileName.endswith('.py'):
                    filePath = os.path.join(directoryPath, fileName)
                    strippedPath = filePath.partition(rootFilesystemPath)[2]
                    pathParts = [x for x in os.path.splitext(
                        strippedPath)[0].split(os.path.sep)[1:] if x]
                    pathParts = ['music21'] + pathParts
                    packagesystemPath = '.'.join(pathParts)
                    try:
                        module = __import__(packagesystemPath, fromlist=['*'])
                        if getattr(module, '_DOC_IGNORE_MODULE_OR_PACKAGE',
                            False):
                            if self.verbose:
                                print '\tIGNORED {0}'.format(
                                    os.path.relpath(filePath))
                            continue
                        yield module
                    except:
                        pass
        raise StopIteration


class CodebaseIterator(Iterator):
    '''
    Iterate over music21's packagesystem, yielding all classes and functions.
    '''

    ### SPECIAL METHODS ###

    def __iter__(self):
        for module in ModuleIterator(verbose=self.verbose):
            for name in dir(module):
                if name.startswith('_'):
                    continue
                named = getattr(module, name)
                validTypes = (type, types.ClassType, types.FunctionType)
                if isinstance(named, validTypes) and \
                    named.__module__ == module.__name__:
                    yield named
        raise StopIteration


class ClassIterator(Iterator):
    '''
    Iterates over music21's packagesystem, yielding all classes discovered:

    ::

        >>> iterator = documentation.ClassIterator(verbose=False)
        >>> classes = [x for x in iterator]
        >>> for cls in classes[:10]:
        ...     cls
        ... 
        <class 'music21.articulations.Accent'>
        <class 'music21.articulations.Articulation'>
        <class 'music21.articulations.ArticulationException'>
        <class 'music21.articulations.Bowing'>
        <class 'music21.articulations.BrassIndication'>
        <class 'music21.articulations.BreathMark'>
        <class 'music21.articulations.Caesura'>
        <class 'music21.articulations.DetachedLegato'>
        <class 'music21.articulations.Doit'>
        <class 'music21.articulations.DoubleTongue'>

    '''

    ### SPECIAL METHODS ###

    def __iter__(self):
        for x in CodebaseIterator(verbose=self.verbose):
            if isinstance(x, (type, types.ClassType)):
                yield x
        raise StopIteration


class FunctionIterator(Iterator):
    '''
    Iterates over music21's packagesystem, yielding all functions discovered:

    ::

        >>> iterator = documentation.FunctionIterator(verbose=False)
        >>> functions = [x for x in iterator]
        >>> for function in sorted(functions,
        ...     key=lambda x: (x.__module__, x.__name__))[:10]:
        ...     function.__module__, function.__name__
        ... 
        ('music21.abc.base', 'mergeLeadingMetaData')
        ('music21.abc.translate', 'abcToStreamOpus')
        ('music21.abc.translate', 'abcToStreamPart')
        ('music21.abc.translate', 'abcToStreamScore')
        ('music21.abc.translate', 'reBar')
        ('music21.analysis.discrete', 'analyzeStream')
        ('music21.analysis.metrical', 'labelBeatDepth')
        ('music21.analysis.metrical', 'thomassenMelodicAccent')
        ('music21.analysis.neoRiemannian', 'L')
        ('music21.analysis.neoRiemannian', 'LRP_combinations')

    '''
    
    ### SPECIAL METHODS ###

    def __iter__(self):
        for x in CodebaseIterator(verbose=self.verbose):
            if isinstance(x, types.FunctionType):
                yield x
        raise StopIteration


if __name__ == '__main__':
    import music21
    music21.mainTest()

