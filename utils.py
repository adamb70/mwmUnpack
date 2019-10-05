import io
from math import acos, sin
from struct import *
from enum import Enum
import binascii


class BinaryStream:
    def __init__(self, base_stream):
        self.base_stream = base_stream

    def readByte(self):
        return self.base_stream.read(1)

    def readBytes(self, length):
        return self.base_stream.read(length)

    def readChar(self):
        return self.unpack('b')

    def readUChar(self):
        return self.unpack('B')

    def readBool(self):
        return self.unpack('?')

    def readInt16(self):
        return self.unpack('h', 2)

    def readUInt16(self):
        return self.unpack('H', 2)

    def readInt32(self):
        return self.unpack('i', 4)

    def readUInt32(self):
        return self.unpack('I', 4)

    def readInt64(self):
        return self.unpack('q', 8)

    def readUInt64(self):
        return self.unpack('Q', 8)

    def readFloat(self):
        return self.unpack('f', 4)

    def readDouble(self):
        return self.unpack('d', 8)

    def readString(self):
        length = self.readUInt16()
        return self.unpack(str(length) + 's', length)

    def readString7(self):
        length = self.readUChar()
        return self.unpack(str(length) + 's', length).decode()


    def writeBytes(self, value):
        self.base_stream.write(value)

    def writeChar(self, value):
        self.pack('c', value)

    def writeUChar(self, value):
        self.pack('B', value)

    def writeBool(self, value):
        self.pack('?', value)

    def writeInt16(self, value):
        self.pack('h', value)

    def writeUInt16(self, value):
        self.pack('H', value)

    def writeInt32(self, value):
        self.pack('i', value)

    def writeUInt32(self, value):
        self.pack('I', value)

    def writeInt64(self, value):
        self.pack('q', value)

    def writeUInt64(self, value):
        self.pack('Q', value)

    def writeFloat(self, value):
        self.pack('f', value)

    def writeDouble(self, value):
        self.pack('d', value)

    def writeString(self, value):
        length = len(value)
        self.writeUInt16(length)
        self.pack(str(length) + 's', value)

    def writeString7(self, value):
        value = value.encode()
        length = len(value)
        self.writeUChar(length)
        self.pack(str(length) + 's', value)

    def pack(self, fmt, data):
        return self.writeBytes(pack(fmt, data))

    def unpack(self, fmt, length=1):
        return unpack(fmt, self.readBytes(length))[0]


class Matrix(object):
    def __init__(self):
        self.M11, self.M12, self.M13, self.M14 = 0, 0, 0, 0
        self.M21, self.M22, self.M23, self.M24 = 0, 0, 0, 0
        self.M31, self.M32, self.M33, self.M34 = 0, 0, 0, 0
        self.M41, self.M42, self.M43, self.M44 = 0, 0, 0, 0

    def as_string(self):
        ret = "[M11: {0}, M12: {1}, M13: {2}, M14: {3}, ".format(self.M11, self.M12, self.M13, self.M14)
        ret += "M21: {0}, M22: {1}, M23: {2}, M24: {3}, ".format(self.M21, self.M22, self.M23, self.M24)
        ret += "M31: {0}, M32: {1}, M33: {2}, M34: {3}, ".format(self.M31, self.M32, self.M33, self.M34)
        ret += "M41: {0}, M42: {1}, M43: {2}, M44: {3}]".format(self.M41, self.M42, self.M43, self.M44)
        return ret

def read_matrix(stream):
    result = Matrix()
    result.M11 = stream.readFloat()
    result.M12 = stream.readFloat()
    result.M13 = stream.readFloat()
    result.M14 = stream.readFloat()
    result.M21 = stream.readFloat()
    result.M22 = stream.readFloat()
    result.M23 = stream.readFloat()
    result.M24 = stream.readFloat()
    result.M31 = stream.readFloat()
    result.M32 = stream.readFloat()
    result.M33 = stream.readFloat()
    result.M34 = stream.readFloat()
    result.M41 = stream.readFloat()
    result.M42 = stream.readFloat()
    result.M43 = stream.readFloat()
    result.M44 = stream.readFloat()
    return result


class HalfVector4(object):
    def __init__(self, x=0.0, y=0.0, z=0.0, w=0.0, packed_value=None):
        self.x, self.y, self.z, self.w = x, y, z, w
        self.packed_value = packed_value


class HalfVector2(object):
    def __init__(self, x=0.0, y=0.0, z=0.0, w=0.0, packed_value=None):
        self.x, self.y, self.z, self.w = x, y, z, w
        self.packed_value = packed_value

