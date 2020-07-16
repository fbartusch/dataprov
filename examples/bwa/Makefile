all: index map clean

clean:
	rm -r mapped_reads genome.fa.*

index:
	dataprov -i genome.fa -o genome.fa.bwt -p genome.fa.bwt.prov run bwa index genome.fa

map:
	mkdir mapped_reads && dataprov -i genome.fa.bwt -i samples/A.fastq -o mapped_reads/A.bam -p mapped_reads/A.bam.prov run 'bwa mem genome.fa samples/A.fastq > mapped_reads/A.bam'