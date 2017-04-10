#!/bin/bash

SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPTDIR" || exit -1

VERSION=0.12.5
for filename in bokeh-$VERSION.min.js \
                bokeh-widgets-$VERSION.min.js \
                bokeh-$VERSION.min.css \
                bokeh-widgets-$VERSION.min.css; do
  curl http://cdn.pydata.org/bokeh/release/$filename > $filename;
done
