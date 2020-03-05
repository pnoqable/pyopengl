"""Transliteration of https://open.gl/feedback into Python"""
from __future__ import print_function
import pygamegltest
from OpenGL.GL import *

import numpy as np
import re
import sys
import time

vertex_shader = """#version 150 core
    in float inValue;
    out float outValue;

    uniform float base[baseCount];
    uniform int count;

    void main() {
        outValue = 0.;
        for( int i = 0; i < count; i++ ) {
            float result = inValue - base[i];
            if( result != 0. )
                outValue += result / result / result / result;
        }
    }
"""

@pygamegltest.pygametest(name="Geometry Shader Test")
def main( nPoints, nFrames ):

    maxBaseLen = glGetInteger( GL_MAX_VERTEX_UNIFORM_VECTORS ) * 4 - 1
    print( "baseCount on this machine: " + str( maxBaseLen ) )

    shader = glCreateShader( GL_VERTEX_SHADER )
    glShaderSource( shader, re.sub( r"\bbaseCount\b", str( maxBaseLen ), vertex_shader ) )
    glCompileShader( shader )

    if glGetShaderiv( shader, GL_COMPILE_STATUS ) != GL_TRUE:
        raise RuntimeError( glGetShaderInfoLog( shader ).decode() )

    shaderProgram = glCreateProgram()
    glAttachShader( shaderProgram, shader )

    buff = ctypes.c_char_p( b"outValue" )
    cBuff = ctypes.cast( ctypes.pointer( buff ), ctypes.POINTER( ctypes.POINTER( GLchar ) ) )
    glTransformFeedbackVaryings( shaderProgram, 1, cBuff, GL_INTERLEAVED_ATTRIBS )

    glLinkProgram( shaderProgram )
    glUseProgram( shaderProgram )

    if glGetProgramiv( shaderProgram, GL_LINK_STATUS ) != GL_TRUE:
        raise RuntimeError(  glGetProgramInfoLog( shaderProgram ).decode() )
    
    uniBase = glGetUniformLocation( shaderProgram, "base" )
    uniCount = glGetUniformLocation( shaderProgram, "count" )

    vao = glGenVertexArrays( 1 )
    glBindVertexArray( vao )

    data = np.arange( nPoints, dtype='float32' )
    print( str( data[:5] ) )
    
    vbo = glGenBuffers( 1 )
    glBindBuffer( GL_ARRAY_BUFFER, vbo )
    glBufferData( GL_ARRAY_BUFFER, data.nbytes, data, GL_DYNAMIC_DRAW )

    inputAttrib = glGetAttribLocation( shaderProgram, "inValue" )
    glEnableVertexAttribArray( inputAttrib )

    # Note the need to cast 0 to a GLvoidp here!
    glVertexAttribPointer( inputAttrib, 1, GL_FLOAT, GL_FALSE, 0, GLvoidp( 0 ) )
    
    nResults = int( np.ceil( nPoints / maxBaseLen ) )
    feedback = np.empty( ( nResults, nPoints ), dtype = 'float32' )

    tbo = glGenBuffers( 1 )
    glBindBuffer( GL_ARRAY_BUFFER, tbo )
    glBufferData( GL_ARRAY_BUFFER, feedback.nbytes, None, GL_DYNAMIC_READ )
    glBindBufferBase( GL_TRANSFORM_FEEDBACK_BUFFER, 0, tbo )

    glEnable( GL_RASTERIZER_DISCARD )

    def now():
        return time.perf_counter()

    def ms( tick, tock, ndigits = 1 ):
        return round( 1000 * ( tock - tick ), ndigits )
    
    np.set_printoptions( suppress = True )

    startTick = now()
    frameTick = startTick

    for _ in range( nFrames ):
    
        glBindBuffer( GL_ARRAY_BUFFER, vbo )
        glBufferSubData( GL_ARRAY_BUFFER, 0, data.nbytes, data )
        uploadTick = now()

        glBeginTransformFeedback(GL_POINTS)
        for base in np.array_split( data, nResults ):
            glUniform1fv( uniBase, base.shape[0], base )
            glUniform1i( uniCount, base.shape[0] )
            glDrawArrays( GL_POINTS, 0, data.shape[0] )
        glEndTransformFeedback()
        glFlush()
        transmitTick = now()

        while ms( transmitTick, now() ) < 0:
            pass # do some stuff
        cpuTick = now()

        glGetBufferSubData( GL_TRANSFORM_FEEDBACK_BUFFER, 0, feedback.nbytes, feedback.data )
        feedbackTick = now()

        delta = feedback.sum( axis = 0 ) / 1000
        print( str( delta[:5] ) )
        data[:] += delta
        print( str( data[:5] ), end = "\t" )
        sumTick = now()

        uploadTime = ms( frameTick, uploadTick )
        transmitTime = ms( uploadTick, transmitTick )
        cpuTime = ms( transmitTick, cpuTick )
        feedbackTime = ms( cpuTick,  feedbackTick )
        sumTime = ms( feedbackTick, sumTick )

        frameTock = now()
        frameTime = ms( frameTick, frameTock )
        frameTick = frameTock

        print( str( uploadTime ) + " + " + str( transmitTime ) + " + " + str( cpuTime ) + " + " +
               str( feedbackTime ) + " + " + str( sumTime ) + " ~= " + str( frameTime ) +
               "ms (" + str( round( 1000 / frameTime, 1 ) ) + "fps)" )
    
    runTime = round( ms( startTick, now() ) / 1000, 3 )
    print( str( nFrames ) + " frames / " + str( runTime ) + "s = ~" + str( round( nFrames / runTime, 1 ) ) + "fps" )
    print( "rendered in " + str( nResults ) + " chunks per frame" )
    print( "maxBaseLen: " + str( maxBaseLen ) )
    print( "feedback shape: " + str( feedback.shape ) )

if __name__ == "__main__":
    nPoints = int( sys.argv[1] ) if len( sys.argv ) > 1 else 5000
    nFrames = int( sys.argv[2] ) if len( sys.argv ) > 2 else 100
    main( nPoints, nFrames )
