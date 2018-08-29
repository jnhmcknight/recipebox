
# Unarchiving

If you want to use the exported data from The Recipe Box app, you will need to run this conversion program on the file. To begin, you will need to be running on Mac OS with XCode installed. Then you will need to install the pip requirements listed in `requirements.txt`. Afterward, it's as simple as running:

```bash
python unarchiver.py -r path/to/export/file -s my-bucket-name [-w recipe-box-conversion.json]
```

If you do not specify the output file, you will be able to view the output directly in your terminal. If you specify an output name other than the example one, you will need to update the application code to be able to find the right data file.

After you have the JSON data file, upload it to your S3 bucket using your chosen filename.
