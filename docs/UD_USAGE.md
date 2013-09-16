###Relevant Scripts###
+ ```populate_db.py``` : Database populate APIs.
+ ```gisc.py``` : The APIs to manipulate and project User Dynamics.
    

###Usage###
1. Run the _populate_db.py_ script with appropriate details for the
archive files to be processed.
2. Run the _gisc.py_ script with the preferences to be filtered.

Both of the above scripts take flagged input from bash shell. A brief
of what all are supported by the scripts are given below. For details
on each, run the file with the flag "-h" or "--help" e.g.

    python populate_db.py -h
    python gisc.py -h
    

###Brief Overview###

**populate_db.py**: The flags represent the details of the archive and
could be one of the followings:-

    + URL for the Github archive(s). _(Not implemented yet)_
    + Date for the Github archive(s). _(Not implemented yet)_
    + Directory containing the archive(s).
    + ZIP file of archive(s).
    + Archive file(s).

**gisc.py**: The flags represent parameters to filter results on and
could be one of the followings:-

    + Repository language to filter on.
    + Count of objects to be considered for the analysis.
    + Directory to plot the results.
    + Image extension for the graph.
