import json, random

dani = ['pon', 'uto', 'sre', 'cet', 'pet']

ucionice = []

class Termin():

    def __init__(self, ucionica, dan, sat, trajanje):
        self.ucionica = ucionica
        self.dan = dan
        self.sat = sat
        self.trajanje = trajanje

    def poklapanje(self, t):
        if self.ucionica != t.ucionica:
            return False

        if self.dan != t.dan:
            return False

        s_f = self.sat + self.trajanje
        t_f = t.sat + t.trajanje

        if s_f <= t.sat:
            return False 
        
        if self.sat >= t_f:
            return False

        if t_f <= self.sat:
            return False

        if t.sat >= s_f:
            return False
            
        return True

    def __eq__(self, t):
        if type(t) != Termin:
            raise ValueError('T mora biti tipa Termin!')

        if self.ucionica != t.ucionica:
            return False

        if self.dan != t.dan:
            return False

        if self.sat != t.sat:
            return False

        return True

    def __ne__(self, t):
        return not (self == t)

    def __lt__(self, t):
        s_i = dani.index(self.dan)
        t_i = dani.index(t.dan)

        if s_i > t_i:
            return False

        if s_i < t_i:
            return True

        if self.sat < t.sat:
            return True

        return False

    def __le__(self, t):
        s_i = dani.index(self.dan)
        t_i = dani.index(t.dan)

        if s_i > t_i:
            return False

        if s_i < t_i:
            return True

        if self.sat <= t.sat:
            return True

        return False

    def __gt__(self, t):
        return not self.__le__(t)

    def __ge__(self, t):
        return not self.__lt__(t)

    def __hash__(self):
        return hash((self.ucionica, self.dan, self.sat))

    def __repr__(self):
        return '{0} - {1}h, {2}'.format(self.dan.upper(), self.sat, self.ucionica)

    def __str__(self):
        return self.__repr__()

class Cas():

    def __init__(self, predmet, tip, nastavnik, grupe, m_ucionice, trajanje, termin):
        self.predmet = predmet
        self.tip = tip
        self.nastavnik = nastavnik
        self.grupe = grupe
        self.m_ucionice = m_ucionice
        self.trajanje = trajanje
        self.termin = termin

    def __eq__(self, c):
        if self.predmet != c.predmet:
            return False

        if self.tip != c.tip:
            return False

        if self.nastavnik != c.nastavnik:
            return False

        if ''.join(self.grupe) != ''.join(c.grupe):
            return False

        if self.m_ucionice != c.m_ucionice:
            return False

        if self.trajanje != c.trajanje:
            return False

        if self.termin != c.termin:
            return False

        return True

    def __ne__(self, c):
        return not (self == c)

    def __repr__(self):
        return f'{self.predmet} ({self.tip}), {self.nastavnik}, {self.termin}, {self.grupe}'
    
    def __str__(self):
        return self.__repr__()

class Hromozom():

    def __init__(self, casovi, raspored=None):
        if raspored is None:
            self.raspored = []

            for c in casovi:
                predmet = c['Predmet']
                tip = c['Tip']
                nastavnik = c['Nastavnik']
                grupe = c['Grupe']
                m_ucionice = c['Ucionica']
                trajanje = int(c['Trajanje'])

                ucionica = random.choice(ucionice[m_ucionice])
                dan = random.choice(dani)
                sat = random.randint(9, 21 - trajanje)
                termin = Termin(ucionica, dan, sat, trajanje)

                self.raspored.append(Cas(predmet, tip, nastavnik, grupe, m_ucionice, trajanje, termin))
        else:
            self.raspored = raspored.copy()

        self.fitnes = 0
        self.evaluacija()

    def evaluacija(self):
        kolizije = 0
        for i in range(len(self.raspored)):
            for j in range(len(self.raspored)):
                if i == j:
                    continue

                if self.raspored[i].termin.poklapanje(self.raspored[j].termin):
                    kolizije += 1

        self.fitnes = kolizije
        return self.fitnes

    def evaluacija2(self):
        kolizije = {}
        for c in self.raspored:
            if c.termin not in kolizije:
                kolizije[c.termin] = 0
            else:
                kolizije[c.termin] += 1

        self.fitnes = sum(kolizije.values()) 
        return self.fitnes

    def mutacija(self):
        casovi = [self.raspored.index(c) for c in random.choices(self.raspored, k=random.randint(1, 5))]
        for i in casovi:
            t = random.uniform(0, 1)
            cas = self.raspored[i]
            termin = Termin(cas.termin.ucionica, cas.termin.dan, cas.termin.sat, cas.termin.trajanje)
            if t < 0.5:
                termin.dan = random.choice(dani)
                termin.sat = random.randint(9, 21 - self.raspored[i].trajanje)
            else:
                termin.ucionica = random.choice(ucionice[cas.m_ucionice])

            self.raspored[i].termin = termin

        return

    def kopija(self):
        return Hromozom(None, raspored=self.raspored)

    def __repr__(self):
        return '\n'.join(map(str, self.raspored)) + f'\nKolizije: {self.fitnes}'

class Populacija():

    def __init__(self, mi, lm, casovi):
        self.mi = mi
        self.lm = lm
        self.hromozomi = [Hromozom(casovi) for i in range(self.mi + self.lm)]
        self.najbolji = self.hromozomi[0].kopija()

    def evaluacija(self):
        for h in self.hromozomi:
            h.evaluacija()
            if h.fitnes < self.najbolji.fitnes:
                self.najbolji = h.kopija()

        return

    def selekcija(self):
        self.hromozomi.sort(key=lambda h: h.fitnes)
        self.hromozomi = self.hromozomi[:self.mi]
        return

    def mutacija(self):
        novi = [random.choice(self.hromozomi).kopija() for _ in range(self.lm)]
        for h in novi:
            h.mutacija()
            self.hromozomi.append(h)

        return

if __name__ == '__main__':

    data = None
    with open('ulaz1.json', 'r') as f:
        data = json.load(f)

    ucionice = data['Ucionice']
    casovi = data['Casovi']

    p = Populacija(20, 60, casovi)
    
    for i in range(500):
        if p.najbolji.fitnes == 0:
            break
        
        p.selekcija()
        p.mutacija()
        p.evaluacija()

        if (i + 1) % 50 == 0:
            print(f'Najbolji hromozom u generaciji {i + 1}: {p.najbolji.fitnes}')

    p.najbolji.raspored.sort(key=lambda c: c.termin)
    print('Konacno resenje:', p.najbolji)
