###Events###
Events are the activities that user perform on particular repo. There
are many events but not limited to:

    Create Event - Creation of a repository.
    Follow Event - User starts following a repository.
    Push Event - User works and pushes the repository.
    Watch Event - User has watched a repository.
For details on events, visit http://developer.github.com/v3/activity/events/types/


###Dataset###
The dataset is in the form of JSON dumps of GitHub events of various
repositories and users. Find the sample files [here](sample_jsons/).


###Database Schema###
Considering the format and variability in dataset, MongoDB, a schema 
free database looked to be the best choice. More benefits but not
limited to, are as under:

    + A document-based data model. The basic unit of storage is
    analogous to JSON, Python dictionaries etc. This is a rich data
    structure capable of holding arrays and other documents. This means
    one can often represent a complete dataset in a single entity that
    would require several tables to properly represent in a relational
    db. This is especially useful if the data is immutable.
    
    + Deep query-ability. MongoDB supports dynamic queries on document
    using a document-based query language, nearly powerful as SQL.
    
    + No schema migrations. The code defines schema.

```Database Name```: **gisc**

For our requirement we maintain three collections to store the events.
They are as under:

    1. AllEvent - PushEvent, WatchEvent, FollowEvent
    2. FollowEvent - FollowEvent
    3. WatchEvent - WatchEvent


###USER DYNAMICS###

####Problem Statement####
Find the relationships between the watchers/committers with the
popularity of a repo. How does the push/watch event of a highly
popular user affect the growth curve of a GitHub repository?

####Algorithm####
+ Select the topmost users aka high profile users(users list
with their followers in descending order). This is information is
obtained from FollowEvent collection.

+ Then get all the WatchEvents of each of these high profile users.
For every WatchEvent by a user on a repository, get all the events
on that repo till 24 hours after the WatchEvent.

+ Then we determine the plot’s eligibility to be drawn. We plot if
the growth curve shows significant deviation from its predicted curve.
The predicted curve is drawn since the timestamp of the WatchEvent.
The data prior to this event is used for prediction. Least squares
polynomial fitting is used to draw the curve.

+ Then we determine the genuineness of a user’s impact on that repo.
If a user’s WatchEvent has actually caused the change in the growth
curve. _(Not implemented yet)_

    + Get all the changes in watch counts of all the repos the user
    has started watching. The initial and final watch counts differ
    by a timestamp of 1 day.
    + Calculate the standard deviation of all these differences.
    + If the standard is low “enough”, we deem the impact to be
    genuine, i.e the growth change has happened due to the user
    watching the repository.

+ We draw a growth curve for this repository based on the above one
day events. The x-axis contains the timestamps represented as float
values and y-axis has the number of watchers of the repo at the
respective timestamps.

####Implementation####
Implementation for the above algorithm is [here](../gisc/gisc.py).

####Sample Plots####

+ [Sample 1](sample_plots/hmans:greenfield.png)
+ [Sample 2](sample_plots/kakutani:hitchhiker-guide.png)
+ [Sample for a language](sample_plots/Java:jabennett86:storm.png)

####Plot properties####
    
+ X-axis indicates the timestamps.
+ Y-axis indicates watcher counts at respective timestamps.
+ Left red line(Impact Start) indicates the timestamp of the
high profile WatchEvent.
+ The second red line(Impact End) is 24 hours after the start
of the user impact.
+ The text below the plot is of the format:

    + USER --> REPO_URL, or,
    + REPO_LANGUAGE : USER --> REPO_URL, for a language.


###FLOCKING USERS###
Using the above generated growth curve, we also try to observe as how
groups work in social coding. Do some users act as flock when one of
them starts watching a repository. _(Not implemented yet)_
