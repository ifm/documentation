# -*- coding: utf-8 -*-
#############################################
# Copyright 2025-present ifm electronic, gmbh
# SPDX-License-Identifier: Apache-2.0
#############################################
import json
import os

import pandas as pd
from jsonschema import RefResolver

# Required File Paths
OUTPUT_DIRECTORY = "./generated_docs/"
ROOT_PARAM_FILES_PATH = "parameter-specification/release/"
ODS_PARAMETER_SPEC_FILE_PATH = (
    ROOT_PARAM_FILES_PATH + "algo/ODS_APP_ALGO.paramSchema.schema.JSON"
)
PDS_PARAMETER_SPEC_FILE_PATH = (
    ROOT_PARAM_FILES_PATH + "algo/PDS.paramSchema.schema.JSON"
)
CAMERA_3D_DI_PARAMETER_SPEC_FILE_PATH = (
    ROOT_PARAM_FILES_PATH + "algo/DI_IRS2381.paramSchema.schema.JSON"
)
CAMERA_3D_4M_PARAMETER_SPEC_FILE_PATH = (
    ROOT_PARAM_FILES_PATH
    + "configuration/ports/port/sensor/any/any/standard_range4m/acquisition.schema.json"
)
CAMERA_3D_2M_PARAMETER_SPEC_FILE_PATH = (
    ROOT_PARAM_FILES_PATH
    + "configuration/ports/port/sensor/any/any/standard_range2m/acquisition.schema.json"
)
CAMERA_3D_CYCLIC_PARAMETER_SPEC_FILE_PATH = (
    ROOT_PARAM_FILES_PATH
    + "configuration/ports/port/sensor/any/any/cyclic_4m_2m_4m_2m/acquisition.schema.json"
)
CAMERA_2D_AUTO_PARAMETER_SPEC_FILE_PATH = (
    ROOT_PARAM_FILES_PATH
    + "configuration/ports/port/sensor/OV9782/any/standard_autoexposure2D/acquisition.schema.json"
)
CAMERA_2D_MANUAL_PARAMETER_SPEC_FILE_PATH = (
    ROOT_PARAM_FILES_PATH
    + "configuration/ports/port/sensor/OV9782/any/standard_manualexposure2D/acquisition.schema.json"
)

ROOT_DIAG_FILE_PATH = "./"
DIAGNOSTIC_FILE_PATH = ROOT_DIAG_FILE_PATH + "40-definitions.json"

files_to_process = {
    ODS_PARAMETER_SPEC_FILE_PATH: "ods",
    PDS_PARAMETER_SPEC_FILE_PATH: "pds",
    CAMERA_3D_DI_PARAMETER_SPEC_FILE_PATH: "camera_3d_di",
    CAMERA_3D_4M_PARAMETER_SPEC_FILE_PATH: "camera_3d_4m",
    CAMERA_3D_2M_PARAMETER_SPEC_FILE_PATH: "camera_3d_2m",
    CAMERA_3D_CYCLIC_PARAMETER_SPEC_FILE_PATH: "camera_3d_cyclic",
    CAMERA_2D_AUTO_PARAMETER_SPEC_FILE_PATH: "camera_2d_auto",
    CAMERA_2D_MANUAL_PARAMETER_SPEC_FILE_PATH: "camera_2d_manual",
    DIAGNOSTIC_FILE_PATH: "diagnostic",
}

schemas_to_split = {
    "pds": [
        "/properties/customization/properties/getPallet",
        "/properties/customization/properties/getRack",
        "/properties/customization/properties/volCheck",
        "/properties/customization/properties/getItem",
        "/properties/parameter/properties/getPallet",
        "/properties/parameter/properties/getRack",
        "/properties/parameter/properties/getItem",
        "/properties/parameter/properties/volCheck",
    ],
    "diagnostic": [
        "/diagnostics",
    ],
}


def resolve_references(schema, resolver):
    """Recursively resolve $ref references in the schema."""
    if isinstance(schema, dict):
        keys_to_process = list(schema.keys())
        for key in keys_to_process:
            if key.isdigit():  # Check if the key is numeric
                # Replace the numeric key with "X"
                schema["X"] = schema.pop(key)
                key = "X"  # Update the key for further processing
            if key == "$ref":
                ref = schema.pop("$ref")
                # if not ref.startswith("http") and not ref.startswith("#"):
                # ref = os.path.normpath(os.path.join(base_uri, ref))
                resolved = resolver.resolve(ref)[1]
                schema.update(resolve_references(resolved, resolver))
            else:
                schema[key] = resolve_references(schema[key], resolver)
    elif isinstance(schema, list):
        for i, s in enumerate(schema):
            schema[i] = resolve_references(s, resolver)
    return schema


def extract_subschema(schema, json_path: str):
    """Extract a subschema from the main schema based on the JSON path."""
    keys = json_path.strip("/").split("/")
    subschema = schema
    for key in keys:
        subschema = subschema[key]
    return subschema