class Vector3(object):
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x, self.y, self.z = x, y, z

    def __sub__(self, other):
        if type(other) != Vector3:
            print("Vector3 can only be subtracted from a Vector3!")
            raise TypeError
        ret = Vector3()
        ret.x = self.x - other.x
        ret.y = self.y - other.y
        ret.z = self.z - other.z
        return ret

    def length_squared(self):
        return self.x**2 + self.y**2 + self.z**2

    @staticmethod
    def lerp(origin, destination, amount):
        result = Vector3()
        result.x = origin.x + (destination.x - origin.x) * amount
        result.y = origin.y + (destination.y - origin.y) * amount
        result.z = origin.z + (destination.z - origin.z) * amount
        return result

    @staticmethod
    def one():
        return Vector3(1.0, 1.0, 1.0)

def read_halfvector4(stream):
    ret = HalfVector4()
    ret.packed_value = stream.readUInt64()
    return ret

def read_halfvector2(stream):
    ret = HalfVector2()
    ret.packed_value = stream.readUInt32()
    return ret

def import_vector3(stream):
    vector3 = Vector3()
    vector3.x = stream.readFloat()
    vector3.y = stream.readFloat()
    vector3.z = stream.readFloat()
    return vector3


class Byte4(object):
    def __init__(self, x=0, y=0, z=0, w=0, packed_value=None):
        self.x, self.y, self.z, self.w = x, y, z, w
        self.packed_value = packed_value


def read_byte4(stream):
    ret = Byte4()
    ret.packed_value = stream.readUInt32()
    return ret

class BoundingBox(object):
    def __init__(self, min=None, max=None):
        self.min = min
        self.max = max

class BoundingSphere(object):
    def __init__(self, centre=None, radius=None):
        self.centre = centre
        self.radius = radius

class MaterialDescriptor(object):
    def __init__(self):
        self.textures = {}
        self.user_data = {}
        self.material_name = ""
        self.technique = "MESH"
        self.glassCW = ""
        self.glassCCW = ""
        self.glassSmoothNormals = True

    def read(self, stream, version):
        self.textures = {}
        self.user_data = {}
        self.material_name = stream.readString7()

        if version < 1052002:
            value = stream.readString7()
            if value:
                self.textures["DiffuseTexture"] = value

            value2 = stream.readString7()
            if value2:
                self.textures["NormalTexture"] = value2

        else:
            num = stream.readInt32()
            for i in range(num):
                key = stream.readString7()
                value3 = stream.readString7()
                self.textures[key] = value3

        if version >= 1068001:
            num2 = stream.readInt32()
            for i in range(num2):
                key2 = stream.readString7()
                value4 = stream.readString7()
                self.user_data[key2] = value4

        if version < 1157001:
            stream.readFloat()
            stream.readFloat()
            stream.readFloat()
            stream.readFloat()
            stream.readFloat()
            stream.readFloat()
            stream.readFloat()

        if version < 1052001:
            techniques_enum = ["MESH", "VOXELS_DEBRIS", "VOXEL_MAP", "ALPHA_MASKED", "FOLIAGE", "DECAL", "DECAL_CUTOUT",
             "HOLO", "VOXEL_MAP_SINGLE", "VOXEL_MAP_MULTI", "SKINNED", "GLASS"]
            technique = techniques_enum[stream.readInt32()]
            self.technique = technique
            print("This file is older than version 1052001. This material technique might not be correct! (probably is)")
        else:
            self.technique = stream.readString7()

        if self.technique == "GLASS":
            if version >= 1043001:
                self.glassCW = stream.readString7()
                self.glassCCW = stream.readString7()
                self.glassSmoothNormals = stream.readBool()
                # if self.glassCCW and :    #TODO: don't think there's much need for this. Not worth the effort of recreating the c# at this time
                #     self.material_name = self.glassCCW
            else:
                stream.readBytes(4)
                stream.readBytes(4)
                stream.readBytes(4)
                stream.readBytes(4)
                self.glassCW = "GlassCW"
                self.glassCCW = "GlassCCW"
                self.glassSmoothNormals = False

        return True

    def write(self, writer):
        writer.writeString7(self.material_name)
        writer.writeInt32(len(self.textures))
        for key, val in self.textures.items():
            writer.writeString7(key)
            writer.writeString7(val)
        writer.writeInt32(len(self.user_data))
        for key2, val2 in self.user_data.items():
            writer.writeString7(key2)
            writer.writeString7(val2)
        writer.writeString7(self.technique)
        if self.technique == "GLASS":
            writer.writeString7(self.glassCW)
            writer.writeString7(self.glassCCW)
            writer.writeBool(self.glassSmoothNormals)
        return True

    def debug_print(self):
        print({'material_name': self.material_name, 'technique': self.technique,
               'textures': self.textures, 'glassCW': self.glassCW, 'glassCCW': self.glassCCW,
               'glassSmoothNormals': self.glassSmoothNormals, 'user_data': self.user_data})


