"""Utilities for file format detection in NPK and WPK files."""

from core.npk.enums import NPKEntryFileCategories
from core.npk.class_types import NPKEntryDataFlags
from core.wpk.class_types import WPKEntryDataFlags

def is_binary(data: bytes):
    """Check if the data is binary.

    Args:
        data: Raw file data

    Returns:
        bool: True if the data is binary, False otherwise
    """
    # Normally text files doesn't contain null bytes
    if b'\x00' in data[:4000]:
        return True
    # Take a sample to check for binary data
    try:
        data[:2048].decode('utf-8', errors='strict')
    except UnicodeDecodeError:
        return True
    return False

def _get_binary_ext(data: bytes, flags: NPKEntryDataFlags | WPKEntryDataFlags):
    """Check for binary file signatures."""
    if data[:3] == b'PVR':
        return 'pvr'
    if data[:4] == bytes([0x34, 0x80, 0xC8, 0xBB]):
        return 'mesh'
    if data[:4] == b'RIFF':
        if b'FEV' in data:
            return 'fev'
        if b'WAVE' in data:
            return 'wem'
    if data[:8] == b'RAWANIMA':
        return 'rawanimation'
    if data[:8] == b'NEOXBIN1':
        return 'uiprefab'
    if data[:8] == b'SKELETON':
        return 'skeleton'
    #if data[1:8] == bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]):
    #    return 'blasttool'
    if data[:6] == bytes([0x01, 0x00, 0x05, 0x00, 0x00, 0x00]):
        return 'foliage'
    if data[:8] == b'NEOXMESH':
        return 'uimesh'
    if data[:33] == b'NVidia(r) GameWorks Blast(tm) v.1':
        return 'blast'
    if data[:4] == bytes([0xE3, 0x00, 0x00, 0x00]) or \
         data[:4] == bytes([0x63, 0x00, 0x00, 0x00]) or \
         data[:4] == bytes([0x4C, 0x0F, 0x00, 0x00]) or \
         data[:4] == bytes([0x27, 0xE3, 0x00, 0x01]):
        return 'pyc'
    if data[:12] == b'CocosStudio-UI':
        return 'coc'
    if data[:4] == bytes([0x13, 0xAB, 0xA1, 0x5C]):
        return 'astc'
    if data[:3] == b'hit':
        return 'hit'
    if data[:3] == b'PKM':
        return 'pkm'
    if data[:3] == b'DDS':
        return 'dds'
    if data[-18:-2] == b'TRUEVISION-XFILE' or \
         data[:3] == bytes([0x00, 0x00, 0x02]) or \
         data[:3] == bytes([0x0D, 0x00, 0x02]):
        return 'tga'
    if data[:4] == b'NFXO':
        return 'nfx'
    if data[:4] == bytes([0xC1, 0x59, 0x41, 0x0D]):
        if b"Material" in data:
            return 'mtg'
        if b"GisFiles" in data:
            return 'gim'
        if b"Anim" in data:
            return 'ags'
        return 'unknown1'
    if data[:8] == b'CompBlks':
        return 'cbk'
    if data [:2] == b'BM':
        return 'bmp'
    if data[1:4] == b'KTX':
        return 'ktx'
    if data[:9] == b'blastmesh':
        return 'blastmesh'
    if data[:10] == b'clothasset':
        return 'clothasset'
    if data[1:4] == b'PNG':
        return 'png'
    if data[:4] == b'FSB5':
        return 'fsb'
    if data[:4] == b'VANT':
        return 'vant'
    if data[:4] == b'MDMP':
        return 'mdmp'
    if data[:4] == b'RGIS':
        return 'gis'
    if data[:4] == b'NTRK':
        return 'trk'
    if data[:4] == b'OggS':
        return 'ogg'
    if data[:4] == bytes([0xFF,0xD8,0xFF,0xE1]):
        return 'jpg'
    if data[:4] == b'BKHD':
        return 'bnk'
    if data[:4] == b'TZif':
        return 'tzif'
    if data[6:10] == b'JFIF':
        return 'jfif'
    if data[4:8] == b'ftyp':
        return 'mp4'
    if data[0x3B: 0x3F] == bytes([0xC5, 0x00, 0x00, 0x80, 0x3F]):
        return 'slpb'
    if bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x55, 0x55]) in data:
        return "animation"

    return None

