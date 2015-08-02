= Use Case =

Rename a hierarchy of people tags in photographies.

= Example of Use =

First, do a backup of your photos.

```sh
renamePeopleTags.py -d  ~/Images -o rename.yaml
```

Edit `rename.yaml` so as to obtain something like:
```yaml
John: People/Smith/John
jony: People/Smith/John
Alex: People/Alexander
```

And the call the script to do the renaming:

```sh
renamePeopleTags.py -d  ~/Images -i rename.yaml
```

= Licence =

GPL v3



