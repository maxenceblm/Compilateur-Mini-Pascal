PROGRAMME myApp; {this is a {nested} comment}
CONST
	x = 'a',
	b = 2;
VAR
	z, t;
DEBUT
	ECRIRE('Type a number: ');
	LIRE(t);
	z := t * b * 2;
	ECRIRE('Of block');
	DEBUT
		ECRIRE('In block');
		ECRIRE('Your number multiplied by 4'' is: ', z); {this is a {nested} comment in the block}
		z := z * z;
	FIN
	ECRIRE('Of block');
	ECRIRE('Your number multiplied by 4 then by itself is: ', z)
FIN.