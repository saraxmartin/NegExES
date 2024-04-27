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
        entity_id = 0  # Initialize entity ID counter
        
        # Process negation terms
        for match in self.negation_pattern.finditer(text):
            start, end = match.span()
            entity_id += 1
            # Create a result with the specified fields
            results.append({
                "value": {"start": start, "end": end, "labels": ["NEG"]},
                "id": f"ent{entity_id}",
                "from_name": "label",
                "to_name": "text",
                "type": "labels"
            })
            # Determine the scope of negation
            scope_start, scope_end = self.find_negation_scope(text, start, end)
            entity_id += 1
            results.append({
                "value": {"start": scope_start, "end": scope_end, "labels": ["NSCO"]},
                "id": f"ent{entity_id}",
                "from_name": "label",
                "to_name": "text",
                "type": "labels"
            })
        # Process uncertainty terms
        for match in self.uncertainty_pattern.finditer(text):
            start, end = match.span()
            entity_id += 1
            results.append({
                "value": {"start": start, "end": end + 1, "labels": ["UNC"]},
                "id": f"ent{entity_id}",
                "from_name": "label",
                "to_name": "text",
                "type": "labels"
            })
            # Determine the scope of uncertainty
            scope_start, scope_end = self.find_uncertainty_scope(text, start, end)
            entity_id += 1
            results.append({
                "value": {"start": scope_start, "end": scope_end, "labels": ["USCO"]},
                "id": f"ent{entity_id}",
                "from_name": "label",
                "to_name": "text",
                "type": "labels"
            })

        # Process medical terms
        for match in self.medical_pattern.finditer(text):
            start, end = match.span()
            results.append({
                "value": {"start": start, "end": end, "labels": ["UMLS"]},
                "id": f"ent{entity_id}",
                "from_name": "label",
                "to_name": "text",
                "type": "labels"
            })
        
        return results


    # def tag_medical_terms(self, text):
    #     # Initialize results list
    #     results = []
        
        
    #     return results
    
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