class MeshPartInfo(object):
    def __init__(self):
        self.material_hash = None
        self.materialDesc = None
        self.indices = None

    def Import(self, stream, version):
        self.indices = []
        self.material_hash = stream.readInt32()
        if version < 1052001:
            stream.readInt32()

        num = stream.readInt32()
        for i in range(num):
            self.indices.append(stream.readInt32())

        flag = stream.readBool()
        flag2 = True
        if flag:
            self.materialDesc = MaterialDescriptor()
            flag2 = self.materialDesc.read(stream, version)
        else:
            self.materialDesc = None
        return flag2

    def Export(self, writer):
        writer.writeInt32(self.material_hash)
        writer.writeInt32(len(self.indices))
        for val in self.indices:
            writer.writeInt32(val)
        ret = True
        if self.materialDesc is not None:
            writer.writeBool(True)
            ret = self.materialDesc.write(writer)
        else:
            writer.writeBool(False)
        return ret

class MeshSectionMeshInfo(object):
    def __init__(self):
        self.materialName = ""
        self.startIndex = ""
        self.indexCount = ""

    def Import(self, stream, version):
        self.materialName = stream.readString7()
        self.startIndex = stream.readInt32()
        self.indexCount = stream.readInt32()
        return True

    def Export(self, writer):
        writer.writeString7(self.materialName)
        writer.writeInt32(self.startIndex)
        writer.writeInt32(self.indexCount)
        return True

class MeshSectionInfo(object):
    def __init__(self):
        self.name = ""
        self.meshes = []

    def Import(self, stream, version):
        self.name = stream.readString7()
        flag = True
        for i in range(stream.readInt32()):
            meshSectionMeshInfo = MeshSectionMeshInfo()
            flag &= meshSectionMeshInfo.Import(stream, version)
            self.meshes.append(meshSectionMeshInfo)
        return flag

    def Export(self, writer):
        writer.writeString7(self.name)
        writer.writeInt32(len(self.meshes))
        flag = True
        for meshsectionmeshinfo in self.meshes:
            flag &= meshsectionmeshinfo.Export(writer)
        return flag

    def debug_print(self):
        print({'name': self.name, 'meshes': self.meshes})

class Vector4(object):
    def __init__(self, x=0.0, y=0.0, z=0.0, w=0.0):
        self.x, self.y, self.z, self.w = x, y, z, w

class Vector4i(object):
    def __init__(self, x=0, y=0, z=0, w=0):
        self.x, self.y, self.z, self.w = x, y, z, w

class Vector3i(object):
    def __init__(self, x=0, y=0, z=0):
        self.x, self.y, self.z = x, y, z

def import_vector4(stream):
    vector4 = Vector4()
    vector4.x = stream.readFloat()
    vector4.y = stream.readFloat()
    vector4.z = stream.readFloat()
    vector4.w = stream.readFloat()
    return vector4

def import_vector4int(stream):
    vector4 = Vector4i()
    vector4.x = stream.readInt32()
    vector4.y = stream.readInt32()
    vector4.z = stream.readInt32()
    vector4.w = stream.readInt32()
    return vector4

def import_vector3int(stream):
    vector3 = Vector3i()
    vector3.x = stream.readInt32()
    vector3.y = stream.readInt32()
    vector3.z = stream.readInt32()
    return vector3


class Quarternion(object):
    def __init__(self, x=0, y=0, z=0, w=0):
        self.x, self.y, self.z, self.w = x, y, z, w

    @staticmethod
    def dot(first, other):
        return first.x * other.x + first.y * other.y + first.z * other.z + first.w * other.w

    @staticmethod
    def slerp(origin, destination, amount):
        num = origin.x*destination.x + origin.y*destination.y + origin.z*destination.z + origin.w*destination.w
        flag = False
        if num < 0.0:
            flag = True
            num = -num
        if num > 0.999998986721039:
            num2 = 1.0 - amount
            num3 = (-amount if flag else amount)
        else:
            num4 = acos(num)
            num5 = acos(1.0/sin(num4))
            num2 = sin((1.0-amount) * num4) * num5
            num3 = -sin((amount*num4)*num5) if flag else sin((amount*num5)*num5)
        result = Quarternion()
        result.x = num2*origin.x + num3*destination.x
        result.y = num2*origin.y + num3*destination.y
        result.z = num2*origin.z + num3*destination.z
        result.w = num2*origin.w + num3*destination.w
        return result


