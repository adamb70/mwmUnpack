import os
import re
from shutil import copyfile
from ImportMWM import BinaryStream, LoadTagData, LoadOldVersion, TagReaders
from ExportMWM import MyModelExporter


class MWMhandler(object):
    def __init__(self, infile=None):
        self.mwm = None
        self.index = None
        self.infile = None
        if infile:
            self.infile = infile
            self.outfile_path, self.outfile_name = os.path.split(infile)
            self.load(infile)

    def load(self, infile):
        if self.infile:
            self.stream = BinaryStream(open(infile, 'rb'))
        else:
            self.infile = infile.name
            self.outfile_path, self.outfile_name = os.path.split(infile.name)
            self.stream = BinaryStream(infile)
        self.mwm = self.LoadTagData(self.stream)

    def LoadTagData(self, stream):
        retTagData = {}
        key = stream.readString7()

        array = []
        for i in range(stream.readInt32()):
            array.append(stream.readString7())
        retTagData[key] = array

        if len(array) > 0 and array[0].startswith('Version:'):
            version = int(array[0].replace('Version:', ''))

        if version >= 1066002:
            index = {}
            num = stream.readInt32()
            for i in range(num):
                key = stream.readString7()
                value = stream.readInt32()
                index[key] = value

            self.index = index

            for key, val in index.items():
                stream.base_stream.seek(val)
                tag = stream.readString7()
                if tag in TagReaders:
                    retTagData[tag] = TagReaders[tag](stream, version=version)
                else:
                    print('#### NO READER AVAILABLE FOR', tag)

            return retTagData
        else:
            LoadOldVersion(stream)

    def save(self, outfile_path="EditedMWMs", **kwargs):
        if outfile_path:
            self.outfile_path = os.path.join(self.outfile_path, outfile_path)
            if not os.path.exists(self.outfile_path):
                os.makedirs(self.outfile_path)
        exporter = MyModelExporter(os.path.join(self.outfile_path, self.outfile_name))
        exporter.exportModelData(self.mwm, **kwargs)

    def replace_texture_prefix(self, prefix, material_names=None):
        """ Replaces 'Textures\...\*.dds' with the prefix, keeping only *.dds. Used to change texture
            directory easily. Can choose which material names to add the prefix to, defaults to all.
            Return list of changed materials. """
        ret = []
        parts = self.mwm["MeshParts"]
        for part in parts:
            if material_names and part.materialDesc.material_name not in material_names:
                continue
            for n, m in part.materialDesc.textures.items():
                suffix = re.search(r'[\\\/](.+[\\\/])*(.+\.dds)', m, flags=re.IGNORECASE).group(2)
                part.materialDesc.textures[n] = (os.path.join(os.path.normpath(prefix), os.path.normpath(suffix))).replace('\/', '\\')
                ret.append("{}.{}".format(part.materialDesc.material_name, n))
        return ret

    def print_material_data(self):
        parts = self.mwm["MeshParts"]
        print('\n### Materials')
        for part in parts:
            part.materialDesc.debug_print()
        print('### End Materials')

    def get_bone_names(self):
        return [x.name for x in self.mwm['Bones']]

    def export_fbx(self):
        """ not implemented yet """
        print(self.mwm['Dummies'])

    def export_havok_collision(self, filename):
        with open(filename, 'wb') as outfile:
            outfile.write(self.mwm["HavokCollisionGeometry"])


def copy_animation(source, dest, outname=None):
    """ Copies animation from source to dest """
    if not outname:
        outname = "{}__{}".format(dest.outfile_name, source.outfile_name)

    #dest_copy = open(os.path.join(dest.outfile_path, outname), 'wb')
    dest_copy = copyfile(dest.infile, os.path.join(dest.outfile_path, outname))
    copy_handler = MWMhandler()
    copy_handler.load(open(dest_copy, 'rb+'))

    print(dest.index)
    print(source.index)
    anim_data_start = source.index['Animations']
    anim_data_end = source.index['Bones']
    anim_data_length = anim_data_end - anim_data_start

    # copy source anim data
    source.stream.base_stream.seek(anim_data_start)
    anim_data = source.stream.readBytes(anim_data_length)

    # copy destination start of file
    old_anim_start = source.index['Animations']
    dest.stream.base_stream.seek(0)
    start = dest.stream.readBytes(old_anim_start)

    # copy destination data from end of file
    ending_start = dest.index['Bones']
    ending_length = os.stat(dest.infile).st_size - ending_start
    dest.stream.base_stream.seek(ending_start)
    ending = dest.stream.readBytes(ending_length)

    """animation object replacement"""
    source_bones = set(source.get_bone_names())
    dest_bones = set(dest.get_bone_names())
    print('Bones missing from dest:', source_bones - dest_bones)
    print('Bones that should not be in dest:', dest_bones - source_bones)

    copy_handler.mwm['Animations'] = source.mwm['Animations']
    copy_handler.save()

    """animation bytes replacing method"""
    # copy_handler.save(animdata=anim_data)

    """byte writing method"""
    # old_anim_end = source.index['Bones']
    # old_anim_length = old_anim_end - old_anim_start
    #
    # after_anim = False
    # for k, v in copy_handler.index.items():
    #     if not after_anim:
    #         if k == 'Animations':
    #             after_anim = True
    #         continue
    #
    #     old_diff = (dest.index[k] - old_anim_length) - old_anim_start
    #     copy_handler.index[k] = v - old_diff + anim_data_length
    #
    # dest_copy.infile.write(ending)
    # dest_copy.write(start)
    # dest_copy.write(anim_data)
