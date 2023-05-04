# PHENOCLINICS DICTS

# Custom dicts to define the 'type' of object
INDIVIDUALS_DICT = {
    "diseases": "array_object_complex",
    "ethnicity": "object_id_label",
    "exposures": "array_object_complex",
    "geographicOrigin": "object_id_label",
    "id": "simple",
    "interventionsOrProcedures": "array_object_complex",
    "measures": "array_object_measures",
    "pedigrees": "array_object_complex",
    "phenotypicFeatures": "array_object_complex",
    "sex": "object_id_label",
    "treatments": "array_object_complex"
}

BIOSAMPLES_DICT = {
    "biosampleStatus": "object_id_label",
    "collectionDate": "simple",
    "collectionMoment": "simple",
    "diagnosticMarkers": "array_object_id_label",
    "histologicalDiagnosis": "object_id_label",
    "id": "simple",
    "individualId": "simple",
    "measurements": "array_object_measures",
    "obtentionProcedure": "object_complex",
    "pathologicalStage": "array_object_id_label",
    "pathologicalTnmFinding": "array_object_id_label",
    "phenotypicFeatures": "array_object_complex",
    "sampleOriginDetail": "object_id_label",
    "sampleOriginType": "object_id_label",
    "sampleProcessing": "object_id_label",
    "sampleStorage": "object_id_label",
    "tumorGrade": "object_id_label",
    "tumorProgression": "object_id_label",
}

# Filtering terms dict as 'filtering term: (target entity, target schema term, label)'
FILTERING_TERMS_DICT = {
    "female": ("individuals", "sex.label", None),
    "NCIT:C16576": ("individuals", "sex.id", "female"),
    "male": ("individuals", "sex.label", None),
    "NCIT:C20197": ("individuals", "sex.id", "male"),
    "England": ("individuals", "geographicOrigin.label", None),
    "GAZ:00002641": ("individuals", "geographicOrigin.id", "England"),
    "Northern Ireland": ("individuals", "geographicOrigin.label", None),
    "GAZ:00002638": ("individuals", "geographicOrigin.id", "Northern Ireland"),
    "Chinese": ("individuals", "ethnicity.label", None),
    "NCIT:C41260": ("individuals", "ethnicity.id", "Chinese"),
    "Black or Black British": ("individuals", "ethnicity.label", None),
    "NCIT:C16352": ("individuals", "ethnicity.id", "Black or Black British"),
    "blood": ("biosamples", "sampleOriginType.label", None),
    "UBERON:0000178": ("biosamples", "sampleOriginType.id", "blood"),
    "reference sample": ("biosamples", "biosampleStatus.label", None),
    "EFO:0009654": ("biosamples", "biosampleStatus.id", "reference sample"),
    "asthma": ("individuals", "diseases.diseaseCode.label", None),
    "ICD10:J45": ("individuals", "diseases.diseaseCode.id", "asthma"),
    "obesity": ("individuals", "diseases.diseaseCode.label", None),
    "ICD10:E66": ("individuals", "diseases.diseaseCode.id", "obesity"),
}