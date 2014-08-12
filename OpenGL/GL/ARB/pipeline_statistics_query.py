'''OpenGL extension ARB.pipeline_statistics_query

This module customises the behaviour of the 
OpenGL.raw.GL.ARB.pipeline_statistics_query to provide a more 
Python-friendly API

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/ARB/pipeline_statistics_query.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.ARB.pipeline_statistics_query import *
from OpenGL.raw.GL.ARB.pipeline_statistics_query import _EXTENSION_NAME

def glInitPipelineStatisticsQueryARB():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )


### END AUTOGENERATED SECTION