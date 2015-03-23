#!/usr/bin/env python

from pdfminer.converter import PDFConverter
from pdfminer.layout import LTContainer, LTText, LTTextBox, LTImage

# Similar a pdfminer/converter.py:
#class TextConverter(PDFConverter)


class BormeConverter(PDFConverter):

    def __init__(self, rsrcmgr, outfp, codec='utf-8', pageno=1,
                 laparams=None, showpageno=False, imagewriter=None):
        PDFConverter.__init__(self, rsrcmgr, outfp, codec=codec, pageno=pageno,
                              laparams=laparams)

        # ...
    # Reimplementar esta func y el LTText...
    #def receive_layout(self, ltpage):
    def receive_layout(self, ltpage):
        def render(item):
            if isinstance(item, LTContainer):
                for child in item:
                    render(child)
            elif isinstance(item, LTText):
                self.write_text(item.get_text())
            if isinstance(item, LTTextBox):
                self.write_text('\n')
            elif isinstance(item, LTImage):
                if self.imagewriter is not None:
                    self.imagewriter.export_image(item)
        if self.showpageno:
            self.write_text('Page %s\n' % ltpage.pageid)
        render(ltpage)
        self.write_text('\f')
        return