def import_quarternion(stream):
    quart = Quarternion()
    quart.x = stream.readFloat()
    quart.y = stream.readFloat()
    quart.z = stream.readFloat()
    quart.w = stream.readFloat()
    return quart


class ModelInfo(object):
    def __init__(self, tris=0, verts=0, bbSize=None):
        self.tri_count = tris
        self.vert_count = verts
        self.bounding_box_size = bbSize


class IndexedVector3(object):
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z

class UShortVector3(object):
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

class AABB(object):
    def __init__(self, min, max):
        self.min = min
        self.max = max


class BT_QUANTIZED_BVH_NODE(object):
    def __init__(self):
        self.escapeIndexOrDataIndex = None
        self.m_quantizedAabbMin = None
        self.m_quantizedAabbMax = None


class QuantizedBvhTree(object):
    def __init__(self):
        self.num_nodes = 0
        self.node_array = None
        self.global_bound = None
        self.bvh_quantization = None

    def load(self, bytearr):
        reader = BinaryStream(io.BytesIO(bytearr))
        self.num_nodes = reader.readInt32()
        indexed_vector = self.readIndexedVector3(reader)
        indexed_vector2 = self.readIndexedVector3(reader)
        self.global_bound = AABB(indexed_vector, indexed_vector2)
        self.bvh_quantization = self.readIndexedVector3(reader)
        self.node_array = []
        for i in range(self.num_nodes):
            num = reader.readInt32()
            quantized_node = BT_QUANTIZED_BVH_NODE()
            quantized_node.escapeIndexOrDataIndex = []
            for j in range(num):
                quantized_node.escapeIndexOrDataIndex.append(reader.readInt32())
            quantized_node.m_quantizedAabbMin = self.readUShortVector3(reader)
            quantized_node.m_quantizedAabbMax = self.readUShortVector3(reader)
            self.node_array.append(quantized_node)

    def save(self):
        writer = BinaryStream(io.BytesIO())
        writer.writeInt32(self.num_nodes)
        self.writeIndexedVector3(self.global_bound.min, writer)
        self.writeIndexedVector3(self.global_bound.max, writer)
        self.writeIndexedVector3(self.bvh_quantization, writer)
        for node in self.node_array:
            writer.writeInt32(len(node.escapeIndexOrDataIndex))
            for data in node.escapeIndexOrDataIndex:
                writer.writeInt32(data)
            self.writeUShortVector3(node.m_quantizedAabbMin, writer)
            self.writeUShortVector3(node.m_quantizedAabbMax, writer)
        return writer.base_stream.getvalue()

    def readIndexedVector3(self, reader):
        return IndexedVector3(reader.readFloat(), reader.readFloat(), reader.readFloat())

    def readUShortVector3(self, reader):
        return UShortVector3(reader.readUInt16(), reader.readUInt16(), reader.readUInt16())

    def writeIndexedVector3(self, vector, writer):
        writer.writeFloat(vector.x)
        writer.writeFloat(vector.y)
        writer.writeFloat(vector.z)

    def writeUShortVector3(self, vector, writer):
        writer.writeUInt16(vector.x)
        writer.writeUInt16(vector.y)
        writer.writeUInt16(vector.z)

class GImpactQuantizedBvh(object):
    def __init__(self):
        self.size = 0
        self.box_tree = QuantizedBvhTree()

    def load(self, bytearr):
        self.box_tree.load(bytearr)
        self.size = len(bytearr)

    def save(self):
        p = self.box_tree.save()
        return p

class AnimationClip(object):
    def __init__(self):
        self.bones = []
        self.name = ""
        self.duration = 0

    class Bone:
        def __init__(self):
            self.keyframes = []
            self.name = ""

    class Keyframe:
        def __init__(self):
            self.time = 0
            self.invTimeDiff = 0
            self.rotation = None
            self.translation = None


def linear_keyframe_reductiom(keyframes, translation_threshold, rotation_threshold):
    if len(keyframes) < 3:
        return
    i = 0
    node = keyframes[i]
    while True:
        i += 1
        next = keyframes[i]
        if not next:
            break
        prev_value = keyframes[i-1].Value
        node_value = node.Value
        next_value = next.Value
        amount = (node_value.Time - prev_value.Time) / (next_value.Time - prev_value.Time)
        value4 = Vector3.lerp(prev_value.Translation, next_value.Translation, amount)
        quart = Quarternion.slerp(prev_value.Rotation, next_value.Rotation, amount)
        if (value4 - node_value.Translation).length_squared() < translation_threshold and Quarternion.dot(quart, node_value.Rotation) > rotation_threshold:
            keyframes.remove(node)
        node = next