# Function to recursively extract "properties" from the schema
def extract_properties(schema, parent_key=""):
    properties_list = []
    if "properties" in schema:
        for prop, details in schema["properties"].items():
            # Skip the property if it contains the "protected" attribute
            if details.get("attributes") and (
                "protected" in details["attributes"]
                or "private" in details["attributes"]
            ) or details.get("readOnly"):
                continue

            key_name = f"{parent_key}.{prop}" if parent_key else prop

            # Recursively handle nested properties
            if "properties" in details:
                properties_list.extend(extract_properties(details, key_name))
            else:
                # Hardcoded fixes for specific properties
                ## channelValue description
                if "channelValue" in key_name and "description" not in details:
                    details["description"] = "Crosstalk can be avoided by ensuring that cameras have different channels assigned. For overlapping fields of view, pick different values at least two steps apart, for example 0 and 2."
                
                elif "minAmplitude" in key_name:
                    details["description"] = ("Invalidates pixels where the amplitude (reflected light) drops below the minimum threshold.")

                ## default Values for `activePorts` in ODS
                elif "activePorts" in key_name or "voPorts" in key_name:
                    details["default"] = "Depends on the ports configured in ODS application instance."

                property_entry = {
                    "Property": f"`{key_name}`",
                    "Type": details.get("type", "N/A"),
                    "Description": details.get("description", "N/A"),
                    "Default": details.get("default", "N/A"),
                    "Minimum": details.get("minimum", "N/A"),
                    "Maximum": details.get("maximum", "N/A"),
                    "Enum": f"`{details.get('enum', 'N/A')}`",
                    "Attributes": details.get("attributes", "N/A"),
                }

                properties_list.append(property_entry)

    # Process patternProperties
    if "patternProperties" in schema:
        for pattern, details in schema["patternProperties"].items():
            key_name = f"{parent_key}.{pattern}" if parent_key else pattern

            # Recursively handle nested pattern properties
            if "properties" in details or "patternProperties" in details:
                properties_list.extend(extract_properties(details, key_name))
            else:
                properties_list.append(
                    {
                        "Property": f"`{key_name}`",
                        "Type": details.get("type", "N/A"),
                        "Description": details.get("description", "N/A"),
                        "Default": details.get("default", "N/A"),
                        "Minimum": details.get("minimum", "N/A"),
                        "Maximum": details.get("maximum", "N/A"),
                        "Enum": f"`{details.get('enum', 'N/A')}`",
                    }
                )
    return properties_list


def json_to_md(file_name: str, data, subpath=None, is_schema=False):
    """This function converts a JSON schema or a normal JSON file to a Markdown table.
    file_name: str: The name of the JSON file, without extension.
    data: dict: The JSON data.
    subpath: str: The subpath within the schema to process (optional, for schemas).
    is_schema: bool: Whether the input is a JSON schema (default: False).
    """
    if is_schema:
        # Handle JSON schema-specific logic
        if subpath:
            data = extract_subschema(data, subpath)

        # Extract properties from the schema
        properties = extract_properties(data)

    else:
        if subpath:
            keys = subpath.strip("/").split("/")
            for key in keys:
                if key in data:
                    data = data[key]
                else:
                    raise KeyError(
                        f"Key '{key}' not found in the JSON at path '{subpath}'")
        # Handle normal JSON files
        if isinstance(data, dict):
            # Convert dictionary to a list of key-value pairs
            properties = [{"Key": k, "Value": v} for k, v in data.items()]
        elif isinstance(data, list):
            # Convert list of dictionaries directly
            properties = []
            for item in data:
                clean_item = {}
                for k, v in item.items():
                    # Rename 'targets' to 'source'
                    new_key = "source" if k == "targets" else k
                    # Clean values
                    if isinstance(v, list):
                        clean_item[new_key] = ', '.join(map(str, v))
                    elif isinstance(v, str):
                        clean_item[new_key] = v.replace('\n', '<br>')
                    else:
                        clean_item[new_key] = v
                properties.append(clean_item)
        else:
            raise ValueError(
                "Unsupported JSON format. Must be a dict or a list.")
                
    # Convert to DataFrame for display
    df = pd.DataFrame(properties)

    # Convert DataFrame to Markdown table
    print(f"Converting: {file_name} to Markdown table")
    markdown_table = df.to_markdown(index=False)
    output_file = (
        f"{file_name}.md"
        if not subpath
        else f"{file_name}_{subpath.strip('/').replace('/', '_')}.md"
    )
    output_dir = OUTPUT_DIRECTORY
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, output_file), "w") as f:
        f.write(markdown_table)


def main():
    # Load all the schemas available in the directory, to be able
    # to resolve cross-file references later on.
    schema_store = {}
    for root, _, files in os.walk(ROOT_PARAM_FILES_PATH):
        for file in files:
            if file.endswith(".json") or file.endswith(".JSON"):
                with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                    schema_store[file] = json.load(f)

    for file_path, file_name in files_to_process.items():
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Check if the file is a JSON schema (contains "properties" or "$ref")
        is_schema = "properties" in data or "$ref" in json.dumps(data)

        if is_schema:
            # Create a resolver with the schema store
            resolver = RefResolver.from_schema(data, store=schema_store)

            # Resolve references in the schema
            data = resolve_references(data, resolver)

        # Generate Markdown for each subpath if defined in schemas_to_split
        if file_name in schemas_to_split:
            for subpath in schemas_to_split[file_name]:
                json_to_md(file_name, data, subpath, is_schema=is_schema)

        # Generate Markdown for the main schema or normal JSON
        json_to_md(file_name, data, is_schema=is_schema)


if __name__ == "__main__":
    main()
