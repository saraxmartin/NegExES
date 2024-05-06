import re

class MedicalReportTagger:
    def __init__(self, negation_terms, uncertainty_terms, conjunctions, medical_terms):
        # Define negation and uncertainty terms in Catalan
        self.negation_terms = negation_terms
        self.uncertainty_terms = uncertainty_terms
        self.conjunctions = conjunctions
        self.medical_terms = medical_terms
        
        # Define patterns for negation and uncertainty using the terms
        self.negation_pattern = re.compile('|'.join(self.negation_terms), re.IGNORECASE)
        self.uncertainty_pattern = re.compile('|'.join(self.uncertainty_terms), re.IGNORECASE)
        self.conj_pattern = re.compile('|'.join(self.conjunctions), re.IGNORECASE)
        self.medical_pattern = re.compile('|'.join(self.medical_terms), re.IGNORECASE)

    def tag_negation_and_uncertainty(self, text):
        # Initialize results list
        results = []
        # Initialize counters for each type of entity
        id = 0
        
        # Process negation terms
        for match in self.negation_pattern.finditer(text):
            start, end = match.span()
            # Create a result for the negation term
            results.append({
                "value": {"start": start, "end": end + 1, "labels": ["NEG"]},
            })
            id += 1  # Increment the negation ID counter
            
            # Determine the scope of negation
            scope_start, scope_end = self.find_negation_scope(text, start, end)
            # Create a result for the scope of negation
            results.append({
                "value": {"start": end+1, "end": scope_end+1, "labels": ["NSCO"]},
            })
            id += 1  # Increment the scope ID counter
    
        # Process uncertainty terms
        for match in self.uncertainty_pattern.finditer(text):
            start, end = match.span()
            # Create a result for the uncertainty term
            results.append({
                "value": {"start": start, "end": end, "labels": ["UNC"]},
            })
            id += 1  # Increment the uncertainty ID counter
            
            # Determine the scope of uncertainty
            scope_start, scope_end = self.find_uncertainty_scope(text, start, end)
            # Create a result for the scope of uncertainty
            results.append({
                "value": {"start": end+1, "end": scope_end+1, "labels": ["USCO"]},
            })
            id += 1  # Increment the scope ID counter
    
            # Process medical terms    
        return results
    
    def find_negation_scope(self, text, start, end):
        # Identify the scope of negation
        # For simplicity, use sentence boundaries as scope
        # This can be refined to improve accuracy
        scope_start = self.find_sentence_start(text, start)
        scope_end = self.find_sentence_end(text, end)
        
        scope_text = text[scope_start:scope_end]
        
        # Search for conjunctions within the scope text
        conj_matches = [(match.start() + scope_start, match.end() + scope_start) for match in self.conj_pattern.finditer(scope_text)]
        if len(conj_matches)>0:
            start_first_conj = conj_matches[0][0]
            scope_end = start_first_conj-1
        return scope_start, scope_end
    
    def find_uncertainty_scope(self, text, start, end):
        # Identify the scope of uncertainty
        # For simplicity, use sentence boundaries as scope
        # This can be refined to improve accuracy
        scope_start = self.find_sentence_start(text, start)
        scope_end = self.find_sentence_end(text, end)
        return scope_start, scope_end

    def find_sentence_start(self, text, index):
        # Find the start of the sentence containing the index
        while index > 0 and text[index] not in ",.?!:":
            index -= 1
        return index + 1
    
    def find_sentence_end(self, text, index):
        # Find the end of the sentence containing the index
        while index < len(text) and text[index] not in ",.?!:":
            index += 1
        return index