def calculate_frame_deltas(keyframes):
    for i in range(len(keyframes)):
        keyframe = keyframes[i-1]
        keyframe2 = keyframes[i]
        keyframe2.InvTimeDiff = 1.0/(keyframe2.Time - keyframe.Time)

def read_clip(stream):
    clip = AnimationClip()
    clip.name = stream.readString7()
    clip.duration = stream.readDouble()
    num = stream.readInt32()
    while num > 0:
        num -= 1
        bone = clip.Bone()
        bone.name = stream.readString7()
        num2 = stream.readInt32()
        while num2 > 0:
            num2 -= 1
            keyframe = clip.Keyframe()
            keyframe.time = stream.readDouble()
            keyframe.rotation = import_quarternion(stream)
            keyframe.translation = import_vector3(stream)
            bone.keyframes.append(keyframe)
        clip.bones.append(bone)
        # TODO: I don't think this stuff is needed for now
        # count = len(bone.keyframes)
        # optimised_keys = 0
        # if count > 3:
        #     if USE_LINEAR_KEYFRAME_REDUCTION:
        #         temp_frame_list = []
        #         for frame in bone.keyframes:
        #             temp_frame_list.append(frame)
        #         linear_keyframe_reductiom(temp_frame_list, 1E-08, 0.9999999)
        #         bone.keyframes = []
        #         bone.keyframes.append(temp_frame_list) #TODO: Maybe this should be + instead of append
        #         optimised_keys = len(bone.keyframes)
        # MyModelImporter.CalculateKeyframeDeltas(bone.Keyframes);
    return clip


class ModelAnimations(object):
    def __init__(self):
        self.skeleton = []
        self.clips = []


class ModelBone(object):
    def __init__(self):
        self.name = ""
        self.transform = Matrix()
        self.index = None
        self.parent = None


class LODDescriptor(object):
    def __init__(self):
        self.distance = 0
        self.model = ''
        self.render_quality = ''

    def read(self, stream):
        self.distance = stream.readFloat()
        m = stream.readString7()
        if m:
            self.model = m
        r = stream.readString7()
        if r:
            self.render_quality = r
        return True

    def write(self, writer):
        writer.writeFloat(self.distance)
        writer.writeString7(self.model)
        writer.writeString7(self.render_quality)

    def debug_print(self):
        print({'distance': self.distance, 'model': self.model, 'render_quality': self.render_quality})

class ModelFractures(object):
    def __init__(self):
        self.version = 1
        self.fractures = []


class FractureSettings(object):
    """ empty class? """

class RandomSplitFractureSettings(FractureSettings):
    def __init__(self):
        self.num_object_level_1 = 2
        self.num_object_level_2 = 0
        self.random_range = None
        self.random_seed_1 = None
        self.random_seed_2 = None
        self.split_plane = ""

class VoronoiFractureSettings(FractureSettings):
    def __init__(self):
        self.seed = 123456
        self.num_sites_to_generate = 8
        self.num_iterations = 1
        self.split_plane = ""

class WoodFractureSettings(FractureSettings):
    Rotation = Enum('Rotation', 'AutoRotate NoRotation Rotate90')

    def __init__(self):
        self.board_custom_splitting_plane_axis = False
        self.board_fracture_line_shearing_range = 0.0
        self.board_fracture_normal_shearing_range = 0.0
        self.board_num_subparts = 3
        self.board_rotate_split_geom = self.Rotation.AutoRotate
        self.board_scale = Vector3.one
        self.board_scale_range = Vector3.one
        self.board_split_geom_shift_range_y = 0.0
        self.board_split_geom_shift_range_z = 0.0
        self.board_splitting_axis = Vector3()
        self.board_splitting_plane = ""
        self.board_surface_normal_shearing_range = 0.0
        self.board_width_range = 0.0
        self.splinter_custom_splitting_plane_axis = False
        self.splinter_fracture_line_shearing_range = 0.0
        self.splinter_fracture_normal_shearing_range = 0.0
        self.splinter_num_subparts = 0.0
        self.splinter_rotate_split_geom = self.Rotation.AutoRotate
        self.splinter_scale = Vector3.one
        self.splinter_scale_range = Vector3.one
        self.splinter_split_geom_shift_range_Y = 0.0
        self.splinter_split_geom_shift_range_z = 0.0
        self.splinter_splitting_axis = Vector3()
        self.splinter_splitting_plane = ""
        self.splinter_surface_normal_shearing_range = 0.0
        self.splinter_width_range = 0.0






