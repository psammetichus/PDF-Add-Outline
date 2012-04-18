#!/usr/bin/python

#a program that uses pyPdf to add an outline--basically, an
#interactive table of contents--to a given PDF file.

#use is:
# addindex.py thefile.pdf toc.json

# the file is not written in-place; a copy is written to "output.pdf"
# the file toc.json--which can be named anything--is a simple json
# file consisting of one object or hash with the outline titles as
# keys and the 0-indexed page numbers as values. An example is given
# below.

# {
#     "Chapter 1" : 0,
#     "Chapter 2" : 20
# }

#at the moment, this only supports single-level outlines; the PDF spec
#supports multi-level outlines, which are feasible under the current
#framework, and would honestly just take a little bit more work.

#Relevant parts of the PDF spec to consult (and really, the thing's
#free and actually fairly clear reading, so don't be bashful) are
#12.3.2 (Destinations) and 12.3.3 (Document Outline), as well as 7.7.2
#(Document Catalog). Note that pyPdf apparently only supports named
#destinations, a complication unnecessary for outlines, which can use
#simple explicit destinations.

# Copyright (c)2012 Tyson Burghardt. Licensed under GPLv3.


import pyPdf
import pyPdf.pdf as PDF
import sys
import json

def name(s):
    """convenience function to construct a pdf NameObject"""
    return PDF.NameObject("/" + s)

def addOutline(pdfw, outline_dict):
    """Given a PdfFileWriter @pdfw, adds an outline defined by the
    outline dictionary @outline_dict."""
    olitems = len(outline_dict)
    #get length of @pdf's _objects list; from this
    # we can derive the next and subsequent idorefs
    idoix = len(pdfw._objects)+1
    idorefs = [PDF.IndirectObject(x+idoix,0,pdfw) 
               for x in range(olitems+1)]
    
    #build outline dictionary
    ol = PDF.DictionaryObject()
    ol.update({name("Type") : name("Outlines"),
               name("First") : idorefs[1],
               name("Last") : idorefs[-1],
               name("Count") : PDF.NumberObject(olitems)})
    
    #build outline items
    olitems = []
    #have to sort the values or they get inserted in random order
    odv = {v:k for k,v in outline_dict.items()}
    for i in sorted(odv.keys()):
        oli = PDF.DictionaryObject()
        oli.update({name("Title") : PDF.TextStringObject(odv[i]),
                    name("Parent") : idorefs[0],
                    name("Dest") : makeDest(pdfw, i)})
        olitems.append(oli)
    for ix,olitem in enumerate(olitems[:-1]):
        olitem.update({name("Next") : idorefs[ix+2]})
    for ix,olitem in enumerate(olitems[1:]):
        olitem.update({name("Prev") : idorefs[ix+1]})
    
    #now add outline dict to pdf obj
    pdfw._addObject(ol)
    for i in olitems:
        pdfw._addObject(i)
    
    #lastly, change catalog
    pdfw._root.getObject().update({name("Outlines") : idorefs[0]})
    
def makeDest(pdfw, pg):
    """function to make an explicit destination, given a PdfFileWriter
    @pdfw and a page number @pg.
    
    We are using explicit destinations (see S12.3.2 of the PDF
    spec). This consists of an array headed by an indirect ref to the
    page, followed by the name XYZ and three size/zoom specifiers,
    which we leave null so that the page remains in the default
    state."""
    d = PDF.ArrayObject()
    d.append(pdfw.getPage(pg).indirectRef)
    d.append(name("XYZ"))
    d.append(PDF.NullObject())
    d.append(PDF.NullObject())
    d.append(PDF.NullObject())
    return d
        
def main():
    #PdfFileWriter needs to have the original PDF (that the
    #PdfFileReader it depends on depends on) still open
    #at the time of writing. If it's closed, you get a 
    #Value I/O error
    w = pyPdf.PdfFileWriter()
    f = file(sys.argv[1], "rb")
    r = pyPdf.PdfFileReader(f)
    for i in r.pages:
        w.addPage(i)
    g = file(sys.argv[2], "r")
    oldict = json.load(g)
    addOutline(w, oldict)
    outputFile = open("output.pdf", "wb")
    w.write(outputFile)
    outputFile.close()
    g.close()
    f.close()

if __name__ == '__main__':
	main()

