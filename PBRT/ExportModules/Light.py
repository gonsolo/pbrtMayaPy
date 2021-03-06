# ------------------------------------------------------------------------------
# PBRT exporter - python  plugin for Maya by Vladimir (Volodymyr) Kazantsev
# 2013
#
# Based on a Python LuxMaya translation by Doug Hammond, in turn base on translation of the c++ luxmaya exporter, 
# in turn based on original maya-pbrt c++ exporter by Mark Colbert
#
# This file is licensed under the GPL (the original exporter uses that license)
# http://www.gnu.org/licenses/gpl-3.0.txt
#
# $Id$
#
# ------------------------------------------------------------------------------
#
# lights export module
#
# ------------------------------------------------------------------------------

import math
from maya import OpenMaya

# uncomment for interactive development
# import ExportModule
# reload(ExportModule)
from ExportModule import ExportModule

class Light(ExportModule):
    """
    Light ExportModule base class. This is primarily a factory for returning
    various light types.
    """
    
    @staticmethod
    def LightFactory( fileHandle, dagPath ):
        """
        Detect the given light type and return a corresponding light object
        """
        
        nodeType = dagPath.node().apiType()

        #print("gonzo: LightFactory: nodeType: " + str(nodeType))
        #OpenMaya.MGlobal.displayInfo( "LightFactory: nodeType: " + str(nodeType) )
        
        OpenMaya.MGlobal.displayInfo('Node tyPpe: {:d}.format(nodeType)')

        if nodeType == OpenMaya.MFn.kSpotLight:
            return SpotLight( fileHandle, dagPath )
        elif nodeType == OpenMaya.MFn.kPointLight:
            return PointLight( fileHandle, dagPath )
        elif nodeType == OpenMaya.MFn.kDirectionalLight:
            return DistantLight( fileHandle, dagPath )
        elif nodeType == OpenMaya.MFn.kAreaLight:
            OpenMaya.MGlobal.displayInfo( "Found area light" )
            return AreaLight( fileHandle, dagPath )

        else:
            OpenMaya.MGlobal.displayWarning("Light type %i not supported" % nodeType)
            return False


    @staticmethod
    def LightFactoryArnold( fileHandle, dagPath ):

        node = OpenMaya.MFnDagNode(dagPath)
        if(node.name() == "aiAreaLight1"):
	    print("Returning Arnold")
            return ArnoldAreaLight( fileHandle, dagPath )
        else:
	    print("Found other node: " + node.name())
            return False

    @staticmethod
    def defaultLighting():
        return """
        AttributeBegin
        CoordSysTransform "camera"
        LightSource "distant" "color I" [ .7 .7 .5 ] "point from" [0 0 0] "point to" [1.0 -1.0 1.0]
        LightSource "distant" "color I" [ .2 .2 .35 ] "point from" [0 0 0] "point to" [0.0 0.0 1.0]
        AttributeEnd

        """
    
    def getOutput(self):
        """
        Nothing to do here, child classes output light type specific syntax.
        """
        pass


class AreaLight(Light):
    """
    Area light type.
    """

    light = OpenMaya.MFnAreaLight()

    def __init__( self, fileHandle, dagPath ):

        self.fileHandle = fileHandle
        self.dagPath = dagPath
        self.light = OpenMaya.MFnAreaLight( dagPath )

    def getOutput(self):

        color = self.light.color()
        intensity = self.light.intensity()

        colorR = self.rgcAndClamp( color.r * intensity )
        colorG = self.rgcAndClamp( color.g * intensity )
        colorB = self.rgcAndClamp( color.b * intensity )
 
        self.addToOutput( '# Area Light ' + self.dagPath.fullPathName() )
        self.addToOutput( 'AttributeBegin' )
        self.addToOutput( self.translationMatrix( self.dagPath ) )

        samples = self.light.numShadowSamples()

        self.addToOutput( '\tAreaLightSource "diffuse" "integer samples" %i "rgb L" [%f %f %f]' % (samples, colorR, colorG, colorB) )

        self.addToOutput( '\tShape "trianglemesh"')
        self.addToOutput( '\t\t"point P"         [ -1 -1   0   1 -1   0      1 1  0   -1 1  0 ]')
        self.addToOutput( '\t\t"normal N"        [  0  0  -1   0  0  -1      0 0 -1    0 0 -1 ]')
        self.addToOutput(' \t\t"integer indices" [  0  1   2   0  2   3 ]')

        self.addToOutput( 'AttributeEnd' )
        self.addToOutput( '' )
 
        self.fileHandle.flush()

