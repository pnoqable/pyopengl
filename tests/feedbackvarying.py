"""Transliteration of https://open.gl/feedback into Python"""
from __future__ import print_function
import pygamegltest
from OpenGL.GL import *

import numpy as np
import re
import sys
import time

shaderSource = """#version 150 core
    uniform int baseCount;
    uniform Base {
        vec4 base[maxBaseCount];
    };

    in vec4 inValue;
    out vec4 outValue;

    void main() {
        outValue = vec4( 0., 0., 0., 0. );
        for( int i = 0; i < baseCount; i++ ) {
            vec4 result = inValue - base[i];
            float sqrLen = dot( result, result );
            if( sqrLen != 0. )
                outValue += result / sqrt( sqrLen ) / sqrLen;
        }
    }
"""

shaderSource2 = """#version 150 core
    uniform int summandsCount;

    in vec4 inValue;
    in vec4 summands[maxSummandsCount];
    out vec4 sum;
    out vec4 outValue;

    void main() {
        sum = vec4( 0. );
        for( int i = 0; i < summandsCount; i++ ) {
            sum += summands[i];
        }
        sum /= 1000.;
        outValue = inValue + sum;
    }
"""

def buildShader( source, constants = {}, feedbackVaryings = [] ):

    for name, value in constants.items():
        source = re.sub( name, str( value ), source )
    
    shader = glCreateShader( GL_VERTEX_SHADER )
    glShaderSource( shader, source )
    glCompileShader( shader )

    if glGetShaderiv( shader, GL_COMPILE_STATUS ) != GL_TRUE:
        raise RuntimeError( glGetShaderInfoLog( shader ).decode() )

    program = glCreateProgram()
    glAttachShader( program, shader )

    buff = ( ctypes.c_char_p * len( feedbackVaryings ) )()
    buff[:] = [ string.encode( "utf-8" ) for string in feedbackVaryings ]
    cBuff = ctypes.cast( buff, ctypes.POINTER( ctypes.POINTER( GLchar ) ) )
    glTransformFeedbackVaryings( program, len( buff ), cBuff, GL_SEPARATE_ATTRIBS )

    glLinkProgram( program )
    glUseProgram( program )

    if glGetProgramiv( program, GL_LINK_STATUS ) != GL_TRUE:
        raise RuntimeError(  glGetProgramInfoLog( program ).decode() )
    
    return program