def _get_text_ext(data: bytes, flags: NPKEntryDataFlags | WPKEntryDataFlags):
    """Check for text file signatures."""
    if data[:18] == b'from typing import ':
        return 'pyi'
    if data[:27] == b'-----BEING PUBLIC KEY-----':
        return 'pem'
    if len(data) < 100000000:
        #NeoXML file detection
        if b'<Material' in data:
            return 'mtl'
        if b'<MaterialGroup' in data:
            return 'mtg'
        if b'<MetaInfo' in data:
            return 'pvr.meta'
        if b'SHEX' in data and b'OSGN' in data:
            return 'binary'
        if b'<Section' in data:
            return 'sec'
        if b'<SubMesh' in data:
            return 'gim'
        if b'<FxGroup' in data:
            return 'sfx'
        if b'<Track' in data:
            return 'trackgroup'
        if b'<Instances' in data:
            return 'decal'
        if b'<Physics' in data:
            return 'col'
        if b'<LODPolicy' in data or b'<LODProfile' in data:
            return 'lod'
        if b'Type="Animation"' in data:
            return 'animation'
        if b'DisableBakeLightProbe=' in data:
            return 'prefab'
        if b'<Scene' in data:
            return 'scn'
        if b'"ParticleSystemTemplate"' in data:
            return 'pse'
        if b'<MainBody' in data:
            return 'nxcompute'
        if b'<MapSkeletonToMeshBone' in data:
            return 'skeletonextra'
        if b'<ShadingModel' in data:
            return 'nxshader'
        if b'<BlastDynamic' in data:
            return 'blt'
        if b'"ParticleAudio"' in data:
            return 'psemusic'
        if b'<BlendSpace' in data:
            if b'is2D="false"' in data:
                return 'blendspace1d'
            return 'blendspace'
        if b'<AnimationConfig' in data:
            return 'animconfig'
        if b'<AnimationGraph' in data:
            return 'animgraph'
        if b'<Head Type="Timeline"' in data:
            return 'timeline'
        if b'<Chain' in data:
            return 'physicalbone'
        if b'<PostProcess' in data:
            return 'postprocess'
        if b'"mesh_import_options":{' in data:
            return 'nxmeta'
        if b'<SceneConfig' in data:
            return 'scnex'
        if b'<LocalPoints' in data:
            return 'localweather'
        if b'GeoBatchHint="0"' in data:
            return 'gimext'
        if b'"AssetType":"HapticsData"' in data:
            return 'haptic'
        if b'<LocalFogParams' in data:
            return 'localfogparams'
        if b'<Audios' in data or b'<AudioSource' in data:
            return 'prefabaudio'
        if b'"ReferenceSkeleton' in data:
            return 'featureschema'
        if b'<Relationships' in data:
            return 'xml.rels'
        if b'<Waterfall' in data:
            return 'waterfall'
        if b'"ReferenceSkeletonPath"' in data:
            return 'mirrortable'
        if b'<ClothAsset' in data:
            return 'clt'
        if b'<plist' in data:
            return 'plist'
        if b'<ShaderCompositor' in data or \
             b'<ShaderFeature' in data or \
             b"<ShaderIndexes" in data or \
             b"<RenderTrigger" in data:
            return 'render'
        if b'<SkeletonRig' in data:
            return 'skeletonrig'
        if b'format: ' in data and b'filter: ' in data:
            return 'atlas'
        if b'<ShaderCache' in data:
            return 'cache'
        if b'char' in data and b'width=' in data and b'height=' in data:
            return 'fnt'
        if b'<AllCaches' in data:
            return 'info'
        if b'<AllPreloadCaches' in data:
            return 'list'
        if b'<Remove_Files' in data:
            return 'map'
        if b'<HLSL File="' in data:
            return 'md5'
        if b'<EnvParticle' in data:
            return 'envp'
        if b'<TextureGroup' in data:
            return 'txg'
        if b'?xml' in data:
            return 'xml'

    return None

def get_ext(data: bytes, flags: NPKEntryDataFlags | WPKEntryDataFlags):
    """Get the file extension based on file signature.

    Args:
        data: Raw file data

    Returns:
        str: File extension without leading dot
    """

    if len(data) == 0:
        return 'empty'

    text_flag = type(flags).TEXT
    if flags & text_flag:
        ext = _get_text_ext(data, flags)
        if ext:
            return ext
    else:
        ext = _get_binary_ext(data, flags)
        if ext:
            return ext

    return 'dat'

def get_file_category(extension):
    """Categorize a file based on its extension.

    Args:
        extension: File extension

    Returns:
        str: Category name
    """
    extension = extension.lower()

    # Textures
    if extension in ["bmp", "gif", "jpg", "jpeg", "png", "pbm", "pgm", "ppm", "xbm",
                     "xpm", "tga", "ico", "tiff", "dds", "pvr", "astc", "ktx", "ktx_low", "cbk"]:
        return NPKEntryFileCategories.TEXTURE

    # 3D Models
    if extension in ["mesh"]:
        return NPKEntryFileCategories.MESH

    if extension in ["bnk"]:
        return NPKEntryFileCategories.BANK

    return NPKEntryFileCategories.OTHER
