# DRAX


DRAX is a biological data collector, fetching information on gene-protein-reaction-compound relationship across multiple databases.
It was built to aid in the mapping of metabolism related components, for example to aid in the expansion of metabolic networks, automating the often monotonous, manual data collection. 

## Installation 


1. `git clone git@github.com:PedroMTQ/DRAX.git`  
2. Go to the cloned DRAX folder and run `conda env create -f drax_env.yml`
3. Run `conda activate drax_env`
4. Download the browser driver for your current OS and current browser version (e.g., [geckodriver](https://github.com/mozilla/geckodriver/releases) for Mozilla Firefox)
5. Move downloaded browser driver to `DRAX/External_Tools/Browser_Drivers/`

#### Browser drivers

DRAX supports two browsers, Mozilla Firefox and Google Chrome, please download the driver for your current browser version and add it to `DRAX/Browser_Drivers`:
- Mozilla Firefox please go to https://github.com/mozilla/geckodriver/releases
- Google Chrome please go to https://chromedriver.chromium.org/downloads 


## Using DRAX


Running DRAX within a personal computer should be straightforward, however keep in mind that in order to scrape websites with Javascript, DRAX (more specifically the package `Selenium`) needs to use a browser. To install browsers in a server you may need admin access. 

You can run the code below to test the execution:

    python DRAX --example

A typical run would look like:

    python DRAX -i input.tsv 




Data collection is possible for multiple databases:
- KEGG
- HMDB
- Biocyc

To avoid overloading these database websites, a 10 seconds pause between requests was added.

DRAX accepts the following parameters:


    python DRAX search_direction search_type -i input_path -o output_folder -rm -db db1,db2

    Mandatory arguments: --input_path / -i
    Optional arguments:  --output_folder / -o
                         --reaction_metabolites / -rm
                         --databases / -db


Where each parameter corresponds to the following:

- `input_path` - the input tsv file path. 
- `output_folder` - the output folder where the spreadsheets are stored
- `reaction_metabolites` - searches for data on each reaction's compound, which improves reaction matching across different databases
- `databases ` - databases that DRAX can search in, by default HMDB,Biocyc, and KEGG
- `politeness_timer` - time (seconds) between requests. Default is 10. Please be careful not to overleaf the corresponding databases, you might get blocked from doing future requests.






Data is  retrieved according to the information provided, for example, if the user provides the KEGG gene ID hsa:150763, then, given that the gpr search direction is used, DRAX would fetch information on this gene, the KEGG protein entries connected to this gene (i.e., 2.3.1.15) and by extent the reactions these protein(s) catalyze (i.e., R00851,R02617,R09380).


- `search_type` - starting point of the search, if the user aims to provide IDs for proteins, then it would be `protein_search`, and the same for the other types of biological instances


### Formatting input file

The input file should be a tab separated file that looks something like this:
 
  | Component  | Search direction | ID type | ID |
  | ---  | ---  | --- | --- |
  | gene |  | biocyc  | HS08548  |
  | gene | gp | hmdb  | HMDBP00087  |
  | gene | global | kegg  | hsa:150763  |
  | gene |  | uniprot  | P19367  |
  | protein |  | enzyme_ec  | 2.7.1.1  |
  | protein | global | kegg  | 2.7.1.1  |
  | protein |  | biocyc  | 2.7.1.1  |
  | protein |  | hmdb  | HMDBP00609  |
  | protein | global | kegg_ko    | K00844   |
  | protein |  | uniprot    | P19367   |
  | reaction |  | biocyc  | PROTOHEMEFERROCHELAT-RXN   |
  | reaction | rp | hmdb  | 14073   |
  | reaction |  | kegg  | R02887   |
  | compound | global | biocyc    | CPD-520   |
  | compound |  | chebi    | 27531   |
  | compound |  | chemspider    | 937   |
  | compound |  | hmdb    | HMDB0000538   |
  | compound |  | kegg    | C00093   |
  | compound |  | inchi_key  | XLYOFNOQVPJJNP-UHFFFAOYSA-N   |
  | compound |  | synonyms    | water   |

I've tried to make this example tsv extensive but some caveats remain:

- the first column corresponds to the component type you provided the ID for

- the second column the search direction, i.e., direction of the search, `global` for searching in both directions, `na` for searching only the provided IDs, without connecting to other instances, `rpg` for searching from reaction->protein->gene, and `pg`, `gpr`, `pr`,`gp`. **Keep in mind you can use multiple search directions**, e.g., `rp,pr`. This is especially useful if you want to map compounds to reactions and proteins (web crawling for kegg and biocyc can be only `rp`, but hmdb needs both `rp,pr`).

- keep in mind DRAX will always try to use all available IDs to search for more information. That is, if you start with a certain ID (e.g., kegg ID), if DRAX finds searchable information for the other databases (in this case biocyc and hmdb) then it will also collect data from those databases. This applies to different components as well, e.g., DRAX starts with gene IDs from kegg, then finds the corresponding proteins for these genes in hmdb and biocyc; DRAX (if the search direction is set to `gp,pg`) will then also find information on genes for these two additional databases.

- Some type of IDs (i.e., `enzyme_ec` and `uniprot`) can be matched with multiple databases. `synonyms` and `chebi` can also be used to query multiple databases. For example, for the line `protein | pr | uniprot | P19367`, DRAX will try to match this Uniprot ID with all the databases



### Supported input IDs

Several IDs are allowed per biological instance:

- Reaction:
    - Biocyc (e.g., "RXN66-521")
    - KEGG (e.g., "R02848")
    - HMDB (e.g., "14073")
    
- Protein:
    - enzyme EC number (e.g., "2.7.1.1")
    - KEGG (e.g., "2.7.1.1")
    - KEGG KO (e.g., "K00844")
    - Biocyc (e.g., "2.7.1.1")
    - Uniprot (e.g., "P10632")
    - HMDB (e.g., "HMDBP00609")
    

- Gene:
    - KEGG (e.g., "hsa:150763")
    - Uniprot (e.g., "P10632")
    - Biocyc (e.g., "HS08548")
    - HMDB (e.g., "HMDBP00087")

- Compound:
    - Biocyc (e.g., the ID "WATER")
    - KEGG (e.g., "C00001")
    - HMDB (e.g., "HMDB02111")
    - InChI key (e.g., "XLYOFNOQVPJJNP-UHFFFAOYSA-N")
    - Chemspider (e.g., "937")
    - Synonym  (e.g., "water")

### Output

DRAX outputs 4 tsv files: `Compounds.tsv`,`Reactions.tsv`,`Proteins.tsv`,`Genes.tsv`
Each file contains multiple instances (e.g., compound) with a tab-separated list of identifiers or other relevant information.
Specifically, all instances contain an `internal_id` which can be used for graph-based approaches cross-linking (e.g., `manuscript.py`), and often a list of identifiers and synonyms.
In the case of reactions, proteins and genes, cross-linking is available in the form of `<instance>_connected`. For example, if the user searches for all reactions of a set of proteins, then the retrieved proteins would have a list of `reactions_connected:<reaction internal_id>` depicting which reactions this protein is connected to. The same would apply for other search directions or search starting points.
Reactions also contain the list of compounds involved in this reaction, e.g.: `reaction_compounds:<C1> + <C2> <=> <C3> + <C4> + <C5>` where `CX` corresponds to a compound's `internal_id`.

Using the example above as an example (with input the enzyme EC 2.7.8.26), the output for each instance would look somewhat like:
- `Proteins.tsv`
  - internal_id:**270**	cas:DA85_04120	enzyme_ec:2.7.8.26	kegg_ko:K02233	reactions_connected:**25550**	genes_connected:**9035**	synonyms:adenosylcobinamide-gdp ribazoletransferase	synonyms:cobalamin (5'-phosphate) synthase	synonyms:cobalamin (5′-phosphate) synthase	synonyms:cobalamin synthase	synonyms:cobalamin-5'-phosphate synthase	synonyms:cobalamin-5′-phosphate synthase	synonyms:cobs	synonyms:α-ribazole ribazoletransferase
- `Reactions.tsv`
  - internal_id:**25550**	biocyc:RXN-19297	pathways:4-methylphenyl adenosylcobamide biosynthesis from adenosylcobinamide-GDP	reaction_compounds:**10310** + 6731 => 21252 + 24415 + 8385	reaction_str:adenosylcobinamide-GDP + 4-methylphenyl ribotide phosphate => 4-methylphenyl-Coβ-adenosylcobamide 5'-phosphate + GMP + H+
- `Compounds.tsv`
  - internal_id:**10310**	bigg:agdpcbi	biocyc:ADENOSYLCOBINAMIDE-GDP	chebi:60487	hmdb:HMDB12185	kegg:C06510	pubchem_cid:135398566	seed:cpd03920	synonyms:adenosine-gdp-cobinamide	synonyms:adenosylcobinamide-gdp

As can be seen, the protein (i.e., `internal_id:270`) shown above is connected to the reaction `25550` which in turn is described as the following interaction between compounds: 10310 + 6731 => 21252 + 24415 + 8385. These compounds are then listed in the `Compounds.tsv` as shown above. For visualization purposess only a small transcript is shown above.


### On search directions

The search direction  `na` removes any type of extra search besides the initial IDs provided, meaning that if the user provides the KEGG gene ID hsa:150763, we would still search for it (and retrieve gene-related data) but we would not search for its respective proteins.

The search direction `global` is an extensive search, where we can search in both directions (i.e. g->p->r and r->p->g), meaning that if the user provides the KEGG gene ID hsa:150763 we would retrieve the respective proteins 2.3.1.15, but we would then also search for all the gene IDs for the protein 2.3.1.15 (e.g., hsa:150763, ptr:107971389, csab:103215676). The same would apply to the protein and reaction search.

Should the user provide a compound name (e.g. "water") the compound search may also retrieve related compounds (since DRAX uses the each website's search bar to retrieve the most likely compound entry). However, if an ID is provided, DRAX will first search for the ID, if information is not found, then the synonyms are used as a search method.
This also applies to when the option `reaction_metabolites` is enabled and the reaction does not contain any compound ID, in that case the reaction string (e.g. "sn-Glycerol 3-phosphate + Acyl-CoA <=> 1-Acyl-sn-glycerol 3-phosphate + CoA") is parsed  and its compounds are searched using the method previously described.
DRAX can also search for information connected to compounds (i.e., reactions) by enabling the required search directions `rp,pr`


# License and copyright

This project is available under the [MIT license](https://github.com/PedroMTQ/DRAX/LICENSE).

# References and acknowledgements

> Minoru Kanehisa, Susumu Goto, KEGG: Kyoto Encyclopedia of Genes and Genomes, Nucleic Acids Research, Volume 28, Issue 1, 1 January 2000, Pages 27–30, https://doi.org/10.1093/nar/28.1.27
> 
> Caspi R, Billington R, Keseler IM, Kothari A, Krummenacker M, Midford PE, Ong WK, Paley S, Subhraveti P, Karp PD. The MetaCyc database of metabolic pathways and enzymes - a 2019 update. Nucleic Acids Res. 2020 Jan 8;48(D1):D445-D453. doi: 10.1093/nar/gkz862. PMID: 31586394; PMCID: PMC6943030.
>
> Wishart DS, Feunang YD, Marcu A, Guo AC, Liang K, Vázquez-Fresno R, Sajed T, Johnson D, Li C, Karu N, Sayeeda Z, Lo E, Assempour N, Berjanskii M, Singhal S, Arndt D, Liang Y, Badran H, Grant J, Serra-Cayuela A, Liu Y, Mandal R, Neveu V, Pon A, Knox C, Wilson M, Manach C, Scalbert A. HMDB 4.0: the human metabolome database for 2018. Nucleic Acids Res. 2018 Jan 4;46(D1):D608-D617. doi: 10.1093/nar/gkx1089. PMID: 29140435; PMCID: PMC5753273.