@pygamegltest.pygametest(name="Geometry Shader Test")
def main( nPoints, nFrames ):

    maxBaseCount = glGetInteger( GL_MAX_VERTEX_UNIFORM_VECTORS ) - 1
    print( "maxBaseCount on this machine: " + str( maxBaseCount ) )

    maxSummandsCount = glGetInteger( GL_MAX_VARYING_VECTORS ) - 1
    print( "maxSummandsCount on this machine: " + str( maxSummandsCount ) )

    summandsCount = int( np.ceil( nPoints / maxBaseCount ) )
    assert summandsCount <= maxSummandsCount

    # set up shader

    shaderProgram = buildShader( shaderSource, { "maxBaseCount" : maxBaseCount }, [ "outValue" ] )
    uniBaseCount = glGetUniformLocation( shaderProgram, "baseCount" )
    baseIndex = glGetUniformBlockIndex( shaderProgram, "Base" )

    vao = glGenVertexArrays( 1 )
    glBindVertexArray( vao )

    data = np.arange( 3 * nPoints, dtype='float32' ).reshape( ( nPoints, 3 ) )
    data = np.insert( data, 3, 0., axis = 1 )
    
    vbo = glGenBuffers( 1 )
    glBindBuffer( GL_ARRAY_BUFFER, vbo )
    glBufferData( GL_ARRAY_BUFFER, data.nbytes, data, GL_DYNAMIC_DRAW )

    inputAttrib = glGetAttribLocation( shaderProgram, "inValue" )
    glEnableVertexAttribArray( inputAttrib )
    glVertexAttribPointer( inputAttrib, 4, GL_FLOAT, GL_FALSE, 0, GLvoidp( 0 ) )
    
    summands = np.zeros( ( summandsCount, nPoints, 4 ), dtype = 'float32' )

    tbo = glGenBuffers( 1 )
    glBindBuffer( GL_TRANSFORM_FEEDBACK_BUFFER, tbo )
    glBufferData( GL_TRANSFORM_FEEDBACK_BUFFER, summands.nbytes, None, GL_DYNAMIC_READ )

    # set up shader 2

    shaderProgram2 = buildShader( shaderSource2, { "maxSummandsCount" : maxSummandsCount }, [ "sum", "outValue" ] )
    uniSummandsCount = glGetUniformLocation( shaderProgram2, "summandsCount" )
    glUniform1i( uniSummandsCount, summandsCount )

    vao2 = glGenVertexArrays( 1 )
    glBindVertexArray( vao2 )

    glBindBuffer( GL_ARRAY_BUFFER, vbo )
    inputAttrib = glGetAttribLocation( shaderProgram2, "inValue" )
    glEnableVertexAttribArray( inputAttrib )
    glVertexAttribPointer( inputAttrib, 4, GL_FLOAT, GL_FALSE, 0, GLvoidp( 0 ) )

    glBindBuffer( GL_ARRAY_BUFFER, tbo )
    for i in range( summandsCount ):
        inputAttrib = glGetAttribLocation( shaderProgram2, "summands[" + str( i ) + "]" )
        glEnableVertexAttribArray( inputAttrib )
        glVertexAttribPointer( inputAttrib, 4, GL_FLOAT, GL_FALSE, 0, GLvoidp( summands[:i].nbytes ) )
    
    # run

    glEnable( GL_RASTERIZER_DISCARD )

    def now():
        return time.perf_counter()

    def ms( tick, tock, ndigits = 1 ):
        return round( 1000 * ( tock - tick ), ndigits )
    
    np.set_printoptions( suppress = True )
    print( str( data[0] ) )

    startTick = now()
    frameTick = startTick

    for _ in range( nFrames ):
    
        glUseProgram( shaderProgram )
        glBindVertexArray( vao )
        glBindBufferBase( GL_TRANSFORM_FEEDBACK_BUFFER, 0, tbo )

        glBeginTransformFeedback( GL_POINTS )
        offset = 0
        for base in np.array_split( data, summandsCount ):
            glUniform1i( uniBaseCount, base.shape[0] )
            glUniformBlockBinding( shaderProgram, baseIndex, 0 )
            glBindBufferRange( GL_UNIFORM_BUFFER, 0, vbo, offset, base.nbytes )
            offset += base.nbytes
            glDrawArrays( GL_POINTS, 0, data.shape[0] )
        glEndTransformFeedback()
        
        glUseProgram( shaderProgram2 )
        glBindVertexArray( vao2 )
        glBindBufferBase( GL_TRANSFORM_FEEDBACK_BUFFER, 0, tbo )
        glBindBufferBase( GL_TRANSFORM_FEEDBACK_BUFFER, 1, vbo )
        
        glBeginTransformFeedback( GL_POINTS )
        glDrawArrays( GL_POINTS, 0, nPoints )
        glEndTransformFeedback()
        glFlush()

        transmitTick = now()

        while ms( transmitTick, now() ) < 0:
            pass # do some stuff
        cpuTick = now()

        glBindBuffer( GL_TRANSFORM_FEEDBACK_BUFFER, tbo )
        glGetBufferSubData( GL_TRANSFORM_FEEDBACK_BUFFER, 0, summands[0].nbytes, summands.data )
        print( str( summands[0,0,:3] ) )

        glBindBuffer( GL_TRANSFORM_FEEDBACK_BUFFER, vbo )
        glGetBufferSubData( GL_TRANSFORM_FEEDBACK_BUFFER, 0, data.nbytes, data.data )
        print( str( data[0,:3] ), end = "\t" )

        feedbackTick = now()

        transmitTime = ms( frameTick, transmitTick )
        cpuTime = ms( transmitTick, cpuTick )
        feedbackTime = ms( cpuTick,  feedbackTick )

        frameTock = now()
        frameTime = ms( frameTick, frameTock )
        frameTick = frameTock

        print( str( transmitTime ) + " + " + str( cpuTime ) + " + " + str( feedbackTime ) +
               " ~= " + str( frameTime ) + "ms (" + str( round( 1000 / frameTime, 1 ) ) + "fps)" )
    
    runTime = round( ms( startTick, now() ) / 1000, 3 )
    print( str( nFrames ) + " frames / " + str( runTime ) + "s = ~" + str( round( nFrames / runTime, 1 ) ) + "fps" )
    print( "rendered in " + str( summandsCount ) + " chunks per frame" )
    print( "maxBaseCount: " + str( maxBaseCount ) )
    print( "summands shape: " + str( summands.shape ) )

if __name__ == "__main__":
    nPoints = int( sys.argv[1] ) if len( sys.argv ) > 1 else 5000
    nFrames = int( sys.argv[2] ) if len( sys.argv ) > 2 else 100
    main( nPoints, nFrames )