class NegationTagger:
    def __init__(self, sentence='', phrases=None, rules=None, negP=True):
        # Initialize sentence, phrases, rules, and negP flag
        self.__sentence = sentence
        self.__phrases = phrases
        self.__rules = rules
        self.__negTaggedSentence = ''
        self.__scopesToReturn = []
        self.__negationFlag = None
        
        # Process rules and apply them to the sentence
        self.apply_rules()
        
        # Process negation and uncertainty based on rules
        self.process_negation_and_uncertainty(negP)

    def apply_rules(self):
        # Initialize filler
        filler = '_'
        
        # Apply rules to the sentence
        for rule in self.__rules:
            reformatRule = re.sub(r'\s+', filler, rule[0].strip())
            self.__sentence = rule[3].sub(' ' + rule[2].strip() + reformatRule + rule[2].strip() + ' ', self.__sentence)
        
        # Process phrases
        for phrase in self.__phrases:
            phrase = re.sub(r'([.^$*+?{\\|()[\]])', r'\\\1', phrase)
            splitPhrase = phrase.split()
            joiner = r'\W+'
            joinedPattern = r'\b' + joiner.join(splitPhrase) + r'\b'
            reP = re.compile(joinedPattern, re.IGNORECASE)
            m = reP.search(self.__sentence)
            if m:
                self.__sentence = self.__sentence.replace(m.group(0), '[PHRASE]' + re.sub(r'\s+', filler, m.group(0).strip()) + '[PHRASE]')
    
    def process_negation_and_uncertainty(self, negP):
        # Initialize flags and variables
        overlapFlag = 0
        prenFlag = 0
        postFlag = 0
        prePossibleFlag = 0
        postPossibleFlag = 0
        
        # Process tokens in the sentence
        sentenceTokens = self.__sentence.split()
        sentencePortion = ''
        aScopes = []
        sb = []
        
        # Check for [PREN] tags
        for i in range(len(sentenceTokens)):
            if sentenceTokens[i][:6] == '[PREN]':
                prenFlag = 1
                overlapFlag = 0
                
            if sentenceTokens[i][:6] in ['[CONJ]', '[PSEU]', '[POST]', '[PREP]', '[POSP]']:
                overlapFlag = 1
                
            if i + 1 < len(sentenceTokens):
                if sentenceTokens[i + 1][:6] == '[PREN]':
                    overlapFlag = 1
                    if sentencePortion.strip():
                        aScopes.append(sentencePortion.strip())
                    sentencePortion = ''
            
            if prenFlag == 1 and overlapFlag == 0:
                sentenceTokens[i] = sentenceTokens[i].replace('[PHRASE]', '[NEGATED]')
                sentencePortion = sentencePortion + ' ' + sentenceTokens[i]
            
            sb.append(sentenceTokens[i])
        
        if sentencePortion.strip():
            aScopes.append(sentencePortion.strip())
        
        # Reverse sentence tokens for POST checks
        sentencePortion = ''
        sb.reverse()
        sentenceTokens = sb
        sb2 = []
        
        # Check for [POST] tags
        for i in range(len(sentenceTokens)):
            if sentenceTokens[i][:6] == '[POST]':
                postFlag = 1
                overlapFlag = 0
                
            if sentenceTokens[i][:6] in ['[CONJ]', '[PSEU]', '[PREN]', '[PREP]', '[POSP]']:
                overlapFlag = 1
                
            if i + 1 < len(sentenceTokens):
                if sentenceTokens[i + 1][:6] == '[POST]':
                    overlapFlag = 1
                    if sentencePortion.strip():
                        aScopes.append(sentencePortion.strip())
                    sentencePortion = ''
            
            if postFlag == 1 and overlapFlag == 0:
                sentenceTokens[i] = sentenceTokens[i].replace('[PHRASE]', '[NEGATED]')
                sentencePortion = sentenceTokens[i] + ' ' + sentencePortion
            
            sb2.insert(0, sentenceTokens[i])
        
        if sentencePortion.strip():
            aScopes.append(sentencePortion.strip())
        
        # Update the sentence with the tokens
        self.__negTaggedSentence = ' '.join(sb2)
        
        # Handle possible negations
        if negP:
            sentenceTokens = sb2
            sb3 = []
            
            # Check for [PREP] tags
            for i in range(len(sentenceTokens)):
                if sentenceTokens[i][:6] == '[PREP]':
                    prePossibleFlag = 1
                    overlapFlag = 0
                
                if sentenceTokens[i][:6] in ['[CONJ]', '[PSEU]', '[POST]', '[PREN]', '[POSP]']:
                    overlapFlag = 1
                
                if i + 1 < len(sentenceTokens):
                    if sentenceTokens[i + 1][:6] == '[PREP]':
                        overlapFlag = 1
                        if sentencePortion.strip():
                            aScopes.append(sentencePortion.strip())
                        sentencePortion = ''
                
                if prePossibleFlag == 1 and overlapFlag == 0:
                    sentenceTokens[i] = sentenceTokens[i].replace('[PHRASE]', '[POSSIBLE]')
                    sentencePortion = sentencePortion + ' ' + sentenceTokens[i]
            
                sb3 += [sentenceTokens[i]]
        
            if sentencePortion.strip():
                aScopes.append(sentencePortion.strip())
        
            # Reverse sentence tokens for POSP checks
            sentencePortion = ''
            sb3.reverse()
            sentenceTokens = sb3 
            sb4 = []
            
            # Check for [POSP] tags
            for i in range(len(sentenceTokens)):
                if sentenceTokens[i][:6] == '[POSP]':
                    postPossibleFlag = 1
                    overlapFlag = 0
                
                if sentenceTokens[i][:6] in ['[CONJ]', '[PSEU]', '[PREN]', '[PREP]', '[POST]']:
                    overlapFlag = 1
                
                if i + 1 < len(sentenceTokens):
                    if sentenceTokens[i + 1][:6] == '[POSP]':
                        overlapFlag = 1
                        if sentencePortion.strip():
                            aScopes.append(sentencePortion.strip())
                        sentencePortion = ''
                
                if postPossibleFlag == 1 and overlapFlag == 0:
                    sentenceTokens[i] = sentenceTokens[i].replace('[PHRASE]', '[POSSIBLE]')
                    sentencePortion = sentenceTokens[i] + ' ' + sentencePortion
            
                sb4.insert(0, sentenceTokens[i])
        
            if sentencePortion.strip():
                aScopes.append(sentencePortion.strip())
        
            # Update the negation tagged sentence
            self.__negTaggedSentence = ' '.join(sb4)
        
        # Determine negation flags
        if '[NEGATED]' in self.__negTaggedSentence:
            self.__negationFlag = 'negated'
        elif '[POSSIBLE]' in self.__negTaggedSentence:
            self.__negationFlag = 'possible'
        else:
            self.__negationFlag = 'affirmed'
        
        # Replace filler with spaces
        self.__negTaggedSentence = self.__negTaggedSentence.replace('_', ' ')
        
        # Prepare the scopes to return
        for line in aScopes:
            tokensToReturn = []
            thisLineTokens = line.split()
            for token in thisLineTokens:
                if token[:6] not in ['[PREN]', '[PREP]', '[POST]', '[POSP]']:
                    tokensToReturn.append(token)
            self.__scopesToReturn.append(' '.join(tokensToReturn))

    def get_neg_tagged_sentence(self):
        return self.__negTaggedSentence
    
    def get_negation_flag(self):
        return self.__negationFlag
    
    def get_scopes(self):
        return self.__scopesToReturn
    
    def __str__(self):
        text = self.__negTaggedSentence
        text += '\t' + self.__negationFlag
        text += '\t' + '\t'.join(self.__scopesToReturn)
        return text

