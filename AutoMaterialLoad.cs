using UnityEditor;
using UnityEngine;
using System.IO;

public class AssignTexturesToMaterials : EditorWindow
{
    private string folderPath = "";

    [MenuItem("Tools/Assign Textures to Materials")]
    public static void ShowWindow()
    {
        GetWindow<AssignTexturesToMaterials>("Texture to Material Assigner");
    }

    private void OnGUI()
    {
        GUILayout.Label("Assign Textures to Materials", EditorStyles.boldLabel);

        if (GUILayout.Button("Select Texture Folder"))
        {
            folderPath = EditorUtility.OpenFolderPanel("Select Folder Containing Textures", "", "");
        }

        if (!string.IsNullOrEmpty(folderPath))
        {
            GUILayout.Label($"Selected Folder: {folderPath}");
        }

        if (GUILayout.Button("Assign Textures"))
        {
            if (string.IsNullOrEmpty(folderPath))
            {
                EditorUtility.DisplayDialog("Error", "Please select a folder first!", "OK");
                return;
            }

            AssignTextures();
        }
    }

    private void AssignTextures()
    {
        string[] textureFiles = Directory.GetFiles(folderPath, "*.*", SearchOption.AllDirectories);
        int assignedCount = 0;

        foreach (string texturePath in textureFiles)
        {
            if (Path.GetExtension(texturePath).ToLower() == ".meta")
                continue;

            string textureName = Path.GetFileNameWithoutExtension(texturePath);
            string relativePath = GetRelativePath(texturePath);

            Debug.Log($"🔍 Checking Texture: {textureName}, Path: {relativePath}");

            Texture2D texture = AssetDatabase.LoadAssetAtPath<Texture2D>(relativePath);

            if (texture == null)
            {
                Debug.LogWarning($"❌ Texture not found in AssetDatabase: {relativePath}");
                continue;
            }

            Debug.Log($"✅ Texture Loaded: {texture.name}");

            // Extract the material name by removing suffixes
            string materialName = textureName
                .Replace("_BaseColor", "")
                .Replace("_Normal", "")
                .Replace("_Metallic", "")
                .Replace("_ambientocclusion", "");

            Debug.Log($"🔍 Extracted Material Name: {materialName}");

            // Find the material by the extracted name
            string[] materialGuids = AssetDatabase.FindAssets(materialName + " t:Material");

            if (materialGuids.Length == 0)
            {
                Debug.LogWarning($"⚠️ No material found for {materialName}");
                continue;
            }

            foreach (string guid in materialGuids)
            {
                string materialPath = AssetDatabase.GUIDToAssetPath(guid);
                Material material = AssetDatabase.LoadAssetAtPath<Material>(materialPath);

                if (material != null)
                {
                    Debug.Log($"🎨 Assigning {texture.name} to Material: {material.name}");

                    // Ensure material uses the Standard Shader
                    if (material.shader.name != "Standard")
                    {
                        material.shader = Shader.Find("Standard");
                        Debug.Log($"🔄 Changed Shader to Standard for {material.name}");
                    }

                    // Set rendering mode to Cutout
                    material.SetFloat("_Mode", 1); // 1 = Cutout mode
                    material.EnableKeyword("_ALPHATEST_ON");
                    material.renderQueue = (int)UnityEngine.Rendering.RenderQueue.AlphaTest;
                    Debug.Log($"✂️ Set Rendering Mode to Cutout for {material.name}");

                    // Set Alpha Cutoff slider to 1
                    material.SetFloat("_Cutoff", 1f);
                    Debug.Log($"🔳 Set Alpha Cutoff to 1 for {material.name}");

                    // Set Albedo Color to White
                    material.SetColor("_Color", Color.white);
                    Debug.Log($"🎨 Set Albedo Color to White (255,255,255) for {material.name}");

                    // Assign textures based on suffix
                    if (textureName.Contains("_BaseColor"))
                        material.SetTexture("_MainTex", texture);
                    else if (textureName.Contains("_Normal"))
                    {
                        material.SetTexture("_BumpMap", texture);
                        FixNormalMap(relativePath);
                    }
                    else if (textureName.Contains("_Metallic"))
                        material.SetTexture("_MetallicGlossMap", texture);
                    else if (textureName.Contains("_ambientocclusion"))
                        material.SetTexture("_OcclusionMap", texture);
                    else
                        Debug.LogWarning($"⚠️ Unknown texture type: {texture.name}");

                    assignedCount++;
                }
            }
        }

        AssetDatabase.SaveAssets();
        EditorUtility.DisplayDialog("Assignment Complete", $"Assigned {assignedCount} textures to materials.", "OK");
    }

    private string GetRelativePath(string absolutePath)
    {
        return "Assets" + absolutePath.Replace(Application.dataPath, "").Replace('\\', '/');
    }

    // ✅ Fix Normal Map issue (Mark it as a Normal Map)
    private void FixNormalMap(string texturePath)
    {
        TextureImporter textureImporter = AssetImporter.GetAtPath(texturePath) as TextureImporter;

        if (textureImporter != null && textureImporter.textureType != TextureImporterType.NormalMap)
        {
            textureImporter.textureType = TextureImporterType.NormalMap;
            textureImporter.SaveAndReimport();
            Debug.Log($"🔧 Marked {texturePath} as Normal Map.");
        }
    }
}
