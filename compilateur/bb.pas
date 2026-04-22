PROGRAMME test;
VAR
    i,
    j; 
DEBUT
    i := 0;
    j := 10;
    SI i ALORS
        ECRIRE('i est non nul')
    SINON
        DEBUT
            ECRIRE('i est nul');
            TANTQUE j FAIRE
            DEBUT
                ECRIRE();
                SI 5-j ALORS 
                    ECRIRE(j);
                j := j - 1
            FIN
        FIN
FIN.