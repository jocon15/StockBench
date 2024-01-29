
"""
To tests the export functionality we need to call the export function.

The export function will create a .xlsx file.

To ensure the function worked correctly,

1. call the function
2. loop through files in the target directory
3. use os.path.getmtime('file_path') to get the creation timestamp for the file [WINDOWS ONLY]
4. find the most recently created file in the directory
5. check cells in that file to make sure data was exported correctly
"""


