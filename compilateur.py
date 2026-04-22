from enum import Enum , auto
import sys
MAXINT = 32767 #D'après l'énoncé 
LONG_MAX_CHAINE = 50 #D'après l'énoncé max 50 caractères
LONG_MAX_IDENT = 20 #D'après l'énoncé max 20 caractères
NB_MOTS_RESERVES = 12
TABLE_MOTS_RESERVES = []  # Tableau des mots-clés réservés 
NB_IDENT_MAX = 100
DERNIERE_ADRESSE_VAR_GLOB = -1
 
# ==== MACHINE VIRTUELLE ====
EMPI = 0
CONT = 1
AFFE = 2
LIRE = 3
ECRL = 4
ECRE = 5
ECRC = 6
FINC = 7
ADDI = 8
MOIN = 9
MULT = 10
DIVI = 11
STOP = 12
ALLE = 13
ALSN = 14

NOM_OPCODE = {
    EMPI:'EMPI', CONT:'CONT', AFFE:'AFFE', LIRE:'LIRE',
    ECRL:'ECRL', ECRE:'ECRE', ECRC:'ECRC', FINC:'FINC',
    ADDI:'ADDI', MOIN:'MOIN', MULT:'MULT', DIVI:'DIVI', STOP:'STOP',
    ALLE:'ALLE', ALSN:'ALSN'
}
 
TAILLE_MAX_MEM = 10000
P_CODE  = [0] * TAILLE_MAX_MEM
MEM_VAR = [0] * TAILLE_MAX_MEM
PILEX   = [0] * TAILLE_MAX_MEM
PILOP   = [0] * TAILLE_MAX_MEM
CO        = 0
SOM_PILEX = -1
SOM_PILOP = -1
# ==== TABLE DES IDENTIFICATEURS ====


class T_ENREG_IDENT:

    def __init__(self, nom: str):
        self.nom = nom
        self.type = None      # vide 
        self.adresse = None   # vide
        self.valeur = None    # vide

TABLE_IDENT = []    # Table des identificateurs 
TABLE_INDEX = []    # Table d'index pour le tri 


def chercher(nom: str) -> int:
    """Recherche dichotomique """
    gauche = 0
    droite = len(TABLE_INDEX) - 1
    
    while gauche <= droite:
        milieu = (gauche + droite) // 2
        nom_milieu = TABLE_IDENT[TABLE_INDEX[milieu]].nom
        
        if nom_milieu == nom:
            return milieu  # trouvé
        elif nom_milieu < nom:
            gauche = milieu + 1
        else:
            droite = milieu - 1
    
    return -1  # Non trouvé


def trouver_position_insertion(nom: str) -> int:
    gauche = 0
    droite = len(TABLE_INDEX)
    
    while gauche < droite:
        milieu = (gauche + droite) // 2
        if TABLE_IDENT[TABLE_INDEX[milieu]].nom < nom:
            gauche = milieu + 1
        else:
            droite = milieu
    
    return gauche


def inserer(nom: str) -> int:
    """Tri par insertion : """
    if len(TABLE_IDENT) >= NB_IDENT_MAX:
        erreur(0, f"Table des identificateurs pleine (max :  {NB_IDENT_MAX})")
    
    nouvelle_entree = T_ENREG_IDENT(nom)
    TABLE_IDENT.append(nouvelle_entree)
    nouvel_indice = len(TABLE_IDENT) - 1
    
    # Tri par insertion 
    pos = trouver_position_insertion(nom)
    TABLE_INDEX.insert(pos, nouvel_indice)
    
    return nouvel_indice


def affiche_table_ident() -> None:
    print("\n" + "=" * 50)
    print("       TABLE DES IDENTIFICATEURS")
    print("=" * 50)
    print(f"{'Nom':<20} {'Type':<10} {'Adresse':<10} {'Valeur':<10}")
    print("-" * 50)
    
    for idx in TABLE_INDEX:
        entry = TABLE_IDENT[idx]
        type_str = str(entry.type) if entry.type else ""
        adr_str = str(entry.adresse) if entry.adresse is not None else ""
        val_str = str(entry.valeur) if entry.valeur is not None else ""
        print(f"{entry.nom:<20} {type_str:<10} {adr_str:<10} {val_str:<10}")
        print("\n" + "-" * 50)
    
    print("-" * 50)
    print(f"Total : {len(TABLE_IDENT)} identificateur(s)")
    print("=" * 50)