if __name__ == "__main__":
    tagger = MedicalReportTagger()
    input_data = {"data": {"cmbd": "null", "id": "19026587", "docid": "null", "page": "null", "paragraph": "null", "text": " n\u00ba historia clinica: ** *** *** n\u00baepisodi: ******** sexe: home data de naixement: 16.05.1936 edat: 82 anys procedencia cex mateix hosp servei urologia data d'ingres 24.07.2018 data d'alta 25.07.2018 08:54:04 ates per ***************, *****; ****************, ****** informe d'alta d'hospitalitzacio motiu d'ingres paciente que ingresa de forma programada para realizacion de uretrotomia interna . antecedents alergia a penicilina y cloramfenicol . no habitos toxicos. antecedentes medicos: bloqueo auriculoventricular de primer grado hipertension arterial. diverticulosis extensa insuficiencia renal cronica colelitiasis antecedentes quirurgicos: exeresis de lesiones cutaneas con anestesia local protesis total de cadera cordectomia herniorrafia inguinal proces actual varon de 81a que a raiz de episodio de hematuria macroscopica se realiza cistoscopia que es negativa para lesiones malignas pero se objetiva estenosis de uretra . se intentan dilataciones progresivas en el gabinete de urologia sin exito. se solicita estudio de imagen que confirma la existencia de estenosis a nivel d uretra bulbar por lo que se indica uretrtomia interna. exploracio complementaria uretrocistografia retrograda + cums (11/2017): la uretrografia retrograda muestra una uretra anterior con dos estenosis focales a nivel de uretra peneana y bulbar, aunque se observa paso de contraste retrogrado a vejiga. vejiga de correcta capacidad (250 cc de contraste), de paredes trabeculadas y con diverticulos, el mayor de ellos en cara posterolateral izquierda, sin observarse defectos de replecion. la uretrografia miccional muestra una uretra prostatica dilatada, sin claras estenosis focales confirmandose la existencia de las dos estenosis de uretra anterior descritas previamente. moderado residuo postmiccional en vejiga asi como en el interior del diverticulo posterolateral izquierdo descrito. uretroscopia (10/2017) falsa via a nivel de uretra peneana, siguiendo la uretra se detecta gran estenosis que no permite el paso de una guia. nhc ** *** *** (********) age-v-uro 1/2 lopd evolucio clinica el 24 de julio de 2018 con el consentimiento informado del paciente y sin contraindicacion preoperatoria se realiza uretrotomia interna sin incidencias. tras el procedimiento el paciente es trasladado a la planta de hospitalizacion siendo portador de lavado vesical continuo. posteriormente se mantiene en buen estado general, afebril, hemodinamicamente estable y con buen control del dolor. aclarado progresivo de la orina con los lavados vesicales continuos, que permiten su retirada, conserva correcta diuresis. tolerancia correcta a dieta oral. dada la buena evolucion se decide alta domiciliaria siendo portador de sonda vesical. orientacio diagnostica n40.0 hiperplasia prostatica benigna sense simptomes en les vies urinaries inferiors procediments 04.81 injeccio en el nervi periferic d'anestesic per a analgesia 58.0 uretrotomia. excisio de septe uretral, uretrostomia perineal, extraccio de calcul uretral per incisio sonda vesical profilaxis antibiotica, antilucerosa y antitrombotica tractament i recomanacions a l'alta -abundante ingesta de liquidos entorno a dos litros y medio de agua al dia. -puede orinar con restos de sangre durante las proximas semanas. -es normal que sienta escozor al orinar y que tenga algun escape de orina y urgencia miccional al retirar la sonda vesical. mantener sonda vesical durante 14 dias (dos semanas). ciprofloxacino 500mg cada 12h durante dos semanas. -paracetamol 1 g cada 8 horas si molestias. -si fiebre mayor de 38\u00bac, empeoramiento claro del estado general o imposibilidad miccional por obstruccion de sonda vesical o despues de su retirada, consultar con el servicio de urgencias. -control en consultas externas de urologia segun cita en hoja adjunta. destinacio a l'alta: a domicili nhc ** *** *** (********) age-v-uro 2/2 lopd"}}


    text = input_data["data"]["text"]
    
    # Run the tagger
    results = tagger.tag_negation_and_uncertainty(text)
    
    # Print the results or compare them with expected predictions
    print(results)
