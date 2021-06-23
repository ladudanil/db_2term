<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="xml"
                doctype-system="http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"
                doctype-public="-//W3C//DTD XHTML 1.1//EN" indent="yes"/>

    <xsl:template match="/">
        <html>
            <head>
                <meta charset="utf-8"/>
                <meta name="viewport" content="width=device-width, initial-scale=1"/>
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bulma/0.7.4/css/bulma.min.css"/>
                <title>
                    sofas
                </title>
            </head>
            <body>
                <div class="container">
                    <div class="notification">
                        <h1 class="title">
                            sofas
                        </h1>
                    </div>

                    <table class="table is-bordered is-striped is-narrow is-hoverable is-fullwidth">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Price</th>
                                <th>Images</th>
                            </tr>
                        </thead>
                        <tbody>
                            <xsl:apply-templates/>
                        </tbody>
                    </table>
                </div>
            </body>
        </html>
    </xsl:template>

    <xsl:template match="item">
        <tr>
            <td style="width:30%">
                    <xsl:value-of select="name"/>
            </td>
            <td>
                <xsl:value-of select="price"/>
            </td>
            <td>
                <xsl:element name="img">
                    <xsl:attribute name="src">
                        <xsl:value-of select="url"/>
                    </xsl:attribute>
                </xsl:element>
            </td>
        </tr>
    </xsl:template>

</xsl:stylesheet>