from lxml import etree

dom = etree.parse("results/meblium.xml")
xslt = etree.parse("xslt/meblium.xslt")
transform = etree.XSLT(xslt)
result = transform(dom)

with open('results/meblium.html', 'wb') as f:
        f.write(etree.tostring(result, pretty_print=True))