class ArnoldAreaLight(Light):

    light = None

    def __init__( self, fileHandle, dagPath ):

	print("Arnold init")
	self.fileHandle = fileHandle
	self.dagPath = dagPath
	#self.light = OpenMaya.MPxLocatorNode( dagPath )

    def getOutput(self):

	print("Arnold getOutput")
        self.addToOutput( '# Arnold Area Light ' + self.dagPath.fullPathName() )
        self.addToOutput( 'AttributeBegin' )
        self.addToOutput( self.translationMatrix( self.dagPath ) )

	#color = self.dagPath.color()
	#intensity = self.dagPath.intensity()

	colorR = 1
	colorG = 1
	colorB = 1
	intensity = 20

        #colorR = self.rgcAndClamp( color.r * intensity )
        #colorG = self.rgcAndClamp( color.g * intensity )
        #colorB = self.rgcAndClamp( color.b * intensity )


        samples = 1

        self.addToOutput( '\tAreaLightSource "diffuse" "integer samples" %i "rgb L" [%f %f %f]' % (samples, colorR, colorG, colorB) )

        self.addToOutput( '\tShape "cylinder"')

        self.addToOutput( 'AttributeEnd' )
        self.addToOutput( '' )
 
        self.fileHandle.flush()


class DistantLight(Light):
    """
    Distant light type.
    """

    light = OpenMaya.MFnDirectionalLight()
    
    def __init__( self, fileHandle, dagPath ):
        """
        Constructor. Sets up this object's data.
        """
        
        self.fileHandle = fileHandle
        self.dagPath = dagPath
        self.light = OpenMaya.MFnDirectionalLight( dagPath )

    def getOutput(self):
        """
        Return LightSource "distant" from the given directional node.
        """

        color = self.light.color()
        intensity = self.light.intensity()
        
        colorR = self.rgcAndClamp( color.r * intensity )
        colorG = self.rgcAndClamp( color.g * intensity )
        colorB = self.rgcAndClamp( color.b * intensity )
    
        self.addToOutput( '# Directional Light ' + self.dagPath.fullPathName() )
        self.addToOutput( 'AttributeBegin' )
        self.addToOutput( self.translationMatrix( self.dagPath ) )
        self.addToOutput( '\tLightSource "distant"' )
        self.addToOutput( '\t\t"color L" [%f %f %f]' % (colorR, colorG, colorB) )
        self.addToOutput( '\t\t"point from" [0 0 0]')
        self.addToOutput( '\t\t"point to" [0 0 -1]' )
        self.addToOutput( 'AttributeEnd' )
        self.addToOutput( '' )
        
        self.fileHandle.flush()
        

class SpotLight(Light):
    """
    Spot light type.
    """

    light = OpenMaya.MFnSpotLight()
    
    def __init__( self, fileHandle, dagPath ):
        """
        Constructor. Sets up this object's data.
        """
        
        self.fileHandle = fileHandle
        self.dagPath = dagPath
        self.light = OpenMaya.MFnSpotLight( dagPath )
        
    def rad2degree(self, rad):
        return rad * 180 / math.pi

    def getOutput(self):
        """
        Return PBRT LightSource "spot" from the given spotlight node.
        """
        
        color = self.light.color()
        intensity = self.light.intensity()
        
        colorR = self.rgcAndClamp( color.r * intensity )
        colorG = self.rgcAndClamp( color.g * intensity )
        colorB = self.rgcAndClamp( color.b * intensity )
    
        self.addToOutput( '# Spot Light ' + self.dagPath.fullPathName() )
        self.addToOutput( 'AttributeBegin' )
        self.addToOutput( self.translationMatrix( self.dagPath ) )
        self.addToOutput( '\tLightSource "spot"' )
        self.addToOutput( '\t\t"color I" [%f %f %f]' % (colorR, colorG, colorB) )
        self.addToOutput( '\t\t"point from" [0 0 0]')
        self.addToOutput( '\t\t"point to" [0 0 -1]' )
        self.addToOutput( '\t\t"float coneangle" [%f]' % ( self.rad2degree(self.light.coneAngle()) / 2 ))
        self.addToOutput( '\t\t"float conedeltaangle" [%f]' % ( self.rad2degree(self.light.dropOff()) / 2 ))
        self.addToOutput( 'AttributeEnd' )
        self.addToOutput( '' )

        self.fileHandle.flush()


class PointLight(Light):
    """
    Point light type.
    """
    
    light = OpenMaya.MFnPointLight()

    def __init__( self, fileHandle, dagPath ):
        """
        Constructor. Sets up this object's data.
        """
        
        self.fileHandle = fileHandle
        self.dagPath = dagPath
        self.light = OpenMaya.MFnPointLight( dagPath )

    def getOutput(self):
        """
        Export Maya Point Light as pbrt's LightSource "point" 
        """
        
        color = self.light.color()
        intensity = self.light.intensity()
        
        colorR = self.rgcAndClamp( color.r * intensity )
        colorG = self.rgcAndClamp( color.g * intensity )
        colorB = self.rgcAndClamp( color.b * intensity )
        
        self.addToOutput( '# Point Light ' + self.dagPath.fullPathName() )
        self.addToOutput( 'AttributeBegin' )
        self.addToOutput( self.translationMatrix( self.dagPath ) )
        self.addToOutput( '\tLightSource "point"' )
        self.addToOutput( '\t\t"color I" [%f %f %f]' % (colorR, colorG, colorB) )
        self.addToOutput( 'AttributeEnd' )
        self.addToOutput( '' )