class TokenType(Enum) : 
    MOTCLE = auto() 
    IDENT = auto()
    ENT = auto() ; 
    CH = auto() 
    PTVIRG = auto()
    VIRG = auto() 
    POINT = auto() 
    DEUXPTS = auto() 
    PAROUV = auto()
    PARFER = auto() 
    INF = auto()
    SUP = auto()
    EG = auto()
    PLUS = auto() 
    MOINS = auto()
    MULTI = auto()
    DIVI = auto()
    INFE = auto()
    SUPE = auto()
    DIFF = auto()
    AFF = auto()
    EOF = auto()


class Token: 
    typ: TokenType
    value: object = None
    line : int=1

def erreur(num_ligne:int , message:str) -> None : #Fonction erreur avec un message et le numéro de ligne où le programme s'arrête
    print(f"Erreur ligne {num_ligne} : {message}")
    sys.exit(1)

class Lexiqueur :  

    def __init__(self, file_name : str):
        self.file_name = file_name  #chemin du fichier
        self.f = open(file_name,"r", encoding='utf-8')#ouverture du fichier
        self.carlu = " "
        self.nombre = None 
        self.chaine = None
        self.num_ligne = 1
        self.lire_car() 

    def lire_car(self) -> None:
        if self.carlu == '':
            erreur(self.num_ligne, "fin de fichier atteint")
        c = self.f.read(1)  # Lit un caractère
        if c == '\n':
            self.num_ligne += 1  # Incrémente le numéro de ligne
        self.carlu = c  
    
    def sauter_separateurs(self) -> None:
        while self.carlu in (' ', '\n', '\t', '{'):
            if self.carlu == '{' : #Ouverture d'un commentaire 
                long = 1
                self.lire_car() 
                while long > 0 : 
                    if self.carlu == '' :
                        erreur(self.num_ligne,'Fin de fichier atteint sans fermer le commentaire')
                    elif self.carlu == '{' :
                        long += 1 
                    elif self.carlu == '}' :#cas 
                        long -=1 
                    self.lire_car()
            else :
                self.lire_car()

    def reco_entier(self) -> TokenType : 
        self.nombre = 0 
        while self.carlu.isdigit() : 
            chiffre = int(self.carlu)
            if self.nombre > (MAXINT - chiffre) // 10 : #test si MAXINT est plus grand avant l'ajout 
                erreur(self.num_ligne, f"On dépasse l'entier maximal étant de capacité : {MAXINT}")
            self.nombre = self.nombre * 10 + chiffre
            self.lire_car()  
        return TokenType.ENT
    
    def reco_chaine(self)  -> TokenType :
        self.chaine = ""
        delimiteur = self.carlu  
        self.lire_car()
        while True : 
            if self.carlu == '' :
                erreur(self.num_ligne, 'Chaine non fermée')
            if self.carlu == delimiteur or (delimiteur in ("'", "'", "'") and self.carlu in ("'", "'", "'")):
                self.lire_car()
                if self.carlu == delimiteur or (delimiteur in ("'", "'", "'") and self.carlu in ("'", "'", "'")):
                    self.chaine += "'"
                    self.lire_car()
                else :
                    break
            else :
                self.chaine += self.carlu
                self.lire_car()

        if len(self.chaine) > LONG_MAX_CHAINE :
            erreur(self.num_ligne, f'Chaine de caractères trop longue : max {LONG_MAX_CHAINE} de caractères compris')
        return TokenType.CH
    
    def reco_symb(self) -> TokenType :
        c = self.carlu
        if c == ';' :
            self.lire_car()
            return TokenType.PTVIRG
        elif c == '.' : 
            self.lire_car()
            return TokenType.POINT
        elif c == '=' :
            self.lire_car()
            return TokenType.EG
        elif c == '+' :
            self.lire_car()
            return TokenType.PLUS
        elif c == '*' :
            self.lire_car()
            return TokenType.MULTI
        elif c == '/' :
            self.lire_car()
            return TokenType.DIVI
        elif c == '-' :
            self.lire_car()
            return TokenType.MOINS
        elif c == '(' :
            self.lire_car()
            return TokenType.PAROUV
        elif c == ')' :
            self.lire_car()
            return TokenType.PARFER
        elif c == ',' :
            self.lire_car()
            return TokenType.VIRG
        elif c == '<' :
            self.lire_car()
            if self.carlu == '=' :
                self.lire_car()
                return TokenType.INFE
            elif self.carlu == '>':
                self.lire_car()
                return TokenType.DIFF  # <>
            else:
                return TokenType.INF
        elif c == '>':
            self.lire_car()
            if self.carlu == '=':
                self.lire_car()
                return TokenType.SUPE  # >=
            else:
                return TokenType.SUP  # >
        elif c == ':':
            self.lire_car()
            if self.carlu == '=':
                self.lire_car()
                return TokenType.AFF  # :=
            else:
                return TokenType.DEUXPTS  # :
        else:
            erreur(self.num_ligne, f"Symbole non reconnu : {c}")
    
    def reco_ident_ou_mot_reserve(self) -> TokenType:
        self.chaine = ""
        while self.carlu.isalnum() or self.carlu == '_': #lettre chiffre ou _
            if len(self.chaine) < LONG_MAX_IDENT:
                self.chaine += self.carlu.upper()  # Convertit en maj pour reconnaitre
            self.lire_car()
        i = 0
        while (i < NB_MOTS_RESERVES) and (TABLE_MOTS_RESERVES[i] < self.chaine):
            i += 1
        est_mot_reserve = (i < NB_MOTS_RESERVES and TABLE_MOTS_RESERVES[i] == self.chaine)
        if est_mot_reserve:
            return TokenType.MOTCLE
        else:
            return TokenType.IDENT

    def analex(self) -> TokenType:
        self.sauter_separateurs()
        if self.carlu == '':
            return TokenType.EOF
        if self.carlu.isdigit():
            return self.reco_entier()
        if self.carlu == "'" or self.carlu == "'" or self.carlu == "'" or self.carlu == '"':
            return self.reco_chaine()
        if self.carlu.isalpha(): #si c'est une suite de lettres
            return self.reco_ident_ou_mot_reserve()
        return self.reco_symb() #sinon un symbole

    def terminer(self) -> None:
        self.f.close()

