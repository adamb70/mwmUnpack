import glob
from DataEditor import MWMhandler, copy_animation


def test_replace_texture():
    for path in glob.glob('dwarven/dwarvenchest*'):
        print('\n\t',path)
        mwm = MWMhandler(path)
        mwm.print_material_data()
        print(mwm.replace_texture_prefix("Textures\Models\Cubes\DwarvenChest"))
        mwm.save()


def test_print_info(infile):
    mwm = MWMhandler(infile)

    for bone in mwm.mwm['Bones']:
        print(bone.name)
        print(bone.index)
        print(bone.parent)

    print(mwm.mwm['Animations'].skeleton)
    print(mwm.mwm['Animations'].clips)
    if mwm.mwm['Animations'].clips:
        print([b.name for b in mwm.mwm['Animations'].clips[0].bones])
        print(mwm.mwm['Animations'].clips[0].name)
        print(mwm.mwm['Animations'].clips[0].duration)

    print(mwm.index)

    mwm.print_material_data()
    mwm.print_mesh_sections()
    mwm.print_lod_data()
    mwm.print_dummies()

    #mwm.export_havok_collision(f"{mwm.infile}.hkt")


def test_material_info(infile):
    mwm = MWMhandler(infile)
    mwm.print_material_data()
    mwm.print_lod_data()
    mwm.print_dummies()
    mwm.replace_texture_prefix("Textures\Models\Farming\compost bin")
    mwm.save()

test_print_info('testfiles/Market_Stand_3.mwm')
