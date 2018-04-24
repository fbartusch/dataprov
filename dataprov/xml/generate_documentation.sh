xsltproc --stringparam title "Dataprov Metadata Schema" \
        --stringparam searchIncludedSchemas true \
        --stringparam searchImportedSchemas true \
        --stringparam linksFile links.xml \
        xs3p/xs3p.xsl cwl/cwlCommandLineTool.xsd > schema_doc/cwl/cwlCommandLineTool.html

xsltproc --stringparam title "Dataprov Metadata Schema" \
        --stringparam searchIncludedSchemas true \
        --stringparam searchImportedSchemas true \
        --stringparam linksFile links.xml \
        xs3p/xs3p.xsl cwl/cwltool.xsd > schema_doc/cwl/cwltool.html

xsltproc --stringparam title "Dataprov Metadata Schema" \
        --stringparam searchIncludedSchemas true \
        --stringparam searchImportedSchemas true \
        --stringparam linksFile links.xml \
        xs3p/xs3p.xsl dataObject.xsd > schema_doc/dataObject.html

xsltproc --stringparam title "Dataprov Metadata Schema" \
        --stringparam searchIncludedSchemas true \
        --stringparam searchImportedSchemas true \
        --stringparam linksFile links.xml \
        xs3p/xs3p.xsl dataObjectList.xsd > schema_doc/dataObjectList.html

xsltproc --stringparam title "Dataprov Metadata Schema" \
        --stringparam searchIncludedSchemas true \
        --stringparam searchImportedSchemas true \
        --stringparam linksFile links.xml \
        xs3p/xs3p.xsl commandLine.xsd > schema_doc/commandLine.html

xsltproc --stringparam title "Dataprov Metadata Schema" \
	--stringparam searchIncludedSchemas true \
	--stringparam searchImportedSchemas true \
	--stringparam linksFile links.xml \
	xs3p/xs3p.xsl dataprov.xsd > schema_doc/dataprov.html

xsltproc --stringparam title "Dataprov Metadata Schema" \
        --stringparam searchIncludedSchemas true \
        --stringparam searchImportedSchemas true \
        --stringparam linksFile links.xml \
        xs3p/xs3p.xsl dict.xsd > schema_doc/dict.html

xsltproc --stringparam title "Dataprov Metadata Schema" \
        --stringparam searchIncludedSchemas true \
        --stringparam searchImportedSchemas true \
        --stringparam linksFile links.xml \
        xs3p/xs3p.xsl directory.xsd > schema_doc/directory.html

xsltproc --stringparam title "Dataprov Metadata Schema" \
        --stringparam searchIncludedSchemas true \
        --stringparam searchImportedSchemas true \
        --stringparam linksFile links.xml \
        xs3p/xs3p.xsl docker/dockerContainer.xsd > schema_doc/docker/dockerContainer.html

xsltproc --stringparam title "Dataprov Metadata Schema" \
        --stringparam searchIncludedSchemas true \
        --stringparam searchImportedSchemas true \
        --stringparam linksFile links.xml \
        xs3p/xs3p.xsl docker.xsd > schema_doc/docker.html

xsltproc --stringparam title "Dataprov Metadata Schema" \
        --stringparam searchIncludedSchemas true \
        --stringparam searchImportedSchemas true \
        --stringparam linksFile links.xml \
        xs3p/xs3p.xsl executor.xsd > schema_doc/executor.html

xsltproc --stringparam title "Dataprov Metadata Schema" \
        --stringparam searchIncludedSchemas true \
        --stringparam searchImportedSchemas true \
        --stringparam linksFile links.xml \
        xs3p/xs3p.xsl file.xsd > schema_doc/file.html

xsltproc --stringparam title "Dataprov Metadata Schema" \
        --stringparam searchIncludedSchemas true \
        --stringparam searchImportedSchemas true \
        --stringparam linksFile links.xml \
        xs3p/xs3p.xsl fileList.xsd > schema_doc/fileList.html

xsltproc --stringparam title "Dataprov Metadata Schema" \
        --stringparam searchIncludedSchemas true \
        --stringparam searchImportedSchemas true \
        --stringparam linksFile links.xml \
	xs3p/xs3p.xsl history.xsd > schema_doc/history.html

xsltproc --stringparam title "Dataprov Metadata Schema" \
        --stringparam searchIncludedSchemas true \
        --stringparam searchImportedSchemas true \
        --stringparam linksFile links.xml \
        xs3p/xs3p.xsl host.xsd > schema_doc/host.html

xsltproc --stringparam title "Dataprov Metadata Schema" \
        --stringparam searchIncludedSchemas true \
        --stringparam searchImportedSchemas true \
        --stringparam linksFile links.xml \
        xs3p/xs3p.xsl operation.xsd > schema_doc/operation.html

xsltproc --stringparam title "Dataprov Metadata Schema" \
        --stringparam searchIncludedSchemas true \
        --stringparam searchImportedSchemas true \
        --stringparam linksFile links.xml \
        xs3p/xs3p.xsl singularity/singularityContainer.xsd > schema_doc/singularity/singularityContainer.html

xsltproc --stringparam title "Dataprov Metadata Schema" \
        --stringparam searchIncludedSchemas true \
        --stringparam searchImportedSchemas true \
        --stringparam linksFile links.xml \
        xs3p/xs3p.xsl singularity.xsd > schema_doc/singularity.html

xsltproc --stringparam title "Dataprov Metadata Schema" \
        --stringparam searchIncludedSchemas true \
        --stringparam searchImportedSchemas true \
        --stringparam linksFile links.xml \
        xs3p/xs3p.xsl snakemake.xsd > schema_doc/snakemake.html