class Analyseur : 
    def __init__(self, lexer : Lexiqueur):
        self.lexer : Lexiqueur = lexer
        self.unilex : TokenType= None 
        self.chaine : str = None
        self.nombre : int = None


    def lecture(self) -> bool :  
        global CO, P_CODE
        if self.unilex == TokenType.MOTCLE and self.chaine == 'LIRE' :
            self.lire_unilex()
            if self.unilex == TokenType.PAROUV :
                self.lire_unilex()
                if self.unilex == TokenType.IDENT :
                    nom = self.chaine
                    idx = chercher(nom)
                    if idx == -1 :
                        erreur(self.lexer.num_ligne, f"Erreur semantique lecture : variable '{nom}' non declaree")
                    if TABLE_IDENT[TABLE_INDEX[idx]].type != 'variable':
                        erreur(self.lexer.num_ligne, f"Erreur semantique lecture : '{nom}' n'est pas une variable")
                    P_CODE[CO]   = EMPI
                    P_CODE[CO+1] = TABLE_IDENT[TABLE_INDEX[idx]].adresse
                    P_CODE[CO+2] = LIRE
                    CO += 3
                    self.lire_unilex()
                    while (self.unilex == TokenType.VIRG) :
                        self.lire_unilex()
                        if self.unilex == TokenType.IDENT :
                            nom = self.chaine
                            idx = chercher(nom) 
                            if idx == -1 : 
                                erreur(self.lexer.num_ligne, f"Erreur semantique lecture : variable '{nom}' non declaree")
                            if TABLE_IDENT[TABLE_INDEX[idx]].type != 'variable':
                                erreur(self.lexer.num_ligne, f"Erreur semantique lecture : '{nom}' n'est pas une variable")
                            P_CODE[CO]   = EMPI
                            P_CODE[CO+1] = TABLE_IDENT[TABLE_INDEX[idx]].adresse
                            P_CODE[CO+2] = LIRE
                            CO += 3
                            self.lire_unilex()
                        else :
                            return False 
                    if self.unilex == TokenType.PARFER:
                        self.lire_unilex()
                        return True
                    else : 
                        return False 
                else :
                    return False 
            else : 
                return False 
        else : 
            return False 

    def ecriture(self) -> bool :
        global CO, P_CODE
        if self.unilex == TokenType.MOTCLE and self.chaine == 'ECRIRE' :
            self.lire_unilex()
            if self.unilex == TokenType.PAROUV :
                self.lire_unilex()
                # Cas ECRIRE() sans argument → ECRL (saut de ligne)
                if self.unilex == TokenType.PARFER :
                    P_CODE[CO] = ECRL
                    CO += 1
                    self.lire_unilex()
                    return True
                # Sinon au moins une expression
                if not self.ecr_exp() :
                    return False
                while self.unilex == TokenType.VIRG :
                    self.lire_unilex()
                    if not self.ecr_exp() :
                        return False
                if self.unilex == TokenType.PARFER :
                    self.lire_unilex()
                    return True
                else :
                    return False
            else :
                return False
        else :
            return False 
    
    def lire_unilex(self) :
        self.unilex = self.lexer.analex() 
        self.chaine = self.lexer.chaine
        self.nombre = self.lexer.nombre 
    
    def prog(self) -> bool:
        global CO, P_CODE
        if self.unilex == TokenType.MOTCLE and self.chaine == 'PROGRAMME':
            self.lire_unilex()
            if self.unilex == TokenType.IDENT:
                self.lire_unilex()
                if self.unilex == TokenType.PTVIRG:
                    self.lire_unilex()
                    # Déclarations optionnelles
                    if self.unilex == TokenType.MOTCLE and self.chaine == 'CONST':
                        if not self.decl_const():
                            return False
                    if self.unilex == TokenType.MOTCLE and self.chaine == 'VAR':
                        if not self.decl_var():
                            return False
                    if not self.bloc():
                        return False
                    P_CODE[CO] = STOP
                    CO += 1 
                    if self.unilex == TokenType.POINT:
                        self.lire_unilex()
                        return True
        return False
                 
    def bloc(self) -> bool :
        if self.unilex == TokenType.MOTCLE and self.chaine == 'DEBUT' :
            self.lire_unilex()
            if not self.instruction() :
                return False 
            while self.unilex == TokenType.PTVIRG:
                self.lire_unilex()
                # Le ; final avant FIN est interdit
                if self.unilex == TokenType.MOTCLE and self.chaine == 'FIN':
                    erreur(self.lexer.num_ligne,"Erreur Syntaxique ; avant le FIN ")
                if not self.instruction():
                    return False 
            if self.unilex == TokenType.MOTCLE and self.chaine == 'FIN':
                self.lire_unilex()
                return True
            else :
                return False 
        else : 
            return False 
    
    def instruction(self) -> bool : 
        if self.unilex == TokenType.MOTCLE and self.chaine == 'SI' :
            return self.inst_cond()
        else : 
            return self.inst_non_cond()
    
    def inst_non_cond(self) -> bool : 
        if self.unilex == TokenType.IDENT : 
            return self.affectation() 
        elif self.unilex == TokenType.MOTCLE and self.chaine == 'LIRE':
            return self.lecture()
        elif self.unilex == TokenType.MOTCLE and self.chaine == 'ECRIRE':
            return self.ecriture()
        elif self.unilex == TokenType.MOTCLE and self.chaine == 'DEBUT':
            return self.bloc()
        elif self.unilex == TokenType.MOTCLE and self.chaine == 'TANTQUE':
            return self.inst_repe()
        else:
            return False
    def inst_cond(self) -> bool:
        global CO, P_CODE, SOM_PILOP, PILOP
        self.lire_unilex()  
        if not self.exp():
            return False
        if not (self.unilex == TokenType.MOTCLE and self.chaine == 'ALORS'):
            return False
        P_CODE[CO] = ALSN
        SOM_PILOP += 1
        PILOP[SOM_PILOP] = CO + 1  
        CO += 2
        self.lire_unilex()
        # Après ALORS 
        if self.unilex == TokenType.MOTCLE and self.chaine == 'SI':
            if not self.inst_cond():
                return False
            P_CODE[PILOP[SOM_PILOP]] = CO
            SOM_PILOP -= 1
            return True
        if not self.inst_non_cond():
            return False
        if self.unilex == TokenType.MOTCLE and self.chaine == 'SINON':
            P_CODE[PILOP[SOM_PILOP]] = CO + 2
            SOM_PILOP -= 1
            P_CODE[CO] = ALLE
            SOM_PILOP += 1
            PILOP[SOM_PILOP] = CO + 1
            CO += 2
            self.lire_unilex()  
            if not self.instruction():
                return False
            P_CODE[PILOP[SOM_PILOP]] = CO
            SOM_PILOP -= 1
        else:
            # Pas de SINON 
            P_CODE[PILOP[SOM_PILOP]] = CO
            SOM_PILOP -= 1
        return True
    def inst_repe(self) -> bool : 
        global CO, P_CODE, SOM_PILOP, PILOP
        self.lire_unilex() 
        adresse_debut = CO
        if not self.exp() :
            return False
        P_CODE[CO] = ALSN
        SOM_PILOP += 1 
        PILOP[SOM_PILOP] = CO +1 
        CO +=2 
        if not (self.unilex == TokenType.MOTCLE and self.chaine == 'FAIRE') :
            return False 
        self.lire_unilex()
        if not self.instruction() :
            return False 
        P_CODE[PILOP[SOM_PILOP]] = CO+2
        SOM_PILOP -= 1
        P_CODE[CO] = ALLE
        P_CODE[CO+1] = adresse_debut
        CO += 2 
        return True 

    def affectation(self) -> bool : 
        global CO , P_CODE
        if self.unilex == TokenType.IDENT :
            nom_var = self.chaine
            # Vérification sémantique : la variable doit être déclarée
            idx = chercher(nom_var)
            if idx == -1:
                erreur(self.lexer.num_ligne, f"Erreur semantique affectation : variable '{nom_var}' non declaree")
            # Vérification sémantique : doit être une variable (pas une constante)
            if TABLE_IDENT[TABLE_INDEX[idx]].type != 'variable':
                erreur(self.lexer.num_ligne, f"Erreur semantique affectation : '{nom_var}' n'est pas une variable")
            
            adr = TABLE_IDENT[TABLE_INDEX[idx]].adresse
            P_CODE[CO] = EMPI
            P_CODE[CO+1] = adr
            CO += 2
            self.lire_unilex()
            if self.unilex == TokenType.AFF :
                self.lire_unilex()
                if not self.exp():
                    return False
                P_CODE[CO] = AFFE
                CO += 1
                return True
            else :
                return False 
        else :
            return False 

    
    def ecr_exp(self) -> bool :
        global CO, P_CODE
        if self.unilex == TokenType.CH :
            chaine = self.chaine
            P_CODE[CO] = ECRC
            for i, c in enumerate(chaine):
                P_CODE[CO+1+i] = ord(c)
            P_CODE[CO+1+len(chaine)] = FINC
            CO += len(chaine) + 2
            self.lire_unilex()
            return True 
        elif self.exp() :
            P_CODE[CO] = ECRE
            CO += 1
            return True
        else :
            return False
    
    def terme(self) -> bool:
        global CO, P_CODE
        if self.unilex == TokenType.ENT:
            P_CODE[CO]   = EMPI
            P_CODE[CO+1] = self.nombre
            CO += 2
            self.lire_unilex()
            return True
        elif self.unilex == TokenType.IDENT:
            nom = self.chaine
            idx = chercher(nom)
            if idx == -1:
                erreur(self.lexer.num_ligne, f"Erreur semantique terme : identificateur '{nom}' non declare")
            entree = TABLE_IDENT[TABLE_INDEX[idx]]
            if entree.type == 'constante' and entree.typc == 1:
                erreur(self.lexer.num_ligne, f"Erreur semantique terme : constante '{nom}' est de type chaine")
            if entree.type == 'constante':
                P_CODE[CO]   = EMPI
                P_CODE[CO+1] = entree.valeur
                CO += 2
            else:
                P_CODE[CO]   = EMPI
                P_CODE[CO+1] = entree.adresse
                P_CODE[CO+2] = CONT
                CO += 3
            self.lire_unilex()
            return True
        elif self.unilex == TokenType.PAROUV:
            self.lire_unilex()
            if self.exp():
                if self.unilex == TokenType.PARFER:
                    self.lire_unilex()
                    return True
                else:
                    return False
            else:
                return False
        elif self.unilex == TokenType.MOINS:
            self.lire_unilex()
            co_avant = CO
            if not self.terme():
                return False
            taille = CO - co_avant
            for k in range(taille - 1, -1, -1):
                P_CODE[co_avant + 2 + k] = P_CODE[co_avant + k]
            P_CODE[co_avant]   = EMPI
            P_CODE[co_avant+1] = 0
            P_CODE[CO+2] = MOIN
            CO += 3
            return True
        else:
            return False
        
    def op_bin(self) -> bool :
        global SOM_PILOP , PILOP
        if self.unilex == TokenType.PLUS :
            SOM_PILOP += 1 
            PILOP[SOM_PILOP] = ADDI
            self.lire_unilex()
            return True 
        elif self.unilex == TokenType.MOINS :
            SOM_PILOP += 1
            PILOP[SOM_PILOP] = MOIN
            self.lire_unilex()
            return True 
        elif self.unilex == TokenType.MULTI :
            SOM_PILOP += 1 
            PILOP[SOM_PILOP] = MULT
            self.lire_unilex()
            return True 
        elif self.unilex == TokenType.DIVI :
            SOM_PILOP += 1 
            PILOP[SOM_PILOP] = DIVI
            self.lire_unilex()
            return True 
        else : 
            return False 

    def definir_constante(self, nom, ul) -> bool:
        # Table pour les constantes chaîne et compteur global
        global NB_CONST_CHAINE, TABLE_CONST_CHAINE  
        if 'NB_CONST_CHAINE' not in globals():
            NB_CONST_CHAINE = 0
        if 'TABLE_CONST_CHAINE' not in globals():
            TABLE_CONST_CHAINE = []
        if chercher(nom) != -1:
            return False
        idx = inserer(nom)
        TABLE_IDENT[idx].type = 'constante'
        if ul == TokenType.ENT:
            TABLE_IDENT[idx].typc = 0
            TABLE_IDENT[idx].valeur = self.lexer.nombre
        else:
            TABLE_IDENT[idx].typc = 1
            NB_CONST_CHAINE += 1
            TABLE_CONST_CHAINE.append(self.lexer.chaine)
            TABLE_IDENT[idx].valeur = NB_CONST_CHAINE  # indice dans TABLE_CONST_CHAINE
        return True
    
    def decl_const(self) -> bool:
        if (self.unilex == TokenType.MOTCLE and self.chaine == 'CONST') :
            self.lire_unilex()
            if (self.unilex == TokenType.IDENT) :
                nom_const = self.chaine 
                self.lire_unilex()
                if self.unilex == TokenType.EG : 
                    self.lire_unilex()
                    if (self.unilex == TokenType.ENT or self.unilex == TokenType.CH) :
                        if self.definir_constante(nom_const,self.unilex) :
                            self.lire_unilex() 
                            non_fin = True
                            while non_fin != False :
                                if (self.unilex == TokenType.VIRG) :
                                    self.lire_unilex()
                                    if (self.unilex == TokenType.IDENT) :
                                        nom_const = self.chaine
                                        self.lire_unilex()
                                        if (self.unilex == TokenType.EG) :
                                            self.lire_unilex()
                                            if (self.unilex == TokenType.ENT or self.unilex == TokenType.CH) :
                                                if self.definir_constante(nom_const,self.unilex) :
                                                    self.lire_unilex()
                                                    non_fin = True 
                                                else :
                                                    non_fin = False 
                                            else : 
                                                non_fin = False 
                                        else :
                                            non_fin = False
                                    else : 
                                        non_fin = False
                                else :
                                    non_fin = False 
                            if self.unilex == TokenType.PTVIRG :
                                self.lire_unilex()
                                return True
                            else :
                                erreur(self.lexer.num_ligne, "Erreur Syntaxique dans les déclarations de constante : point virgule attendu")
                                return False
                        else :
                            erreur(self.lexer.num_ligne, "Erreur Syntaxique dans les déclarations de constante : Indicateur déjà déclaré ")
                            return False
                    else :
                        erreur(self.lexer.num_ligne, "Erreur Syntaxique dans les déclarations de constante : Entier ou Chaine Attendu")
                        return False
                else :
                    erreur(self.lexer.num_ligne, "Erreur Syntaxique dans les déclarations de constante : symbole attendu")
                    return False
            else :
                erreur(self.lexer.num_ligne, "Erreur Syntaxique dans les déclarations de constante : Identificateur attendu")
                return False
        else :
            erreur(self.lexer.num_ligne, "Erreur Syntaxique dans les déclarations de constante : Mot clé Const Attendu")
            return False

    def decl_var(self) -> bool:
        global DERNIERE_ADRESSE_VAR_GLOB
        if not (self.unilex == TokenType.MOTCLE and self.chaine == 'VAR'):
            erreur(self.lexer.num_ligne, "Erreur syntaxique decl_var : mot-cle VAR attendu")
        self.lire_unilex()
        if self.unilex != TokenType.IDENT:
            erreur(self.lexer.num_ligne, "Erreur syntaxique decl_var : identificateur attendu")
        while True:
            nom = self.chaine
            if chercher(nom) != -1:
                erreur(self.lexer.num_ligne, f"Erreur semantique decl_var : identificateur '{nom}' deja declare")
            idx = inserer(nom)
            # Remplissage sémantique de l'entrée
            DERNIERE_ADRESSE_VAR_GLOB += 1
            TABLE_IDENT[idx].type   = 'variable'
            TABLE_IDENT[idx].typc   = 0         
            TABLE_IDENT[idx].adresse = DERNIERE_ADRESSE_VAR_GLOB
            TABLE_IDENT[idx].valeur  = None
            self.lire_unilex()
            if self.unilex == TokenType.VIRG:
                self.lire_unilex()
                if self.unilex != TokenType.IDENT:
                    erreur(self.lexer.num_ligne, "Erreur syntaxique decl_var : identificateur attendu apres virgule")
            else:
                break
        if self.unilex != TokenType.PTVIRG:
            erreur(self.lexer.num_ligne, "Erreur syntaxique decl_var : point-virgule attendu")
        self.lire_unilex()
        return True 

    def exp(self) -> bool :
        global CO,P_CODE,SOM_PILOP
        if not self.terme() :
            return False
        if self.unilex in (TokenType.PLUS, TokenType.DIVI, TokenType.MOINS, TokenType.MULTI) :
            # Mémoriser l'opérateur dans PILOP
            if not self.op_bin():
                return False
            # Générer le code de l'expression droite
            if not self.exp():
                return False
            # Dépiler et émettre l'instruction de l'opérateur
            P_CODE[CO] = PILOP[SOM_PILOP]
            SOM_PILOP -= 1
            CO += 1
        return True 
    
    def anasynt(self):
        self.lire_unilex()
        if self.prog() and self.unilex == TokenType.EOF:
            print("Le programme source est syntaxiquement correct")
        else:
            erreur(self.lexer.num_ligne, "Erreur syntaxique ")

