#!/usr/bin/env python3
"""Apply live Word numbering to a built .docx. See docx_fields for what each pass does.

Run: python apply_fields.py Paper_v20.docx
"""
import sys
from docx import Document
import docx_fields

path = sys.argv[1]
d = Document(path)
st = docx_fields.apply(d)
d.save(path)
print("apply_fields: %d equations, %d captions, %d cross-references"
      % (st.get("equations", 0), st.get("captions", 0), st.get("refs", 0)))
