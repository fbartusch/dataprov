xsltproc --stringparam title "Documentation test" \
	--stringparam searchIncludedSchemas true \
	--stringparam searchImportedSchemas true \
	--stringparam linksFile links.xml \
	xs3p.xsl dataprov.xsd > documentation/dataprov.xsd.html

xsltproc --stringparam title "Documentation test" \
        --stringparam searchIncludedSchemas true \
        --stringparam searchImportedSchemas true \
        --stringparam linksFile links.xml \
	xs3p.xsl history.xsd > documentation/history.xsd.html