def insere_table_mots_reserves(mot: str) -> None:
    i = 0
    while i < len(TABLE_MOTS_RESERVES) and TABLE_MOTS_RESERVES[i] < mot:
        i += 1
    TABLE_MOTS_RESERVES.insert(i, mot)


def initialiser(file_name: str) -> 'Lexiqueur':
    global DERNIERE_ADRESSE_VAR_GLOB, TABLE_IDENT, TABLE_INDEX, TABLE_MOTS_RESERVES
    global  P_CODE, MEM_VAR, PILEX, PILOP, CO, SOM_PILEX, SOM_PILOP
    DERNIERE_ADRESSE_VAR_GLOB = -1
    TABLE_IDENT = []
    TABLE_INDEX = []
    TABLE_MOTS_RESERVES = []
    P_CODE    = [0] * TAILLE_MAX_MEM
    MEM_VAR   = [0] * TAILLE_MAX_MEM
    PILEX     = [0] * TAILLE_MAX_MEM
    PILOP     = [0] * TAILLE_MAX_MEM
    CO        = 0
    SOM_PILEX = -1
    SOM_PILOP = -1
    
    # Insertion des mots-clés 
    insere_table_mots_reserves("CONST")
    insere_table_mots_reserves("DEBUT")
    insere_table_mots_reserves("ECRIRE")
    insere_table_mots_reserves("FIN")
    insere_table_mots_reserves("LIRE")
    insere_table_mots_reserves("PROGRAMME")
    insere_table_mots_reserves("VAR")
    insere_table_mots_reserves("ALORS")
    insere_table_mots_reserves("FAIRE")
    insere_table_mots_reserves("SI")
    insere_table_mots_reserves("SINON")
    insere_table_mots_reserves("TANTQUE")
    
    # Création du lexiqueur 
    lexer = Lexiqueur(file_name)
    return lexer


