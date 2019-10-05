from hashlib import md5
from utils import *


class MyModelDummy(object):
    def __init__(self):
        self.SUBBLOCK_PREFIX = "subblock_"
        self.SUBPART_PREFIX = "subpart_"
        self.ATTRIBUTE_FILE = "file"
        self.ATTRIBUTE_HIGHLIGHT = "highlight"
        self.ATTRIBUTE_HIGHLIGHT_SEPARATOR = ";"
        self.name = ""
        self.customdata = {}
        self.matrix = Matrix()

    def debug_print(self):
        print(f"'name': {self.name}, 'customdata': {self.customdata}")


def read_dummies(stream, **kwargs):
    dummies = {}
    num = stream.readInt32()
    for i in range(num):
        text = stream.readString7()
        matrix = read_matrix(stream)
        dummy = MyModelDummy()
        dummy.name = text
        dummy.matrix = matrix
        for j in range(stream.readInt32()):
            key = stream.readString7()
            value = stream.readString7()
            dummy.customdata[key] = value
        dummies[text] = dummy
    return dummies


def read_array_halfvector4(stream, **kwargs):
    halfvector4 = []
    for i in range(stream.readInt32()):
        halfvector4.append(read_halfvector4(stream))
    return halfvector4

def read_array_halfvector2(stream, **kwargs):
    halfvector2 = []
    for i in range(stream.readInt32()):
        halfvector2.append(read_halfvector2(stream))
    return halfvector2

def read_array_byte4(stream, **kwargs):
    byte4 = []
    for i in range(stream.readInt32()):
        byte4.append(read_byte4(stream))
    return byte4

def read_array_bytes(stream, **kwargs):
    count = stream.readInt32()
    return stream.readBytes(count)

def read_single(stream, **kwargs):
    return stream.readFloat()

def read_boolean(stream, **kwargs):
    return stream.readBool()

def read_bounding_box(stream, **kwargs):
    ret = BoundingBox()
    ret.min = import_vector3(stream)
    ret.max = import_vector3(stream)
    return ret

def read_bounding_sphere(stream, **kwargs):
    ret = BoundingSphere()
    ret.centre = import_vector3(stream)
    ret.radius = stream.readFloat()
    return ret

def read_mesh_parts(stream, version):
    meshparts = []
    for i in range(stream.readInt32()):
        meshpartinfo = MeshPartInfo()
        meshpartinfo.Import(stream, version)
        meshparts.append(meshpartinfo)
    return meshparts

def read_mesh_section(stream, version):
    meshsections = []
    for i in range(stream.readInt32()):
        meshsectioninfo = MeshSectionInfo()
        meshsectioninfo.Import(stream, version)
        meshsections.append(meshsectioninfo)
    return meshsections

def read_array_vector4(stream, **kwargs):
    vector4i = []
    for i in range(stream.readInt32()):
        vector4i.append(import_vector4(stream))
    return vector4i

def read_array_vector4Int(stream, **kwargs):
    vector4i = []
    for i in range(stream.readInt32()):
        vector4i.append(import_vector4int(stream))
    return vector4i

def read_array_vector3Int(stream, **kwargs):
    vector3i = []
    for i in range(stream.readInt32()):
        vector3i.append(import_vector3int(stream))
    return vector3i

def read_model_info(stream, **kwargs):
    tri_count = stream.readInt32()
    vert_count = stream.readInt32()
    bounding_box_size = import_vector3(stream)
    return ModelInfo(tri_count, vert_count, bounding_box_size)

def read_bvh(stream, **kwargs):
    bvh = GImpactQuantizedBvh()
    bvh.load(read_array_bytes(stream))
    return bvh

def read_animations(stream, **kwargs):
    num = stream.readInt32()
    animations = ModelAnimations()
    while num > 0:
        num -= 1
        item = read_clip(stream)
        animations.clips.append(item)

    num2 = stream.readInt32()
    while num2 > 0:
        num2 -= 1
        item2 = stream.readInt32()
        animations.skeleton.append(item2)
    return animations

def read_bones(stream, **kwargs):
    num = stream.readInt32()
    bone_list = []
    i = 0
    for _ in range(num):
        bone = ModelBone()
        bone.name = stream.readString7()
        i += 1
        bone.index = i
        bone.parent = stream.readInt32()
        bone.transform = read_matrix(stream)
        bone_list.append(bone)
    return bone_list

def read_LODs(stream, **kwargs):
    num = stream.readInt32()
    lod_list = []
    for _ in range(num):
        descriptor = LODDescriptor()
        descriptor.read(stream)
        lod_list.append(descriptor)
    return lod_list

