import pandas as pd

folder = '/data/rxnorm/rrf/'

# Simple Concept and Atom Attributes (File = RXNSAT.RRF)
sat_header = dict({
    'RXCUI': 'Unique identifier for concept (concept id)',
    'LUI':'Unique identifier for term (no value provided)',
    'SUI':'Unique identifier for string (no value provided)',
    'RXAUI':'RxNorm atom identifier (RXAUI) or RxNorm relationship identifier (RUI).',
    'STYPE':'The name of the column in RXNCONSO.RRF or RXNREL.RRF that contains the identifier to which the attribute is attached, e.g., CUI, AUI.',
    'CODE':'"Most useful" source asserted identifier (if the source vocabulary has more than one identifier), or a RxNorm-generated source entry identifier (if the source vocabulary has none.)',
    'ATUI':'Unique identifier for attribute',
    'SATUI':'Source asserted attribute identifier (optional - present if it exists)',
    'ATN':'Attribute name (e.g. NDC). Possible values appear in RXNDOC.RRF and are described on the UMLS Attribute Names page',
    'SAB':'Abbreviation of the source of the attribute. Possible values appear in RXNSAB. RRF and are listed on the UMLS Source Vocabularies page',
    'ATV':'Attribute value described under specific attribute name on the UMLS Attribute Names page (e.g. 000023082503 where ATN = "NDC"). A few attribute values exceed 1,000 characters. Many of the abbreviations used in attribute values are explained in RXNDOC.RRF and included UMLS Abbreviations Used in Data Elements page',
    'SUPPRESS':'Suppressible flag. Values = O, Y, or N. Reflects the suppressible status of the attribute. N - Attribute is not suppressed. O - Attribute is suppressed at source level. Y - Attribute is suppressed by RxNorm editors.',
    'CVF':'Content view flag. RxNorm includes one value, "4096", to denote inclusion in the Current Prescribable Content subset. All rows with CVF="4096" can be found in the subset.'
})

# Concept Names and Sources (File = RXNCONSO.RRF)
conso_header = dict({
    'RXCUI':'RxNorm Unique identifier for concept (concept ID)',
    'LAT':'Language of Term',
    'TS':'Term status (no value provided)',
    'LUI':'Unique identifier for term (no value provided)',
    'STT':'String type (no value provided)',
    'SUI':'Unique identifier for string (no value provided)',
    'ISPREF':'Atom status - preferred (Y) or not (N) for this string within this concept (no value provided)',
    'RXAUI':'Unique identifier for atom (RxNorm Atom ID)',
    'SAUI':'Source asserted atom identifier [optional]',
    'SCUI':'Source asserted concept identifier [optional]',
    'SDUI':'Source asserted descriptor identifier [optional]',
    'SAB':'Source abbreviation',
    'TTY':'Term type in source',
    'CODE':'"Most useful" source asserted identifier (if the source vocabulary has more than one identifier), or a RxNorm-generated source entry identifier (if the source vocabulary has none.)',
    'STR':'String',
    'SRL':'Source Restriction Level (no value provided)',
    'SUPPRESS':'Suppressible flag. Values = N, O, Y, or E. N - not suppressible. O - Specific individual names (atoms) set as Obsolete because the name is no longer provided by the original source. Y - Suppressed by RxNorm editor. E - unquantified, non-prescribable drug with related quantified, prescribable drugs. NLM strongly recommends that users not alter editor-assigned suppressibility.',
    'CVF':'Content view flag. RxNorm includes one value, "4096", to denote inclusion in the Current Prescribable Content subset. All rows with CVF="4096" can be found in the subset.'
})

s = pd.read_csv(f'{folder}/RXNSAT.RRF', sep='|', header=0,index_col=False, names=sat_header.keys())  
c = pd.read_csv(f'{folder}/RXNCONSO.RRF', sep='|', header=0, index_col=False, names=conso_header.keys())

# query_rxcuis = sat[sat.ATV == '513ecb5b-062f-455f-b798-1c9a54222ff3']
# filter_list = query_rxcuis.to_numpy()
# sat.query('RXCUI.isin(@filter_list)')

query_rxcuis = pd.DataFrame( {'RXCUI': rxcuis} )

print('hello')


#
#
#
#
#