def terminer(lexer: 'Lexiqueur') -> None:
    lexer.terminer()

def creer_fichier_code(nom_fichier : str) -> None :
    """Crée un fichier .cod lisible avec le code généré"""
    import os
    base = os.path.splitext(nom_fichier)[0]
    nom_cod = base + '.cod'
    nb_vars = DERNIERE_ADRESSE_VAR_GLOB + 1
    with open(nom_cod, 'w', encoding='utf-8') as f:
        f.write(f"{nb_vars} mot(s) reservé(s) pour les variables globales\n\n")
        i = 0
        while i < CO:
            op = P_CODE[i]
            nom = NOM_OPCODE.get(op, str(op))
            if op == EMPI:
                f.write(f"EMPI {P_CODE[i+1]}\n")
                i += 2
            elif op == ALLE :
                f.write(f"ALLE {P_CODE[i+1]}\n")
                i += 2
            elif op == ALSN :
                f.write(f"ALSN {P_CODE[i+1]}\n")
                i += 2
            elif op == ECRC:
                i += 1
                chaine = ""
                while P_CODE[i] != FINC:
                    chaine += chr(P_CODE[i])
                    i += 1
                f.write(f"ECRC '{chaine}' FINC\n")
                i += 1  # sauter FINC
            else:
                f.write(f"{nom}\n")
                i += 1
    print(f"Code généré dans : {nom_cod}")

