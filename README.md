pop music corpus
===================
The most popular music, in HTML form.
---------------------

This is a script that locally mirrors a copy of mobile Wikipedia for a fuzzy
list of musicians. 

Fetching from last.fm
---------------------
The script can fetch the list of the N top artists of all time on last.fm using
the last.fm API. To get this list, run:

    artists.py top [N]

Where `[N]` is the number of artists you want to list. It will save the list in
`top-artists.txt`.

Fetching artist pages
---------------------
The script can then fetch all of the Wikipedia pages for the artists in the
`top-artists.txt` list. It does this by first searching on MusicBrainz, getting
the Wikipedia URL from there, and then downloading the source of the Wikipedia
article in Mediawiki format. Articles are saved to the `artists/` directory.
