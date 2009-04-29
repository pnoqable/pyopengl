'''OpenGL extension NV.texgen_reflection

Overview (from the spec)
	
	This extension provides two new texture coordinate generation modes
	that are useful texture-based lighting and environment mapping.
	The reflection map mode generates texture coordinates (s,t,r)
	matching the vertex's eye-space reflection vector.  The reflection
	map mode is useful for environment mapping without the singularity
	inherent in sphere mapping.  The normal map mode generates texture
	coordinates (s,t,r) matching the vertex's transformed eye-space
	normal.  The normal map mode is useful for sophisticated cube map
	texturing-based diffuse lighting models.

The official definition of this extension is available here:
	http://oss.sgi.com/projects/ogl-sample/registry/NV/texgen_reflection.txt

Automatically generated by the get_gl_extensions script, do not edit!
'''
from OpenGL import platform, constants, constant, arrays
from OpenGL import extensions
from OpenGL.GL import glget
import ctypes
EXTENSION_NAME = 'GL_NV_texgen_reflection'
GL_NORMAL_MAP_NV = constant.Constant( 'GL_NORMAL_MAP_NV', 0x8511 )
GL_REFLECTION_MAP_NV = constant.Constant( 'GL_REFLECTION_MAP_NV', 0x8512 )


def glInitTexgenReflectionNV():
	'''Return boolean indicating whether this extension is available'''
	return extensions.hasGLExtension( EXTENSION_NAME )