def interpreter() -> None :
    global P_CODE, PILEX, SOM_PILEX , MEM_VAR
    pc = 0 
    SOM_PILEX = -1 

    while P_CODE[pc] != STOP:
        op = P_CODE[pc]
        if op == EMPI : 
            #Empiler la valeur immédiate suivante
            SOM_PILEX += 1 
            PILEX[SOM_PILEX] = P_CODE[pc+1]
            pc += 2

        elif op == ALLE :
            pc = P_CODE[pc+1]
    
        elif op == ALSN :
            if PILEX[SOM_PILEX] == 0 :
                pc = P_CODE[pc+1]
            else :
                pc += 2
            SOM_PILEX -= 1 
        
        elif op == CONT : 
            PILEX[SOM_PILEX] = MEM_VAR[PILEX[SOM_PILEX]] 
            pc += 1 
        
        elif op == AFFE : 
            valeur  = PILEX[SOM_PILEX]
            adresse = PILEX[SOM_PILEX-1]
            MEM_VAR[adresse] = valeur
            SOM_PILEX -= 2
            pc += 1

        elif op == LIRE : 
            adresse = PILEX[SOM_PILEX]
            SOM_PILEX -= 1 
            try: 
                valeur = int(input("? "))
            except ValueError:
                print("Erreur : entier attendu")
                sys.exit(1)
            MEM_VAR[adresse] = valeur
            pc += 1

        elif op == ADDI:
            PILEX[SOM_PILEX-1] = PILEX[SOM_PILEX-1] + PILEX[SOM_PILEX]
            SOM_PILEX -= 1
            pc += 1
 
        elif op == MOIN:
            PILEX[SOM_PILEX-1] = PILEX[SOM_PILEX-1] - PILEX[SOM_PILEX]
            SOM_PILEX -= 1
            pc += 1
        
        elif op == MULT:
            PILEX[SOM_PILEX-1] = PILEX[SOM_PILEX-1]* PILEX[SOM_PILEX]
            SOM_PILEX -= 1 
            pc += 1

        elif op == DIVI :
            if PILEX[SOM_PILEX] == 0:
                print("Erreur : division par zéro")
                sys.exit(1)
            PILEX[SOM_PILEX-1] = PILEX[SOM_PILEX-1] // PILEX[SOM_PILEX]
            SOM_PILEX -= 1
            pc += 1

        elif op == ECRL:
            # Saut de ligne
            print()
            pc += 1
        
        elif op == ECRE:
            # Afficher l'entier au sommet de pile
            print(PILEX[SOM_PILEX], end='')
            SOM_PILEX -= 1
            pc += 1
        elif op == ECRC:
            # Afficher une chaîne en ASCII jusqu'à FINC
            pc += 1
            chaine = ""
            while P_CODE[pc] != FINC:
                chaine += chr(P_CODE[pc])
                pc += 1
            print(chaine, end='')
            pc += 1  # sauter FINC
 
        else:
            print(f"Erreur : opcode inconnu {op} à pc={pc}")
            sys.exit(1)

def analyser_syntaxiquement(nom_fichier: str):
    lexer = initialiser(nom_fichier)
    analyseur = Analyseur(lexer)
    analyseur.anasynt()
    terminer(lexer)
    affiche_table_ident()
    creer_fichier_code(nom_fichier)
    interpreter()
    print("\n=== Compilation terminée ===")

if __name__ == "__main__":
    # Analyse syntaxique complète du fichier Mini-Pascal
    analyser_syntaxiquement('bb.pas')