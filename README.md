abYannotate
===========

abYannotate is a simple application for annotating a batch of antibody
sequences (in FASTA format) with the locations of the CDRs.

_Note that you need `abnum` (or an equivalent program able to generate
Chothia numberintg) to use this program._

It can be used from the command line (create a config file
[`config.cfg`] based on one of the samples and type
`./abyannotate.pl -h` for help) or via a web interface.

Install the software and web interface by creating the config file and
typing:
```
./install.sh destination
```
where `destination` is the web directory in which you wish to place
the software.

Web code structure
==================

- `abyannotate.pl` is the main annotation script

- `monitor.cgi` is the CGI script called by the web interface. It
  grabs parameters, writes the sequence data to a file, runs
  `cgiwrap.cgi` in the background, waits for `cgiwrap.cgi` to create an
  HTML page and then displays that page, but substitutes the refresh
  header with a redirect header so that the HTML page is now shown
  directly.

- `cgiwrap.cgi` calculates an estimated wait time, prints the HTML page
  that refreshes itself every 10 seconds and then calls the
  `abyannotate.cgi` script (note that these two could easily be
  combined into one)!

- `abyannotate.cgi` calls the main `abyannotate.pl` script to perform
  the annnotation and then reformats into HTML if required. This then
  overwrites the refreshing page created by `cgiwrap.cgi`

