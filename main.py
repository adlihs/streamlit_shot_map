import dropbox
import pandas as pd

def dropbox_list_files(path):
    """Return a Pandas dataframe of files in a given Dropbox folder path in the Apps directory.
    """
    # Configurar el token de acceso
    token = 'sl.Bf8HEf15Vg82vh1xrPd4iy4x56AUz7q0HMPfK5ggkXpy0kZypbeaxTZ2FwiA1oSxTMY8kBUomrHt490uMX5D4WlOrRtNZ5DrX8ZOn81U4UuUEbpprL7CyP4e9l3mJJ0If6DELP10'

    # Crear una instancia del cliente de Dropbox
    dbx = dropbox.Dropbox(token)

    #dbx = dropbox_connect()

    try:
        files = dbx.files_list_folder(path).entries
        files_list = []
        for file in files:
            if isinstance(file, dropbox.files.FileMetadata):
                metadata = {
                    'name': file.name,
                    'path_display': file.path_display,
                    'client_modified': file.client_modified,
                    'server_modified': file.server_modified
                }
                files_list.append(metadata)

        df = pd.DataFrame.from_records(files_list)
        return df.sort_values(by='server_modified', ascending=False)

    except Exception as e:
        print('Error getting list of files from Dropbox: ' + str(e))



dropbox_list_files('/PFSA')