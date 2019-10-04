from utils import *
import io

class MyModelExporter(object):
    def __init__(self, filepath):
        self.filepath = filepath
        self.m_writer = BinaryStream(io.BytesIO())
        self.m_cacheStream = None
        self.m_originalWriter = None

    def exportModelData(self, tagData, **kwargs):
        dict = {}
        debug_collection = tagData["Debug"]
        # Remove version info and replace with new version
        list = [x for x in debug_collection if 'Version:' not in x]
        list.append("Version:01157001")
        self.exportStrArray("Debug", list)
        self.startCacheWrite()

        dict["Dummies"] = self.getCachePosition()
        self.exportDict("Dummies", tagData["Dummies"])
        dict["Vertices"] = self.getCachePosition()
        self.exportHalfVector4("Vertices", tagData["Vertices"])
        dict["Normals"] = self.getCachePosition()
        self.exportByte4("Normals", tagData["Normals"])
        dict["TexCoords0"] = self.getCachePosition()
        self.exportHalfVector2("TexCoords0", tagData["TexCoords0"])
        dict["Binormals"] = self.getCachePosition()
        self.exportByte4("Binormals", tagData["Binormals"])
        dict["Tangents"] = self.getCachePosition()
        self.exportByte4("Tangents", tagData["Tangents"])
        dict["TexCoords1"] = self.getCachePosition()
        self.exportHalfVector2("TexCoords1", tagData["TexCoords1"])
        dict["RescaleFactor"] = self.getCachePosition()
        self.exportFloat("RescaleFactor", tagData["RescaleFactor"])
        dict["UseChannelTextures"] = self.getCachePosition()
        self.exportBool("UseChannelTextures", tagData["UseChannelTextures"])
        dict["BoundingBox"] = self.getCachePosition()
        self.exportBoundingBox("BoundingBox", tagData["BoundingBox"])
        dict["BoundingSphere"] = self.getCachePosition()
        self.exportBoundingSphere("BoundingSphere", tagData["BoundingSphere"])
        dict["SwapWindingOrder"] = self.getCachePosition()
        self.exportBool("SwapWindingOrder", tagData["SwapWindingOrder"])
        dict["MeshParts"] = self.getCachePosition()
        self.exportMeshParts("MeshParts", tagData["MeshParts"])
        dict["Sections"] = self.getCachePosition()
        self.exportMeshSections("Sections", tagData["Sections"])
        dict["ModelBvh"] = self.getCachePosition()
        self.exportByteArray("ModelBvh", tagData["ModelBvh"].save())
        dict["ModelInfo"] = self.getCachePosition()
        self.exportModelInfo("ModelInfo", tagData["ModelInfo"])
        dict["BlendIndices"] = self.getCachePosition()
        self.exportVector4i("BlendIndices", tagData["BlendIndices"])
        dict["BlendWeights"] = self.getCachePosition()
        self.exportVector4("BlendWeights", tagData["BlendWeights"])
        dict["Animations"] = self.getCachePosition()
        animdata = kwargs.get('animdata', False)
        if animdata:
            self.m_writer.writeBytes(animdata)
        else:
            self.exportModelAnimations("Animations", tagData["Animations"])
        dict["Bones"] = self.getCachePosition()
        self.exportModelBones("Bones", tagData["Bones"])
        dict["BoneMapping"] = self.getCachePosition()
        self.exportVector3i("BoneMapping", tagData["BoneMapping"])
        dict["HavokCollisionGeometry"] = self.getCachePosition()
        self.exportByteArray("HavokCollisionGeometry", tagData["HavokCollisionGeometry"])
        dict["PatternScale"] = self.getCachePosition()
        self.exportFloat("PatternScale", tagData["PatternScale"])
        dict["LODs"] = self.getCachePosition()
        self.exportLODDescriptor("LODs", tagData["LODs"])

        fbxhash = tagData.get("FBXHash", None)
        if fbxhash:
            dict["FBXHash"] = self.getCachePosition()
            self.exportMD5("FBXHash", fbxhash)

        hkthash = tagData.get("HKTHash", None)
        if hkthash:
            dict["HKTHash"] = self.getCachePosition()
            self.exportMD5("HKTHash", hkthash)

        xmlhash = tagData.get("XMLHash", None)
        if xmlhash:
            dict["XMLHash"] = self.getCachePosition()
            self.exportMD5("XMLHash", xmlhash)

        modelfractures = tagData.get("ModelFractures", None)
        if modelfractures:
            dict["ModelFractures"] = self.getCachePosition()
            self.exportModelFractures("ModelFractures", modelfractures)

        self.stopCacheWrite()
        self.writeIndexDictionary(dict)
        self.flushCache()
        with open(self.filepath, 'wb') as outfile:
            outfile.write(self.m_writer.base_stream.getvalue())

    def writeTag(self, tagname):
        self.m_writer.writeString7(tagname)

    def startCacheWrite(self):
        if self.m_cacheStream is not None:
            self.m_cacheStream.close()
        self.m_originalWriter = self.m_writer
        self.m_cacheStream = io.BytesIO()
        self.m_writer = BinaryStream(self.m_cacheStream)

    def stopCacheWrite(self):
        self.m_writer = self.m_originalWriter

    def getCachePosition(self):
        return self.m_writer.base_stream.tell()

    def flushCache(self):
        buffer = self.m_cacheStream.getbuffer()
        self.m_writer.writeBytes(buffer)

    def calculateIndexSize(self, dict):
        num = 4
        for key, val in dict.items():
            num += len(key.encode()) + 1
            num += 4
        return num

    def writeIndexDictionary(self, dict):
        num = self.m_writer.base_stream.tell()
        num2 = self.calculateIndexSize(dict)
        self.m_writer.writeInt32(len(dict))
        for key, val in dict.items():
            self.m_writer.writeString7(key)
            self.m_writer.writeInt32(val+num2+num)

    def exportBool(self, tagname, val):
        self.writeTag(tagname)
        self.m_writer.writeBool(val)

    def exportFloat(self, tagname, flt):
        self.writeTag(tagname)
        self.m_writer.writeFloat(flt)
        return True

    def exportByteArray(self, tagname, bytearr):
        self.writeTag(tagname)
        if not bytearr:
            self.m_writer.writeInt32(0)
            return True
        self.m_writer.writeInt32(len(bytearr))
        self.m_writer.writeBytes(bytearr)
        return True

    def exportModelInfo(self, tagname, modelinfo):
        self.writeTag(tagname)
        self.m_writer.writeInt32(modelinfo.tri_count)
        self.m_writer.writeInt32(modelinfo.vert_count)
        self.writeVector3(modelinfo.bounding_box_size)
        return True

    def exportModelAnimations(self, tagname, animations):
        print('WRITING ANIMATIONS')
        self.writeTag(tagname)
        self.m_writer.writeInt32(len(animations.clips))
        for clip in animations.clips:
            print(clip.name)
            print(clip.duration)
            print([x.name for x in clip.bones])
            self.writeAnimationClip(clip)
        self.m_writer.writeInt32(len(animations.skeleton))
        for val in animations.skeleton:
            self.m_writer.writeInt32(val)
        return True

    def exportModelBones(self, tagname, bones):
        self.writeTag(tagname)
        self.m_writer.writeInt32(len(bones))
        for bone in bones:
            self.m_writer.writeString7(bone.name)
            self.m_writer.writeInt32(bone.parent)
            self.writeMatrix(bone.transform)
        return True

    def exportMeshParts(self, tagname, lst):
        self.writeTag(tagname)
        self.m_writer.writeInt32(len(lst))
        for meshpart in lst:
            meshpart.Export(self.m_writer)
        return True

    def exportMeshSections(self, tagname, lst):
        self.writeTag(tagname)
        self.m_writer.writeInt32(len(lst))
        for meshsection in lst:
            meshsection.Export(self.m_writer)
        return True

    def exportLODDescriptor(self, tagname, lods):
        self.writeTag(tagname)
        self.m_writer.writeInt32(len(lods))
        for lod in lods:
            lod.write(self.m_writer)
        return True

    def exportBoundingBox(self, tagname, boundingbox):
        self.writeTag(tagname)
        self.writeVector3(boundingbox.min)
        self.writeVector3(boundingbox.max)
        return True

    def exportBoundingSphere(self, tagname, boundingsphere):
        self.writeTag(tagname)
        self.writeVector3(boundingsphere.centre)
        self.m_writer.writeFloat(boundingsphere.radius)

    def exportModelFractures(self, tagname, model_fractures):
        self.writeTag(tagname)
        self.m_writer.writeInt32(model_fractures.version)
        self.m_writer.writeInt32(len(model_fractures.fractures))
        for fracture_settings in model_fractures:
            if type(fracture_settings) == RandomSplitFractureSettings:
                self.m_writer.writeString7("RandomSplit")
                self.m_writer.writeInt32(fracture_settings.num_object_level_1)
                self.m_writer.writeInt32(fracture_settings.num_object_level_2)
                self.m_writer.writeFloat(fracture_settings.random_range)
                self.m_writer.writeInt32(fracture_settings.random_seed_1)
                self.m_writer.writeInt32(fracture_settings.random_seed_2)
                self.m_writer.writeString7(fracture_settings.split_plane)
            elif type(fracture_settings) == VoronoiFractureSettings:
                self.m_writer.writeString7("Voronoi")
                self.m_writer.writeInt32(fracture_settings.seed)
                self.m_writer.writeInt32(fracture_settings.num_sites_to_generate)
                self.m_writer.writeInt32(fracture_settings.num_iterations)
                self.m_writer.writeString7(fracture_settings.split_plane)
            elif type(fracture_settings) == WoodFractureSettings:
                self.m_writer.writeString7("WoodFracture")
                self.m_writer.writeBool(fracture_settings.board_custom_splitting_plane_axis)
                self.m_writer.writeFloat(fracture_settings.board_fracture_line_shearing_range)
                self.m_writer.writeFloat(fracture_settings.board_fracture_normal_shearing_range)
                self.m_writer.writeInt32(fracture_settings.board_num_subparts)
                self.m_writer.writeInt32(fracture_settings.board_rotate_split_geom)
                self.writeVector3(fracture_settings.board_scale)
                self.writeVector3(fracture_settings.board_scale_range)
                self.m_writer.writeFloat(fracture_settings.board_split_geom_shift_range_y)
                self.m_writer.writeFloat(fracture_settings.board_split_geom_shift_range_z)
                self.writeVector3(fracture_settings.board_splitting_axis)
                self.m_writer.writeString7(fracture_settings.board_splitting_plane)
                self.m_writer.writeFloat(fracture_settings.board_surface_normal_shearing_range)
                self.m_writer.writeFloat(fracture_settings.board_width_range)
                self.m_writer.writeBool(fracture_settings.splinter_custom_splitting_plane_axis)
                self.m_writer.writeFloat(fracture_settings.splinter_fracture_line_shearing_range)
                self.m_writer.writeFloat(fracture_settings.splinter_fracture_normal_shearing_range)
                self.m_writer.writeInt32(fracture_settings.splinter_num_subparts)
                self.m_writer.writeInt32(fracture_settings.splinter_rotate_split_geom)
                self.writeVector3(fracture_settings.splinter_scale)
                self.writeVector3(fracture_settings.splinter_scale_range)
                self.m_writer.writeFloat(fracture_settings.splinter_split_geom_shift_range_Y)
                self.m_writer.writeFloat(fracture_settings.splinter_split_geom_shift_range_z)
                self.writeVector3(fracture_settings.splinter_splitting_axis)
                self.m_writer.writeString7(fracture_settings.splinter_splitting_plane)
                self.m_writer.writeFloat(fracture_settings.splinter_surface_normal_shearing_range)
                self.m_writer.writeFloat(fracture_settings.splinter_width_range)

    def exportStrArray(self, tagname, array):
        self.writeTag(tagname)
        if not array:
            self.m_writer.writeInt32(0)
            return True
        self.m_writer.writeInt32(len(array))
        for val in array:
            self.m_writer.writeString7(str(val))
        return True

    def exportDict(self, tagname, dict):
        self.writeTag(tagname)
        self.m_writer.writeInt32(len(dict))
        for key, val in dict.items():
            self.m_writer.writeString7(key)
            self.writeMatrix(val.matrix)
            self.m_writer.writeInt32(len(val.customdata))
            for key2, val2 in val.customdata.items():
                self.m_writer.writeString7(key2)
                self.m_writer.writeString7(str(val2))
        return True

    def exportMD5(self, tagname, hash):
        self.writeTag(tagname)
        self.m_writer.writeBytes(hash)

    def exportHalfVector2(self, tagname, vctArr):
        self.writeTag(tagname)
        if vctArr is None:
            self.m_writer.writeInt32(0)
            return True
        self.m_writer.writeInt32(len(vctArr))
        for val in vctArr:
            self.writeHalfVector2(val)
        return True

    def exportHalfVector4(self, tagname, vctArr):
        self.writeTag(tagname)
        if vctArr is None:
            self.m_writer.writeInt32(0)
            return True
        self.m_writer.writeInt32(len(vctArr))
        for val in vctArr:
            self.writeHalfVector4(val)
        return True

    def exportVector4(self, tagname, vctArr):
        self.writeTag(tagname)
        if vctArr is None:
            self.m_writer.writeInt32(0)
            return True
        self.m_writer.writeInt32(len(vctArr))
        for vct in vctArr:
            self.writeVector4(vct)
        return True

    def exportVector4i(self, tagname, vctArr):
        if vctArr is None:
            return True
        self.writeTag(tagname)
        self.m_writer.writeInt32(len(vctArr))
        for vct in vctArr:
            self.writeVector4i(vct)
        return True

    def exportVector3i(self, tagname, vctArr):
        if vctArr is None:
            return True
        self.writeTag(tagname)
        self.m_writer.writeInt32(len(vctArr))
        for vct in vctArr:
            self.writeVector3i(vct)
        return True

    def exportByte4(self, tagname, vctArr):
        self.writeTag(tagname)
        if not vctArr:
            self.m_writer.writeInt32(0)
            return True
        self.m_writer.writeInt32(len(vctArr))
        for val in vctArr:
            self.writeByte4(val)
        return True

    def writeByte4(self, val):
        self.m_writer.writeUInt32(val.packed_value)

    def writeHalfVector2(self, val):
        self.m_writer.writeUInt32(val.packed_value)

    def writeHalfVector4(self, val):
        self.m_writer.writeUInt64(val.packed_value)

    def writeVector3(self, val):
        self.m_writer.writeFloat(val.x)
        self.m_writer.writeFloat(val.y)
        self.m_writer.writeFloat(val.z)

    def writeVector4(self, vct):
        self.m_writer.writeFloat(vct.x)
        self.m_writer.writeFloat(vct.y)
        self.m_writer.writeFloat(vct.z)
        self.m_writer.writeFloat(vct.w)

    def writeVector4i(self, vct):
        self.m_writer.writeInt32(vct.x)
        self.m_writer.writeInt32(vct.y)
        self.m_writer.writeInt32(vct.z)
        self.m_writer.writeInt32(vct.w)

    def writeVector3i(self, vct):
        self.m_writer.writeInt32(vct.x)
        self.m_writer.writeInt32(vct.y)
        self.m_writer.writeInt32(vct.z)

    def writeMatrix(self, matrix):
        self.m_writer.writeFloat(matrix.M11)
        self.m_writer.writeFloat(matrix.M12)
        self.m_writer.writeFloat(matrix.M13)
        self.m_writer.writeFloat(matrix.M14)
        self.m_writer.writeFloat(matrix.M21)
        self.m_writer.writeFloat(matrix.M22)
        self.m_writer.writeFloat(matrix.M23)
        self.m_writer.writeFloat(matrix.M24)
        self.m_writer.writeFloat(matrix.M31)
        self.m_writer.writeFloat(matrix.M32)
        self.m_writer.writeFloat(matrix.M33)
        self.m_writer.writeFloat(matrix.M34)
        self.m_writer.writeFloat(matrix.M41)
        self.m_writer.writeFloat(matrix.M42)
        self.m_writer.writeFloat(matrix.M43)
        self.m_writer.writeFloat(matrix.M44)

    def writeQuarternion(self, q):
        self.m_writer.writeFloat(q.x)
        self.m_writer.writeFloat(q.y)
        self.m_writer.writeFloat(q.z)
        self.m_writer.writeFloat(q.w)

    def writeAnimationClip(self, clip):
        self.m_writer.writeString7(clip.name)
        self.m_writer.writeDouble(clip.duration)
        self.m_writer.writeInt32(len(clip.bones))
        for bone in clip.bones:
            self.m_writer.writeString7(bone.name)
            self.m_writer.writeInt32(len(bone.keyframes))
            for keyframe in bone.keyframes:
                self.m_writer.writeDouble(keyframe.time)
                self.writeQuarternion(keyframe.rotation)
                self.writeVector3(keyframe.translation)
