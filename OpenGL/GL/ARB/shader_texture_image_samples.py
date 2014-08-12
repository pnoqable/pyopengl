'''OpenGL extension ARB.shader_texture_image_samples

This module customises the behaviour of the 
OpenGL.raw.GL.ARB.shader_texture_image_samples to provide a more 
Python-friendly API

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/ARB/shader_texture_image_samples.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.ARB.shader_texture_image_samples import *
from OpenGL.raw.GL.ARB.shader_texture_image_samples import _EXTENSION_NAME

def glInitShaderTextureImageSamplesARB():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )


### END AUTOGENERATED SECTION