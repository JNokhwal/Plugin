import mset
import os
import re

patterns = [
    {
        "[Hh]eight|h": [
            {
                "category": "displacement",
                "shader": "Height",
                "fields": [
                    {"Displacement Map": "[name]"},
                    {"Scale": 0}
                ]
            }
        ]
    },
    {

        "[Aa]lbedo([Ss]pec)?|a(s)?|basecolor|BaseColor": [
            {
                "category": "albedo",
                "shader": "Albedo",
                "fields": [
                    {"Albedo Map": "[name]"},
                    {"sRGB Color Space" : True},
                    {"useMipmaps": False}


                ]
            }
        ]
    },
    {
        "[Nn]ormal|n": [
            {
                "category": "surface",
                "shader": "Normals",
                "fields": [
                    {"Normal Map": "[name]"},
                    {"Object Space": False},
                    {"Flip Y": True}
                ]
            }
        ]
    },
    {
        "[Rr]oughness|r": [
            {
                "category": "microsurface",
                "shader": "Roughness",
                "fields": [
                    {"Roughness Map": "[name]"},
                    {"Roughness" : 1.0}
                ]
            }
        ]
    },
    {
        "[Mm]etalness|m|[Mm]etallic": [
            {
                "category": "reflectivity",
                "shader": "Metalness",
                "fields": [
                    {"Metalness Map": "[name]"},
                    {"Metalness" : 1.0}
                ]
            }
        ]
    },
    {
        "[Oo]cclusion|ao|ambientocclusion|ambient_occlusion": [
            {
                "category": "occlusion",
                "shader": "Occlusion",
                "fields": [
                    {"Occlusion Map": "[name]"}
                ]
            }
        ]
    },
    {
        "[Tt]ransparency|[Aa]lpha|[Oo]pacity": [
            {
                "category": "transparency",
                "shader": "Dither",
                "fields": [
                    {"Alpha Map": "[name]"},
                    {"Channel": 0}

                ]
            }
        ]
    }

]

# File formats
formats = [
    "psd",
    "png",
    "jpg",
    "jpeg",
    "tga",
    "bmp"
]

###############################################################

# UI Functionality
window = mset.UIWindow("Select Texture Location Folder")

window.addElement(mset.UILabel("Folder"))

folder_field = mset.UITextField()
folder_field.value = ""
window.addElement(folder_field)


def get_material_folder():
    path = mset.showOpenFolderDialog()
    if path != '':
        folder_field.value = path


file_button = mset.UIButton("...")
file_button.onClick = get_material_folder
window.addElement(file_button)
window.addReturn()

###############################################################

# Gets the search directory from the UI input field


def get_search_dir():
    search_dir = ""

    if os.path.isfile(folder_field.value):
        search_dir = os.path.abspath(os.path.join(folder_field.value, '..'))
    elif os.path.isdir(folder_field.value):
        search_dir = os.path.abspath(folder_field.value)
    else:
        return RuntimeWarning("Please enter valid folder or file you want to generate materials with.")

    folder_field.value = search_dir

    return search_dir

# traverses the folder and attempts to create materials from images.


def create_material():

    # Determine search area
    search_dir = get_search_dir()

    # Group each file according to the suffix portion of their name.
    files = os.listdir(search_dir)
    image_files = []
    prefix_set = set()

    for file in files:
        # If the file format is a texture
        ext = os.path.splitext(file)
        extMatch = False
        for f in formats:
            extMatch = extMatch or "." + f == ext[1]

        if extMatch:
            # perform regex match to find possible textures
            m = re.search('.*\_', file)
            if m:
                prefix_set.add(m.group(0))
                image_files.append(file)

    # Check each prefix in the with `patterns` data structure,
    # and attempt to match prefixes with subroutine settings.
    for prefix in prefix_set:
        try:
            matName = prefix.replace("_", "")
            mat = None
    
            try:
                mat = mset.findMaterial(matName)  # Try to find the material
            except Exception as e:
                print(f"Error finding material '{matName}': {e}")
    
            if mat is None:  # Material not found, create new one
                print(f"Material '{matName}' not found. Creating a new material.")
                mat = mset.Material(name=matName)
            else:  # Material found, update it
                print(f"Material '{matName}' found. Updating texture channels.")

            for item in patterns:

                for suffixRegex in item.keys():

                    for file in files:

                        # Match any files that have the suffix or an
                        # underscore followed by the suffix
                        suffixMatch = re.match(
                            prefix + "((" + suffixRegex + ")|" + prefix + "_" + "(" + suffixRegex + "))\.", file)
                        # We've found a file for this pattern to use, set
                        # the material accordingly
                        if suffixMatch:

                            for subSettings in item[suffixRegex]:
                                try:
                                    # Setting the subroutine according to the
                                    # specified settings for this match
                                    mat.setSubroutine(
                                        subSettings["category"], subSettings["shader"])
                                    sub = mat.getSubroutine(
                                        subSettings["category"])

                                    # Setting any fields that this subroutine
                                    # might need
                                    for field in subSettings["fields"]:
                                        for fieldKey, fieldValue in field.items():
                                            try:
                                                sub.setField(fieldKey, os.path.join(
                                                    search_dir, file) if fieldValue == "[name]" else fieldValue)
                                            except NameError:
                                                print("Field '" + fieldKey + "' in subroutine '" +
                                                      subSettings["shader"] + "' doesn't exist, skipping.")
                                                continue
                                except ReferenceError:
                                    print(
                                        "Material Subroutine'" + subSettings["shader"] + "' doesn't exist, skipping.")
                                    continue
        except NameError:
            print("Material '" + prefix + "' already exists, skipping.")
            continue

###############################################################

# Finish UI


add_button = mset.UIButton("Add")
add_button.onClick = create_material
window.addElement(add_button)

close_button = mset.UIButton("Close")
close_button.onClick = lambda: mset.shutdownPlugin()
window.addElement(close_button)

window.visible = True
