If you've ever gotten a PDF that you wished had an outline, then this
simple tool can help.

PDF Outlines are bookmarks that act like an interactive table of contents.
The spec supports nested outlines, which wouldn't be hard to add, but this
tool only does single-level outlines.

The program uses pyPdf, which should be available from your distro's repository;
you can also pip install it.

The spec json file is a simple associate array mapping outline titles to 
(0-indexed) page numbers. If your PDF has PageLabel ranges set (ie, if the
PDF reader's stated page number is not the same as the logical page number)
then you'll have to allow for this.

Licensed under GPLv3.

