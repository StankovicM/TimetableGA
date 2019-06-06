import json, random
from threading import Thread

dani = ['pon', 'uto', 'sre', 'cet', 'pet']

ucionice = None

ulaz = 'ulaz3.json'
izlaz = 'izlaz2.json'
sacuvaj_rez = False

class Termin():

    def __init__(self, predmet, tip, nastavnik, grupe, kod_ucionica, trajanje):
        self.predmet = predmet
        self.tip = tip
        self.nastavnik = nastavnik
        self.grupe = grupe
        self.kod_ucionica = kod_ucionica
        self.trajanje = trajanje

        self.dan = random.choice(dani)
        self.sat = random.randint(9, 21 - self.trajanje)
        self.ucionica = random.choice(ucionice[kod_ucionica])

    def __repr__(self):
        return f'{self.predmet} ({self.tip}), {self.nastavnik}, {self.grupe}, {self.dan.upper()} {self.sat}h-{self.sat + self.trajanje}h, {self.ucionica}'

    def __str__(self):
        return self.__repr__()

    def __eq__(self, t):
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

def poklapanje_vremena(t1, t2):
    t1_s = t1.sat
    t1_f = t1.sat + t1.trajanje

    t2_s = t2.sat
    t2_f = t2.sat + t2.trajanje

    if t1.dan != t2.dan:
        return False

    if t1_f <= t2_s:
        return False 
    
    if t1_s >= t2_f:
        return False

    if t2_f <= t1_s:
        return False

    if t2_s >= t1_f:
        return False

    return True

def poklapanje_ucionica(t1, t2):
    if t1.ucionica != t2.ucionica:
        return False

    return True

def poklapanje_nastavnika(t1, t2):
    if t1.nastavnik != t2.nastavnik:
        return False

    return True

def poklapanje_grupa(t1, t2):
    for g in t1.grupe:
        if g in t2.grupe:
            return True

    return False

def poklapanje(t1, t2):
    poklapanja = 0

    if poklapanje_vremena(t1, t2):
        if poklapanje_ucionica(t1, t2):
            poklapanja += 1

        if poklapanje_nastavnika(t1, t2):
            poklapanja += 1

        if poklapanje_grupa(t1, t2):
            poklapanja += 1

    return poklapanja

class Hromozom():

    def __init__(self, casovi, raspored=None):
        if raspored is None:
            self.raspored = []

            for c in casovi:
                predmet = c['Predmet']
                tip = c['Tip']
                nastavnik = c['Nastavnik']
                grupe = c['Grupe']
                kod_ucionica = c['Ucionica']
                trajanje = int(c['Trajanje'])

                self.raspored.append(Termin(predmet, tip, nastavnik, grupe, kod_ucionica, trajanje))

        else:
            self.raspored = raspored.copy()

        self.fitnes = 0
        self.kolizije = set()
        self.evaluacija()

    def evaluacija(self):
        self.kolizije.clear()
        for i in range(len(self.raspored)):
            for j in range(len(self.raspored)):
                if i - j >= 0:
                    continue

                p = poklapanje(self.raspored[i], self.raspored[j])
                if p > 0:
                    self.fitnes += p
                    self.kolizije.add(j)

        return

    def mutacija(self):
        termini_ind = list(self.kolizije)
        for i in termini_ind:
            t = random.uniform(0, 1)
            if t < 0.5:
                self.raspored[i].dan = random.choice(dani)
                self.raspored[i].sat = random.randint(9, 21 - self.raspored[i].trajanje)
            else:
                self.raspored[i].ucionica = random.choice(ucionice[self.raspored[i].kod_ucionica])

        return

    def kopija(self):
        return Hromozom(None, raspored=self.raspored)

    def __repr__(self):
        return '\n'.join(map(str, self.raspored))


class Populacija():

    def __init__(self, mi, lm, casovi):
        self.mi = mi
        self.lm = lm
        self.hromozomi = [Hromozom(casovi.copy()) for i in range(self.mi + self.lm)]
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

class GenetskiAlgoritam(Thread):

    def __init__(self, mi, lm, casovi, gen):
        Thread.__init__(self)
        self.populacija = Populacija(mi, lm, casovi)
        self.generacije = gen

    def run(self):
        i = 0
        for i in range(self.generacije):
            if self.populacija.najbolji.fitnes == 0:
                break

            self.populacija.selekcija()
            self.populacija.mutacija()
            self.populacija.evaluacija()

            if (i + 1) % 50 == 0:
                print(f'Najbolji hromozom u generaciji {i + 1}: {self.populacija.najbolji.fitnes}')

        self.populacija.najbolji.raspored.sort(key=lambda t: t)    
        print(self.populacija.najbolji)
        print(f'Konacno resenje posle {i} generacija. Broj kolizija: {self.populacija.najbolji.fitnes}.')
        if sacuvaj_rez:
            raspored = {"Raspored":[{'Predmet':c.predmet, 'Tip':c.tip, 'Nastavnik':c.nastavnik, \
                'Grupe':c.grupe, 'Termin':str(c.termin)} for c in self.populacija.najbolji.raspored]}
            with open(izlaz, 'w') as f:
                json.dump(raspored, f, indent=4)

        return

if __name__ == '__main__':

    data = None
    with open(ulaz, 'r') as f:
        data = json.load(f)

    ucionice = data['Ucionice']
    casovi = data['Casovi']

    ga = GenetskiAlgoritam(4, 8, casovi, 5000)
    ga.start()
    