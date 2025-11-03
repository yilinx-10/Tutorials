import json

def convert_leaflet_to_geojson(input_filename, output_filename):
    """
    Converts a specific Leaflet JSON format to a GeoJSON FeatureCollection.

    This script is tailored to parse a JSON file containing Leaflet map data,
    find the 'addPolygons' call, and extract the necessary data to create
    a valid GeoJSON file.

    Args:
        input_filename (str): The path to the input Leaflet JSON file.
        output_filename (str): The path for the output GeoJSON file.
    """
    try:
        # Load the leaflet JSON data from the input file
        with open(input_filename, 'r', encoding='utf-8') as f:
            leaflet_data = json.load(f)

        # Navigate through the JSON structure to find the 'addPolygons' call
        add_polygons_call = None
        for call in leaflet_data.get('x', {}).get('calls', []):
            if call.get('method') == 'addPolygons':
                add_polygons_call = call
                break

        if not add_polygons_call:
            print("Error: Could not find 'addPolygons' call in the JSON file.")
            return

        # Extract the arguments from the found call
        args = add_polygons_call.get('args', [])
        if len(args) < 7:
            print("Error: 'addPolygons' arguments are not in the expected format.")
            return
            
        multipolygons = args[0]
        options = args[3]
        popup_names = args[6]

        # Extract colors and names from the data
        colors = options.get('fillColor', [])
        
        # Initialize the structure for our output GeoJSON FeatureCollection
        geojson_feature_collection = {
            "type": "FeatureCollection",
            "features": []
        }

        # Process each polygon's data
        for i in range(len(multipolygons)):
            multipolygon = multipolygons[i]
            
            # Combine latitudes and longitudes into coordinate pairs [longitude, latitude]
            # as required by the GeoJSON specification.
            cleaned = []
            for polygon in multipolygon[0]:
                lon = polygon["lng"]
                lat = polygon["lat"]
                cleaned.append([[l1, l2] for l1, l2 in zip(lon, lat)])
            
            # Safely get properties, providing defaults if arrays are misaligned
            neighborhood_name = popup_names[i] if i < len(popup_names) else "Unnamed"
            fill_color = colors[i] if i < len(colors) else "#808080" # Default gray

            # Create the GeoJSON Feature for the current neighborhood
            feature = {
                "type": "Feature",
                "properties": {
                    "id": len(geojson_feature_collection["features"]),
                    "name": neighborhood_name,
                    "color": fill_color
                },
                "geometry": {
                    "type": "MultiPolygon",
                    # GeoJSON Polygon coordinates are nested in an array (to allow for holes)
                    "coordinates": [cleaned]
                }
            }
            
            # Add the newly created feature to our collection
            geojson_feature_collection["features"].append(feature)

        # Save the complete GeoJSON FeatureCollection to the output file
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(geojson_feature_collection, f, indent=2)

        print(f"Successfully converted {len(geojson_feature_collection['features'])} neighborhoods to '{output_filename}'")

    except FileNotFoundError:
        print(f"Error: The file '{input_filename}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from the file '{input_filename}'.")
    except (KeyError, IndexError) as e:
        print(f"Error: Unexpected JSON structure. Missing key or index: {e}")


if __name__ == '__main__':
    # Define the input and output file names
    # This script assumes 'chicago.json' is in the same directory.
    INPUT_FILE = 'chicago-neighborhoods/chicago.json'
    OUTPUT_FILE = 'chicago-neighborhoods/chicago.geojson'
    
    # Run the conversion process
    convert_leaflet_to_geojson(INPUT_FILE, OUTPUT_FILE)
