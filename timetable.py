import json, random
from threading import Thread

dani = ['pon', 'uto', 'sre', 'cet', 'pet']

ulaz = 'ulaz1.json'
izlaz = 'izlaz1.json'
sacuvaj_rez = False

ucionice = None

debug = False

class S_Termin():

    def __init__(self, dan, sat, ucionica):
        self.dan = dan
        self.sat = sat
        self.ucionica = ucionica
        self.zauzet = False

    def __eq__(self, s):
        if self.dan != s.dan:
            return False

        if self.sat != s.sat:
            return False

        if self.ucionica != s.ucionica:
            return False

        return True

    def __hash__(self):
        return hash((self.dan, self.sat, self.ucionica))

    def __repr__(self):
        return f'{self.dan.upper()} {self.sat}h, {self.ucionica}'

    def __str__(self):
        return self.__repr__()

def svi_termini(s_termini):
    for k_u in ucionice:
        for ucionica in ucionice[k_u]:
            for dan in dani:
                for sat in range(9, 21):
                    s_termini.append(S_Termin(dan, sat, ucionica))

    return

def nadji_termin(s_termini, kod_ucionica, trajanje):
    for s_t in s_termini:
        nadjen = True

        if s_t.ucionica not in ucionice[kod_ucionica]:
            nadjen = False
            continue

        if s_t.sat + trajanje > 21:
            nadjen = False
            continue

        ind = s_termini.index(s_t)

        for i in range(trajanje):
            try:
                if s_termini[ind + i].zauzet:
                    nadjen = False
                    break
            except IndexError:
                nadjen = False
                break
        
        if nadjen:
            for i in range(trajanje):
                s_termini[ind + i].zauzet = True

            return s_t

    return None

class Termin():

    def __init__(self, predmet, tip, nastavnik, grupe, kod_ucionica, trajanje, s_termini):
        self.predmet = predmet
        self.tip = tip
        self.nastavnik = nastavnik
        self.grupe = grupe
        self.kod_ucionica = kod_ucionica
        self.trajanje = trajanje

        s_t = nadji_termin(s_termini, kod_ucionica, trajanje)
        self.dan = s_t.dan
        self.sat = s_t.sat
        self.ucionica = s_t.ucionica

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

    def __init__(self, casovi, raspored=None, s_termini=None):
        if raspored is None:
            self.raspored = []
            self.s_termini = list()
            svi_termini(self.s_termini)

            for c in casovi:
                #print(f'{casovi.index(c) + 1} / {len(casovi)}')
                predmet = c['Predmet']
                tip = c['Tip']
                nastavnik = c['Nastavnik']
                grupe = c['Grupe']
                kod_ucionica = c['Ucionica']
                trajanje = int(c['Trajanje'])
                
                self.raspored.append(Termin(predmet, tip, nastavnik, grupe, kod_ucionica, trajanje, self.s_termini))
        
            if debug:
                print('Slobodno:', sum([1 for s_t in self.s_termini if not s_t.zauzet]), '/', len(self.s_termini))

        else:
            self.raspored = raspored.copy()
            self.s_termini = s_termini.copy()

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
        for t_i in termini_ind:
            t = random.uniform(0, 1)
            if t < 0.8:
                while True:
                    ok = True
                    s_t = random.choice(self.s_termini)

                    if s_t.zauzet:
                        ok = False
                        continue

                    if s_t.ucionica not in ucionice[self.raspored[t_i].kod_ucionica]:
                        ok = False
                        continue

                    if s_t.sat + self.raspored[t_i].trajanje > 21:
                        ok = False
                        continue

                    i = self.s_termini.index(s_t)
                    for j in range(self.raspored[t_i].trajanje):
                        if self.s_termini[i + j].zauzet:
                            ok = False
                            break

                    if ok:
                        p_i = self.s_termini.index(S_Termin(self.raspored[t_i].dan, self.raspored[t_i].sat, self.raspored[t_i].ucionica))

                        self.raspored[t_i].dan = s_t.dan
                        self.raspored[t_i].sat = s_t.sat
                        self.raspored[t_i].ucionica = s_t.ucionica

                        for j in range(self.raspored[t_i].trajanje):
                            self.s_termini[i + j].zauzet = True
                            self.s_termini[p_i + j].zauzet = False

                        break                    

    def kopija(self):
        return Hromozom(None, raspored=self.raspored, s_termini=self.s_termini)

    def __repr__(self):
        return '\n'.join(map(str, sorted(self.raspored, key=lambda t: t)))


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
        self.casovi = casovi.copy()

    def run(self):
        i = 0
        for i in range(self.generacije):
            if self.populacija.najbolji.fitnes == 0:
                break

            self.populacija.selekcija()
            self.populacija.mutacija()
            self.populacija.evaluacija()

            #if (i + 1) % 50 == 0:
            print(f'Najbolji hromozom u generaciji {i + 1}: {self.populacija.najbolji.fitnes}')
        
        self.populacija.najbolji.raspored.sort(key=lambda t: t)    
        print(self.populacija.najbolji)
        print(f'Konacno resenje posle {i} generacija. Broj kolizija: {self.populacija.najbolji.fitnes}.')
        if sacuvaj_rez:
            with open('raspored3.txt', 'w') as f:
                f.write(str(self.populacija.najbolji))

            raspored = {'Raspored':[{'Predmet':t.predmet, 'Tip':t.tip, 'Nastavnik':t.nastavnik,\
                'Grupe':t.grupe, 'Termin':f'{t.dan} {t.sat}h-{t.sat + t.trajanje}, {t.ucionica}'}\
                for t in self.populacija.najbolji.raspored]}
            with open(izlaz, 'w') as f:
                json.dump(raspored, f, indent=4)

        return

if __name__ == '__main__':

    data = None
    with open(ulaz, 'r') as f:
        data = json.load(f)

    ucionice = data['Ucionice']
    casovi = data['Casovi']

    ga = GenetskiAlgoritam(4, 8, casovi, 500)
    ga.start()