def read_hash(stream, **kwargs):
    # TODO: this is not at all like the keen one. Might not need theirs
    # This function just returns the hash directly as a string instead of a Hash object
    return stream.readBytes(16)

def read_model_fractures(stream, **kwargs):
    model_fractures = ModelFractures()
    model_fractures.version = stream.readInt32()
    for i in range(stream.readInt32()):
        type = stream.readString7()
        if type == 'RandomSplit':
            randomsplit = RandomSplitFractureSettings()
            randomsplit.num_object_level_1 = stream.readInt32()
            randomsplit.num_object_level_2 = stream.readInt32()
            randomsplit.random_range = float(stream.readInt32())
            randomsplit.random_seed_1 = stream.readInt32()
            randomsplit.random_seed_2 = stream.readInt32()
            randomsplit.split_plane = stream.readString7()
            model_fractures.fractures = [randomsplit]
        elif type == 'Voronoi':
            voronoi = VoronoiFractureSettings()
            voronoi.seed = stream.readInt32()
            voronoi.num_sites_to_generate = stream.readInt32()
            voronoi.num_iterations = stream.readInt32()
            voronoi.split_plane = stream.readString7()
            model_fractures.fractures = [voronoi]
        elif type == 'WoodFracture':
            woodfracture = WoodFractureSettings()
            woodfracture.board_custom_splitting_plane_axis = read_boolean(stream)
            woodfracture.board_fracture_line_shearing_range = stream.readFloat()
            woodfracture.board_fracture_normal_shearing_range = stream.readFloat()
            woodfracture.board_num_subparts = stream.readInt32()
            woodfracture.board_rotate_split_geom = woodfracture.Rotation(int(stream.readInt32)+1)
            woodfracture.board_scale = import_vector3(stream)
            woodfracture.board_scale_range = import_vector3(stream)
            woodfracture.board_split_geom_shift_range_y = stream.readFloat()
            woodfracture.board_split_geom_shift_range_z = stream.readFloat()
            woodfracture.board_splitting_axis = import_vector3(stream)
            woodfracture.board_splitting_plane = stream.readString7()
            woodfracture.board_surface_normal_shearing_range = stream.readFloat()
            woodfracture.board_width_range = stream.readFloat()
            woodfracture.splinter_custom_splitting_plane_axis = read_boolean(stream)
            woodfracture.splinter_fracture_line_shearing_range = stream.readFloat()
            woodfracture.splinter_fracture_normal_shearing_range = stream.readFloat()
            woodfracture.splinter_num_subparts = stream.readInt32()
            woodfracture.splinter_rotate_split_geom = woodfracture.Rotation(int(stream.readInt32)+1)
            woodfracture.splinter_scale = import_vector3(stream)
            woodfracture.splinter_scale_range = import_vector3(stream)
            woodfracture.splinter_split_geom_shift_range_Y = stream.readFloat()
            woodfracture.splinter_split_geom_shift_range_z = stream.readFloat()
            woodfracture.splinter_splitting_axis = import_vector3(stream)
            woodfracture.splinter_splitting_plane = import_vector3(stream)
            woodfracture.splinter_surface_normal_shearing_range = stream.readFloat()
            woodfracture.splinter_width_range = stream.readFloat()
    return model_fractures


TagReaders = {
    'Vertices': read_array_halfvector4,
    'Normals': read_array_byte4,
    'TexCoords0': read_array_halfvector2,
    'Binormals': read_array_byte4,
    'Tangents': read_array_byte4,
    'TexCoords1': read_array_halfvector2,
    'UseChannelTextures': read_boolean,
    'BoundingBox': read_bounding_box,
    'BoundingSphere': read_bounding_sphere,
    'RescaleFactor': read_single,
    'SwapWindingOrder': read_boolean,
    'Dummies': read_dummies,
    'MeshParts': read_mesh_parts,
    'Sections': read_mesh_section,
    'ModelBvh': read_bvh,
    'ModelInfo': read_model_info,
    'BlendIndices': read_array_vector4Int,
    'BlendWeights': read_array_vector4,
    'Animations': read_animations,
    'Bones': read_bones,
    'BoneMapping': read_array_vector3Int,
    'HavokCollisionGeometry': read_array_bytes,
    'PatternScale': read_single,
    'LODs': read_LODs,
    'HavokDestructionGeometry': read_array_bytes,
    'HavokDestruction': read_array_bytes,
    'FBXHash': read_hash,
    'HKTHash': read_hash,
    'XMLHash': read_hash,
    'ModelFractures': read_model_fractures,




}





